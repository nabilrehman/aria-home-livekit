"""Tests for the fake AnyCompany backend.

These cover the things that actually break on a voice channel: order numbers
arriving as loose digits, partial numbers, numbers that don't exist, and dates
that have to be spoken rather than displayed.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import store


class TestNormalizeOrderId:
    @pytest.mark.parametrize(
        "spoken,expected",
        [
            ("44721", "44721"),
            ("4 4 7 2 1", "44721"),  # STT often spaces out dictated digits
            ("4-4-7-2-1", "44721"),
            ("order 44,721", "44721"),
            ("it's 44721.", "44721"),
            ("", ""),
        ],
    )
    def test_strips_everything_but_digits(self, spoken, expected):
        assert store.normalize_order_id(spoken) == expected


class TestGetOrder:
    def test_finds_order_from_clean_number(self):
        order = store.get_order("44721")
        assert order is not None
        assert order.status == "shipped"
        assert order.item == "Smart Thermostat V2"

    def test_finds_order_from_dictated_digits(self):
        assert store.get_order("4 4 7 2 1").order_id == "44721"

    def test_unknown_order_returns_none(self):
        assert store.get_order("99999") is None

    def test_partial_number_returns_none(self):
        """A half-heard number must not accidentally match a real order."""
        assert store.get_order("447") is None

    @pytest.mark.parametrize(
        "order_id,status",
        [
            ("44721", "shipped"),
            ("44722", "delayed"),
            ("44723", "delivered"),
            ("44724", "processing"),
            ("44725", "cancelled"),
        ],
    )
    def test_every_status_is_reachable(self, order_id, status):
        assert store.get_order(order_id).status == status


class TestSpokenDate:
    @pytest.mark.parametrize(
        "iso,expected",
        [
            ("2026-08-01", "August first"),
            ("2026-08-11", "August eleventh"),
            ("2026-08-20", "August twentieth"),
            ("2026-08-21", "August twenty first"),
            ("2026-08-25", "August twenty fifth"),
            ("2026-08-30", "August thirtieth"),
            ("2026-08-31", "August thirty first"),
        ],
    )
    def test_reads_as_words(self, iso, expected):
        assert store.spoken_date(iso) == expected

    def test_missing_date_is_spoken_not_blank(self):
        assert store.spoken_date(None) == "no date yet"

    def test_never_emits_bare_digits_with_suffix(self):
        """'25th' is fine on screen and bad in a TTS voice."""
        for day in range(1, 32):
            spoken = store.spoken_date(f"2026-08-{day:02d}")
            assert "th" not in spoken.split()[-1] or spoken.split()[-1].isalpha()
            assert not any(ch.isdigit() for ch in spoken)


class TestCustomers:
    def test_finds_customer_by_phone_ignoring_formatting(self):
        assert store.find_customer_by_phone("(737) 205-9240").name == "Nabil Rehman"

    def test_unknown_phone_returns_none(self):
        assert store.find_customer_by_phone("+15550000000") is None

    def test_orders_listed_newest_first(self):
        orders = store.orders_for_customer("C-1001")
        assert len(orders) == 6  # 3 legacy + 3 mirrored from Cloud SQL
        assert orders == sorted(orders, key=lambda o: o.placed_on, reverse=True)


class TestTickets:
    def test_ticket_gets_id_and_is_open(self):
        ticket = store.create_ticket("44722", "Escalate delayed camera")
        assert ticket.ticket_id.startswith("T-")
        assert ticket.status == "open"
        assert store.TICKETS[ticket.ticket_id] is ticket

    def test_ticket_ids_are_unique(self):
        a = store.create_ticket(None, "first")
        b = store.create_ticket(None, "second")
        assert a.ticket_id != b.ticket_id
