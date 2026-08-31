"""
store.py — a fake AnyCompany Smart Home backend.

Everything here is invented and lives in memory on your laptop. It stands in for
the "Customer data" box on the architecture diagram: customers, their devices,
their orders, and the tickets you file against them.

The point is not the data. It's that the agent has to *call* something to know
anything — so you can watch a tool call happen, watch it succeed, and watch what
the agent does when it fails.

Order numbers are deliberately five digits so they're easy to read aloud over a
voice channel, and 44721 is the one used throughout the study notes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Order:
    order_id: str
    customer_id: str
    item: str
    status: str
    placed_on: str
    detail: str
    tracking: str | None = None
    delivers_on: str | None = None


@dataclass
class Customer:
    customer_id: str
    name: str
    phone: str
    email: str
    devices: list[str] = field(default_factory=list)


@dataclass
class Ticket:
    ticket_id: str
    order_id: str | None
    summary: str
    status: str = "open"


# ---------------------------------------------------------------- customers

CUSTOMERS: dict[str, Customer] = {
    "C-2001": Customer(
        customer_id="C-2001",
        name="John Doe",
        phone="+15125551188",
        email="johndoe@gmail.com",
        devices=["Living Room Thermostat", "Front Door Camera", "Front Door Lock"],
    ),
    "C-1001": Customer(
        customer_id="C-1001",
        name="Nabil Rehman",
        phone="+17372059240",
        email="nabilrehman8@gmail.com",
        devices=[
            "Aria Thermostat",
            "Aria Doorbell Cam",
            "Aria Floodlight Cam",
            "Aria Smart Lock",
            "Aria Motion Sensor",
        ],
    ),
    "C-1002": Customer(
        customer_id="C-1002",
        name="Dana Whitfield",
        phone="+14845550193",
        email="dana@example.com",
        devices=["Smart Lock Mini"],
    ),
}

# ------------------------------------------------------------------- orders
# A spread of statuses on purpose, so you can hear the agent handle each one.

ORDERS: dict[str, Order] = {
    "58120": Order(
        order_id="58120",
        customer_id="C-2001",
        item="Smart Thermostat V2",
        status="shipped",
        placed_on="2026-08-22",
        detail="Left the Austin facility and is moving normally.",
        tracking="1Z999AA10158120007",
        delivers_on="2026-08-30",
    ),
    "58121": Order(
        order_id="58121",
        customer_id="C-2001",
        item="Indoor Camera two pack",
        status="processing",
        placed_on="2026-08-26",
        detail="Still in the warehouse. Nothing has shipped yet.",
        tracking=None,
        delivers_on="2026-09-03",
    ),
    # Nabil's orders — mirror Cloud SQL so the legacy refund/tracking tools agree.
    "58131": Order(
        order_id="58131",
        customer_id="C-1001",
        item="Smart Sensor four pack",
        status="processing",
        placed_on="2026-08-28",
        detail="Picked in the warehouse, not yet shipped.",
        tracking=None,
        delivers_on="2026-09-04",
    ),
    "58130": Order(
        order_id="58130",
        customer_id="C-1001",
        item="Video Doorbell Pro",
        status="shipped",
        placed_on="2026-08-26",
        detail="With the carrier, arriving Sunday.",
        tracking="1Z58130",
        delivers_on="2026-08-31",
    ),
    "58129": Order(
        order_id="58129",
        customer_id="C-1001",
        item="Outdoor Camera Mount",
        status="delivered",
        placed_on="2026-08-14",
        detail="Signed for at the front door.",
        tracking="1Z58129",
        delivers_on="2026-08-20",
    ),
    "44721": Order(
        order_id="44721",
        customer_id="C-1001",
        item="Smart Thermostat V2",
        status="shipped",
        placed_on="2026-08-14",
        detail="Left the Dallas facility and is moving normally.",
        tracking="1Z999AA10123456784",
        delivers_on="2026-08-25",
    ),
    "44722": Order(
        order_id="44722",
        customer_id="C-1001",
        item="Doorbell Camera Pro",
        status="delayed",
        placed_on="2026-08-10",
        detail=(
            "Held at the carrier's Memphis hub because of weather. "
            "No new delivery date has been committed yet."
        ),
        tracking="1Z999AA10123459981",
        delivers_on=None,
    ),
    "44723": Order(
        order_id="44723",
        customer_id="C-1002",
        item="Smart Lock Mini",
        status="delivered",
        placed_on="2026-08-02",
        detail="Left at the front porch and signed for by D. WHITFIELD.",
        tracking="1Z999AA10123441122",
        delivers_on="2026-08-07",
    ),
    "44724": Order(
        order_id="44724",
        customer_id="C-1001",
        item="Smart Thermostat V2 wall plate",
        status="processing",
        placed_on="2026-08-21",
        detail="Still in the warehouse. Nothing has shipped yet.",
        tracking=None,
        delivers_on="2026-08-29",
    ),
    "44725": Order(
        order_id="44725",
        customer_id="C-1002",
        item="Doorbell Camera Pro",
        status="cancelled",
        placed_on="2026-07-30",
        detail="Cancelled at the customer's request. Refund issued to the original card.",
        tracking=None,
        delivers_on=None,
    ),
}

TICKETS: dict[str, Ticket] = {}
_ticket_seq = 5000


# ------------------------------------------------------------------ lookups


def normalize_order_id(raw: str) -> str:
    """
    Spoken order numbers arrive messy.

    Speech-to-text will hand you "4 4 7 2 1", "44,721", "order 44721" or
    "four four seven two one" already digitised. Strip everything that isn't a
    digit and work with what's left.
    """
    return "".join(ch for ch in str(raw) if ch.isdigit())


def get_order(raw_order_id: str) -> Order | None:
    return ORDERS.get(normalize_order_id(raw_order_id))


def get_customer(customer_id: str) -> Customer | None:
    return CUSTOMERS.get(customer_id)


def find_customer_by_phone(phone: str) -> Customer | None:
    digits = "".join(ch for ch in phone if ch.isdigit())[-10:]
    for customer in CUSTOMERS.values():
        if customer.phone.endswith(digits):
            return customer
    return None


def orders_for_customer(customer_id: str) -> list[Order]:
    found = [o for o in ORDERS.values() if o.customer_id == customer_id]
    return sorted(found, key=lambda o: o.placed_on, reverse=True)


def create_ticket(order_id: str | None, summary: str) -> Ticket:
    global _ticket_seq
    _ticket_seq += 1
    ticket = Ticket(ticket_id=f"T-{_ticket_seq}", order_id=order_id, summary=summary)
    TICKETS[ticket.ticket_id] = ticket
    return ticket


def spoken_date(iso: str | None) -> str:
    """Turn 2026-08-25 into 'August twenty fifth' — TTS reads that far better."""
    if not iso:
        return "no date yet"
    d = date.fromisoformat(iso)
    return f"{d.strftime('%B')} {_ordinal_words(d.day)}"


_ONES = [
    "",
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
    "ninth",
    "tenth",
    "eleventh",
    "twelfth",
    "thirteenth",
    "fourteenth",
    "fifteenth",
    "sixteenth",
    "seventeenth",
    "eighteenth",
    "nineteenth",
    "twentieth",
]
_TENS = {20: "twenty", 30: "thirty"}


def _ordinal_words(day: int) -> str:
    """1 -> 'first', 25 -> 'twenty fifth'. TTS reads words far better than '25th'."""
    if day <= 20:
        return _ONES[day]
    tens, units = divmod(day, 10)
    if units == 0:
        return "thirtieth" if day == 30 else _TENS[day]
    return f"{_TENS[tens * 10]} {_ONES[units]}"


# ------------------------------------------------------------------ refunds
# Simulated backend latency. Real refund flows really are this slow: an order
# service, a payment processor, and a ledger write, none of them local.

REFUND_STEP_SECONDS = {
    "eligibility": 1.6,  # order service
    "processor": 3.2,  # payment gateway — the slow one
    "ledger": 1.4,  # write the refund record
}

REFUNDS: dict[str, str] = {}


def refund_eligibility(order: Order) -> tuple[bool, str]:
    """Can this order be refunded? Returns (ok, reason_to_speak)."""
    if order.status == "cancelled":
        return False, "That order was already cancelled and refunded."
    if order.status == "processing":
        return False, (
            "That order has not shipped yet, so it can be cancelled outright "
            "rather than refunded — which is faster for the customer."
        )
    if order.status in ("shipped", "delayed", "delivered"):
        return True, ""
    return False, "That order is not in a refundable state."


def record_refund(order_id: str) -> str:
    """Mark the refund and return a reference number."""
    reference = f"RF-{7000 + len(REFUNDS) + 1}"
    REFUNDS[order_id] = reference
    return reference
