"""One live check of the KBA flow: the identify task against the real endpoint.

No LLM involved — this exercises the verification seam itself: the task's
attempt logic on top of the deployed /api/verify compare. Needs .env.local.
"""

import os

import pytest
from dotenv import load_dotenv

load_dotenv(".env.local")

from agent import Assistant  # noqa: E402
from tasks import IdentifyCallerTask  # noqa: E402

pytestmark = pytest.mark.skipif(
    not os.getenv("ORDERS_API_KEY"), reason="needs .env.local"
)


@pytest.mark.asyncio
async def test_kba_against_the_live_endpoint(monkeypatch):
    a = Assistant()
    t = IdentifyCallerTask([], a._verify_caller)
    done = {}
    monkeypatch.setattr(t, "complete", lambda r: done.setdefault("r", r))
    monkeypatch.setattr(t, "done", lambda: "r" in done)

    # lookup located Sarah's account — not verified yet
    t.identified("AH-4821")
    assert "r" not in done

    # wrong email -> rejected, one attempt used
    out = await t.verify_identity(None, "Sarah", email="wrong@example.com")
    assert out["verified"] is False and "r" not in done

    # right email (as the model would assemble it from speech) -> verified
    await t.verify_identity(None, "Sarah", email="sarah@example.com")
    assert done["r"].account == "AH-4821" and done["r"].first_name == "Sarah"
