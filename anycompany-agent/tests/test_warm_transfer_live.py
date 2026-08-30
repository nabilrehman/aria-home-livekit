"""LIVE warm-transfer test: refund request → transfer → Twilio actually dials.

Drives the real agent in a text session (no audio), asks for a refund and a
person, and then checks Twilio's Calls API for an outbound call to the transfer
target placed in the last two minutes. Needs:

    SIP_OUTBOUND_TRUNK_ID, TRANSFER_TO_NUMBER      (agent env)
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN          (to verify the dial happened)
    TOOLBOX_MCP_URL / MCP_TELEMETRY_URL            (as for the other live tests)

Skips cleanly when any of those are missing.
"""

import base64
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

import pytest
from livekit.agents import AgentSession

from agent import Assistant

NEEDED = (
    "SIP_OUTBOUND_TRUNK_ID",
    "TRANSFER_TO_NUMBER",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TOOLBOX_MCP_URL",
)
pytestmark = pytest.mark.skipif(
    not all(os.getenv(k) for k in NEEDED), reason=f"needs {', '.join(NEEDED)}"
)


def twilio_calls_to(number: str, since: datetime) -> list[dict]:
    sid, tok = os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"]
    url = (
        f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Calls.json"
        f"?To={number}&StartTime%3E={since.strftime('%Y-%m-%d')}&PageSize=20"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": "Basic "
            + base64.b64encode(f"{sid}:{tok}".encode()).decode()
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        calls = json.load(r).get("calls", [])
    out = []
    for c in calls:
        started = c.get("date_created")
        try:
            when = datetime.strptime(started, "%a, %d %b %Y %H:%M:%S %z")
        except Exception:
            continue
        if when >= since:
            out.append(c)
    return out


@pytest.mark.asyncio
async def test_refund_request_triggers_a_real_warm_transfer():
    started = datetime.now(timezone.utc) - timedelta(seconds=30)
    fired: dict = {}

    class Observed(Assistant):
        async def transfer_to_human(
            self, context, summary: str, department: str = "the support team"
        ):
            fired["summary"] = summary
            return await Assistant.transfer_to_human(self, context, summary, department)

    async with AgentSession() as session:
        await session.start(Observed())
        await session.run(user_input="Hi, I'm calling from +1 512 555 1188.")
        await session.run(
            user_input="I want a refund on order five eight one two zero, "
            "it arrived damaged. Please put me through to a person."
        )

    assert fired, "the agent never called transfer_to_human"
    assert "sarah" in fired["summary"].lower()

    calls = twilio_calls_to(os.environ["TRANSFER_TO_NUMBER"], started)
    assert calls, "Twilio shows no outbound call to the transfer target"
    assert calls[0]["direction"].startswith("outbound"), calls[0]["direction"]
