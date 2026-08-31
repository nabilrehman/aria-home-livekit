"""The signed-in half of the panel demo: Nabil's call, exactly as the runbook
plays it.

John's guest call is test_demo_beats.py::test_full_demo_happy_path. This is
the other call: the caller arrived authenticated (account on the LiveKit
token), the preload already ran, so the agent starts knowing the devices, the
latest order, and the Memory Bank facts — and the interesting assertions are
that it USES that context instead of calling tools, and that the refund ask
ends in a transfer with a summary.

Live integration test: LiveKit Inference + the deployed web preload + MCP.
Run:  uv run pytest tests/test_demo_nabil.py -v -s
"""

import json
import os
import urllib.request

import pytest
from dotenv import load_dotenv
from livekit.agents import AgentSession, inference

from agent import ORDERS_API_URL, Assistant

load_dotenv(".env.local")


def _judge():
    return inference.LLM(model="openai/gpt-4.1-mini")


def _called(result, *names) -> bool:
    for n in names:
        try:
            result.expect.contains_function_call(name=n)
            return True
        except AssertionError:
            continue
    return False


def _live_preload() -> dict:
    """The same payload the entrypoint fetches in parallel with session start."""
    req = urllib.request.Request(
        f"{ORDERS_API_URL}/api/preload?account=AH-7104",
        headers={"X-Api-Key": os.environ["ORDERS_API_KEY"]},
    )
    return json.load(urllib.request.urlopen(req, timeout=20))


@pytest.mark.asyncio
async def test_nabil_signed_in_demo_flow() -> None:
    pre = _live_preload()
    assert pre.get("first_name") == "Nabil" and pre.get("devices"), (
        "preload endpoint did not return Nabil's home"
    )

    async with _judge() as judge, AgentSession() as session:
        await session.start(
            Assistant(known_account="AH-7104", known_name="Nabil", preload=pre)
        )

        # --- Act 1: greeting knows him; no identification questions ---
        r = await session.run(user_input="Hi")
        assert not _called(r, "lookup_account_by_phone", "lookup_account_by_number"), (
            "signed-in caller was asked to identify again"
        )
        await r.expect.contains_message(role="assistant").judge(
            judge,
            intent="Greets the caller by the name Nabil (already knows who he is); "
            "does NOT ask for a phone or account number.",
        )

        # --- Act 1: hallway sensor — answered from preloaded live state ---
        r = await session.run(user_input="What do you know about my hallway sensor?")
        await r.expect.contains_message(role="assistant").judge(
            judge,
            intent="Says the hallway motion sensor is not reporting / offline or "
            "needs attention (e.g. a battery). Grounded, no invented readings.",
        )

        # --- Act 2: most recent order ---
        r = await session.run(user_input="What's the status of my most recent order?")
        await r.expect.contains_message(role="assistant").judge(
            judge,
            intent="Gives the status of Nabil's most recent order: order five "
            "eight one three one (58131) is processing, due around September "
            "fourth. Saying that order number and date is CORRECT — it is his "
            "real order.",
        )

        # --- Act 2: living room thermostat ---
        r = await session.run(
            user_input="Is my living room thermostat on, and what is it set to?"
        )
        await r.expect.contains_message(role="assistant").judge(
            judge,
            intent="Says whether the living room thermostat is on and gives its "
            "current reading or setting as a specific number of degrees.",
        )

        # --- Act 3: remember for next time ---
        r = await session.run(
            user_input="Please remember that my back door lock sticks when it's cold."
        )
        if not _called(r, "remember"):
            evs = getattr(r, "events", None) or []
            print("\nDEBUG remember turn events:")
            for e in evs:
                print("  ", type(e).__name__, str(getattr(e, "item", e))[:220])
            raise AssertionError("agent did not store the fact with remember")
        await r.expect.contains_message(role="assistant").judge(
            judge, intent="Confirms it will remember that for next time."
        )

        # --- Act 4: damaged order -> return flow or straight transfer ---
        r = await session.run(
            user_input="My order five eight one three zero arrived damaged. "
            "I want a refund — please put me through to someone."
        )
        assert _called(r, "start_return", "transfer_to_human"), (
            "refund request triggered neither the return intake nor a transfer"
        )
        await r.expect.contains_message(role="assistant").judge(
            judge,
            intent="Moves the refund forward: either starts taking the return "
            "details (asks about the order/damage) or says it is connecting him "
            "to a specialist with a summary passed along.",
        )
