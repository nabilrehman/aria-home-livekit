"""Data-layer tests for the Aria Home MCP server.

The architecture being pinned down: the device REGISTRY is relational (Cloud SQL)
and the device STATE is a document (Firestore), joined on device_id. These tests
fake both stores so they run offline, and assert the seam holds — including that
a store being down surfaces as an error the agent can escalate on, never as a
guessed temperature.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

MCP_DIR = (
    Path(__file__).resolve().parents[2]
    / "build-archive"
    / "deploy"
    / "aug24-mcp-server"
)
sys.path.insert(0, str(MCP_DIR))

import data as data_mod  # noqa: E402
import seed_data  # noqa: E402
from data import DataUnavailable, Repo, digits  # noqa: E402

NOW = datetime.now(timezone.utc)


# ── fakes ───────────────────────────────────────────────────────────────────


class FakeRepo(Repo):
    """Repo with both stores replaced by the seed rows, honouring the real SQL."""

    def __init__(self, *, sql_down=False, telemetry_down=False):
        super().__init__()
        self.sql_down = sql_down
        self.telemetry_down = telemetry_down
        self.tickets: list[dict] = []

    def _rows(self, sql: str, **p):
        if self.sql_down:
            raise DataUnavailable("Cloud SQL read failed: connection refused")
        q = " ".join(sql.split())

        if "FROM customers" in q:
            rows = []
            for c in seed_data.CUSTOMERS:
                if (
                    "account_number" in q
                    and "want" in p
                    and digits(c["account_number"]) != p["want"]
                ):
                    continue
                if (
                    "phone_e164" in q
                    and "tail" in p
                    and not digits(c["phone_e164"]).endswith(p["tail"])
                ):
                    continue
                if (
                    "LOWER(c.email)" in q
                    and "email" in p
                    and (c["email"] or "").lower() != p["email"].lower()
                ):
                    continue
                sub = c["subscription"]
                rows.append(
                    {
                        "customer_id": c["customer_id"],
                        "account_number": c["account_number"],
                        "first_name": c["first_name"],
                        "last_name": c["last_name"],
                        "email": c["email"],
                        "phone_e164": c["phone_e164"],
                        "tier": sub["tier"],
                        "sub_status": sub["status"],
                        "renews_on": sub["renews_on"],
                        "monthly_usd": sub["monthly_usd"],
                    }
                )
            return rows[:1] if "LIMIT 1" in q else rows

        if "FROM devices" in q:
            rows = [d for d in seed_data.DEVICES if d["customer_id"] == p.get("cid")]
            if "device_type = 'thermostat'" in q:
                rows = [d for d in rows if d["device_type"] == "thermostat"]
            if "like" in p:
                n = p["like"].strip("%")
                if n:
                    rows = [
                        d
                        for d in rows
                        if n in d["room"].lower()
                        or n in d["device_type"].lower()
                        or n in d["name"].lower()
                    ]
            rows = [
                {
                    k: d.get(k)
                    for k in ("device_id", "name", "device_type", "room", "sku")
                }
                for d in rows
            ]
            return rows[:1] if "LIMIT 1" in q else rows

        if "INSERT INTO support_tickets" in q:
            key = (p["cid"], p["oid"], p["summary"])
            for t in self.tickets:
                if (t["customer_id"], t["order_id"], t["summary"]) == key:
                    return [
                        {
                            "ticket_id": t["ticket_id"],
                            "status": "open",
                            "was_existing": True,
                        }
                    ]
            t = {
                "ticket_id": 4400 + len(self.tickets) + 1,
                "customer_id": p["cid"],
                "order_id": p["oid"],
                "summary": p["summary"],
            }
            self.tickets.append(t)
            return [
                {"ticket_id": t["ticket_id"], "status": "open", "was_existing": False}
            ]

        if "FROM orders" in q:
            rows = list(seed_data.ORDERS)
            if "order_id = :oid" in q:
                rows = [o for o in rows if o["order_id"] == p.get("oid")]
            elif "customer_id = :cid" in q:
                rows = [o for o in rows if o["customer_id"] == p.get("cid")]
            rows = sorted(rows, key=lambda o: o["placed_on"], reverse=True)
            return [
                {
                    k: o.get(k)
                    for k in (
                        "order_id",
                        "item",
                        "sku",
                        "status",
                        "detail",
                        "placed_on",
                        "delivers_on",
                    )
                }
                for o in rows
            ]

        raise AssertionError(f"unhandled query: {q[:90]}")

    def device_state(self, device_id):
        if self.telemetry_down:
            raise DataUnavailable(f"telemetry read failed for {device_id}")
        st = seed_data.TELEMETRY.get(device_id)
        return (
            {**st, "device_id": device_id, "reported_at": NOW - timedelta(seconds=20)}
            if st
            else {}
        )

    def products(self):
        return {sku: dict(p) for sku, p in seed_data.PRODUCTS.items()}

    def device_history(self, device_id, limit=10):
        if self.telemetry_down:
            raise DataUnavailable(f"history read failed for {device_id}")
        st = seed_data.TELEMETRY.get(device_id, {})
        return [{**st, "reported_at": NOW - timedelta(minutes=m)} for m in range(limit)]


@pytest.fixture
def repo():
    return FakeRepo()


SARAH = 1  # AH-4821


# ── identification: assignment requirement 1 ────────────────────────────────


@pytest.mark.parametrize(
    "spoken",
    [
        "AH-4821",
        "ah-4821",
        "AH 4821",
        "4821",
        "A H 4 8 2 1",
        "  ah4821  ",
    ],
)
def test_account_number_is_matched_however_it_is_spoken(repo, spoken):
    """People read account numbers back in every format there is."""
    c = repo.find_customer(account_number=spoken)
    assert c is not None and c["name"] == "Sarah Chen"


@pytest.mark.parametrize(
    "caller_id",
    [
        "+15125551188",
        "15125551188",
        "5125551188",
        "(512) 555-1188",
        "512 555 1188",
    ],
)
def test_phone_lookup_matches_on_the_last_ten_digits(repo, caller_id):
    """Inbound ANI has no formatting agreement."""
    c = repo.find_customer(phone=caller_id)
    assert c is not None and c["account_number"] == "AH-4821"


def test_unknown_caller_returns_none_rather_than_a_guess(repo):
    assert repo.find_customer(phone="+15550000000") is None
    assert repo.find_customer(account_number="AH-0000") is None
    assert repo.find_customer() is None


def test_lookup_returns_the_subscription(repo):
    sub = repo.find_customer(account_number="AH-4821")["subscription"]
    assert sub["tier"] == "Video Plus" and sub["status"] == "active"

    past_due = repo.find_customer(account_number="AH-6012")["subscription"]
    assert past_due["status"] == "past_due"


# ── the registry / telemetry split ──────────────────────────────────────────


def test_registry_lists_devices_without_any_state(repo):
    """The relational side knows what you own, not what it's doing."""
    devices = repo.devices_for(SARAH)
    assert len(devices) == 4
    for d in devices:
        assert set(d) == {"device_id", "name", "device_type", "room", "sku"}
        assert "reading" not in d and "active" not in d


def test_state_comes_from_the_document_store_keyed_by_device_id(repo):
    device = repo.find_device(SARAH, "living room")
    assert device["device_id"] == "AH4821-D1"

    state = repo.device_state(device["device_id"])
    assert state["reading"] == "71 degrees"
    assert state["temp_f"] == 71
    assert state["active"] is True


def test_telemetry_shape_differs_by_device_type(repo):
    """The reason state isn't a Postgres table: no shared column set."""
    thermostat = repo.device_state("AH4821-D1")
    lock = repo.device_state("AH4821-D4")
    camera = repo.device_state("AH4821-D2")

    assert "temp_f" in thermostat and "mode" in thermostat
    assert "bolt" in lock and "battery_pct" in lock
    assert "stream" in camera
    assert "temp_f" not in lock and "bolt" not in camera


@pytest.mark.parametrize(
    "said,expect",
    [
        ("thermostat", "AH4821-D1"),
        ("living room", "AH4821-D1"),
        ("front door camera", "AH4821-D2"),
        ("backyard", "AH4821-D3"),
        ("lock", "AH4821-D4"),
    ],
)
def test_devices_are_found_however_the_caller_names_them(repo, said, expect):
    assert repo.find_device(SARAH, said)["device_id"] == expect


def test_a_device_the_customer_does_not_own_is_not_found(repo):
    assert repo.find_device(SARAH, "pool sensor") is None


def test_thermostat_lookup_by_room_and_without_a_room(repo):
    assert repo.find_thermostat(SARAH, "living room")["device_id"] == "AH4821-D1"
    assert repo.find_thermostat(SARAH, "")["device_id"] == "AH4821-D1"
    assert repo.find_thermostat(SARAH, "attic") is None


def test_an_offline_device_reports_inactive_not_missing(repo):
    """Marcus's garage camera is offline — that's a reading, not an absence."""
    device = repo.find_device(2, "garage")
    state = repo.device_state(device["device_id"])
    assert state["active"] is False
    assert state["reading"] == "offline"


def test_a_device_that_never_reported_returns_empty(repo):
    assert repo.device_state("AH9999-D9") == {}


# ── orders ──────────────────────────────────────────────────────────────────


def test_most_recent_order_is_the_newest_one(repo):
    """ "What's the status of my most recent order?" — assignment requirement 2."""
    recent = repo.most_recent_order(SARAH)
    assert recent["order_id"] == "58121"  # placed 27 Aug, newer than 58120
    assert recent["status"] == "processing"


def test_orders_come_back_newest_first(repo):
    ids = [o["order_id"] for o in repo.orders_for(SARAH)]
    assert ids == ["58121", "58120"]


def test_order_lookup_tolerates_spoken_digits(repo):
    assert repo.get_order("5 8 1 2 0")["item"] == "Smart Thermostat V2"
    assert repo.get_order("58120")["status"] == "shipped"


def test_unknown_order_returns_none(repo):
    assert repo.get_order("99999") is None


def test_orders_do_not_leak_across_customers(repo):
    assert all(o["order_id"] != "58122" for o in repo.orders_for(SARAH))


# ── tickets: the retry-storm guard ──────────────────────────────────────────


def test_an_identical_open_ticket_is_reused_not_duplicated(repo):
    """A tool timeout makes the model retry. It filed four tickets once."""
    first = repo.open_ticket(SARAH, "58120", "Package appears stuck in transit.")
    again = repo.open_ticket(SARAH, "58120", "Package appears stuck in transit.")

    assert first["duplicate"] is False
    assert again["duplicate"] is True
    assert again["ticket_id"] == first["ticket_id"]
    assert len(repo.tickets) == 1


def test_a_genuinely_different_ticket_still_opens(repo):
    repo.open_ticket(SARAH, "58120", "Package appears stuck in transit.")
    other = repo.open_ticket(SARAH, "58121", "Wants to cancel this order.")
    assert other["duplicate"] is False
    assert len(repo.tickets) == 2


# ── failure surfaces honestly ───────────────────────────────────────────────


def test_sql_outage_raises_rather_than_returning_nothing(repo):
    """Silently returning None would look identical to 'no such customer'."""
    down = FakeRepo(sql_down=True)
    with pytest.raises(DataUnavailable):
        down.find_customer(account_number="AH-4821")


def test_telemetry_outage_raises_so_the_agent_never_guesses(repo):
    down = FakeRepo(telemetry_down=True)
    with pytest.raises(DataUnavailable):
        down.device_state("AH4821-D1")


def test_registry_still_works_when_telemetry_is_down():
    """Two stores, two blast radii — she can still say what you own."""
    down = FakeRepo(telemetry_down=True)
    assert len(down.devices_for(SARAH)) == 4


# ── seed integrity ──────────────────────────────────────────────────────────


def test_every_registered_device_has_telemetry():
    missing = [
        d["device_id"]
        for d in seed_data.DEVICES
        if d["device_id"] not in seed_data.TELEMETRY
    ]
    assert not missing, f"devices with no telemetry seeded: {missing}"


def test_every_telemetry_document_belongs_to_a_real_device():
    known = {d["device_id"] for d in seed_data.DEVICES}
    assert not set(seed_data.TELEMETRY) - known


def test_seed_matches_the_sql_schema():
    """seed_data.py and schema.sql must not drift apart."""
    ddl = (MCP_DIR / "schema.sql").read_text()
    for c in seed_data.CUSTOMERS:
        assert c["account_number"] in ddl
    for d in seed_data.DEVICES:
        assert d["device_id"] in ddl
    for o in seed_data.ORDERS:
        assert o["order_id"] in ddl


def test_schema_declares_the_types_the_seed_uses():
    ddl = (MCP_DIR / "schema.sql").read_text()
    for kind in {d["device_type"] for d in seed_data.DEVICES}:
        assert f"'{kind}'" in ddl
    for status in {o["status"] for o in seed_data.ORDERS}:
        assert f"'{status}'" in ddl


def test_module_defaults_point_at_the_real_stores():
    """No in-memory fallback: the services read from Cloud SQL and Firestore."""
    assert data_mod.TELEMETRY_COLLECTION == "device_telemetry"
    assert not hasattr(data_mod, "TELEMETRY"), (
        "seed data must not be a runtime fallback"
    )
    assert not hasattr(data_mod, "CUSTOMERS")


# ── product catalogue: pictures come from data, not name-matching ───────────


def test_every_device_and_order_has_a_sku_in_the_catalogue():
    skus = set(seed_data.PRODUCTS)
    assert all(d["sku"] in skus for d in seed_data.DEVICES)
    assert all(o["sku"] in skus for o in seed_data.ORDERS)


def test_with_product_attaches_image_price_category(repo):
    order = repo.most_recent_order(SARAH)
    out = repo.with_product(order)
    assert out["image_url"].endswith("aria-sensor.png") or out["image_url"].endswith(
        ".png"
    )
    assert out["category"] and out["price_usd"]


def test_unknown_sku_yields_no_image_rather_than_a_crash(repo):
    out = repo.with_product({"order_id": "x", "sku": "NOPE"})
    assert out["image_url"] is None
