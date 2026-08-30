import asyncio
import json
import logging
import os
import textwrap

import httpx

from dotenv import load_dotenv
from livekit import api
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    RunContext,
    ToolError,
    TurnHandlingOptions,
    cli,
    function_tool,
    inference,
    mcp,
    room_io,
)
from livekit.plugins import ai_coustics

import opaque_backend
import store
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
# Our own MCP server: Firestore device telemetry + the policy corpus.
MCP_TELEMETRY_URL = os.getenv(
    "MCP_TELEMETRY_URL",
    "https://aug24-mcp-549403515075.us-central1.run.app/mcp",
)


class Assistant(Agent):
    def __init__(
        self, room_name: str = "", known_account: str = "", known_name: str = ""
    ) -> None:
        self.room_name = room_name
        # Set when the caller signed in on the web: the token carried their account.
        self.known_account = known_account
        self.known_name = known_name
        # Set in the entrypoint so tools can publish data + call the SIP API.
        self._ctx: JobContext | None = None
        # order_number -> Ticket, so a retry reuses rather than duplicates
        self._timeout_tickets: dict[str, object] = {}
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
                    # Orders are deliberately NOT taken from here — a one-line status
                    # lookup is an HTTP function tool, not an MCP round trip.
                    allowed_tools=[
                        "lookup_account_by_phone",
                        "lookup_account_by_number",
                        "list_devices",
                        "find_device",
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
                then ask what you can help with. Call lookup_account_by_number with
                account_number "{known_account}" straight away so you have their
                customer_id before you answer anything factual.
                """
            )

        super().__init__(
            mcp_servers=self._mcp_servers,
            # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
            # See all available models at https://docs.livekit.io/agents/models/llm/
            llm=inference.LLM(model="google/gemma-4-31b-it"),
            instructions=textwrap.dedent(
                """\
                You are Ember, the voice support agent for Aria Home, a smart-home
                company.
                Aria Home sells connected devices — thermostats, cameras, door locks
                and sensors — plus a cloud video subscription. Customers reach you by
                phone or on the website.

                # First thing, every call

                Identify the caller before anything else. If you already have their
                phone number, look their account up with it. Otherwise ask for their
                phone number, or their Aria Home account number (it starts with "A H"),
                and look them up. Greet them by their first name as soon as you find
                them, and briefly confirm you can see their account. Use
                lookup_account_by_phone when you have a number, otherwise
                lookup_account_by_number. Keep the customer_id it returns — every
                other lookup needs it.

                # What you can do

                Use your tools for anything factual. Never guess an order status, a
                temperature, a date, or whether a device is on.

                - Devices are a two-step read. First find_device (or list_devices)
                  with the customer_id to turn "my thermostat" or "the front door"
                  into a device_id. Then get_device_state with that device_id for
                  whether it is on and what it is reading right now — temperature,
                  locked, recording. For "has it been like this all day", use
                  get_device_history.
                - "My most recent order" or "where is my order": get_recent_order
                  with their account number. A specific order number: lookup_order.
                - Policy questions — returns, refunds, warranty, subscription terms:
                  search_knowledge. Never guess policy; always search. The policy
                  documents call the company "AnyCompany" — that is an old name.
                  Never say AnyCompany out loud; always say Aria Home.
                - Refunds, warranty checks, device sync and package tracking have
                  their own tools; confirm the order number first.
                - When they ask for a person, are frustrated, or you cannot resolve it:
                  transfer_to_human. Compose a short summary first so the human is briefed.
                - When they say goodbye or the call is clearly finished: end_call.

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

                Never leave a dead end. If you do not have something — a serial number,
                a detail that is not in your tools — say so in one sentence and offer a
                next step in the same breath: file a ticket so someone follows up, or
                put them through to a person. Then ask if there is anything else.

                Sound like a person, not a script. Use the customer's first name once
                early, not every sentence. Acknowledge what they said before answering
                ("Sure — let me check that"). Vary your phrasing; never repeat the same
                sentence twice in a call.

                Open with an actual greeting, then introduce yourself by name, warmly
                and briefly: "Hi there — thanks for calling Aria Home. This is Ember,
                and I'm glad to help." Then ask for the phone number or account number
                on the account so you can pull it up. Always say hello or hi first; do
                not open on the thank-you.
                """
            )
            + identified,
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
        ctx = self._ctx
        logger.info("TRANSFER -> %s\n  SUMMARY: %s", department, summary)

        # 1. Hand the summary to the web frontend — it renders in the summary
        #    panel, so a human watching the screen is briefed instantly.
        if ctx is not None:
            try:
                payload = json.dumps(
                    {"type": "handoff", "department": department, "summary": summary}
                ).encode()
                await ctx.room.local_participant.publish_data(
                    payload, reliable=True, topic="summary"
                )
            except Exception as err:
                logger.warning(f"could not publish summary to frontend: {err}")

        # 2. Warm SIP transfer: dial the human's number INTO the room, if an
        #    outbound trunk is configured. The participant_connected handler
        #    then steps the agent back automatically. Guarded so a missing trunk
        #    degrades to the in-room fallback rather than failing the call.
        if ctx is not None and SIP_OUTBOUND_TRUNK_ID:
            try:
                await ctx.api.sip.create_sip_participant(
                    api.CreateSIPParticipantRequest(
                        sip_trunk_id=SIP_OUTBOUND_TRUNK_ID,
                        sip_call_to=TRANSFER_TO_NUMBER,
                        room_name=ctx.room.name,
                        participant_identity="human-agent",
                        participant_name="Human Agent",
                        wait_until_answered=False,
                    )
                )
                logger.info(f"SIP transfer: dialing {TRANSFER_TO_NUMBER}")
            except Exception as err:
                logger.warning(
                    f"SIP dial-out failed ({err}); using in-room fallback instead"
                )
        else:
            logger.info(
                "No SIP_OUTBOUND_TRUNK_ID set — summary delivered to the frontend; "
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

    async def _orders_api(self, path: str, **params) -> dict:
        async with httpx.AsyncClient(base_url=ORDERS_API_URL, timeout=8.0) as client:
            r = await client.get(
                path, params=params, headers={"X-Api-Key": ORDERS_API_KEY}
            )
        if r.status_code == 404:
            return {"found": False}
        r.raise_for_status()
        return r.json()

    @function_tool
    async def get_recent_order(self, context: RunContext, account_number: str):
        """The customer's most recent order and its status.

        Use for "where is my order?" or "what's the status of my most recent order?"
        when they do not give an order number.

        Args:
            account_number: their Aria Home account number, e.g. "AH-4821".
        """
        try:
            data = await self._orders_api("/api/orders", account=account_number)
        except Exception as err:
            logger.error(f"orders API failed: {err}")
            return {
                "found": False,
                "say": "Tell them the order system is not "
                "reachable right now and offer to file a ticket.",
            }
        orders = data.get("orders") or []
        if not orders:
            return {"found": False, "say": "There are no orders on this account."}
        recent = orders[0]
        logger.info(f"orders API: recent for {account_number} -> {recent['order_id']}")
        return {
            "found": True,
            **recent,
            "older_orders": len(orders) - 1,
            "say": "Say the item and the status plainly, and the delivery date as "
            "words. Read the order number digit by digit only if asked.",
        }

    @function_tool
    async def lookup_order(self, context: RunContext, order_number: str):
        """Look up one order by the number the customer reads out.

        Use exactly the digits they say; never pad them to a fixed length.

        Args:
            order_number: the order number as spoken, digits only, e.g. "58120".
        """
        digits = "".join(c for c in order_number if c.isdigit())
        try:
            data = await self._orders_api(f"/api/orders/{digits}")
        except Exception as err:
            logger.error(f"orders API failed: {err}")
            return {
                "found": False,
                "say": "Tell them the order system is not reachable right now.",
            }
        if not data.get("found"):
            return {
                "found": False,
                "say": "No order with that number. Ask them to "
                "check it; never pad the digits.",
            }
        logger.info(f"orders API: {digits} -> {data.get('status')}")
        return data

    @function_tool
    async def end_call(self, context: RunContext):
        """End the call once the customer is done.

        Use this only after they have said goodbye or confirmed there is nothing
        else — never mid-conversation. Say a short warm goodbye first; the room
        closes a moment after you finish speaking.
        """
        ctx = self._ctx
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
            "say": "Thank them for calling Aria Home, say goodbye, then stop talking.",
        }

    @function_tool
    async def request_refund(self, context: RunContext, order_number: str):
        """Refund an order the customer is unhappy with.

        Use this when the customer asks for a refund, their money back, or to
        return something. Confirm the order number with them before calling.

        Args:
            order_number: the order number to refund.
        """
        order = store.get_order(order_number)
        if order is None:
            return {
                "ok": False,
                "say": "No order with that number. Ask them to check it.",
            }

        eligible, why_not = store.refund_eligibility(order)
        if not eligible:
            logger.info(f"refund refused: {order.order_id} is {order.status}")
            return {"ok": False, "reason": order.status, "say": why_not}

        steps = store.REFUND_STEP_SECONDS

        if REFUND_MODE == "blocking":
            logger.info(f"refund [blocking] starting for {order.order_id}")
            await asyncio.sleep(steps["eligibility"])
            await asyncio.sleep(steps["processor"])
            await asyncio.sleep(steps["ledger"])
            reference = store.record_refund(order.order_id)
            logger.info(f"refund [blocking] done — {reference}")
            return {
                "ok": True,
                "reference": reference,
                "amount_status": "refunded to the original card",
            }

        logger.info(f"refund [async] starting for {order.order_id}")

        # First update() hands the conversation back immediately (non-blocking).
        await context.update(
            f"Starting the refund for order {order.order_id}, the {order.item}. "
            "This takes a few seconds."
        )

        async with context.with_filler(
            "Just checking that order, one moment.", delay=2
        ):
            await asyncio.sleep(steps["eligibility"])
        await context.update(
            "The order is eligible. Sending it to the payment processor."
        )

        waiting_lines = [
            "Still with the payment processor, hang tight.",
            "Almost there, just waiting on their confirmation.",
        ]
        async with context.with_filler(
            lambda step: waiting_lines[step],
            delay=2,
            interval=4,
            max_steps=len(waiting_lines),
        ):
            await asyncio.sleep(steps["processor"])
        await context.update("The processor accepted it. Writing the record now.")

        async with context.with_filler("Nearly done.", delay=2):
            await asyncio.sleep(steps["ledger"])

        reference = store.record_refund(order.order_id)
        logger.info(f"refund [async] done — {reference}")

        return {
            "ok": True,
            "reference": reference,
            "amount_status": "refunded to the original card",
            "arrives_in": "three to five business days",
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
    async def sync_device(self, context: RunContext, order_number: str):
        """Push a settings refresh to the customer's device and wait for it to apply.

        Use this when a device is misbehaving, unresponsive, or the customer asks
        you to reset or refresh it.

        Args:
            order_number: the order number for the device.
        """
        digits = store.normalize_order_id(order_number)
        order = store.get_order(digits)
        if order is None:
            return {"ok": False, "say": "No order with that number."}

        holding = [
            "Still pushing that update to your device.",
            "It is taking a moment, the device has to acknowledge it.",
            "Nearly there, thanks for waiting.",
        ]
        took = opaque_backend.warranty_latency()
        logger.info(f"sync: opaque call will take {took}s")

        try:
            async with context.with_filler(
                lambda step: holding[step],
                delay=2,
                interval=3,
                max_steps=len(holding),
            ):
                async with asyncio.timeout(12):
                    await opaque_backend.opaque_call("device.sync", seconds=took)
        except (asyncio.TimeoutError, opaque_backend.BackendTimeout) as err:
            raise ToolError(
                "The device did not respond to the refresh. Tell the customer it "
                "failed and offer to file a ticket."
            ) from err

        return {
            "ok": True,
            "device": order.item,
            "say": "Confirm it refreshed successfully.",
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
        stt=inference.STT(model="assemblyai/universal-3-5-pro", language="en"),
        tts=inference.TTS(
            model="fishaudio/s2.1-pro", voice="fa4c9eb3dccc4806b382b40d61c6b10a"
        ),
        expressive=True,
        max_tool_steps=3,
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

    # Create the agent first so we can hand it the JobContext — the transfer
    # tool needs the live room (to publish the summary) and the SIP API.
    assistant = Assistant(
        room_name=ctx.room.name, known_account=known_account, known_name=known_name
    )
    assistant._ctx = ctx

    await session.start(
        agent=assistant,
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=ai_coustics.audio_enhancement(
                    model=ai_coustics.EnhancerModel.QUAIL_VF_S
                ),
            ),
        ),
    )

    TurnLatency().attach(session, ctx)

    # ------------------------------------------------------------------
    # Human handoff: the human (SIP dial-out) or a manual specialist is just
    # another participant arriving. When one joins, announce them and mute the
    # agent's voice — transcription keeps running so the record is intact.
    # ------------------------------------------------------------------
    handoff_tasks: set[asyncio.Task] = set()

    def _spawn(coro) -> None:
        task = asyncio.create_task(coro)
        handoff_tasks.add(task)
        task.add_done_callback(handoff_tasks.discard)

    def _is_human(identity: str) -> bool:
        low = identity.lower()
        return "specialist" in low or "human" in low or "agent" in low

    async def _step_back(identity: str) -> None:
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

    # Speak first — otherwise the caller is met with silence.
    await session.generate_reply(
        instructions=(
            "Greet the caller warmly as Aria Home support, and ask for the phone "
            "number or account number on the account so you can pull it up. "
            "One or two sentences."
        )
    )


if __name__ == "__main__":
    cli.run_app(server)
