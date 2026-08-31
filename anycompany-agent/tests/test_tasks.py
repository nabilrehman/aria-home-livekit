"""Bounded sub-workflows (tasks.py) and the tool gating around them.

Pins the properties that matter:
  - the return decision is code, driven by dates and condition, never the model
  - each task exposes only its own tools, plus an explicit exit
  - scoped tools do not exist until the caller is identified, and reappear after
  - the identification backstop completes the task from the verified DB row
"""

import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent import Assistant  # noqa: E402
from tasks import (  # noqa: E402
    RETURN_WINDOW_DAYS,
    SECURITY_WINDOW_DAYS,
    IdentifyCallerTask,
    ReturnIntakeTask,
    TroubleshootDeviceTask,
    decide_return,
)

TODAY = date(2026, 8, 30)


def _names(tools) -> set[str]:
    return {Assistant._tool_name(t) for t in tools}


# ── the decision is code ─────────────────────────────────────────────────────


def test_damaged_goes_to_refund_desk_regardless_of_window():
    old = {"status": "delivered", "delivers_on": "2026-01-01"}
    assert decide_return(old, "damaged", TODAY) == (True, "refund_desk")
    assert decide_return(old, "defective", TODAY) == (True, "refund_desk")
    assert decide_return(old, "wrong_item", TODAY) == (True, "refund_desk")


def test_unwanted_inside_window_is_refund_desk_outside_is_declined():
    # Policy v3: 30 days for most devices...
    assert RETURN_WINDOW_DAYS == 30
    inside = {
        "status": "delivered",
        "delivers_on": "2026-08-05",
        "item": "Aria Thermostat",
    }
    outside = {
        "status": "delivered",
        "delivers_on": "2026-07-01",
        "item": "Aria Thermostat",
    }
    assert decide_return(inside, "unwanted", TODAY) == (True, "refund_desk")
    assert decide_return(outside, "unwanted", TODAY) == (False, "declined")
    edge = {
        "status": "delivered",
        "delivers_on": "2026-07-31",
        "item": "Aria Thermostat",
    }
    assert (TODAY - date(2026, 7, 31)).days == RETURN_WINDOW_DAYS
    assert decide_return(edge, "unwanted", TODAY)[0] is True


def test_locks_and_doorbells_get_the_14_day_security_window():
    # ...and 14 days for security devices (Smart Locks, Doorbell Cameras).
    assert SECURITY_WINDOW_DAYS == 14
    lock_20d = {
        "status": "delivered",
        "delivers_on": "2026-08-10",
        "item": "Aria Smart Lock",
    }
    bell_10d = {
        "status": "delivered",
        "delivers_on": "2026-08-20",
        "item": "Aria Doorbell Cam",
    }
    assert decide_return(lock_20d, "unwanted", TODAY) == (False, "declined")
    assert decide_return(bell_10d, "unwanted", TODAY) == (True, "refund_desk")
    # damaged overrides the window even for security devices
    assert decide_return(lock_20d, "damaged", TODAY) == (True, "refund_desk")


def test_not_yet_delivered_is_a_cancellation_to_the_desk():
    assert decide_return({"status": "processing"}, "unwanted", TODAY) == (
        True,
        "refund_desk",
    )
    assert decide_return({"status": "shipped"}, "other", TODAY) == (True, "refund_desk")


def test_unknown_delivery_date_falls_back_to_a_ticket():
    assert decide_return({"status": "delivered"}, "unwanted", TODAY) == (
        False,
        "ticket",
    )


# ── each task sees only its own tools ────────────────────────────────────────


@pytest.mark.asyncio
async def test_return_task_tools_are_lookup_record_stop_plus_policy():
    async def lookup(n=""):
        return {"found": True}

    fake_policy = SimpleNamespace(info=SimpleNamespace(name="search_knowledge"))
    t = ReturnIntakeTask(lookup, policy_tools=[fake_policy], order_hint="58130")
    assert _names(t.tools) == {
        "lookup_order",
        "record_return",
        "stop_return",
        "search_knowledge",
    }
    assert "58130" in t.instructions
    assert "never" not in t.instructions.lower() or "refund" in t.instructions.lower()


@pytest.mark.asyncio
async def test_troubleshoot_task_tools_are_find_conclude_stop_plus_telemetry():
    async def find(d):
        return {"found": True}

    tel = [
        SimpleNamespace(info=SimpleNamespace(name=n))
        for n in ("get_device_state", "get_device_history", "search_knowledge")
    ]
    t = TroubleshootDeviceTask(find, telemetry_tools=tel, description="hallway sensor")
    assert _names(t.tools) == {
        "find_device",
        "conclude",
        "stop_troubleshooting",
        "get_device_state",
        "get_device_history",
        "search_knowledge",
    }


@pytest.mark.asyncio
async def test_identify_task_tools_are_the_two_lookups_plus_verify_and_give_up():
    lookups = [
        SimpleNamespace(info=SimpleNamespace(name=n))
        for n in ("lookup_account_by_phone", "lookup_account_by_number")
    ]
    t = IdentifyCallerTask(lookups, _always_pass)
    assert _names(t.tools) == {
        "lookup_account_by_phone",
        "lookup_account_by_number",
        "verify_identity",
        "confirm_identity",  # registered always; refuses at runtime when KBA is on
        "cannot_identify",
    }


# ── task completion carries the typed result ─────────────────────────────────


@pytest.mark.asyncio
async def test_record_return_completes_with_a_typed_result(monkeypatch):
    async def lookup(n=""):
        return {
            "found": True,
            "order_id": "58130",
            "item": "Aria Doorbell",
            "status": "delivered",
            "delivers_on": "2026-08-25",
        }

    t = ReturnIntakeTask(lookup)
    got = {}
    monkeypatch.setattr(t, "complete", lambda r: got.setdefault("r", r))
    monkeypatch.setattr(t, "done", lambda: False)
    await t.record_return(None, "58130", "damaged", "arrived cracked")
    r = got["r"]
    assert r.order_id == "58130" and r.condition == "damaged"
    assert r.next == "refund_desk" and r.within_window is True


@pytest.mark.asyncio
async def test_record_return_refuses_an_order_not_on_the_account():
    from livekit.agents import llm

    async def lookup(n=""):
        return {"found": False}

    t = ReturnIntakeTask(lookup)
    with pytest.raises(llm.ToolError):
        await t.record_return(None, "58131", "damaged", "x")


@pytest.mark.asyncio
async def test_stop_return_and_conclude_map_to_next_steps(monkeypatch):
    async def lookup(n=""):
        return {}

    t = ReturnIntakeTask(lookup)
    got = {}
    monkeypatch.setattr(t, "complete", lambda r: got.setdefault("r", r))
    monkeypatch.setattr(t, "done", lambda: False)
    await t.stop_return(None, "wants_person")
    assert got["r"].next == "person"

    async def find(d):
        return {}

    t2 = TroubleshootDeviceTask(find)
    got2 = {}
    monkeypatch.setattr(t2, "complete", lambda r: got2.setdefault("r", r))
    monkeypatch.setattr(t2, "done", lambda: False)
    await t2.conclude(None, "AH7104-D5", "Hallway Sensor", "battery flat", False)
    assert got2["r"].next == "ticket" and got2["r"].resolved is False


async def _always_pass(account, email="", phone=""):
    return True


@pytest.mark.asyncio
async def test_lookup_alone_no_longer_completes_identification(monkeypatch):
    """A located account is not a verified caller."""
    t = IdentifyCallerTask([], _always_pass)
    got = {}
    monkeypatch.setattr(t, "complete", lambda r: got.setdefault("r", r))
    monkeypatch.setattr(t, "done", lambda: False)
    a = Assistant()
    a._identify_task = t
    a._identified("AH-4821")
    assert a.known_account == ""  # NOT adopted until verification passes
    assert "r" not in got  # and the task is not complete
    assert t._account == "AH-4821"  # held as a candidate inside the task only


@pytest.mark.asyncio
async def test_without_kba_lookup_still_identifies(monkeypatch):
    t = IdentifyCallerTask([])  # verify=None: the assignment's minimal beat
    got = {}
    monkeypatch.setattr(t, "complete", lambda r: got.setdefault("r", r))
    monkeypatch.setattr(t, "done", lambda: "r" in got)
    a = Assistant()
    a._identify_task = t
    a._identified("AH-4821")
    assert a.known_account == "AH-4821"
    assert got["r"].account == "AH-4821"


@pytest.mark.asyncio
async def test_verify_pass_completes_and_fail_twice_ends_identification(monkeypatch):
    answers = iter([False, False])

    async def verify(account, email="", phone=""):
        return next(answers)

    t = IdentifyCallerTask([], verify)
    t._account = "AH-4821"
    got = {}
    monkeypatch.setattr(t, "complete", lambda r: got.setdefault("r", r))
    monkeypatch.setattr(t, "done", lambda: False)
    out = await t.verify_identity(None, "John", email="wrong@example.com")
    assert out["verified"] is False and "r" not in got
    await t.verify_identity(None, "John", email="still-wrong@example.com")
    assert got["r"] is None  # two strikes -> unverified

    t2 = IdentifyCallerTask([], _always_pass)
    t2._account = "AH-4821"
    got2 = {}
    monkeypatch.setattr(t2, "complete", lambda r: got2.setdefault("r", r))
    monkeypatch.setattr(t2, "done", lambda: False)
    await t2.verify_identity(None, "John", email="johndoe@gmail.com")
    assert got2["r"].account == "AH-4821" and got2["r"].first_name == "John"


# ── gating: scoped tools do not exist until the caller is known ──────────────


def test_scoped_tools_are_gated_for_an_unknown_caller():
    a = Assistant()
    visible = _names(a.gated_tools())
    assert visible == {"end_call", "transfer_to_human"}
    assert Assistant.GATED_TOOLS <= _names(a.tools)


def test_start_return_and_troubleshoot_are_registered_and_old_tools_are_gone():
    names = _names(Assistant().tools)
    assert {"start_return", "troubleshoot_device"} <= names
    assert not {"request_refund", "sync_device"} & names


@pytest.mark.asyncio
async def test_wordless_tts_utterances_are_swallowed():
    from agent import _speakable_only

    async def gen(chunks):
        for c in chunks:
            yield c

    async def collect(chunks):
        return [c async for c in _speakable_only(gen(chunks))]

    # real words pass through untouched, markup and all
    assert await collect(["Okay, ", "found it."]) == ["Okay, ", "found it."]
    assert await collect(['<expr type="calm"/>', "One sec."]) == [
        '<expr type="calm"/>',
        "One sec.",
    ]
    # wordless streams are swallowed instead of becoming babble
    assert await collect(["…", " ", "..."]) == []
    assert await collect(['<expr type="sigh"/>', "(break)"]) == []
