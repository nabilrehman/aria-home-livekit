"""Acceptance suite — the four things the assignment actually grades.

    1. Greet the caller by name and look up their account details
       - Ask for their account number if not using phone
    2. Respond to 2-3 questions about their smart home setup
       - What is the status of my most recent order?
       - Is my thermostat active?
       - What is the temperature in my living room?
    3. Transfer the caller to another number
       - When transferred, the human agent should get a summary of the discussion
    4. Answer questions from the customer

One test per requirement, using the assignment's own wording as the caller's
lines. These drive the real agent against the live MCP servers, so they need the
data plane up:

    export TOOLBOX_MCP_URL=https://<aria-toolbox>/mcp     # Cloud SQL
    export MCP_TELEMETRY_URL=https://<aug24-mcp>/mcp      # Firestore + RAG
    uv run pytest tests/test_assignment_beats.py -v -s

Without TOOLBOX_MCP_URL the agent has no lookup tools at all, so these skip
rather than fail misleadingly.
"""

import os

import pytest
from livekit.agents import AgentSession, RunContext, function_tool, inference

from agent import Assistant

pytestmark = pytest.mark.skipif(
    not os.getenv("TOOLBOX_MCP_URL"),
    reason="needs the Cloud SQL toolset: set TOOLBOX_MCP_URL",
)

SARAH_PHONE = "+15125551188"
SARAH_ACCOUNT = "AH-4821"


def judge():
    return inference.LLM(model="openai/gpt-4.1-mini")


def called(result, *names: str) -> bool:
    """True if the turn made a function call with any of these names."""
    for n in names:
        try:
            result.expect.contains_function_call(name=n)
            return True
        except AssertionError:
            continue
    return False


def tools_in(result) -> list[str]:
    out = []
    for ev in getattr(result, "events", []):
        name = getattr(getattr(ev, "item", None), "name", None)
        if name:
            out.append(name)
    return out


# ═══════════════════ 1 · greet by name, look up the account ═══════════════════


@pytest.mark.asyncio
async def test_beat1_identifies_the_caller_from_their_phone_number():
    """The phone path: caller ID is enough, no account number needed."""
    async with judge() as j, AgentSession() as session:
        await session.start(Assistant())

        r = await session.run(user_input=f"Hi, I'm calling from {SARAH_PHONE}.")
        assert called(r, "lookup_account_by_phone", "lookup_account_by_number"), (
            f"no account lookup fired; tools seen: {tools_in(r)}"
        )
        await r.expect.contains_message(role="assistant").judge(
            j,
            intent="Greets the caller by the first name Sarah and indicates it can "
            "see her account. Must not ask her to repeat an account number.",
        )


@pytest.mark.asyncio
async def test_beat1_asks_for_the_account_number_when_there_is_no_phone():
    """The assignment's explicit sub-requirement: ask if not using phone."""
    async with judge() as j, AgentSession() as session:
        await session.start(Assistant())

        opening = await session.run(user_input="Hi, I need some help with my account.")
        await opening.expect.contains_message(role="assistant").judge(
            j,
            intent="Asks the caller for their phone number or their Aria Home "
            "account number so it can look the account up.",
        )

        r = await session.run(user_input="My account number is A H four eight two one.")
        assert called(r, "lookup_account_by_number", "lookup_account_by_phone"), (
            f"spoken account number did not trigger a lookup; tools: {tools_in(r)}"
        )
        await r.expect.contains_message(role="assistant").judge(
            j,
            intent="Greets the caller by the first name Sarah, having found her account.",
        )


@pytest.mark.asyncio
async def test_beat1_an_unknown_caller_is_not_invented():
    async with judge() as j, AgentSession() as session:
        await session.start(Assistant())

        r = await session.run(user_input="Hi, my number is 555 000 0000.")
        await r.expect.contains_message(role="assistant").judge(
            j,
            intent="Says it could not find an account for that number and asks for "
            "the account number. It must NOT invent a customer name.",
        )


# ═══════════════════ 2 · questions about the smart home ═══════════════════════


@pytest.mark.asyncio
async def test_beat2_status_of_my_most_recent_order():
    async with judge() as j, AgentSession() as session:
        await session.start(Assistant())
        await session.run(user_input=f"Hi, I'm calling from {SARAH_PHONE}.")

        r = await session.run(user_input="What is the status of my most recent order?")
        assert called(r, "get_recent_order", "list_orders", "lookup_order"), (
            f"no order lookup fired; tools: {tools_in(r)}"
        )
        await r.expect.contains_message(role="assistant").judge(
            j,
            intent="States the status of a specific order — naming the item and where "
            "it is. Must be a concrete status, not a vague reassurance.",
        )


@pytest.mark.asyncio
async def test_beat2_is_my_thermostat_active():
    """Crosses both stores: Postgres finds the device, Firestore says what it's doing."""
    async with judge() as j, AgentSession() as session:
        await session.start(Assistant())
        await session.run(user_input=f"Hi, I'm calling from {SARAH_PHONE}.")

        r = await session.run(user_input="Is my thermostat active?")
        assert called(r, "get_device_state", "find_device"), (
            f"no device tools fired; tools: {tools_in(r)}"
        )
        await r.expect.contains_message(role="assistant").judge(
            j, intent="Confirms the thermostat is active / on, based on a real reading."
        )


@pytest.mark.asyncio
async def test_beat2_temperature_in_my_living_room():
    async with judge() as j, AgentSession() as session:
        await session.start(Assistant())
        await session.run(user_input=f"Hi, I'm calling from {SARAH_PHONE}.")

        r = await session.run(user_input="What is the temperature in my living room?")
        assert called(r, "get_device_state", "find_device"), (
            f"no telemetry read; tools: {tools_in(r)}"
        )
        await r.expect.contains_message(role="assistant").judge(
            j,
            intent="Gives a specific temperature for the living room — the number 71 "
            "or seventy-one degrees. A refusal or a vague answer fails.",
        )


@pytest.mark.asyncio
async def test_beat2_does_not_answer_about_a_device_she_does_not_own():
    async with judge() as j, AgentSession() as session:
        await session.start(Assistant())
        await session.run(user_input=f"Hi, I'm calling from {SARAH_PHONE}.")

        r = await session.run(user_input="Is my garage camera recording?")
        await r.expect.contains_message(role="assistant").judge(
            j,
            intent="Says there is no garage camera on this account, and may list the "
            "devices she does have. It must NOT report a state for it.",
        )


# ═══════════════════ 3 · transfer, with a summary ═════════════════════════════


@pytest.mark.asyncio
async def test_beat3_transfers_and_hands_over_a_summary():
    async with judge() as j, AgentSession() as session:
        await session.start(Assistant())
        await session.run(user_input=f"Hi, I'm calling from {SARAH_PHONE}.")
        await session.run(user_input="What is the status of my most recent order?")

        r = await session.run(
            user_input="I'd like to change the delivery address. Can I speak to a person?"
        )
        assert called(r, "transfer_to_human"), (
            f"no transfer fired; tools: {tools_in(r)}"
        )
        await r.expect.contains_message(role="assistant").judge(
            j,
            intent="Tells the caller it is connecting them to a person and that it has "
            "passed along a summary so they will not have to repeat themselves.",
        )


@pytest.mark.asyncio
async def test_beat3_the_summary_actually_contains_the_conversation():
    """The graded half: the human must arrive briefed, not just connected."""
    captured: dict = {}

    class Recording(Assistant):
        # Overriding drops the decorator, so re-apply it or the model never sees it.
        @function_tool
        async def transfer_to_human(
            self,
            context: RunContext,
            summary: str,
            department: str = "the support team",
        ):
            """Transfer the caller to a human agent, handing them a summary of the call.

            Args:
                summary: two or three sentences — who the caller is, what they asked
                    about, what was resolved so far, and why they need a human.
                department: which team to route to.
            """
            captured["summary"] = summary
            captured["department"] = department
            return {
                "transferred": True,
                "say": "Tell them you are connecting them now.",
            }

    async with AgentSession() as session:
        await session.start(Recording())
        await session.run(user_input=f"Hi, I'm calling from {SARAH_PHONE}.")
        await session.run(user_input="Where is my camera order?")
        await session.run(
            user_input="It's the wrong address. Put me through to someone please."
        )

    assert captured, "transfer_to_human was never called"
    summary = captured["summary"]
    assert len(summary.split()) >= 12, f"summary too thin to brief anyone: {summary!r}"

    low = summary.lower()
    assert "sarah" in low, f"summary does not name the caller: {summary!r}"
    assert any(w in low for w in ("order", "camera", "address", "delivery")), (
        f"summary does not carry what the call was about: {summary!r}"
    )


# ═══════════════════ 4 · answer questions from the customer ═══════════════════


@pytest.mark.asyncio
async def test_beat4_answers_a_policy_question_from_the_documents():
    """Grounded in the returns policy — 14 days is unique to the document."""
    async with judge() as j, AgentSession() as session:
        await session.start(Assistant())
        await session.run(user_input=f"Hi, I'm calling from {SARAH_PHONE}.")

        r = await session.run(
            user_input="How long do I have to return a doorbell camera?"
        )
        assert called(r, "search_knowledge"), f"RAG not consulted; tools: {tools_in(r)}"
        await r.expect.contains_message(role="assistant").judge(
            j,
            intent="States the return window for a camera as fourteen days. Any other "
            "number, or a generic thirty-day answer, fails.",
        )


@pytest.mark.asyncio
async def test_beat4_answers_a_question_about_the_subscription():
    async with judge() as j, AgentSession() as session:
        await session.start(Assistant())
        await session.run(user_input=f"Hi, I'm calling from {SARAH_PHONE}.")

        r = await session.run(user_input="Which plan am I on?")
        await r.expect.contains_message(role="assistant").judge(
            j, intent="Tells the caller she is on the Video Plus plan."
        )


@pytest.mark.asyncio
async def test_beat4_says_it_does_not_know_rather_than_guessing():
    """The failure mode that matters on security hardware."""
    async with judge() as j, AgentSession() as session:
        await session.start(Assistant())
        await session.run(user_input=f"Hi, I'm calling from {SARAH_PHONE}.")

        r = await session.run(
            user_input="What was the exact serial number printed on my lock's box?"
        )
        await r.expect.contains_message(role="assistant").judge(
            j,
            intent="Admits it does not have that information, and offers to find out "
            "or pass the caller to a person. Inventing a serial number fails.",
        )


@pytest.mark.asyncio
async def test_beat4_reads_numbers_out_as_speech_not_digits():
    """Voice output rule: order numbers spoken digit by digit, dates as words."""
    async with judge() as j, AgentSession() as session:
        await session.start(Assistant())
        await session.run(user_input=f"Hi, I'm calling from {SARAH_PHONE}.")

        r = await session.run(user_input="Read me my most recent order number.")
        await r.expect.contains_message(role="assistant").judge(
            j,
            intent="Reads the order number back as separate spoken digits, and uses no "
            "markdown, bullet points or symbols anywhere in the reply.",
        )
