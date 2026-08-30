"""Specialist desk: the human-support console that receives warm handoffs.

Agent posts a brief → desk sees it ringing → Accept mints a room token for a
`specialist-*` identity (the agent steps back on that) → Decline records why.
"""

import base64
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tests.test_web_auth import API_SECRET, main  # noqa: E402  (app with stubs)

AGENT = {"X-Api-Key": "test-orders-key"}
DESK = {"X-Desk-Pin": "4321"}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main, "ORDERS_API_KEY", "test-orders-key")
    monkeypatch.setattr(main, "DESK_PIN", "4321")
    main._handoffs.clear()
    main.app.config["TESTING"] = True
    with main.app.test_client() as c:
        yield c


BRIEF = {
    "room": "web-abc123",
    "department": "the refunds team",
    "brief": {
        "summary": "Sarah wants a refund on 58120.",
        "next_steps": ["Check damage photos"],
        "mood": "frustrated",
        "urgency": "high",
    },
    "caller": {"name": "Sarah Chen", "account": "AH-4821"},
}


def claims(tok):
    p = tok.split(".")[1]
    p += "=" * (-len(p) % 4)
    return json.loads(base64.urlsafe_b64decode(p))


def test_agent_needs_the_api_key_to_ring(client):
    assert client.post("/api/handoffs", json=BRIEF).status_code == 401


def test_desk_needs_the_pin(client):
    assert client.get("/api/handoffs").status_code == 401
    assert (
        client.get("/api/handoffs", headers={"X-Desk-Pin": "nope"}).status_code == 401
    )


def test_handoff_rings_and_is_visible_to_the_desk(client):
    r = client.post("/api/handoffs", json=BRIEF, headers=AGENT)
    assert r.status_code == 201
    hid = r.get_json()["id"]

    desk = client.get("/api/handoffs", headers=DESK).get_json()["handoffs"]
    assert desk[0]["id"] == hid and desk[0]["status"] == "ringing"
    assert desk[0]["brief"]["mood"] == "frustrated"
    assert desk[0]["caller"]["name"] == "Sarah Chen"


def test_accept_mints_a_specialist_token_for_the_callers_room(client):
    hid = client.post("/api/handoffs", json=BRIEF, headers=AGENT).get_json()["id"]
    r = client.post(f"/api/handoffs/{hid}/accept", json={"name": "Ahmad"}, headers=DESK)
    assert r.status_code == 200
    body = r.get_json()
    c = claims(body["token"])
    assert c["video"]["room"] == "web-abc123"
    assert c["sub"].startswith("specialist-")  # the agent's step-back trigger
    assert c["video"]["canPublish"] is True
    assert API_SECRET not in json.dumps(body)

    # the agent, polling, now sees it accepted
    st = client.get(f"/api/handoffs/{hid}", headers=AGENT).get_json()
    assert st["status"] == "accepted" and st["specialist"] == "Ahmad"


def test_decline_is_recorded_for_the_agent(client):
    hid = client.post("/api/handoffs", json=BRIEF, headers=AGENT).get_json()["id"]
    client.post(f"/api/handoffs/{hid}/decline", json={"reason": "busy"}, headers=DESK)
    assert (
        client.get(f"/api/handoffs/{hid}", headers=AGENT).get_json()["status"]
        == "declined"
    )


def test_desk_page_is_served(client):
    r = client.get("/desk")
    assert r.status_code == 200 and b"Specialist Desk" in r.data


# ── agent side ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_agent_rings_the_desk_and_returns_the_answer(monkeypatch):
    import agent as agent_mod
    from agent import Assistant

    monkeypatch.setattr(agent_mod, "ORDERS_API_KEY", "k")
    monkeypatch.setattr(agent_mod, "DESK_RING_SECONDS", 4)
    calls = []

    class Resp:
        def __init__(self, code, body):
            self.status_code, self._b = code, body

        def json(self):
            return self._b

        def raise_for_status(self):
            pass

    class Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, path, json=None, headers=None):
            calls.append(("post", path, json))
            return Resp(201, {"id": "h1"})

        async def get(self, path, headers=None):
            calls.append(("get", path, None))
            return Resp(200, {"status": "accepted"})

    monkeypatch.setattr(agent_mod, "_DeskClient", Client)
    monkeypatch.setattr(agent_mod.asyncio, "sleep", lambda s: _noop())

    a = Assistant(known_account="AH-4821", known_name="Sarah Chen")
    out = await a._ring_desk(
        "the refunds team",
        {"summary": "x", "next_steps": [], "mood": "calm", "urgency": "normal"},
    )
    assert out == "accepted"
    assert (
        calls[0][1] == "/api/handoffs" and calls[0][2]["caller"]["account"] == "AH-4821"
    )


async def _noop():
    return None


@pytest.mark.asyncio
async def test_agent_treats_a_dead_desk_as_unanswered(monkeypatch):
    import agent as agent_mod
    from agent import Assistant

    monkeypatch.setattr(agent_mod, "ORDERS_API_KEY", "k")

    class Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            raise RuntimeError("connection refused")

        async def __aexit__(self, *a):
            return False

    monkeypatch.setattr(agent_mod, "_DeskClient", Client)
    assert await Assistant()._ring_desk("x", {}) == "unanswered"
