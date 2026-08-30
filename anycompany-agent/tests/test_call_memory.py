"""Call memory + PII masking: what leaves the agent at hang-up, and what comes back."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pii  # noqa: E402
from agent import Assistant  # noqa: E402
from tests.test_web_auth import main  # noqa: E402


# ── masking ──────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "raw,expect",
    [
        ("call me on 737 205 9240", "[phone]"),
        ("my number is +1 (512) 555-1188 thanks", "[phone]"),
        ("email nabilrehman8@gmail.com", "[email]"),
        ("card 4111 1111 1111 1111 please", "[card]"),
        ("ssn 123-45-6789", "[ssn]"),
        ("account AH-4821", "AH-••21"),
        ("tracking 1Z999AA10123459981", "[number]"),
    ],
)
def test_mask_redacts(raw, expect):
    assert expect in pii.mask(raw)


def test_mask_keeps_what_the_business_needs():
    out = pii.mask("order 58131 is processing, thermostat at 69 degrees")
    assert "58131" in out and "69" in out  # 5-digit orders and readings survive


def test_mask_brief_only_touches_free_text():
    b = pii.mask_brief(
        {
            "summary": "Sarah on 512 555 1188 wants a refund",
            "mood": "calm",
            "next_steps": ["Call back on 512-555-1188"],
        }
    )
    assert "[phone]" in b["summary"] and "[phone]" in b["next_steps"][0]
    assert b["mood"] == "calm"


# ── call record ──────────────────────────────────────────────────────────────


def _history():
    msg = lambda role, text: SimpleNamespace(
        type="message", role=role, text_content=text
    )
    fc = lambda name, args: SimpleNamespace(
        type="function_call", name=name, arguments=args
    )
    out = lambda o: SimpleNamespace(type="function_call_output", output=o)
    return SimpleNamespace(
        items=[
            msg("assistant", "Hi, this is Ember."),
            msg("user", "My number is 512 555 1188."),
            fc("lookup_account_by_phone", '{"phone": "512 555 1188"}'),
            out('{"customer_id":1,"account_number":"AH-4821","first_name":"Sarah"}'),
            msg("assistant", "Hi Sarah, I can see your account."),
            msg("user", "Where's order 58121?"),
        ]
    )


def test_call_record_is_masked_and_structured():
    rec = Assistant().call_record(_history())
    assert rec["turns"] == 2
    assert rec["transcript"][1]["text"] == "My number is [phone]."
    assert rec["tool_calls"][0]["tool"] == "lookup_account_by_phone"
    assert "[phone]" in rec["tool_calls"][0]["args"]
    assert "58121" in rec["transcript"][-1]["text"]


def test_account_is_recovered_from_a_guest_calls_history():
    assert Assistant._account_from_history(_history()) == "AH-4821"


def test_last_call_is_injected_for_signed_in_callers():
    a = Assistant(
        known_account="AH-7104",
        known_name="Nabil Rehman",
        last_call={
            "ended_at": "2026-08-29T21:00:00",
            "summary": "Asked about the doorbell order.",
            "next_steps": ["Check delivery"],
        },
    )
    assert "Their previous call" in a.instructions
    assert "doorbell order" in a.instructions and "2026-08-29" in a.instructions
    assert "Their previous call" not in Assistant(known_account="AH-7104").instructions


# ── endpoints ────────────────────────────────────────────────────────────────


@pytest.fixture
def client(monkeypatch):
    saved = {}

    class Repo:
        def save_call(self, account, call):
            saved[account] = call
            return "c1"

        def recent_calls(self, account, limit=3):
            c = saved.get(account)
            return (
                [
                    {
                        "call_id": "c1",
                        "ended_at": "2026-08-30T15:00:00",
                        **{
                            k: c[k]
                            for k in ("summary", "next_steps", "mood", "outcome")
                        },
                    }
                ]
                if c
                else []
            )

    monkeypatch.setattr(main, "repo", Repo())
    monkeypatch.setattr(main, "ORDERS_API_KEY", "k")
    main.app.config["TESTING"] = True
    with main.app.test_client() as c:
        yield c


def test_calls_round_trip(client):
    body = {
        "account_number": "ah-7104",
        "summary": "Refund on 58130.",
        "next_steps": ["Approve"],
        "mood": "calm",
        "urgency": "normal",
        "outcome": "transferred",
        "transcript": [{"role": "user", "text": "hi"}],
    }
    assert (
        client.post("/api/calls", json=body, headers={"X-Api-Key": "k"}).status_code
        == 201
    )
    calls = client.get(
        "/api/calls?account=AH-7104", headers={"X-Api-Key": "k"}
    ).get_json()["calls"]
    assert (
        calls[0]["summary"] == "Refund on 58130."
        and calls[0]["outcome"] == "transferred"
    )


def test_calls_need_the_key(client):
    assert (
        client.post("/api/calls", json={"account_number": "AH-7104"}).status_code == 401
    )
    assert client.get("/api/calls?account=AH-7104").status_code == 401
