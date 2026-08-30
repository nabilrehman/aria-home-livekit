"""
opaque_backend.py — what a real integration actually looks like.

The refund tool in agent.py is a teaching fiction: it has three neatly labelled
phases, so it can announce progress at each boundary. Almost no real tool works
that way.

A real tool is usually a thin wrapper around someone else's API — often reached
through MCP — and it looks like this:

    result = await client.call_tool("get_warranty", {"order_id": ...})

One await. It either returns or it doesn't. There is no progress callback, no
percentage, no phase. You know two things: when you started, and when it
finished. Everything in between is a black box whose duration you cannot
predict.

That constraint changes which tool you reach for, and this module exists so the
demo is honest about it.
"""

from __future__ import annotations

import asyncio
import os
import random


class BackendTimeout(Exception):
    """The upstream API did not answer in time."""


async def opaque_call(
    endpoint: str,
    *,
    seconds: float,
    timeout: float = 12.0,
) -> dict:
    """
    Stand-in for one call to somebody else's API.

    Deliberately gives you nothing while it runs — no progress, no phases, no
    way to know how much longer. Exactly like the real thing.

    Args:
        endpoint: Which fake endpoint is being called, for logging.
        seconds: How long this particular call will take.
        timeout: Give up after this long.
    """
    try:
        await asyncio.wait_for(asyncio.sleep(seconds), timeout=timeout)
    except asyncio.TimeoutError as exc:
        raise BackendTimeout(f"{endpoint} did not respond within {timeout}s") from exc

    return {"endpoint": endpoint, "took_seconds": round(seconds, 1), "ok": True}


# Fake warranty records, keyed by order.
WARRANTY = {
    "58120": {
        "covered": True,
        "expires": "August thirtieth, twenty twenty eight",
        "plan": "two year standard",
    },
    "58121": {
        "covered": True,
        "expires": "September third, twenty twenty eight",
        "plan": "two year standard",
    },
    "44721": {
        "covered": True,
        "expires": "August fourteenth, twenty twenty eight",
        "plan": "two year standard",
    },
    "44722": {
        "covered": True,
        "expires": "August tenth, twenty twenty eight",
        "plan": "two year standard",
    },
    "44723": {"covered": False, "expires": "expired", "plan": "none"},
}


def warranty_latency() -> float:
    """
    How long the warranty API takes today.

    Unpredictable on purpose. This is the honest situation: you cannot write
    "this takes about four seconds" into a prompt, because sometimes it's one
    second and sometimes it's nine.
    """
    return random.choice([1.1, 2.4, 4.8, 7.5])


# --------------------------------------------------------------- bimodal API
# The genuinely awkward case: usually fast, occasionally very slow, and you
# cannot tell which you are getting until it answers.


def carrier_latency(force: str | None = None) -> float:
    """
    Carrier tracking API. Comes back in ~2s most of the time, ~15s sometimes.

    There is no header, no hint, no way to predict it at call time. Design for
    both or you will be wrong half the time.
    """
    # CARRIER_SPEED=fast|slow forces a path so you can test deterministically.
    forced = force or os.getenv("CARRIER_SPEED")
    if forced == "fast":
        return 2.0
    if forced == "slow":
        return 15.0
    return random.choice([1.8, 2.1, 2.3, 14.6, 15.2])
