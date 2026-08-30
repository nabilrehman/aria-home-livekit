"""Seed rows for Aria Home. Loaded into Cloud SQL and Firestore by seed.py.

This is not a runtime fallback — the services read from the real stores.
"""

from datetime import date

IMAGE_BASE = "https://aug24-web-549403515075.us-central1.run.app/assets/products/"

# The product catalogue — lives in Firestore (`products`), keyed by SKU. Devices and
# orders in Cloud SQL carry a sku, so any screen or agent answer can pull the image,
# price and category without matching on names.
PRODUCTS = {
    "ARIA-THERM": {
        "name": "Aria Thermostat",
        "category": "thermostat",
        "price_usd": 129,
        "image_url": IMAGE_BASE + "aria-thermostat.png",
    },
    "ARIA-DBELL": {
        "name": "Aria Doorbell Cam",
        "category": "camera",
        "price_usd": 179,
        "image_url": IMAGE_BASE + "aria-doorbell.png",
    },
    "ARIA-FLOOD": {
        "name": "Aria Floodlight Cam",
        "category": "camera",
        "price_usd": 229,
        "image_url": IMAGE_BASE + "aria-floodlight.png",
    },
    "ARIA-LOCK": {
        "name": "Aria Smart Lock",
        "category": "lock",
        "price_usd": 199,
        "image_url": IMAGE_BASE + "aria-lock.png",
    },
    "ARIA-SENSE": {
        "name": "Aria Motion Sensor",
        "category": "sensor",
        "price_usd": 39,
        "image_url": IMAGE_BASE + "aria-sensor.png",
    },
}

CUSTOMERS = [
    {
        "customer_id": 1,
        "account_number": "AH-4821",
        "first_name": "Sarah",
        "last_name": "Chen",
        "email": "sarah@example.com",
        "phone_e164": "+15125551188",
        "subscription": {
            "tier": "Video Plus",
            "status": "active",
            "renews_on": date(2026, 9, 14),
            "monthly_usd": 12.00,
        },
    },
    {
        "customer_id": 2,
        "account_number": "AH-3390",
        "first_name": "Marcus",
        "last_name": "Webb",
        "email": "marcus@example.com",
        "phone_e164": "+14695552210",
        "subscription": {
            "tier": "Video Basic",
            "status": "active",
            "renews_on": date(2026, 9, 2),
            "monthly_usd": 6.00,
        },
    },
    {
        "customer_id": 3,
        "account_number": "AH-5567",
        "first_name": "Priya",
        "last_name": "Raman",
        "email": "priya@example.com",
        "phone_e164": "+17375553301",
        "subscription": {
            "tier": "Video Plus",
            "status": "active",
            "renews_on": date(2026, 10, 1),
            "monthly_usd": 12.00,
        },
    },
    {
        "customer_id": 4,
        "account_number": "AH-6012",
        "first_name": "Daniel",
        "last_name": "Okafor",
        "email": "daniel@example.com",
        "phone_e164": "+15125554412",
        "subscription": {
            "tier": "Video Basic",
            "status": "past_due",
            "renews_on": date(2026, 8, 21),
            "monthly_usd": 6.00,
        },
    },
    # The signed-in demo account. Deliberately a different home from Sarah's, so the
    # panel sees two unrelated customers come out of the same system.
    {
        "customer_id": 5,
        "account_number": "AH-7104",
        "first_name": "Nabil",
        "last_name": "Rehman",
        "email": "nabilrehman8@gmail.com",
        "phone_e164": "+17372059240",
        "subscription": {
            "tier": "Video Plus",
            "status": "active",
            "renews_on": date(2026, 9, 22),
            "monthly_usd": 12.00,
        },
    },
]

# The registry: what they own. No state here — that's the point.
DEVICES = [
    {
        "device_id": "AH4821-D1",
        "customer_id": 1,
        "name": "Living Room Thermostat",
        "device_type": "thermostat",
        "room": "living room",
        "sku": "ARIA-THERM",
    },
    {
        "device_id": "AH4821-D2",
        "customer_id": 1,
        "name": "Front Door Camera",
        "device_type": "camera",
        "room": "front door",
        "sku": "ARIA-FLOOD",
    },
    {
        "device_id": "AH4821-D3",
        "customer_id": 1,
        "name": "Backyard Camera",
        "device_type": "camera",
        "room": "backyard",
        "sku": "ARIA-FLOOD",
    },
    {
        "device_id": "AH4821-D4",
        "customer_id": 1,
        "name": "Front Door Lock",
        "device_type": "lock",
        "room": "front door",
        "sku": "ARIA-LOCK",
    },
    {
        "device_id": "AH3390-D1",
        "customer_id": 2,
        "name": "Hallway Thermostat",
        "device_type": "thermostat",
        "room": "hallway",
        "sku": "ARIA-THERM",
    },
    {
        "device_id": "AH3390-D2",
        "customer_id": 2,
        "name": "Garage Camera",
        "device_type": "camera",
        "room": "garage",
        "sku": "ARIA-FLOOD",
    },
    {
        "device_id": "AH5567-D1",
        "customer_id": 3,
        "name": "Nursery Sensor",
        "device_type": "sensor",
        "room": "nursery",
        "sku": "ARIA-SENSE",
    },
    {
        "device_id": "AH5567-D2",
        "customer_id": 3,
        "name": "Kitchen Thermostat",
        "device_type": "thermostat",
        "room": "kitchen",
        "sku": "ARIA-THERM",
    },
    {
        "device_id": "AH5567-D3",
        "customer_id": 3,
        "name": "Side Door Lock",
        "device_type": "lock",
        "room": "side door",
        "sku": "ARIA-LOCK",
    },
    {
        "device_id": "AH6012-D1",
        "customer_id": 4,
        "name": "Front Door Camera",
        "device_type": "camera",
        "room": "front door",
        "sku": "ARIA-FLOOD",
    },
    {
        "device_id": "AH6012-D2",
        "customer_id": 4,
        "name": "Study Thermostat",
        "device_type": "thermostat",
        "room": "study",
        "sku": "ARIA-THERM",
    },
    {
        "device_id": "AH7104-D1",
        "customer_id": 5,
        "name": "Aria Thermostat",
        "device_type": "thermostat",
        "room": "living room",
        "sku": "ARIA-THERM",
    },
    {
        "device_id": "AH7104-D2",
        "customer_id": 5,
        "name": "Aria Doorbell Cam",
        "device_type": "camera",
        "room": "front door",
        "sku": "ARIA-DBELL",
    },
    {
        "device_id": "AH7104-D3",
        "customer_id": 5,
        "name": "Aria Floodlight Cam",
        "device_type": "camera",
        "room": "driveway",
        "sku": "ARIA-FLOOD",
    },
    {
        "device_id": "AH7104-D4",
        "customer_id": 5,
        "name": "Aria Smart Lock",
        "device_type": "lock",
        "room": "back door",
        "sku": "ARIA-LOCK",
    },
    {
        "device_id": "AH7104-D5",
        "customer_id": 5,
        "name": "Aria Motion Sensor",
        "device_type": "sensor",
        "room": "hallway",
        "sku": "ARIA-SENSE",
    },
]

ORDERS = [
    {
        "order_id": "58120",
        "customer_id": 1,
        "item": "Smart Thermostat V2",
        "sku": "ARIA-THERM",
        "status": "shipped",
        "detail": "Left the Austin facility and is moving normally.",
        "placed_on": date(2026, 8, 24),
        "delivers_on": date(2026, 8, 30),
    },
    {
        "order_id": "58121",
        "customer_id": 1,
        "item": "Indoor Camera two pack",
        "sku": "ARIA-FLOOD",
        "status": "processing",
        "detail": "Still in the warehouse, nothing has shipped yet.",
        "placed_on": date(2026, 8, 27),
        "delivers_on": date(2026, 9, 3),
    },
    {
        "order_id": "58122",
        "customer_id": 2,
        "item": "Door Lock Pro",
        "sku": "ARIA-LOCK",
        "status": "delivered",
        "detail": "Left with a neighbour at number forty two.",
        "placed_on": date(2026, 8, 11),
        "delivers_on": date(2026, 8, 15),
    },
    {
        "order_id": "58123",
        "customer_id": 3,
        "item": "Nursery Sensor two pack",
        "sku": "ARIA-SENSE",
        "status": "shipped",
        "detail": "Out for delivery with the carrier today.",
        "placed_on": date(2026, 8, 26),
        "delivers_on": date(2026, 8, 29),
    },
    {
        "order_id": "58124",
        "customer_id": 4,
        "item": "Outdoor Camera",
        "sku": "ARIA-FLOOD",
        "status": "processing",
        "detail": "On hold until the subscription is brought up to date.",
        "placed_on": date(2026, 8, 25),
        "delivers_on": None,
    },
    # Nabil's history — three orders so the order page has something to show.
    {
        "order_id": "58130",
        "customer_id": 5,
        "item": "Video Doorbell Pro",
        "sku": "ARIA-DBELL",
        "status": "shipped",
        "detail": "With the carrier, arriving Sunday.",
        "placed_on": date(2026, 8, 26),
        "delivers_on": date(2026, 8, 31),
    },
    {
        "order_id": "58131",
        "customer_id": 5,
        "item": "Smart Sensor four pack",
        "sku": "ARIA-SENSE",
        "status": "processing",
        "detail": "Picked in the warehouse, not yet shipped.",
        "placed_on": date(2026, 8, 28),
        "delivers_on": date(2026, 9, 4),
    },
    {
        "order_id": "58129",
        "customer_id": 5,
        "item": "Outdoor Camera Mount",
        "sku": "ARIA-FLOOD",
        "status": "delivered",
        "detail": "Signed for at the front door.",
        "placed_on": date(2026, 8, 14),
        "delivers_on": date(2026, 8, 20),
    },
]

# The document side: what each device is reporting. Note the shapes differ by
# type — that heterogeneity is the reason this isn't a Postgres table.
TELEMETRY = {
    "AH4821-D1": {
        "active": True,
        "reading": "71 degrees",
        "temp_f": 71,
        "mode": "heat",
    },
    "AH4821-D2": {"active": True, "reading": "recording", "stream": "1080p"},
    "AH4821-D3": {"active": True, "reading": "recording", "stream": "1080p"},
    "AH4821-D4": {
        "active": True,
        "reading": "locked",
        "bolt": "extended",
        "battery_pct": 82,
    },
    "AH3390-D1": {
        "active": True,
        "reading": "68 degrees",
        "temp_f": 68,
        "mode": "cool",
    },
    "AH3390-D2": {"active": False, "reading": "offline", "last_seen": "2026-08-27"},
    "AH5567-D1": {"active": True, "reading": "quiet", "sound_db": 31},
    "AH5567-D2": {
        "active": True,
        "reading": "70 degrees",
        "temp_f": 70,
        "mode": "auto",
    },
    "AH5567-D3": {
        "active": False,
        "reading": "unlocked",
        "bolt": "retracted",
        "battery_pct": 41,
    },
    "AH6012-D1": {"active": True, "reading": "recording", "stream": "720p"},
    "AH6012-D2": {
        "active": True,
        "reading": "72 degrees",
        "temp_f": 72,
        "mode": "heat",
    },
    "AH7104-D1": {
        "active": True,
        "reading": "69 degrees",
        "temp_f": 69,
        "mode": "cool",
    },
    "AH7104-D2": {"active": True, "reading": "recording", "stream": "1080p"},
    "AH7104-D3": {"active": True, "reading": "recording", "stream": "1080p"},
    "AH7104-D4": {
        "active": True,
        "reading": "locked",
        "bolt": "extended",
        "battery_pct": 91,
    },
    "AH7104-D5": {"active": False, "reading": "needs battery", "battery_pct": 6},
    "AH8230-D1": {"active": True,  "reading": "recording",  "stream": "1080p"},
    "AH8230-D2": {"active": True,  "reading": "73 degrees", "temp_f": 73, "mode": "cool"},
    "AH8230-D3": {"active": True,  "reading": "unlocked",   "bolt": "retracted",
                  "battery_pct": 64},
}


# ── Anam Nabil — second real Google account, a different home ────────────────
CUSTOMERS.append(
    {
        "customer_id": 6,
        "account_number": "AH-8230",
        "first_name": "Anam",
        "last_name": "Nabil",
        "email": "anam.nabil1@gmail.com",
        "phone_e164": "+15125559877",
        "subscription": {
            "tier": "Video Basic",
            "status": "active",
            "renews_on": date(2026, 9, 9),
            "monthly_usd": 6.00,
        },
    }
)
DEVICES.extend(
    [
        {"device_id": "AH8230-D1", "customer_id": 6, "name": "Aria Doorbell Cam",
         "device_type": "camera", "room": "front door", "sku": "ARIA-DBELL"},
        {"device_id": "AH8230-D2", "customer_id": 6, "name": "Aria Thermostat",
         "device_type": "thermostat", "room": "bedroom", "sku": "ARIA-THERM"},
        {"device_id": "AH8230-D3", "customer_id": 6, "name": "Aria Smart Lock",
         "device_type": "lock", "room": "front door", "sku": "ARIA-LOCK"},
    ]
)
ORDERS.extend(
    [
        {"order_id": "58140", "customer_id": 6, "item": "Aria Floodlight Cam", "sku": "ARIA-FLOOD",
         "status": "shipped", "detail": "Left the Dallas facility this morning.",
         "placed_on": date(2026, 8, 27), "delivers_on": date(2026, 9, 1)},
        {"order_id": "58139", "customer_id": 6, "item": "Aria Thermostat", "sku": "ARIA-THERM",
         "status": "delivered", "detail": "Delivered to the front porch.",
         "placed_on": date(2026, 8, 5), "delivers_on": date(2026, 8, 9)},
    ]
)
