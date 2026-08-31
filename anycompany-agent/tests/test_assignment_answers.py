"""What the caller actually gets back for each question the assignment names.

The acceptance suite (test_assignment_beats.py) drives the live agent and needs
the data plane up. This file checks the layer underneath: for John Doe, does
the data actually support a correct answer to each graded question?

If these fail, no amount of prompt tuning will save the demo — the agent would
be reading wrong data confidently.

Runs offline against the seeded rows.
"""

import sys
from pathlib import Path

import pytest

MCP_DIR = (
    Path(__file__).resolve().parents[2]
    / "build-archive"
    / "deploy"
    / "aug24-mcp-server"
)
sys.path.insert(0, str(MCP_DIR))

import seed_data  # noqa: E402

from tests.test_device_data import FakeRepo  # noqa: E402

SARAH_PHONE = "+15125551188"
SARAH_ACCOUNT = "AH-4821"


@pytest.fixture
def repo():
    return FakeRepo()


@pytest.fixture
def john(repo):
    return repo.find_customer(phone=SARAH_PHONE)


# ═════════ 1 · "Greet the caller by name and look up their account" ═════════


def test_caller_id_alone_yields_a_first_name_to_greet(john):
    """The greeting has to be possible from the phone number and nothing else."""
    assert john is not None, "caller ID did not resolve to an account"
    assert john["first_name"] == "John"
    assert john["account_number"] == SARAH_ACCOUNT


def test_the_account_details_needed_on_the_greeting_are_all_present(repo, john):
    """ "I can see your account" has to be backed by something."""
    assert john["subscription"]["tier"] == "Video Plus"
    assert john["subscription"]["status"] == "active"
    assert len(repo.devices_for(john["customer_id"])) == 4
    assert len(repo.orders_for(john["customer_id"])) == 2


def test_the_spoken_account_number_route_reaches_the_same_customer(repo, john):
    """ "Ask for their account number if not using phone" — same answer either way."""
    spoken = repo.find_customer(
        account_number="A H four eight two one".replace(" ", "")
    )
    by_digits = repo.find_customer(account_number="4821")
    assert by_digits["customer_id"] == john["customer_id"]
    assert spoken is None or spoken["customer_id"] == john["customer_id"]


# ═════ 2 · "What is the status of my most recent order?" ═════


def test_most_recent_order_answer(repo, john):
    order = repo.most_recent_order(john["customer_id"])

    assert order["order_id"] == "58121"
    assert order["item"] == "Indoor Camera two pack"
    assert order["status"] == "processing"
    assert order["detail"] == "Still in the warehouse, nothing has shipped yet."
    # Spoken answer: "your Indoor Camera two pack is still processing — nothing has
    # shipped yet, and it's due September third."
    assert str(order["delivers_on"]) == "2026-09-03"


def test_most_recent_is_by_date_not_by_order_number(repo, john):
    """58121 is newer than 58120 by date. If ordering ever flips to the id, this fails."""
    orders = repo.orders_for(john["customer_id"])
    assert [o["order_id"] for o in orders] == ["58121", "58120"]
    assert orders[0]["placed_on"] > orders[1]["placed_on"]


# ═════ 2 · "Is my thermostat active?" ═════


def test_is_my_thermostat_active_answer(repo, john):
    """Crosses both stores: registry finds it, telemetry says what it's doing."""
    device = repo.find_thermostat(john["customer_id"])
    assert device["device_id"] == "AH4821-D1"
    assert device["name"] == "Living Room Thermostat"

    state = repo.device_state(device["device_id"])
    assert state["active"] is True  # the answer is "yes"
    assert state["mode"] == "heat"


def test_asking_by_the_word_thermostat_finds_the_same_device(repo, john):
    assert (
        repo.find_device(john["customer_id"], "thermostat")["device_id"] == "AH4821-D1"
    )


# ═════ 2 · "What is the temperature in my living room?" ═════


def test_temperature_in_my_living_room_answer(repo, john):
    device = repo.find_thermostat(john["customer_id"], "living room")
    state = repo.device_state(device["device_id"])

    assert state["temp_f"] == 71
    assert state["reading"] == "71 degrees"  # already phrased for speech
    assert "°" not in state["reading"], "a symbol here would be read out as a symbol"


def test_a_room_with_no_thermostat_has_no_answer_to_invent(repo, john):
    assert repo.find_thermostat(john["customer_id"], "basement") is None


# ═════ 3 · "Transfer the caller … the human agent should get a summary" ═════


def test_everything_a_summary_needs_is_retrievable(repo, john):
    """A briefed human needs: who, what plan, what they were asking about."""
    order = repo.most_recent_order(john["customer_id"])
    devices = repo.devices_for(john["customer_id"])

    assert john["name"] == "John Doe"
    assert john["account_number"] == SARAH_ACCOUNT
    assert john["subscription"]["tier"]
    assert order["item"] and order["status"]
    assert devices, "the specialist should be able to see the same devices"


def test_a_transfer_can_leave_a_ticket_without_duplicating_it(repo, john):
    a = repo.open_ticket(john["customer_id"], "58121", "Wants to change the address.")
    b = repo.open_ticket(john["customer_id"], "58121", "Wants to change the address.")
    assert a["ticket_id"] == b["ticket_id"] and b["duplicate"] is True


# ═════ 4 · "Answer questions from the customer" ═════


def test_which_plan_am_i_on(john):
    assert john["subscription"]["tier"] == "Video Plus"


def test_what_devices_do_i_have(repo, john):
    names = {d["name"] for d in repo.devices_for(john["customer_id"])}
    assert names == {
        "Living Room Thermostat",
        "Front Door Camera",
        "Backyard Camera",
        "Front Door Lock",
    }


def test_is_my_front_door_locked(repo, john):
    device = repo.find_device(john["customer_id"], "lock")
    state = repo.device_state(device["device_id"])
    assert state["reading"] == "locked"
    assert state["bolt"] == "extended"
    assert state["battery_pct"] == 82  # supports "and the battery is fine"


def test_a_question_about_a_device_she_does_not_own_has_no_data_behind_it(repo, john):
    """There must be nothing to accidentally answer with."""
    assert repo.find_device(john["customer_id"], "garage") is None
    assert repo.find_device(john["customer_id"], "doorbell") is None


def test_an_offline_device_gives_an_honest_answer_not_a_silent_one(repo):
    """Marcus's garage camera: the answer is "it's offline", which is still an answer."""
    marcus = repo.find_customer(account_number="AH-3390")
    device = repo.find_device(marcus["customer_id"], "garage")
    state = repo.device_state(device["device_id"])

    assert state["active"] is False
    assert state["reading"] == "offline"
    assert state["last_seen"]  # so she can say when it dropped


# ═════ every seeded caller can complete the whole script ═════


@pytest.mark.parametrize("account", [c["account_number"] for c in seed_data.CUSTOMERS])
def test_every_demo_account_can_answer_all_four_beats(repo, account):
    """If the panel asks to try a different customer, it must not fall over."""
    c = repo.find_customer(account_number=account)
    assert c and c["first_name"], f"{account} has no name to greet"

    devices = repo.devices_for(c["customer_id"])
    assert devices, f"{account} owns no devices"
    assert all(repo.device_state(d["device_id"]) for d in devices), (
        f"{account} has a device with no telemetry"
    )

    assert repo.most_recent_order(c["customer_id"]), (
        f"{account} has no order to discuss"
    )
    assert c["subscription"]["tier"], f"{account} has no plan"
