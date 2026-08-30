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
    """Find out who a guest caller is, by phone or account number.

    The lookup tools come from the Cloud SQL Toolbox (MCP). The task completes
    either when the model confirms a found account, or — as a backstop — when
    the Assistant's MCP result resolver sees a verified row and calls
    `identified()`. Either way the account comes from the database row, never
    from what the caller asserted.
    """

    def __init__(
        self,
        lookup_tools: list[llm.Tool],
        chat_ctx: llm.ChatContext | None = None,
        model: llm.LLM | None = None,
    ) -> None:
        super().__init__(
            llm=model if model is not None else NOT_GIVEN,
            instructions=_VOICE_RULES
            + "You are Ember, the voice support agent for Aria Home. Your only job "
            "right now is to find out who is calling. Open with a warm hello, "
            "introduce yourself by name, and ask for the phone number or the Aria "
            "Home account number on the account (it starts with 'A H'). Use "
            "lookup_account_by_phone for a phone number and "
            "lookup_account_by_number for an account number, with exactly the "
            "digits they said. People read numbers slowly, in pieces — wait until "
            "they have clearly finished, and read the number back before looking "
            "it up. When a lookup returns a customer, greet them by first name, "
            "say you can see their account, and call confirm_identity. If it "
            "returns nothing, say so plainly and ask them to check the number, "
            "once; if it fails again or they cannot give one, call "
            "cannot_identify. Do not answer any other question yet — say you will "
            "get to it as soon as you have their account.",
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
        """Backstop completion from the verified MCP result (see Assistant)."""
        if not self.done():
            self.complete(Identity(account=account, first_name=first_name))

    @function_tool()
    async def confirm_identity(
        self, context: RunContext, account_number: str, first_name: str
    ) -> None:
        """Call once a lookup has returned the caller's account.

        Args:
            account_number: the account_number from the lookup result, e.g. "AH-4821".
            first_name: the first_name from the lookup result.
        """
        if not self.done():
            self.complete(
                Identity(account=account_number.strip().upper(), first_name=first_name)
            )

    @function_tool()
    async def cannot_identify(self, context: RunContext) -> None:
        """Call when the caller cannot be found after a second try, or has no
        phone or account number to give."""
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
