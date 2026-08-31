"""Bounded sub-workflows for Ember, built on LiveKit's AgentTask.

Why tasks and not a second agent: a task takes the wheel for one job, sees only
the tools for that job, hands back a *typed* result, and Ember's persona,
identity and preloaded context never leave the session. This is the shape of
LiveKit's own hotel-receptionist and healthcare examples (GetInsuranceTask,
ScheduleAppointmentTask, BookRoomTask), and of Parloa's production "subtask
agents": one agent per user goal, deterministic gating, no routing LLM call.

Three tasks:

  IdentifyCallerTask      guest path — who is this? Returns the account or None.
                          Everything scoped is gated on its result.
  ReturnIntakeTask        return / refund intake — which order, what is wrong,
                          is it inside the window. The decision is computed in
                          code from dates and policy: the LLM never owns money.
  TroubleshootDeviceTask  a device "not working" — find it, read its live state
                          and history, try the manual, conclude fixed / not.

Each result is a dataclass so the calling tool can act on it without parsing
prose. Every task also has an explicit exit tool ("they want a person", "they
changed their mind") so the model is never stuck inside a task.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

from livekit.agents import NOT_GIVEN, AgentTask, RunContext, function_tool, llm

logger = logging.getLogger("aria.tasks")

# The returns policy (RAG corpus, v3): 30 days from delivery for most devices,
# 14 days for security devices (Smart Locks, Doorbell Cameras). Kept in code so
# the refund decision is deterministic and testable, not model-recalled.
RETURN_WINDOW_DAYS = 30
SECURITY_WINDOW_DAYS = 14
_SECURITY_WORDS = ("lock", "doorbell")


def return_window_days(item: str) -> int:
    low = (item or "").lower()
    return (
        SECURITY_WINDOW_DAYS
        if any(w in low for w in _SECURITY_WORDS)
        else RETURN_WINDOW_DAYS
    )


_VOICE_RULES = (
    "You are speaking out loud: plain speech, one to three sentences, one "
    "question at a time, numbers digit by digit, dates as words. Spoken "
    "grammar, always contractions, calm baseline; think out loud briefly "
    "before a lookup ('let me check that…') so there is never dead air. "
)


# ─────────────────────────────────────────────────────────── identification


@dataclass
class Identity:
    account: str
    first_name: str


class IdentifyCallerTask(AgentTask[Identity | None]):
    """Find out who a guest caller is — and, when enabled, verify it is them.

    Stage 1 — locate: phone number or account number, via the Cloud SQL
    Toolbox lookups. The verified DB row records the candidate account.
    Stage 2 — verify (only when a `verify` callable is given): ask for the
    email (or phone) on file and check the answer server-side. The model only
    learns pass/fail — it cannot read the stored value, so it cannot leak it
    or be talked into "close enough". Two failed attempts end identification.

    verify=None turns stage 2 off: a located account then counts as
    identified — the assignment's minimal beat. The Assistant chooses via the
    VERIFY_GUESTS env var.

    Real-world upgrade path (say it if asked): SMS one-time codes beat KBA,
    and 2025-26 guidance pushes liveness checks because voice cloning has
    weakened knowledge questions. Same task shape, stronger challenge.
    """

    MAX_ATTEMPTS = 3

    _VERIFY_STEP = (
        "Step two, when a lookup returns a customer: do NOT confirm any "
        "account details yet. Say something like 'Found it — and just to make "
        "sure it's you, what's the email address on the account?' (if they "
        "identified by account number, the phone number on file also works). "
        "People say emails as words ('john doe at gmail dot com') or spell "
        "them letter by letter. Assemble what they said into a normal address, "
        "READ IT BACK, and wait for them to confirm you heard it right — only "
        "then call verify_identity. Never guess at a garbled address. "
        "If the check fails, the most likely cause is that YOU misheard: "
        "apologise for the trouble and ask them to spell it out letter by "
        "letter, assemble it, read it back, confirm, and check again. If it "
        "fails a second time, offer the other route: 'we can try the phone "
        "number on the account instead'. Only after the third failed check "
        "call cannot_identify, and do not reveal anything about the account. "
        "Never read out or hint at the email or phone on file, and never "
        "treat a partial or similar answer as correct — the check is done "
        "for you. Only after verify_identity succeeds, greet them by first "
        "name and say you can see their account. "
    )
    _NO_VERIFY_STEP = (
        "Step two, when a lookup returns a customer: greet them by first name, "
        "say you can see their account, and call confirm_identity with the "
        "account_number and first_name from the lookup result. "
    )

    def __init__(
        self,
        lookup_tools: list[llm.Tool],
        verify=None,
        chat_ctx: llm.ChatContext | None = None,
        model: llm.LLM | None = None,
    ) -> None:
        self._verify = verify
        self._account = ""
        self._attempts = 0
        step_two = self._NO_VERIFY_STEP if verify is None else self._VERIFY_STEP
        super().__init__(
            llm=model if model is not None else NOT_GIVEN,
            instructions=_VOICE_RULES
            + "You are Ember, the voice support agent for Aria Home. Your only job "
            "right now is to find out who is calling. Step one: open with a warm "
            "hello, introduce yourself by name, and ask for the phone number or "
            "the Aria Home account number on the account (it starts with 'A H'). "
            "Use lookup_account_by_phone for a phone number and "
            "lookup_account_by_number for an account number, with exactly the "
            "digits they said — read the number back first; people say numbers "
            "slowly, in pieces. If a lookup finds nothing, say so plainly and "
            "let them check the number once. "
            + step_two
            + "Do not answer any other question before that — say you will get "
            "to it as soon as you have the account.",
            tools=list(lookup_tools),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions=(
                "Say hello, introduce yourself as Ember from Aria Home, and ask "
                "for the phone number or account number on the account. Two "
                "sentences."
            )
        )

    def identified(self, account: str, first_name: str = "") -> None:
        """Record the candidate account from the verified MCP lookup row.

        With verification enabled this does NOT complete the task — a located
        account is not a verified caller. Without it, locating IS identifying,
        so complete straight away (backstop for a forgotten confirm call).
        """
        if not self._account:
            self._account = account
            logger.info(f"identify: candidate account {account}")
        if self._verify is None and not self.done():
            self.complete(Identity(account=account, first_name=first_name))

    @function_tool()
    async def confirm_identity(
        self, context: RunContext, account_number: str, first_name: str
    ) -> None:
        """Call once a lookup has returned the caller's account (only when no
        security question was asked).

        Args:
            account_number: the account_number from the lookup result.
            first_name: the first_name from the lookup result.
        """
        if self._verify is not None:
            raise llm.ToolError(
                "Verification is required on this call — ask the security "
                "question and use verify_identity instead."
            )
        if not self.done():
            self.complete(
                Identity(account=account_number.strip().upper(), first_name=first_name)
            )

    @function_tool()
    async def verify_identity(
        self,
        context: RunContext,
        first_name: str,
        email: str = "",
        phone_number: str = "",
    ) -> dict | None:
        """Check the caller's verification answer against the account on file.

        Call after a lookup found the account AND the caller answered the
        security question. Pass exactly what they said, assembled.

        Args:
            first_name: the first_name from the lookup result.
            email: the email address the caller said, if that was the question.
            phone_number: the phone number the caller said, if that was the question.
        """
        if self._verify is None:
            raise llm.ToolError("No verification needed — use confirm_identity.")
        if not self._account:
            raise llm.ToolError("Look the account up first, then verify.")
        try:
            ok = await self._verify(self._account, email=email, phone=phone_number)
        except Exception as err:
            logger.error(f"verify call failed: {err}")
            raise llm.ToolError(
                "Verification is unavailable right now. Apologise and offer to "
                "connect them to a person instead."
            ) from err
        if ok:
            logger.info(f"identify: {self._account} verified")
            if not self.done():
                self.complete(Identity(account=self._account, first_name=first_name))
            return None
        self._attempts += 1
        logger.info(f"identify: {self._account} verification failed ({self._attempts})")
        if self._attempts >= self.MAX_ATTEMPTS and not self.done():
            self.complete(None)
            return None
        say = (
            "Say it does not match — you may have misheard — apologise and ask "
            "them to spell the email letter by letter, then read it back and "
            "confirm before checking again."
            if self._attempts == 1
            else "Say it still does not match and offer to try the phone number "
            "on the account instead."
        )
        return {
            "verified": False,
            "attempts_left": self.MAX_ATTEMPTS - self._attempts,
            "say": say,
        }

    @function_tool()
    async def cannot_identify(self, context: RunContext) -> None:
        """Call when the caller cannot be found, fails verification twice, or
        has no phone or account number to give."""
        if not self.done():
            self.complete(None)


# ─────────────────────────────────────────────────────────── returns


ReturnNext = Literal["refund_desk", "ticket", "declined", "person", "abandoned"]


@dataclass
class ReturnIntake:
    order_id: str
    item: str
    status: str
    condition: str
    reason: str
    within_window: bool
    next: ReturnNext


def decide_return(
    order: dict, condition: str, today: date | None = None
) -> tuple[bool, ReturnNext]:
    """The return decision, in code.

    - damaged / defective / wrong item: always goes to the refunds desk (the
      specialist decides transit damage vs customer damage — policy sends the
      latter to warranty repair, and that judgement is theirs, not the model's).
    - unwanted: inside the item's window (30 days; 14 for locks and doorbells)
      -> refunds desk, outside -> declined (offer a ticket for review).
    - not delivered yet (processing / shipped): a cancellation, refunds desk.
    """
    today = today or date.today()
    status = (order.get("status") or "").lower()
    if condition in ("damaged", "defective", "wrong_item"):
        return True, "refund_desk"
    if status != "delivered":
        return True, "refund_desk"
    delivered = order.get("delivers_on") or order.get("delivered_on")
    try:
        d = datetime.fromisoformat(str(delivered)[:10]).date()
    except (TypeError, ValueError):
        return False, "ticket"
    within = (today - d).days <= return_window_days(order.get("item", ""))
    return within, ("refund_desk" if within else "declined")


class ReturnIntakeTask(AgentTask[ReturnIntake]):
    """Collect what is needed for a return, decide in code, hand back a result."""

    def __init__(
        self,
        lookup_order,
        policy_tools: list[llm.Tool] | None = None,
        chat_ctx: llm.ChatContext | None = None,
        order_hint: str = "",
        reason_hint: str = "",
        model: llm.LLM | None = None,
    ) -> None:
        self._lookup_order = lookup_order
        hint = ""
        if order_hint:
            hint += f" They mentioned order {order_hint}."
        if reason_hint:
            hint += f" They said: {reason_hint!r}."
        super().__init__(
            llm=model if model is not None else NOT_GIVEN,
            instructions=_VOICE_RULES
            + "You are Ember from Aria Home, taking the details for a return or "
            "refund. You need three things, in order, one question at a time: "
            "(1) the order — call lookup_order with the number they give, or if "
            "they do not know it, lookup_order with no number returns their most "
            "recent order to confirm; read the item back; (2) what is wrong — "
            "damaged, defective, wrong item, or simply not wanted; (3) one line "
            "of reason in their words. Then call record_return. Do not promise a "
            "refund, an amount, or a timeline — the decision is made after you "
            "record it. If they ask about the policy, search_knowledge answers "
            "it. If they ask for a person or change their mind, call stop_return."
            + hint,
            tools=list(policy_tools or []),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions=(
                "Say you can help with that return, and ask which order it is "
                "— or confirm the order they already named. One sentence."
            )
        )

    @function_tool()
    async def lookup_order(self, context: RunContext, order_number: str = "") -> dict:
        """Look up one of the caller's orders by number, or their most recent
        order when no number is given.

        Args:
            order_number: digits only as the caller said them, or empty.
        """
        return await self._lookup_order(order_number)

    @function_tool()
    async def record_return(
        self,
        context: RunContext,
        order_number: str,
        condition: Literal["damaged", "defective", "wrong_item", "unwanted", "other"],
        reason: str,
    ) -> None:
        """Record the return once you have the order, the condition and the reason.

        Args:
            order_number: the confirmed order number, digits only.
            condition: damaged, defective, wrong_item, unwanted, or other.
            reason: one short sentence in the caller's words.
        """
        order = await self._lookup_order(order_number)
        if not order.get("found"):
            raise llm.ToolError(
                "That order is not on this account. Ask them to check the number."
            )
        within, nxt = decide_return(order, condition)
        logger.info(
            f"return intake: {order['order_id']} {condition} within={within} -> {nxt}"
        )
        if not self.done():
            self.complete(
                ReturnIntake(
                    order_id=order["order_id"],
                    item=order.get("item", ""),
                    status=order.get("status", ""),
                    condition=condition,
                    reason=reason,
                    within_window=within,
                    next=nxt,
                )
            )

    @function_tool()
    async def stop_return(
        self, context: RunContext, why: Literal["wants_person", "changed_mind"]
    ) -> None:
        """Leave the return flow: the caller wants a person, or no longer wants
        to return anything.

        Args:
            why: wants_person or changed_mind.
        """
        if not self.done():
            self.complete(
                ReturnIntake(
                    order_id="",
                    item="",
                    status="",
                    condition="",
                    reason="",
                    within_window=False,
                    next="person" if why == "wants_person" else "abandoned",
                )
            )


# ─────────────────────────────────────────────────────────── troubleshooting


@dataclass
class Troubleshoot:
    device_id: str
    name: str
    finding: str
    resolved: bool
    next: Literal["done", "ticket", "person", "abandoned"]


class TroubleshootDeviceTask(AgentTask[Troubleshoot]):
    """Work one misbehaving device to a conclusion.

    find_device is the Assistant's scoped HTTP lookup (the account is pinned by
    the server); state, history and the manuals come from the telemetry MCP
    server and the RAG corpus, passed in as tools so nothing else is visible
    while this runs.
    """

    def __init__(
        self,
        find_device,
        telemetry_tools: list[llm.Tool] | None = None,
        chat_ctx: llm.ChatContext | None = None,
        description: str = "",
        model: llm.LLM | None = None,
    ) -> None:
        self._find_device = find_device
        super().__init__(
            llm=model if model is not None else NOT_GIVEN,
            instructions=_VOICE_RULES
            + "You are Ember from Aria Home, helping with one device that is not "
            "behaving. Steps: find_device with the caller's words for it; read "
            "its live state — if it is not reporting, say so; get_device_history "
            "to see whether it has been like this for a while; search_knowledge "
            "for the manual's fix for that symptom and talk them through ONE "
            "step; ask if that fixed it. Then call conclude with what you found "
            "and whether it is resolved. Never guess a reading. If they want a "
            "person or want to stop, call stop_troubleshooting."
            + (f" The device they described: {description!r}." if description else ""),
            tools=list(telemetry_tools or []),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions=(
                "Say you will take a look at that device, then look it up. One "
                "sentence before the lookup."
            )
        )

    @function_tool()
    async def find_device(self, context: RunContext, description: str) -> dict:
        """Find the caller's device by room, type or name and read its live state.

        Args:
            description: the caller's own words, e.g. "hallway sensor".
        """
        return await self._find_device(description)

    @function_tool()
    async def conclude(
        self,
        context: RunContext,
        device_id: str,
        device_name: str,
        finding: str,
        resolved: bool,
    ) -> None:
        """Finish troubleshooting with what you found.

        Args:
            device_id: the device_id from find_device.
            device_name: the device's name.
            finding: one sentence: what was wrong and what was done.
            resolved: true if the caller confirmed it is working now.
        """
        if not self.done():
            self.complete(
                Troubleshoot(
                    device_id=device_id,
                    name=device_name,
                    finding=finding,
                    resolved=resolved,
                    next="done" if resolved else "ticket",
                )
            )

    @function_tool()
    async def stop_troubleshooting(
        self, context: RunContext, why: Literal["wants_person", "changed_mind"]
    ) -> None:
        """Leave troubleshooting: the caller wants a person, or wants to stop.

        Args:
            why: wants_person or changed_mind.
        """
        if not self.done():
            self.complete(
                Troubleshoot(
                    device_id="",
                    name="",
                    finding="",
                    resolved=False,
                    next="person" if why == "wants_person" else "abandoned",
                )
            )
