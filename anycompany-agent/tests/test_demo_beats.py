"""Heavy end-to-end behavior tests for the Aria Home panel demo.

Runs the REAL agent (gemma via LiveKit Inference) with the LIVE MCP tools,
driving Sarah Chen's whole call, and judges each of the four demo beats:
identify -> device state -> order status -> policy (RAG) -> warm transfer.

These are integration tests: they hit LiveKit Inference + the deployed MCP.
Run with:  uv run pytest tests/test_demo_beats.py -v -s
"""

import pytest
from livekit.agents import AgentSession, inference

from agent import Assistant


def _judge():
    return inference.LLM(model="openai/gpt-4.1-mini")


def _called(result, name: str) -> bool:
    """True if the agent made a function call with this name during the turn."""
    try:
        result.expect.contains_function_call(name=name)
        return True
    except AssertionError:
        return False


async def _judge_any(results, judge, intent: str) -> None:
    """Pass if ANY of the given turns has an assistant message matching intent.

    The agent may greet on the number turn OR after a read-back confirmation,
    so we don't hard-code which turn carries the greeting.
    """
    last = None
    for res in results:
        try:
            await res.expect.contains_message(role="assistant").judge(
                judge, intent=intent
            )
            return
        except AssertionError as e:
            last = e
    raise last


@pytest.mark.asyncio
async def test_full_demo_happy_path() -> None:
    """The whole hero-journey call, one beat at a time, with the live MCP."""
    tools_seen: set[str] = set()

    async with _judge() as judge, AgentSession() as session:
        await session.start(Assistant())

        # --- greeting ---
        r = await session.run(user_input="Hi")
        await r.expect.contains_message(role="assistant").judge(
            judge,
            intent=(
                "Greets the caller as Aria Home support. It may then either offer help OR ask "
                "for their phone number / account number to look up their account — both are fine."
            ),
        )

        # --- BEAT 1: identify by phone (agent may read the number back first) ---
        r = await session.run(user_input="My phone number is 512 555 1188")
        for n in ("lookup_account_by_phone", "lookup_account_by_number"):
            if _called(r, n):
                tools_seen.add(n)
        # confirm if it asked to
        r2 = await session.run(user_input="Yes, that's correct")
        if _called(r2, "lookup_account_by_phone") or _called(
            r2, "lookup_account_by_number"
        ):
            tools_seen.add("lookup_account")
        assert tools_seen & {
            "lookup_account",
            "lookup_account_by_phone",
            "lookup_account_by_number",
        }, "agent never called lookup_account to identify the caller"
        await _judge_any(
            [r, r2],
            judge,
            intent="Greets the customer by the name Sarah (Sarah Chen), or clearly confirms it can see Sarah's account.",
        )

        # --- BEAT 2: device state ---
        r = await session.run(user_input="Is my thermostat on?")
        assert _called(r, "get_device_state") or _called(r, "find_device"), (
            "agent did not check device state"
        )
        await r.expect.contains_message(role="assistant").judge(
            judge,
            intent="States the thermostat is active/on and reads about 71 degrees. Does not make up a number.",
        )

        r = await session.run(user_input="What's the temperature in my living room?")
        await r.expect.contains_message(role="assistant").judge(
            judge, intent="Says the living room is about 71 degrees."
        )

        # --- BEAT 3: order status ---
        # The agent may answer from the orders already returned by lookup_account
        # (grounded, no extra tool call) OR re-query lookup_order — both are valid.
        r = await session.run(user_input="What's the status of my most recent order?")
        await r.expect.contains_message(role="assistant").judge(
            judge,
            intent=(
                "Gives the status of one of Sarah's real orders — the Smart Thermostat V2 has "
                "shipped, or the Indoor Camera two pack is still processing. Does not invent an order."
            ),
        )

        # --- BEAT 4: policy via RAG ---
        r = await session.run(user_input="How long do I have to return a camera?")
        assert _called(r, "search_knowledge"), (
            "agent did not consult the policy knowledge base (RAG)"
        )

        # --- BEAT 5: warm transfer with summary ---
        r = await session.run(
            user_input="I'd like to talk to a real person about my subscription, please."
        )
        assert _called(r, "transfer_to_human"), (
            "agent did not initiate a transfer to a human"
        )
        await r.expect.contains_message(role="assistant").judge(
            judge,
            intent="Tells the customer it is connecting them to a person and that they won't need to repeat themselves.",
        )


@pytest.mark.asyncio
async def test_unknown_caller_is_handled() -> None:
    """An unrecognized account is handled gracefully, not hallucinated."""
    async with _judge() as judge, AgentSession() as session:
        await session.start(Assistant())
        await session.run(user_input="Hi")
        r = await session.run(user_input="My account number is A H zero zero zero zero")
        r2 = await session.run(user_input="Yes that's right")
        # should NOT greet a fake person; should ask again / say not found
        target = r2 if True else r
        await target.expect.contains_message(role="assistant").judge(
            judge,
            intent="Does not greet a specific named customer. Indicates the account wasn't found or asks them to re-read it.",
        )


@pytest.mark.asyncio
async def test_does_not_pad_order_numbers() -> None:
    """Regression: the agent must not invent/pad digits in a number read to it."""
    async with _judge() as judge, AgentSession() as session:
        await session.start(Assistant())
        await session.run(user_input="Hi")
        # give a short partial number; agent must not silently pad it to five digits
        r = await session.run(user_input="My order number is four four seven two")
        await r.expect.contains_message(role="assistant").judge(
            judge,
            intent=(
                "Does not confidently invent a five digit number from an incomplete one. "
                "Either asks for the rest of the number or reads back only what was given (4 4 7 2)."
            ),
        )
