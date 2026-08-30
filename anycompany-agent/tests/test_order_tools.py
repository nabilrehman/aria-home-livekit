"""The order tools are plain HTTP function tools, not MCP.

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
    "found": True,
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

    monkeypatch.setattr(Assistant, "_orders_api", _fake)


@pytest.mark.asyncio
async def test_recent_order_returns_the_newest_with_context(monkeypatch):
    calls = []
    stub(monkeypatch, lambda p, q: (calls.append((p, q)), NABIL_ORDERS)[1])

    out = await Assistant().get_recent_order(None, "AH-7104")

    assert calls == [("/api/orders", {"account": "AH-7104"})]
    assert out["found"] is True
    assert out["order_id"] == "58131" and out["status"] == "processing"
    assert out["older_orders"] == 2
    assert "say" in out


@pytest.mark.asyncio
async def test_recent_order_with_no_orders_says_so(monkeypatch):
    stub(monkeypatch, lambda p, q: {"found": True, "orders": []})
    out = await Assistant().get_recent_order(None, "AH-0000")
    assert out["found"] is False and "no orders" in out["say"].lower()


@pytest.mark.asyncio
async def test_lookup_order_normalises_spoken_digits(monkeypatch):
    seen = []
    stub(
        monkeypatch,
        lambda p, q: (
            seen.append(p),
            {"found": True, "order_id": "58130", "status": "shipped"},
        )[1],
    )
    out = await Assistant().lookup_order(None, "5 8 1 3 0")
    assert seen == ["/api/orders/58130"]
    assert out["status"] == "shipped"


@pytest.mark.asyncio
async def test_lookup_order_not_found_forbids_padding(monkeypatch):
    stub(monkeypatch, lambda p, q: {"found": False})
    out = await Assistant().lookup_order(None, "4472")
    assert out["found"] is False
    assert "pad" in out["say"].lower()


@pytest.mark.asyncio
async def test_orders_api_outage_degrades_honestly(monkeypatch):
    async def _boom(self, path, **params):
        raise RuntimeError("connection refused")

    monkeypatch.setattr(Assistant, "_orders_api", _boom)
    out = await Assistant().get_recent_order(None, "AH-7104")
    assert out["found"] is False
    assert "not reachable" in out["say"]


def test_toolbox_does_not_also_serve_orders():
    """No duplicate tools: orders come from HTTP, identity/devices from Toolbox."""
    src = (Path(__file__).resolve().parents[1] / "src" / "agent.py").read_text()
    block = src[
        src.index("allowed_tools=[") : src.index("]", src.index("allowed_tools=["))
    ]
    assert "get_recent_order" not in block and "lookup_order" not in block
    assert "lookup_account_by_phone" in block and "find_device" in block
