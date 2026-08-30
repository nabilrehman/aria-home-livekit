"""The order/device tools are plain HTTP function tools, scoped by the agent, not MCP.

They call the orders REST API on the web service. These tests stub the HTTP
layer and check the tool contract the model sees: found / not found / API down,
and that spoken digits are normalised before the call.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent import Assistant  # noqa: E402

NABIL_ORDERS = {
    "account": "AH-7104",
    "orders": [
        {
            "order_id": "58131",
            "item": "Smart Sensor four pack",
            "status": "processing",
            "detail": "Picked in the warehouse, not yet shipped.",
            "placed_on": "2026-08-28",
            "delivers_on": "2026-09-04",
        },
        {
            "order_id": "58130",
            "item": "Video Doorbell Pro",
            "status": "shipped",
            "detail": "With the carrier, arriving Sunday.",
            "placed_on": "2026-08-26",
            "delivers_on": "2026-08-31",
        },
        {
            "order_id": "58129",
            "item": "Outdoor Camera Mount",
            "status": "delivered",
            "detail": "Signed for at the front door.",
            "placed_on": "2026-08-14",
            "delivers_on": "2026-08-20",
        },
    ],
}


def stub(monkeypatch, handler):
    async def _fake(self, path, **params):
        return handler(path, params)

    monkeypatch.setattr(Assistant, "_my", _fake)


@pytest.mark.asyncio
async def test_recent_order_returns_the_newest_with_context(monkeypatch):
    calls = []
    stub(monkeypatch, lambda p, q: (calls.append((p, q)), NABIL_ORDERS)[1])

    a = Assistant(known_account="AH-7104")
    out = await a.my_recent_order(None)

    assert calls == [("/api/my/orders", {})]
    assert out["found"] is True
    assert out["order_id"] == "58131" and out["status"] == "processing"
    assert out["older_orders"] == 2
    assert "say" in out


@pytest.mark.asyncio
async def test_recent_order_with_no_orders_says_so(monkeypatch):
    stub(monkeypatch, lambda p, q: {"orders": []})
    out = await Assistant(known_account="AH-0000").my_recent_order(None)
    assert out["found"] is False and "no orders" in out["say"].lower()


@pytest.mark.asyncio
async def test_lookup_order_normalises_spoken_digits(monkeypatch):
    seen = []
    stub(monkeypatch, lambda p, q: (seen.append(p), NABIL_ORDERS)[1])
    out = await Assistant(known_account="AH-7104").my_order(None, "5 8 1 3 0")
    assert seen == ["/api/my/orders"]
    assert out["status"] == "shipped" and out["order_id"] == "58130"


@pytest.mark.asyncio
async def test_lookup_order_not_found_forbids_padding(monkeypatch):
    stub(monkeypatch, lambda p, q: NABIL_ORDERS)
    out = await Assistant(known_account="AH-7104").my_order(None, "4472")
    assert out["found"] is False
    assert "pad" in out["say"].lower()


@pytest.mark.asyncio
async def test_orders_api_outage_degrades_honestly(monkeypatch):
    async def _boom(self, path, **params):
        raise RuntimeError("connection refused")

    monkeypatch.setattr(Assistant, "_orders_api", _boom)
    a = Assistant(known_account="AH-7104")
    out = await a.my_recent_order(None)
    assert out["found"] is False
    assert "not reachable" in out["say"]


def test_toolbox_does_not_also_serve_orders():
    """No duplicate tools: orders come from HTTP, identity/devices from Toolbox."""
    src = (Path(__file__).resolve().parents[1] / "src" / "agent.py").read_text()
    block = src[
        src.index("allowed_tools=[") : src.index("]", src.index("allowed_tools=["))
    ]
    assert "find_device" not in block and "list_devices" not in block
    assert "lookup_account_by_phone" in block and "file_ticket" in block


@pytest.mark.asyncio
async def test_unidentified_caller_cannot_read_anything():
    """No account in state → no request is even made."""
    out = await Assistant().my_recent_order(None)
    assert out["found"] is False and "Identify the caller" in out["say"]


def test_identity_is_captured_from_the_verified_lookup_result():
    import agent as agent_mod
    from types import SimpleNamespace

    seen = []
    agent_mod._identity_sink = seen.append
    ctx = SimpleNamespace(
        tool_name="lookup_account_by_phone",
        result=SimpleNamespace(
            content=[
                SimpleNamespace(
                    text='{"customer_id":5,"account_number":"AH-7104","first_name":"Nabil"}',
                    model_dump_json=lambda: "{}",
                )
            ]
        ),
    )
    agent_mod._mcp_result(ctx)
    assert seen == ["AH-7104"]
    agent_mod._identity_sink = None
