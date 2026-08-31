import asyncio
import json
import logging
import os
import re
import textwrap

import httpx

from dotenv import load_dotenv
from livekit import api
from livekit.agents import (
    Agent,
    AgentServer,
    AudioConfig,
    BackgroundAudioPlayer,
    BuiltinAudioClip,
    AgentSession,
    JobContext,
    RunContext,
    ToolError,
    TurnHandlingOptions,
    cli,
    function_tool,
    inference,
    llm,
    mcp,
    room_io,
)
from livekit.plugins import ai_coustics

import opaque_backend
import pii
import store
from tasks import IdentifyCallerTask, ReturnIntakeTask, TroubleshootDeviceTask
from turn_latency import TurnLatency

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Flip to "blocking" to hear the same refund with no progress updates at all.
#   REFUND_MODE=blocking lk agent dev
REFUND_MODE = os.getenv("REFUND_MODE", "async")

# Where a human handoff dials out to. Point this at your own phone for the demo.
TRANSFER_TO_NUMBER = os.getenv("TRANSFER_TO_NUMBER", "+15125846942")
# Set this to a configured LiveKit outbound SIP trunk id to enable real dial-out.
# If unset, the transfer still summarises + hands off in-room (the web fallback).
SIP_OUTBOUND_TRUNK_ID = os.getenv("SIP_OUTBOUND_TRUNK_ID", "")

# Google's MCP Toolbox for Databases, serving the Cloud SQL toolset (see
# build-archive/deploy/aria-toolbox). Account, device registry and order lookups.
TOOLBOX_MCP_URL = os.getenv("TOOLBOX_MCP_URL", "")
# Orders are a plain REST call, not MCP — see get_recent_order / lookup_order.
ORDERS_API_URL = os.getenv(
    "ORDERS_API_URL", "https://aug24-web-549403515075.us-central1.run.app"
)
ORDERS_API_KEY = os.getenv("ORDERS_API_KEY", "")
# How long the specialist desk rings before we try the phone / in-room fallback.
DESK_RING_SECONDS = int(os.getenv("DESK_RING_SECONDS", "40"))
# Swappable in tests without touching httpx for the inference client.
_DeskClient = httpx.AsyncClient


def _mcp_result(ctx, on_identified=None) -> str:
    """Resolve an MCP tool result for the model.

    Also the one place identity is captured for guest callers: when an
    identification tool returns a row, the account number is recorded in agent
    state from the *verified result* — the model never gets to assert it later.

    An empty result (a SQL query that matched nothing) is a legitimate answer —
    "no such device" — not a failure. The SDK default raises a ToolError there,
    which made the model retry or guess. Turn it into something it can say.
    """
    content = ctx.result.content or []
    if len(content) == 1:
        if ctx.tool_name in ("lookup_account_by_phone", "lookup_account_by_number"):
            m = re.search(
                r'"account_number"\s*:\s*"(AH-\d{4})"',
                getattr(content[0], "text", "") or "",
            )
            if m and on_identified:
                on_identified(m.group(1))
        return str(content[0].model_dump_json())
    if len(content) > 1:
        return json.dumps([item.model_dump() for item in content])
    return json.dumps(
        {
            "found": False,
            "say": "Nothing matched. Tell the customer you cannot see that on their "
            "account and, if it was a device, list the devices they do have.",
        }
    )


# Our own MCP server: Firestore device telemetry + the policy corpus.
MCP_TELEMETRY_URL = os.getenv(
    "MCP_TELEMETRY_URL",
    "https://aug24-mcp-549403515075.us-central1.run.app/mcp",
)


class Assistant(Agent):
    def __init__(
        self,
        room_name: str = "",
        known_account: str = "",
        known_name: str = "",
        last_call: dict | None = None,
        preload: dict | None = None,
    ) -> None:
        self.room_name = room_name
        # Set when the caller signed in on the web: the token carried their account.
        self.known_account = known_account
        self.known_name = known_name
        # Set once a human has taken the call; end_call must not fire after that.
        self._handed_off = False
        # Set in the entrypoint so tools can publish data + call the SIP API.
        self._ctx: JobContext | None = None
        # order_number -> Ticket, so a retry reuses rather than duplicates
        self._timeout_tickets: dict[str, object] = {}
        # The identification task while it runs (guest path), and the full tool
        # set kept aside while scoped tools are gated.
        self._identify_task: IdentifyCallerTask | None = None
        self._all_tools: list = []
        # Two MCP servers, split by what the data actually is.
        #
        #   Toolbox   -> Cloud SQL : who is calling, what they own, what they bought.
        #                Google's MCP Toolbox for Databases serves these straight from
        #                declarative SQL in tools.yaml, so there is no data API to write.
        #   aug24-mcp -> Firestore : what each device is reporting right now, plus the
        #                policy corpus. Neither of those is SQL.
        #
        # They join on device_id: find_device comes from Postgres, get_device_state
        # from Firestore. "Is my thermostat active?" crosses both.
        #
        # Cloud Run scales to zero, and the default 5s session timeout expires during a
        # cold start — MCP init then fails and every tool is missing for the whole call.
        servers = [
            mcp.MCPServerHTTP(
                url=MCP_TELEMETRY_URL,
                transport_type="streamable_http",
                timeout=20,
                client_session_timeout_seconds=20,
                tool_result_resolver=self._resolve_mcp,
            )
        ]
        if TOOLBOX_MCP_URL:
            servers.insert(
                0,
                mcp.MCPServerHTTP(
                    url=TOOLBOX_MCP_URL,
                    transport_type="streamable_http",
                    timeout=20,
                    client_session_timeout_seconds=20,
                    tool_result_resolver=self._resolve_mcp,
                    # Orders are deliberately NOT taken from here — a one-line status
                    # lookup is an HTTP function tool, not an MCP round trip.
                    # Identification and ticketing only. Device and order reads are
                    # agent-side tools that inject the verified account themselves,
                    # and the database enforces the filter (secure views).
                    allowed_tools=[
                        "lookup_account_by_phone",
                        "lookup_account_by_number",
                        "file_ticket",
                    ],
                ),
            )
        else:
            logger.warning(
                "TOOLBOX_MCP_URL unset — no Cloud SQL tools, so the agent cannot "
                "look anyone up. Deploy aria-toolbox and set it."
            )
        self._mcp_servers = servers
        # What this customer called about last time (Firestore call memory), for
        # signed-in callers. Guests get it through the get_previous_calls tool.
        memory = ""
        if preload:
            memory += self._preload_text(preload)
        if last_call and last_call.get("summary"):
            memory = textwrap.dedent(
                f"""

                # Their previous call

                On {last_call.get("ended_at", "a recent day")[:10]} they called about:
                {last_call["summary"]}
                Open items then: {"; ".join(map(str, last_call.get("next_steps") or [])) or "none"}.
                If it is relevant to why they are calling now, acknowledge it in one
                natural sentence. Do not recite it, and never mention it if they are
                clearly calling about something new.
                """
            )

        # A signed-in web caller is already authenticated, so never make them prove
        # who they are a second time — that is the whole point of the login.
        identified = ""
        if known_account:
            identified = textwrap.dedent(
                f"""

                # This caller is already identified

                They signed in, so you already know who they are: {known_name},
                account {known_account}. Do NOT ask for a phone number or an account
                number — they have already proved who they are and asking again is the
                exact annoyance we removed.

                Instead, greet them by first name and say you can see their account,
                then ask what you can help with.
                """
            )

        super().__init__(
            mcp_servers=self._mcp_servers,
            # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
            # See all available models at https://docs.livekit.io/agents/models/llm/
            # Provider failover: if Gemma stalls or errors mid-call, the same
            # session continues on Gemini Flash instead of the call dying.
            llm=llm.FallbackAdapter(
                [
                    inference.LLM(model="google/gemma-4-31b-it"),
                    inference.LLM(model="google/gemini-2.5-flash"),
                ],
                attempt_timeout=6.0,
            ),
            instructions=textwrap.dedent(
                """\
                You are Ember, the voice support agent for Aria Home, a smart-home
                company.
                Aria Home sells connected devices — thermostats, cameras, door locks
                and sensors — plus a cloud video subscription. Customers reach you by
                phone or on the website.

                # First thing, every call

                Know who is calling before you answer anything about an account.
                Usually that is done for you — they signed in, or you confirmed
                their account at the start of the call. But if you do not yet
                know who they are, ask for their phone number or their Aria Home
                account number (it starts with "A H") and look it up with
                lookup_account_by_phone or lookup_account_by_number before
                anything else. Once identified, every customer tool is scoped to
                them automatically; you never pass an account number to a tool.
                If they cannot be found, keep helping with general questions and
                offer a ticket or a person. Call get_previous_calls once with their
                account number;
                if their last call is relevant, acknowledge it in one sentence,
                otherwise say nothing about it.

                # What you can do

                Use your tools for anything factual. Never guess an order status, a
                temperature, a date, or whether a device is on.

                - Devices: find_my_device with the caller's own words ("living room
                  thermostat", "back door") returns the device and its live state
                  in one call. my_devices lists everything they own. Then get_device_state with that device_id for
                  whether it is on and what it is reading right now — temperature,
                  locked, recording. For "has it been like this all day", use
                  get_device_history.
                - "My most recent order" or "where is my order": my_recent_order.
                  A specific order number: my_order. Both are scoped to the caller
                  automatically — you never pass an account number.
                - Policy questions — returns, refunds, warranty, subscription terms:
                  search_knowledge — call it once per question and answer from what
                  comes back. Never guess policy; always search. The policy
                  documents call the company "AnyCompany" — that is an old name.
                  Never say AnyCompany out loud; always say Aria Home.
                - A return, refund, money back, or "it arrived damaged":
                  start_return. It takes the details with the caller and tells
                  you what happens next — you never decide a refund yourself.
                - A device that is not working, offline, unresponsive, or
                  misbehaving: troubleshoot_device with the caller's words for it.
                  ("Is it on?" is a quick find_my_device, not troubleshooting.)
                - Warranty: check_warranty. Exactly where a package is right now:
                  track_package. Confirm the order number first.
                - When they ask for a person, are frustrated, or you cannot resolve it:
                  transfer_to_human. Compose a short summary first so the human is briefed.
                - If they ask you to remember something for next time — a preference,
                  a detail about their home — you MUST call the remember tool with
                  one plain sentence before you confirm. Never say you have noted
                  or will remember something unless the tool call happened; a
                  promise without the call loses the fact. To check what they
                  told us before, use recall.
                - When they say goodbye or the call is clearly finished: end_call.
                  Never end the call after a transfer — once a specialist has taken
                  over, stay silent unless the customer addresses you.

                # Numbers

                Read any order or account number back to confirm before acting on it.
                People read them slowly, in pieces, with pauses — wait until they have
                clearly finished. Use exactly the digits they say; never add or pad digits.

                # Output rules

                You are speaking out loud, so:
                - Plain speech only. No markdown, no lists, no symbols, no emoji.
                - One to three sentences. Ask one question at a time.
                - Say numbers digit by digit: "four eight two one", not "four thousand".
                - Say dates as words: "August thirtieth".

                # Manner

                Warm and efficient. Get to the answer. If an order is delayed or a
                device is offline, acknowledge it once, plainly, without over-apologising,
                then say what happens next.

                # How you sound (behaviours you can HEAR — not a mood)

                - Contractions always: "I'll", "that's", "you're". Never "I will
                  check that for you".
                - Start sentences with "So", "And", "Okay" sometimes — spoken
                  grammar, not written grammar.
                - Before a lookup, think out loud briefly: "Let me pull that up…",
                  "one sec…", then give the answer. Never go silent.
                - Loop back naturally: "Oh — and about that sensor you mentioned…"
                - If you missed something: "Sorry, I think I missed that — what
                  was the number?"
                - Emotional baseline: calm and settled. Save brightness for
                  genuinely good news ("Good news — it's out for delivery!") and
                  drop to steady and warmer when something's wrong. Never swing.
                - A soft "hmm" or "let's see" once in a while is human; more than
                  once in a couple of minutes is a tic. No "um, like" chains.

                Examples of the register (do not repeat these verbatim):
                BAD:  "Could you please provide me with your account number so I
                      can look into available options?"
                GOOD: "Sure — do you have your account number handy?"
                BAD:  "I have located your order. It is currently in transit and
                      is expected to arrive on September fourth."
                GOOD: "Okay, found it. So it's on the way — should be with you
                      September fourth."
                BAD:  "I apologise for the inconvenience this has caused you."
                GOOD: "Ah, that's annoying — let's get it sorted."

                Never leave a dead end. If you do not have something — a serial number,
                a detail that is not in your tools — say so in one sentence and offer a
                next step in the same breath: file a ticket so someone follows up, or
                put them through to a person. Then ask if there is anything else.

                Sound like a person, not a script. Use the customer's first name once
                early, not every sentence. Acknowledge what they said before answering
                ("Sure — let me check that"). Vary your phrasing; never repeat the same
                sentence twice in a call. And once more, because it matters: spoken
                grammar, contractions, think out loud before lookups, calm baseline —
                the "How you sound" list above is a hard requirement, not a vibe.

                When you are asked to greet, say hello first, then introduce yourself
                by name, warmly and briefly: "Hi there — thanks for calling Aria Home.
                This is Ember, and I'm glad to help." Do not open on the thank-you,
                and never re-introduce yourself later in the call.
                """
            )
            + identified
            + memory,
        )

    # ---------------------------------------------------------------- tools
    # The docstring teaches the model when to call each tool, so treat it as
    # prompt engineering rather than documentation.
    #
    # Note: account lookup, device state, room temperature, order lookup and
    # policy search all live on the GCP MCP server and are exposed to the model
    # automatically. The tools below are the ones that need to run *inside* the
    # agent — because they touch the live room (transfer) or demonstrate the
    # async progress patterns (refund, warranty, sync, tracking).

    def _resolve_mcp(self, ctx) -> str:
        """MCP results for this agent; captures identity from a verified lookup."""
        return _mcp_result(ctx, on_identified=self._identified)

    def _identified(self, account: str) -> None:
        if not self.known_account:
            self.known_account = account
            logger.info(f"identity captured from verified lookup: {account}")
        # Backstop: the verified row completes the identification task even if
        # the model forgets to call confirm_identity.
        if self._identify_task is not None:
            self._identify_task.identified(account)
        self._ungate_soon()

    # ------------------------------------------------ tool gating
    #
    # Parloa's "eligibility layer" in LiveKit terms: tools that read a customer's
    # data do not exist until the customer is known. Code decides what the model
    # may call; the model only chooses among what is eligible.

    GATED_TOOLS = frozenset(
        {
            "my_devices",
            "find_my_device",
            "my_recent_order",
            "my_order",
            "start_return",
            "troubleshoot_device",
            "check_warranty",
            "track_package",
        }
    )

    @staticmethod
    def _tool_name(t) -> str:
        info = getattr(t, "info", None)
        return getattr(info, "name", None) or getattr(t, "__name__", "") or ""

    def gated_tools(self) -> list:
        """The tool set for an unidentified caller."""
        return [t for t in self.tools if self._tool_name(t) not in self.GATED_TOOLS]

    async def gate_tools(self) -> None:
        self._all_tools = list(self.tools)
        await self.update_tools(self.gated_tools())
        logger.info(f"tools gated until identified: {len(self.tools)} visible")

    async def ungate_tools(self) -> None:
        if self._all_tools and len(self.tools) < len(self._all_tools):
            await self.update_tools(self._all_tools)
            logger.info(f"tools ungated: {len(self.tools)} visible")

    def _ungate_soon(self) -> None:
        if not self._all_tools or self._activity is None:
            return
        try:
            self._ungate_handle = asyncio.get_running_loop().create_task(
                self.ungate_tools()
            )
        except RuntimeError:  # no loop (unit tests); nothing to ungate yet
            pass

    async def _mcp_tools(self, *names: str) -> list:
        """Specific MCP tools, by name, from the already-connected servers — so a
        task can carry e.g. search_knowledge without seeing the other five."""
        out = []
        for server in self.mcp_servers or []:
            try:
                for t in await server.list_tools():
                    if self._tool_name(t) in names:
                        out.append(t)
            except Exception as err:
                logger.warning(f"could not list MCP tools from {server}: {err}")
        return out

    # ------------------------------------------------ lifecycle

    async def on_enter(self) -> None:
        """Signed-in callers are greeted by the entrypoint. Guests are handed to
        IdentifyCallerTask first: it owns the greeting and the two lookup tools,
        and nothing customer-scoped is reachable until it returns an account."""
        # Only in a live job (the entrypoint sets _ctx). Offline evals drive the
        # Assistant directly with session.run(), where a blocking on_enter task
        # has no caller to talk to.
        if self.known_account or self._ctx is None:
            return
        await self.gate_tools()
        lookups = await self._mcp_tools(
            "lookup_account_by_phone", "lookup_account_by_number"
        )
        if not lookups:
            logger.warning("no identification tools available — skipping identify task")
            await self.session.generate_reply(
                instructions="Greet the caller warmly as Ember from Aria Home and ask how you can help."
            )
            return
        self._identify_task = IdentifyCallerTask(
            lookups, self._verify_caller, chat_ctx=self.chat_ctx, model=self.llm
        )
        try:
            who = await self._identify_task
        finally:
            self._identify_task = None
        if who is None:
            logger.info("caller not identified/verified — general help only")
            await self.session.generate_reply(
                instructions=(
                    "Say you were not able to verify the account, that you can "
                    "still help with general questions, and offer to file a ticket "
                    "or connect them to a person. Do not share any account "
                    "details. One or two sentences."
                )
            )
            return
        self.known_account = who.account
        self.known_name = who.first_name or self.known_name
        await self.ungate_tools()
        await self.session.generate_reply(
            instructions="Ask what you can help with today. One sentence."
        )

    # ------------------------------------------------ tasks
    #
    # Bounded sub-workflows (see tasks.py). Each hides its own tools from every
    # other turn and returns a typed result that code — not the model — acts on.

    async def _lookup_order_for_task(self, order_number: str = "") -> dict:
        if order_number.strip():
            return await self.my_order(None, order_number)
        return await self.my_recent_order(None)

    @function_tool
    async def start_return(
        self, context: RunContext, order_number: str = "", reason: str = ""
    ):
        """Start a return or refund for one of the caller's orders.

        Use this the moment the caller wants to return something, get money back,
        or says an item arrived damaged, defective or wrong. It takes the details
        with them and decides what happens next.

        Args:
            order_number: the order number if they already said it, else empty.
            reason: what they said is wrong, if anything, else empty.
        """
        policy = await self._mcp_tools("search_knowledge")
        result = await ReturnIntakeTask(
            self._lookup_order_for_task,
            policy_tools=policy,
            chat_ctx=self.chat_ctx,
            order_hint=order_number,
            reason_hint=reason,
            model=self.llm,
        )
        logger.info(f"return intake -> {result}")
        if result.next == "person":
            return await self._transfer(
                context,
                f"{self.known_name or 'The caller'} asked for a person during a return.",
                "the refunds team",
            )
        if result.next == "abandoned":
            return {"ok": True, "say": "Say no problem, and ask what else you can do."}
        if result.next == "refund_desk":
            summary = (
                f"{self.known_name or 'The caller'} wants to return order "
                f"{result.order_id} ({result.item}, {result.status}): {result.condition}. "
                f"They said: {result.reason} Inside the return window: "
                f"{'yes' if result.within_window else 'no'}. Needs a refund decision."
            )
            return await self._transfer(context, summary, "the refunds team")
        if result.next == "declined":
            return {
                "ok": False,
                "order": result.order_id,
                "say": (
                    f"Tell them order {result.order_id} is outside its return "
                    f"window (thirty days from delivery; fourteen for locks and "
                    f"doorbell cameras), and offer "
                    "to file a ticket so a specialist can review it as an exception."
                ),
            }
        return {
            "ok": False,
            "say": "Say you could not confirm the delivery date and offer to file a "
            "ticket so someone follows up.",
        }

    @function_tool
    async def troubleshoot_device(self, context: RunContext, description: str):
        """Work through a device that is not working, offline, unresponsive, or
        misbehaving, to a conclusion.

        Args:
            description: the device in the caller's words, e.g. "hallway sensor".
        """
        tools = await self._mcp_tools(
            "get_device_state", "get_device_history", "search_knowledge"
        )
        result = await TroubleshootDeviceTask(
            lambda d: self.find_my_device(None, d),
            telemetry_tools=tools,
            chat_ctx=self.chat_ctx,
            description=description,
            model=self.llm,
        )
        logger.info(f"troubleshoot -> {result}")
        if result.next == "person":
            return await self._transfer(
                context,
                f"{self.known_name or 'The caller'} asked for a person while "
                f"troubleshooting {description}.",
                "device support",
            )
        if result.next == "done":
            return {
                "ok": True,
                "say": "Say you are glad it is sorted, and ask what else you can do.",
            }
        if result.next == "ticket":
            return {
                "ok": False,
                "device": result.name,
                "finding": result.finding,
                "say": (
                    "Say it did not resolve, that you will file a ticket so a "
                    "specialist follows up, and offer to connect them to a person "
                    "now if they prefer. Use file_ticket with the finding."
                ),
            }
        return {"ok": True, "say": "Ask what else you can help with."}

    @staticmethod
    def _preload_text(pre: dict) -> str:
        """Render the preloaded home into instructions: devices with live state,
        the latest order, and long-term memories. Fetched in parallel with
        session start, so the first answer needs no tool call."""
        lines = ["", "", "# What you already know about this caller", ""]
        devs = pre.get("devices") or []
        if devs:
            lines.append("Devices (live state, read just now):")
            for d in devs:
                state = "on" if d.get("on") else "NOT reporting"
                lines.append(
                    f"- {d['name']} in the {d['room']} (device_id {d['device_id']}): "
                    f"{state}, {d.get('reading')}"
                )
        order = pre.get("recent_order")
        if order:
            lines.append(
                f"Most recent order: {order['order_id']} — {order['item']}, {order['status']}"
                + (f", due {order['delivers_on']}" if order.get("delivers_on") else "")
                + f". {order.get('detail') or ''}"
            )
        mems = pre.get("memories") or []
        if mems:
            lines.append("Things they have told us before (long-term memory):")
            lines += [f"- {m['fact']}" for m in mems[:8]]
        lines.append(
            "Answer from this directly when it covers the question; only call a tool "
            "for something not listed or to re-check a live reading if they doubt it. "
            "If they ask you to remember something, you MUST call the remember tool "
            "before confirming — never just say you noted it."
        )
        return "\n".join(lines) + "\n"

    # ------------------------------------------------ handoff brief (LLM)
    #
    # Before a human takes the call we ask the model for a structured brief —
    # not just a summary but what to do next and how the caller is feeling.
    # It is spoken to the specialist by the transfer agent and shown on screen.

    BRIEF_PROMPT = textwrap.dedent(
        """\
        You are preparing a handoff brief for a human Aria Home support
        specialist who is about to take over this call. Read the conversation
        and answer ONLY with compact JSON, no prose, with these keys:
          "summary":    2-3 sentences — who the caller is, what they asked, what
                        was resolved so far, and why they need a person.
          "next_steps": a list of 1-3 short imperative actions for the specialist.
          "mood":       one of "calm", "frustrated", "worried", "upset", "happy".
          "urgency":    one of "low", "normal", "high".
        Never invent facts that are not in the conversation.
        """
    )

    async def _handoff_brief(self, fallback_summary: str) -> dict:
        """Ask the LLM for a structured brief from the live chat context."""
        brief = {
            "summary": fallback_summary,
            "next_steps": [],
            "mood": "calm",
            "urgency": "normal",
        }
        try:
            ctx = self.chat_ctx.copy()
            ctx.add_message(role="system", content=self.BRIEF_PROMPT)
            ctx.add_message(role="user", content="Produce the handoff brief JSON now.")
            text = ""
            async with self.llm.chat(chat_ctx=ctx) as stream:
                async for chunk in stream:
                    delta = getattr(chunk, "delta", None)
                    if delta and getattr(delta, "content", None):
                        text += delta.content
            start, end = text.find("{"), text.rfind("}")
            if start >= 0 and end > start:
                parsed = json.loads(text[start : end + 1])
                if isinstance(parsed, dict):
                    brief.update({k: parsed[k] for k in brief if k in parsed})
        except Exception as err:
            logger.warning(
                f"handoff brief generation failed ({err}); using tool summary"
            )
        if not isinstance(brief.get("next_steps"), list):
            brief["next_steps"] = [str(brief["next_steps"])]
        return brief

    @staticmethod
    def _brief_for_speech(brief: dict) -> str:
        steps = "; ".join(str(x) for x in brief.get("next_steps") or []) or "none"
        return (
            f"{brief['summary']} Caller mood: {brief['mood']}. "
            f"Urgency: {brief['urgency']}. Suggested next steps: {steps}."
        )

    async def _ring_desk(self, department: str, brief: dict) -> str:
        """Post the handoff to the specialist desk and wait for accept/decline.

        Returns "accepted", "declined", or "unanswered". Never raises — a desk
        that is down simply means we fall through to the next transfer path.
        """
        if not ORDERS_API_KEY:
            return "unanswered"
        payload = {
            "room": self._ctx.room.name if self._ctx is not None else "",
            "department": department,
            "brief": brief,
            "caller": {"name": self.known_name, "account": self.known_account},
        }
        try:
            async with _DeskClient(base_url=ORDERS_API_URL, timeout=8.0) as c:
                r = await c.post(
                    "/api/handoffs", json=payload, headers={"X-Api-Key": ORDERS_API_KEY}
                )
                r.raise_for_status()
                hid = r.json()["id"]
                logger.info(f"desk: ringing handoff {hid}")
                for _ in range(DESK_RING_SECONDS // 2):
                    await asyncio.sleep(2)
                    st = await c.get(
                        f"/api/handoffs/{hid}", headers={"X-Api-Key": ORDERS_API_KEY}
                    )
                    status = st.json().get("status") if st.status_code == 200 else None
                    if status in ("accepted", "declined"):
                        logger.info(f"desk: handoff {hid} {status}")
                        return status
        except Exception as err:
            logger.warning(
                f"desk unreachable ({err}); continuing to next transfer path"
            )
        return "unanswered"

    @function_tool
    async def transfer_to_human(
        self, context: RunContext, summary: str, department: str = "the support team"
    ):
        """Transfer the caller to a human agent, handing them a summary of the call.

        Use this when the customer asks for a person, when they are clearly
        frustrated, or when you cannot resolve their problem. Compose the summary
        BEFORE calling so the human picks up already briefed and the customer does
        not have to repeat themselves.

        Args:
            summary: two or three sentences — who the caller is, what they asked
                about, what was resolved so far, and why they need a human.
            department: which team to route to, e.g. "the subscription team".
        """
        return await self._transfer(context, summary, department)

    async def _transfer(self, context: RunContext, summary: str, department: str):
        ctx = self._ctx
        # Bridge the wait with an immediate line, then protect the handoff: a
        # cough or "hello?" while the desk is ringing must not cancel it.
        if context is not None:
            try:
                await context.session.say(
                    "One moment — I'm bringing in a specialist and passing along "
                    "a summary so you won't have to repeat yourself."
                )
                context.disallow_interruptions()
            except Exception as err:
                logger.info(f"transfer preamble skipped: {err}")
        brief = pii.mask_brief(await self._handoff_brief(summary))
        logger.info("TRANSFER -> %s\n  BRIEF: %s", department, json.dumps(brief))

        # 1. Hand the summary to the web frontend — it renders in the summary
        #    panel, so a human watching the screen is briefed instantly.
        if ctx is not None:
            try:
                payload = json.dumps(
                    {
                        "type": "handoff",
                        "department": department,
                        "summary": brief["summary"],
                        "next_steps": brief["next_steps"],
                        "mood": brief["mood"],
                        "urgency": brief["urgency"],
                    }
                ).encode()
                await ctx.room.local_participant.publish_data(
                    payload, reliable=True, topic="summary"
                )
            except Exception as err:
                logger.warning(f"could not publish summary to frontend: {err}")

        # 2a. Ring the specialist desk (the web "human agent" console). The desk
        #     shows the brief and, on Accept, joins this room as a participant —
        #     the participant_connected handler then steps the agent back.
        desk_answer = await self._ring_desk(department, brief)
        if desk_answer == "accepted":
            self._handed_off = True
            return {
                "transferred": True,
                "say": "Tell the customer a specialist has picked up and has the "
                "summary in front of them, then stop talking.",
            }
        if desk_answer == "declined":
            return {
                "transferred": False,
                "say": "Tell the customer no specialist is free right now, apologise "
                "once, and offer to file a ticket so someone calls them back.",
            }

        # 2b. Warm transfer, when an outbound trunk exists: LiveKit's prebuilt
        #    WarmTransferTask holds the caller, dials the human into a private
        #    consult room, briefs them from the conversation so far, then merges
        #    the two. If nobody answers it returns to the caller. Without a trunk
        #    we keep the in-room handoff (summary on screen, specialist joins).
        if ctx is not None and SIP_OUTBOUND_TRUNK_ID and TRANSFER_TO_NUMBER:
            try:
                from livekit.agents.beta.workflows import WarmTransferTask

                logger.info(f"warm transfer: dialing {TRANSFER_TO_NUMBER}")
                result = await WarmTransferTask(
                    sip_call_to=TRANSFER_TO_NUMBER,
                    sip_trunk_id=SIP_OUTBOUND_TRUNK_ID,
                    chat_ctx=self.chat_ctx,
                    ringing_timeout=30.0,
                    extra_instructions=(
                        "You are briefing a human Aria Home specialist before "
                        "connecting the caller. Open with this brief, then ask if "
                        "they are ready to take the call: "
                        + self._brief_for_speech(brief)
                    ),
                )
                logger.info(f"warm transfer result: {result}")
                return {
                    "transferred": True,
                    "say": "The specialist is on the line and has been briefed. "
                    "Introduce them in one sentence, then stop talking.",
                }
            except Exception as err:
                logger.warning(f"warm transfer failed ({err}); using in-room fallback")
        else:
            logger.info(
                "No outbound trunk — summary delivered to the frontend; "
                "a specialist can join the room to take over."
            )

        return {
            "transferred": True,
            "say": (
                f"Tell the customer you are connecting them to {department} now, that "
                "you have passed along a summary so they will not need to repeat "
                "anything, then stop talking and wait."
            ),
        }

    # ------------------------------------------------ orders: plain HTTP tools
    #
    # Not every integration wants MCP. Order status is a single REST lookup, so
    # these are ordinary function tools over HTTP: less machinery, one fewer
    # round trip, and the shape a customer's existing order API already has.

    _http: httpx.AsyncClient | None = None

    def _client(self) -> httpx.AsyncClient:
        """One client per agent (per job): keeps the TLS connection to the orders
        API warm instead of paying a handshake on every lookup."""
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(base_url=ORDERS_API_URL, timeout=8.0)
        return self._http

    async def _orders_api(self, path: str, **params) -> dict:
        r = await self._client().get(
            path, params=params, headers={"X-Api-Key": ORDERS_API_KEY}
        )
        if r.status_code == 404:
            return {"found": False}
        r.raise_for_status()
        return r.json()

    # ------------------------------------------------ scoped reads (RLS)
    #
    # The account comes from self.known_account — set from the LiveKit token for
    # signed-in callers, or captured from the verified identification result for
    # guests. It is sent as a header; the model never supplies it, and the
    # database only ever answers through views filtered by that account.

    async def _verify_caller(
        self, account: str, email: str = "", phone: str = ""
    ) -> bool:
        """Server-side KBA check: code compares, the model only learns pass/fail."""
        r = await self._client().post(
            "/api/verify",
            json={"account": account, "email": email, "phone": phone},
            headers={"X-Api-Key": ORDERS_API_KEY},
        )
        r.raise_for_status()
        return bool(r.json().get("verified"))

    async def _my(self, path: str, **params) -> dict:
        if not self.known_account:
            return {
                "found": False,
                "say": "Identify the caller first with "
                "lookup_account_by_phone or lookup_account_by_number.",
            }
        r = await self._client().get(
            path,
            params=params,
            headers={"X-Api-Key": ORDERS_API_KEY, "X-Account": self.known_account},
        )
        r.raise_for_status()
        return r.json()

    @function_tool
    async def my_devices(self, context: RunContext):
        """List the caller's devices with what each is doing right now.

        No arguments — it is scoped to the identified caller automatically.
        """
        try:
            data = await self._my("/api/my/devices")
        except Exception as err:
            logger.error(f"my_devices failed: {err}")
            return {
                "found": False,
                "say": "Tell them the device system is not reachable.",
            }
        if not data.get("found", True) or not data.get("devices"):
            return (
                {**data, "found": False}
                if "say" in data
                else {"found": False, "say": "No devices on this account."}
            )
        logger.info(f"my_devices({self.known_account}) -> {len(data['devices'])}")
        return {"found": True, "devices": data["devices"]}

    @function_tool
    async def find_my_device(self, context: RunContext, description: str):
        """Find one of the caller's devices and read its live state.

        Use for "is my thermostat on?", "what's the living room temperature?",
        "is the back door locked?". Every word you pass must match the device, so
        use the caller's own words: "living room thermostat", "hallway sensor".

        Args:
            description: the room, device type or name, as the caller said it.
        """
        try:
            data = await self._my("/api/my/devices", search=description)
        except Exception as err:
            logger.error(f"find_my_device failed: {err}")
            return {
                "found": False,
                "say": "Tell them the device system is not reachable.",
            }
        if "say" in data and not data.get("devices"):
            return data
        devs = data.get("devices") or []
        if not devs:
            return {
                "found": False,
                "say": f"There is no {description} on this account. "
                "Say so plainly and list what they do have if helpful.",
            }
        d = devs[0]
        logger.info(
            f"find_my_device({self.known_account}, {description!r}) -> {d['device_id']} {d['reading']}"
        )
        return {"found": True, **d, "as_of": "just now"}

    @function_tool
    async def my_recent_order(self, context: RunContext):
        """The caller's most recent order and its status. No arguments."""
        try:
            data = await self._my("/api/my/orders")
        except Exception as err:
            logger.error(f"my_recent_order failed: {err}")
            return {
                "found": False,
                "say": "Tell them the order system is not reachable.",
            }
        if "say" in data and not data.get("orders"):
            return data
        orders = data.get("orders") or []
        if not orders:
            return {"found": False, "say": "There are no orders on this account."}
        logger.info(f"my_recent_order({self.known_account}) -> {orders[0]['order_id']}")
        return {
            "found": True,
            **orders[0],
            "older_orders": len(orders) - 1,
            "say": "Say the item and the status plainly, and the date as words.",
        }

    @function_tool
    async def my_order(self, context: RunContext, order_number: str):
        """One of the caller's orders by the number they read out.

        Use exactly the digits they say; never pad them. Only this caller's
        orders are visible.

        Args:
            order_number: digits only, e.g. "58130".
        """
        digits = "".join(c for c in order_number if c.isdigit())
        try:
            data = await self._my("/api/my/orders")
        except Exception as err:
            logger.error(f"my_order failed: {err}")
            return {
                "found": False,
                "say": "Tell them the order system is not reachable.",
            }
        for o in data.get("orders") or []:
            if o["order_id"] == digits:
                return {"found": True, **o}
        return {
            "found": False,
            "say": "No order with that number on this account. "
            "Ask them to check it; never pad the digits.",
        }

    # ------------------------------------------------ call memory
    #
    # LiveKit keeps the conversation only for the length of the job. At hang-up we
    # write the full call — masked transcript, tool calls, and the LLM brief — to
    # Firestore through the web service, so the next call can start informed.

    @staticmethod
    def _account_from_history(history) -> str:
        """Find the account number an identification tool returned, if any."""
        for item in getattr(history, "items", []):
            if getattr(item, "type", "") == "function_call_output":
                out = str(getattr(item, "output", "") or "")
                m = pii._ACCOUNT.search(out)
                if m and "account_number" in out:
                    raw = re.search(r"AH[\s-]?(\d{4})", out, re.I)
                    if raw:
                        return f"AH-{raw.group(1)}"
        return ""

    def call_record(self, history, outcome: str = "completed") -> dict:
        """Everything worth keeping from this call, PII-masked."""
        transcript, tool_calls = [], []
        for item in getattr(history, "items", []):
            kind = getattr(item, "type", "")
            if kind == "message":
                text = getattr(item, "text_content", None) or ""
                if text:
                    transcript.append({"role": item.role, "text": text})
            elif kind == "function_call":
                tool_calls.append(
                    {
                        "tool": getattr(item, "name", ""),
                        "args": pii.mask(str(getattr(item, "arguments", "")))[:300],
                    }
                )
        return {
            "room": self.room_name,
            "outcome": outcome,
            "transcript": pii.mask_transcript(transcript),
            "tool_calls": tool_calls,
            "turns": sum(1 for t in transcript if t["role"] == "user"),
        }

    async def save_call_memory(self, history) -> None:
        account = self.known_account or self._account_from_history(history)
        if not account or not ORDERS_API_KEY:
            logger.info("call memory: no identified account, nothing saved")
            return
        record = self.call_record(
            history, "transferred" if self._handed_off else "completed"
        )
        fallback = (
            f"Call with {self.known_name or 'the customer'} on account {account}."
        )
        brief = pii.mask_brief(await self._handoff_brief(fallback))
        record.update(
            {k: brief.get(k) for k in ("summary", "next_steps", "mood", "urgency")}
        )
        record["account_number"] = account
        try:
            r = await self._client().post(
                "/api/calls", json=record, headers={"X-Api-Key": ORDERS_API_KEY}
            )
            logger.info(f"call memory saved for {account}: {r.status_code}")
        except Exception as err:
            logger.warning(f"call memory not saved: {err}")

    @function_tool
    async def end_call(self, context: RunContext):
        """End the call once the customer is done.

        Use this only after they have said goodbye or confirmed there is nothing
        else — never mid-conversation. Say a short warm goodbye first; the room
        closes a moment after you finish speaking.
        """
        ctx = self._ctx
        if self._handed_off:
            logger.info("END CALL refused: a specialist has the call")
            return {
                "ok": False,
                "say": "Do not end the call. A specialist is handling it now; stay "
                "silent unless the customer speaks to you directly.",
            }
        logger.info("END CALL requested by the model")

        async def _close() -> None:
            # Let the goodbye finish playing before the room goes away.
            await asyncio.sleep(4)
            if ctx is not None:
                try:
                    await ctx.api.room.delete_room(
                        api.DeleteRoomRequest(room=ctx.room.name)
                    )
                except Exception as err:
                    logger.warning(f"could not close room: {err}")

        asyncio.create_task(_close())
        return {
            "ok": True,
            "say": "Thank them for calling Aria Home warmly, wish them a good "
            "rest of their day by name, then stop talking.",
        }

    @function_tool
    async def check_warranty(self, context: RunContext, order_number: str):
        """Check whether the device on an order is still under warranty.

        Use this when the customer asks about warranty, coverage, or whether a
        repair would be free.

        Args:
            order_number: the order number.
        """
        digits = store.normalize_order_id(order_number)
        record = opaque_backend.WARRANTY.get(digits)
        if record is None:
            return {"found": False, "say": "No warranty record for that order."}

        await context.update(
            f"Checking the warranty on order {digits} with the manufacturer now."
        )

        took = opaque_backend.warranty_latency()
        logger.info(f"warranty: opaque call will take {took}s")
        try:
            async with asyncio.timeout(10):
                await opaque_backend.opaque_call("warranty.get", seconds=took)
        except (asyncio.TimeoutError, opaque_backend.BackendTimeout) as err:
            raise ToolError(
                "The warranty system is not responding. Tell the customer you "
                "cannot check it right now and offer to follow up."
            ) from err

        return {
            "found": True,
            "covered": record["covered"],
            "plan": record["plan"],
            "expires": record["expires"],
        }

    @function_tool
    async def track_package(self, context: RunContext, order_number: str):
        """Get live tracking detail for a shipped order from the carrier.

        Use this when the customer wants to know exactly where their package is
        right now, beyond the basic status.

        Args:
            order_number: the order number.
        """
        digits = store.normalize_order_id(order_number)
        order = store.get_order(digits)
        if order is None or not order.tracking:
            return {"ok": False, "say": "No tracking available for that order."}

        await context.update(
            f"Getting live tracking for order {digits} from the carrier."
        )

        holding = [
            "Still waiting on the carrier.",
            "They are being slow today, bear with me.",
            "This is taking longer than it should. Almost there.",
        ]

        took = opaque_backend.carrier_latency()
        logger.info(
            f"tracking: carrier will take {took}s ({'SLOW' if took > 5 else 'fast'} path)"
        )

        try:
            async with context.with_filler(
                lambda step: holding[step],
                delay=3.5,
                interval=4,
                max_steps=len(holding),
            ):
                async with asyncio.timeout(13):
                    await opaque_backend.opaque_call(
                        "carrier.track", seconds=took, timeout=20
                    )

        except (asyncio.TimeoutError, opaque_backend.BackendTimeout) as err:
            # Idempotency: without this the model retries on ToolError, pays the
            # full timeout again, and files ANOTHER ticket.
            ticket = self._timeout_tickets.get(digits)
            if ticket is None:
                ticket = store.create_ticket(
                    digits, "Carrier tracking timed out; send an update to the customer"
                )
                self._timeout_tickets[digits] = ticket
                logger.info(f"tracking: timed out, filed {ticket.ticket_id}")
            else:
                logger.info(f"tracking: timed out again, reusing {ticket.ticket_id}")

            raise ToolError(
                f"The carrier is not responding and a retry will not help. "
                f"Do NOT call this tool again for this order. Tell the customer "
                f"you have logged ticket {ticket.ticket_id}, they will get an "
                f"update by text, and then move the conversation on."
            ) from err

        return {
            "ok": True,
            "status": order.status,
            "detail": order.detail,
            "expected": store.spoken_date(order.delivers_on),
            "took_seconds": took,
        }


# Session behaviour, reviewed as a set (see tests/test_review_findings.py):
#   user_away_timeout        the caller has gone quiet — check on them rather than
#                            sit in silence
#   resume_false_interruption a cough or "mm-hm" mid-sentence must not derail the
#                            answer; the agent picks up where it left off
#   preemptive_generation    start the reply before end-of-turn is confirmed
SESSION_OPTIONS = dict(
    user_away_timeout=15.0,
    turn_handling=TurnHandlingOptions(
        turn_detection=inference.TurnDetector(),
        interruption={
            "mode": "adaptive",
            "resume_false_interruption": True,
            "false_interruption_timeout": 1.0,
        },
        preemptive_generation={"enabled": True},
    ),
)

server = AgentServer()


@server.rtc_session(agent_name="anycompany-agent")
async def my_agent(ctx: JobContext):
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Voice pipeline: AssemblyAI STT, Gemma LLM, Fish Audio TTS, LiveKit turn detector.
    session = AgentSession(
        # Provider failover on the speech legs too: an STT or TTS outage falls
        # through to a second provider inside the same call.
        stt=inference.STT(
            model="assemblyai/universal-3-5-pro",
            language="en",
            fallback=["deepgram/nova-3"],
        ),
        tts=inference.TTS(
            model="fishaudio/s2.1-pro",
            # "Sarah — an engaged speaker": LiveKit's curated female voice for
            # this model. Staying on Fish Audio keeps expressive mode rendering.
            voice="933563129e564b19a115bedd57b7406a",
            fallback=["cartesia/sonic-3"],
        ),
        expressive=True,
        # identify → list_devices → find_device → get_device_state is 4 chained
        # steps; 3 forced retries and guessed ids. 6 leaves headroom, still bounded.
        max_tool_steps=6,
        **SESSION_OPTIONS,
    )

    # The web app signs the caller in with Firebase and puts their Aria Home account
    # on the LiveKit token as a participant attribute, so we know who this is before
    # anyone speaks. Phone callers arrive without attributes and get identified by ANI
    # the usual way.
    known_account = known_name = ""
    try:
        participant = await ctx.wait_for_participant()
        attrs = dict(getattr(participant, "attributes", {}) or {})
        known_account = attrs.get("aria_account", "")
        known_name = attrs.get("aria_name", "") or (participant.name or "")
        if known_account:
            logger.info(f"authenticated caller: {known_name} ({known_account})")
        else:
            logger.info("caller not pre-identified — will ask for phone or account")
    except Exception as err:
        logger.warning(f"could not read caller attributes: {err}")

    async def _preload(account: str) -> dict | None:
        """Profile + devices + latest order + last call + memories in one call.
        Runs concurrently with session start so it costs the greeting nothing."""
        if not (account and ORDERS_API_KEY):
            return None
        try:
            async with _DeskClient(base_url=ORDERS_API_URL, timeout=6.0) as c:
                r = await c.get(
                    "/api/preload",
                    params={"account": account},
                    headers={"X-Api-Key": ORDERS_API_KEY},
                )
                if r.status_code == 200:
                    data = r.json()
                    logger.info(
                        f"preload: {len(data.get('devices', []))} devices, "
                        f"{len(data.get('memories', []))} memories, "
                        f"last call {'yes' if data.get('last_call') else 'no'}"
                    )
                    return data
        except Exception as err:
            logger.warning(f"preload unavailable: {err}")
        return None

    # Create the agent first so we can hand it the JobContext — the transfer
    # tool needs the live room (to publish the summary) and the SIP API.
    assistant = Assistant(
        room_name=ctx.room.name, known_account=known_account, known_name=known_name
    )
    assistant._ctx = ctx

    _, pre = await asyncio.gather(
        session.start(
            agent=assistant,
            room=ctx.room,
            room_options=room_io.RoomOptions(
                audio_input=room_io.AudioInputOptions(
                    noise_cancellation=ai_coustics.audio_enhancement(
                        model=ai_coustics.EnhancerModel.QUAIL_VF_S
                    ),
                ),
            ),
        ),
        _preload(known_account),
    )
    if pre:
        extra = Assistant._preload_text(pre)
        last = pre.get("last_call")
        if last and last.get("summary"):
            extra += (
                f"\n# Their previous call\nOn {str(last.get('ended_at', ''))[:10]} "
                f"they called about: {last['summary']} If relevant now, acknowledge it "
                "in one sentence; otherwise say nothing.\n"
            )
        await assistant.update_instructions(assistant.instructions + extra)

    TurnLatency().attach(session, ctx)

    async def _remember() -> None:
        await assistant.save_call_memory(session.history)

    ctx.add_shutdown_callback(_remember)

    # ------------------------------------------------------------------
    # Human handoff: the human (SIP dial-out) or a manual specialist is just
    # another participant arriving. When one joins, announce them and mute the
    # agent's voice — transcription keeps running so the record is intact.
    # ------------------------------------------------------------------
    handoff_tasks: set[asyncio.Task] = set()

    def _spawn(coro) -> None:
        async def _guarded():
            try:
                await coro
            except RuntimeError as err:  # session already closing — nothing to say to
                logger.info(f"handoff announcement skipped: {err}")

        task = asyncio.create_task(_guarded())
        handoff_tasks.add(task)
        task.add_done_callback(handoff_tasks.discard)

    def _is_human(identity: str) -> bool:
        low = identity.lower()
        return "specialist" in low or "human" in low or "agent" in low

    async def _step_back(identity: str) -> None:
        assistant._handed_off = True
        await session.say(
            "Good news — a specialist has just joined and they can see everything "
            "we've talked about. I'll leave you with them."
        )
        session.output.set_audio_enabled(False)
        logger.info(f"agent stepped back — {identity} is handling the call")

    async def _step_forward(identity: str) -> None:
        session.output.set_audio_enabled(True)
        logger.info(f"{identity} left — agent is speaking again")
        await session.say("The specialist has dropped off. I'm back with you.")

    @ctx.room.on("participant_connected")
    def _on_participant_connected(p) -> None:
        if _is_human(p.identity):
            _spawn(_step_back(p.identity))

    @ctx.room.on("participant_disconnected")
    def _on_participant_disconnected(p) -> None:
        if _is_human(p.identity):
            _spawn(_step_forward(p.identity))

    await ctx.connect()

    # Sound design, exclusive by state: while Ember is working on a question
    # ("thinking"), the caller hears keyboard typing; the rest of the call
    # carries quiet office ambience. The two never overlap.
    background_audio = BackgroundAudioPlayer()
    _amb: dict = {"h": None, "typing": None}

    def _play_ambient() -> None:
        if _amb["typing"] is not None:
            _amb["typing"].stop()
            _amb["typing"] = None
        if _amb["h"] is None or _amb["h"].done():
            _amb["h"] = background_audio.play(
                AudioConfig(BuiltinAudioClip.OFFICE_AMBIENCE, volume=0.5), loop=True
            )

    def _play_typing() -> None:
        if _amb["h"] is not None:
            _amb["h"].stop()
            _amb["h"] = None
        if _amb["typing"] is None or _amb["typing"].done():
            _amb["typing"] = background_audio.play(
                AudioConfig(BuiltinAudioClip.KEYBOARD_TYPING, volume=0.6), loop=True
            )

    @session.on("agent_state_changed")
    def _on_state(ev) -> None:
        try:
            if ev.new_state == "thinking":
                _play_typing()
            else:
                _play_ambient()
        except Exception as err:
            logger.warning(f"background audio switch failed: {err}")

    try:
        await background_audio.start(room=ctx.room, agent_session=session)
        _play_ambient()
    except Exception as err:  # never let ambience block a call
        logger.warning(f"background audio unavailable: {err}")

    # Speak first — otherwise the caller is met with silence. Guests are greeted
    # by IdentifyCallerTask (Assistant.on_enter), which owns the whole
    # who-are-you exchange; only signed-in callers are greeted here.
    if known_account:
        await session.generate_reply(
            instructions=(
                "Greet the caller by first name, say you can see their account, "
                "and ask what you can help with. One or two sentences."
            )
        )


if __name__ == "__main__":
    cli.run_app(server)
