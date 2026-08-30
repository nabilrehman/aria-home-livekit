"""Long-term memory (Vertex AI Memory Bank) + the parallel preload."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from agent import Assistant  # noqa: E402
from tests.test_web_auth import main  # noqa: E402

PRE = {
    "devices": [
        {
            "device_id": "AH7104-D1",
            "name": "Aria Thermostat",
            "room": "living room",
            "on": True,
            "reading": "69 degrees",
        },
        {
            "device_id": "AH7104-D5",
            "name": "Aria Motion Sensor",
            "room": "hallway",
            "on": False,
            "reading": "needs battery",
        },
    ],
    "recent_order": {
        "order_id": "58131",
        "item": "Smart Sensor four pack",
        "status": "processing",
        "delivers_on": "2026-09-04",
        "detail": "Picked, not shipped.",
    },
    "memories": [
        {"fact": "Prefers to be contacted by text message."},
        {"fact": "The back door lock sticks in cold weather."},
    ],
}


def test_preload_renders_devices_order_and_memories():
    text = Assistant(
        known_account="AH-7104", known_name="Nabil", preload=PRE
    ).instructions
    assert "AH7104-D1" in text and "69 degrees" in text
    assert "NOT reporting" in text and "needs battery" in text
    assert "58131" in text and "2026-09-04" in text
    assert "text message" in text and "back door lock" in text
    assert "remember tool" in text


def test_no_preload_means_no_section():
    assert (
        "What you already know" not in Assistant(known_account="AH-7104").instructions
    )


@pytest.fixture
def client(monkeypatch):
    from tests.test_device_data import FakeRepo

    class Repo(FakeRepo):
        def memories(self, account, query="", top_k=5):
            return (
                [{"fact": "Prefers text messages.", "updated": "2026-08-30"}]
                if account == "AH-7104"
                else []
            )

        def recent_calls(self, account, limit=3):
            return [
                {
                    "call_id": "c1",
                    "ended_at": "2026-08-30T15:00:00",
                    "summary": "Asked about 58131.",
                    "next_steps": [],
                    "mood": "calm",
                    "outcome": "completed",
                }
            ]

    monkeypatch.setattr(main, "repo", Repo())
    monkeypatch.setattr(main, "ORDERS_API_KEY", "k")
    main.app.config["TESTING"] = True
    with main.app.test_client() as c:
        yield c


def test_preload_endpoint_is_one_round_trip(client):
    r = client.get("/api/preload?account=AH-7104", headers={"X-Api-Key": "k"})
    assert r.status_code == 200
    d = r.get_json()
    assert d["first_name"] == "Nabil" and len(d["devices"]) == 5
    assert d["recent_order"]["order_id"] == "58131"
    assert d["memories"][0]["fact"].startswith("Prefers")
    assert d["last_call"]["summary"] == "Asked about 58131."


def test_preload_needs_key_and_a_real_account(client):
    assert client.get("/api/preload?account=AH-7104").status_code == 401
    assert (
        client.get(
            "/api/preload?account=AH-0000", headers={"X-Api-Key": "k"}
        ).status_code
        == 404
    )
