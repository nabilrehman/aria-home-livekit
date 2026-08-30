-- Aria Home — relational system of record (Cloud SQL for PostgreSQL).
--
-- What lives here vs. Firestore:
--   Postgres  — things with relationships and transactions: who the customer is,
--               what they bought, what they own, what a human still owes them.
--               Joins matter, referential integrity matters, an order status
--               change is a transaction.
--   Firestore — device telemetry: high write volume, per-device-type shape
--               (a thermostat reports degrees, a lock reports bolt position),
--               append-only, and you almost always want just the latest reading.
--               Modelling that as relational rows would be a slow mistake.
--
-- The device REGISTRY is relational (a device belongs to a customer, was bought
-- on an order). The device STATE is not. That boundary is the whole design.

BEGIN;

DROP TABLE IF EXISTS support_tickets CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS devices CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- ── who they are ───────────────────────────────────────────────────────────
CREATE TABLE customers (
    customer_id    BIGSERIAL PRIMARY KEY,
    account_number TEXT        NOT NULL UNIQUE,          -- "AH-4821", spoken on calls
    first_name     TEXT        NOT NULL,
    last_name      TEXT        NOT NULL,
    email          TEXT        UNIQUE,
    phone_e164     TEXT        UNIQUE,                   -- "+15125551188", matched on ANI
    firebase_uid   TEXT        UNIQUE,                   -- set once they sign in on the web
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Inbound calls arrive as a caller ID with no formatting agreement, so the last
-- ten digits are what we actually match on.
CREATE INDEX customers_phone_tail_idx
    ON customers (RIGHT(regexp_replace(phone_e164, '\D', '', 'g'), 10));

-- ── what they pay for ──────────────────────────────────────────────────────
CREATE TABLE subscriptions (
    customer_id BIGINT      PRIMARY KEY REFERENCES customers ON DELETE CASCADE,
    tier        TEXT        NOT NULL,                    -- "Video Plus"
    status      TEXT        NOT NULL DEFAULT 'active'
                CHECK (status IN ('active','past_due','cancelled','trial')),
    renews_on   DATE,
    monthly_usd NUMERIC(6,2)
);

-- ── what they own ──────────────────────────────────────────────────────────
CREATE TABLE devices (
    device_id    TEXT   PRIMARY KEY,                     -- "AH4821-D1", joins to telemetry
    customer_id  BIGINT NOT NULL REFERENCES customers ON DELETE CASCADE,
    name         TEXT   NOT NULL,                        -- "Living Room Thermostat"
    device_type  TEXT   NOT NULL
                 CHECK (device_type IN ('thermostat','camera','lock','sensor')),
    room         TEXT   NOT NULL,
    sku          TEXT,                                   -- joins to the Firestore `products` catalogue
    installed_on DATE
);
CREATE INDEX devices_customer_idx ON devices (customer_id);
CREATE INDEX devices_lookup_idx   ON devices (customer_id, device_type);

-- ── what they bought ───────────────────────────────────────────────────────
CREATE TABLE orders (
    order_id    TEXT   PRIMARY KEY,                      -- "58120", read out digit by digit
    customer_id BIGINT NOT NULL REFERENCES customers ON DELETE CASCADE,
    item        TEXT   NOT NULL,
    sku         TEXT,                                    -- Firestore `products` key: image, price, category
    status      TEXT   NOT NULL
                CHECK (status IN ('processing','shipped','delivered','cancelled','returned')),
    detail      TEXT,                                    -- one spoken sentence
    placed_on   DATE   NOT NULL,
    delivers_on DATE
);
CREATE INDEX orders_customer_recent_idx ON orders (customer_id, placed_on DESC);

-- ── what a human still owes them ───────────────────────────────────────────
CREATE TABLE support_tickets (
    ticket_id   BIGSERIAL   PRIMARY KEY,
    customer_id BIGINT      REFERENCES customers ON DELETE SET NULL,
    order_id    TEXT        REFERENCES orders    ON DELETE SET NULL,
    summary     TEXT        NOT NULL,
    status      TEXT        NOT NULL DEFAULT 'open'
                CHECK (status IN ('open','in_progress','resolved')),
    opened_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX tickets_open_idx ON support_tickets (status, opened_at DESC);

-- The agent retries on a tool timeout. Without this, one slow carrier lookup
-- becomes four identical tickets for the same customer — which is exactly what
-- happened in testing.
CREATE UNIQUE INDEX tickets_no_duplicates_idx
    ON support_tickets (customer_id, order_id, summary)
    WHERE status = 'open';

-- ═══════════════════════════ seed ═══════════════════════════

INSERT INTO customers (account_number, first_name, last_name, email, phone_e164) VALUES
    ('AH-4821','Sarah','Chen',   'sarah@example.com',  '+15125551188'),
    ('AH-3390','Marcus','Webb',  'marcus@example.com', '+14695552210'),
    ('AH-5567','Priya','Raman',  'priya@example.com',  '+17375553301'),
    ('AH-6012','Daniel','Okafor','daniel@example.com', '+15125554412'),
    ('AH-7104','Nabil','Rehman', 'nabilrehman8@gmail.com', '+17372059240'),
    ('AH-8230','Anam','Nabil',   'anam.nabil1@gmail.com',  '+15125559877');

INSERT INTO subscriptions (customer_id, tier, status, renews_on, monthly_usd)
SELECT customer_id, t.tier, t.status, t.renews_on, t.usd
FROM customers c
JOIN (VALUES
    ('AH-4821','Video Plus',  'active',   DATE '2026-09-14', 12.00),
    ('AH-3390','Video Basic', 'active',   DATE '2026-09-02',  6.00),
    ('AH-5567','Video Plus',  'active',   DATE '2026-10-01', 12.00),
    ('AH-6012','Video Basic', 'past_due', DATE '2026-08-21',  6.00),
    ('AH-7104','Video Plus',  'active',   DATE '2026-09-22', 12.00),
    ('AH-8230','Video Basic', 'active',   DATE '2026-09-09',  6.00)
) AS t(acct, tier, status, renews_on, usd) ON t.acct = c.account_number;

INSERT INTO devices (device_id, customer_id, name, device_type, room, installed_on)
SELECT d.device_id, c.customer_id, d.name, d.device_type, d.room, d.installed_on
FROM customers c
JOIN (VALUES
    ('AH4821-D1','AH-4821','Living Room Thermostat','thermostat','living room', DATE '2025-11-03'),
    ('AH4821-D2','AH-4821','Front Door Camera',     'camera',    'front door',  DATE '2025-11-03'),
    ('AH4821-D3','AH-4821','Backyard Camera',       'camera',    'backyard',    DATE '2026-02-19'),
    ('AH4821-D4','AH-4821','Front Door Lock',       'lock',      'front door',  DATE '2026-02-19'),
    ('AH3390-D1','AH-3390','Hallway Thermostat',    'thermostat','hallway',     DATE '2025-06-12'),
    ('AH3390-D2','AH-3390','Garage Camera',         'camera',    'garage',      DATE '2025-06-12'),
    ('AH5567-D1','AH-5567','Nursery Sensor',        'sensor',    'nursery',     DATE '2026-01-08'),
    ('AH5567-D2','AH-5567','Kitchen Thermostat',    'thermostat','kitchen',     DATE '2026-01-08'),
    ('AH5567-D3','AH-5567','Side Door Lock',        'lock',      'side door',   DATE '2026-03-30'),
    ('AH6012-D1','AH-6012','Front Door Camera',     'camera',    'front door',  DATE '2025-09-21'),
    ('AH6012-D2','AH-6012','Study Thermostat',      'thermostat','study',       DATE '2025-09-21'),
    ('AH7104-D1','AH-7104','Aria Thermostat',     'thermostat','living room', DATE '2025-10-05'),
    ('AH7104-D2','AH-7104','Aria Doorbell Cam',    'camera',    'front door',  DATE '2025-10-05'),
    ('AH7104-D3','AH-7104','Aria Floodlight Cam',  'camera',    'driveway',    DATE '2025-10-05'),
    ('AH7104-D4','AH-7104','Aria Smart Lock',      'lock',      'back door',   DATE '2026-04-12'),
    ('AH7104-D5','AH-7104','Aria Motion Sensor',   'sensor',    'hallway',     DATE '2026-04-12'),
    ('AH8230-D1','AH-8230','Aria Doorbell Cam',    'camera',    'front door',  DATE '2026-05-02'),
    ('AH8230-D2','AH-8230','Aria Thermostat',      'thermostat','bedroom',     DATE '2026-05-02'),
    ('AH8230-D3','AH-8230','Aria Smart Lock',      'lock',      'front door',  DATE '2026-05-02')
) AS d(device_id, acct, name, device_type, room, installed_on) ON d.acct = c.account_number;

INSERT INTO orders (order_id, customer_id, item, status, detail, placed_on, delivers_on)
SELECT o.order_id, c.customer_id, o.item, o.status, o.detail, o.placed_on, o.delivers_on
FROM customers c
JOIN (VALUES
    ('58120','AH-4821','Smart Thermostat V2',   'shipped',
     'Left the Austin facility and is moving normally.', DATE '2026-08-24', DATE '2026-08-30'),
    ('58121','AH-4821','Indoor Camera two pack','processing',
     'Still in the warehouse, nothing has shipped yet.', DATE '2026-08-27', DATE '2026-09-03'),
    ('58122','AH-3390','Door Lock Pro',         'delivered',
     'Left with a neighbour at number forty two.',       DATE '2026-08-11', DATE '2026-08-15'),
    ('58123','AH-5567','Nursery Sensor two pack','shipped',
     'Out for delivery with the carrier today.',         DATE '2026-08-26', DATE '2026-08-29'),
    ('58124','AH-6012','Outdoor Camera',        'processing',
     'On hold until the subscription is brought up to date.', DATE '2026-08-25', NULL),
    ('58130','AH-7104','Video Doorbell Pro',    'shipped',
     'With the carrier, arriving Sunday.',               DATE '2026-08-26', DATE '2026-08-31'),
    ('58131','AH-7104','Smart Sensor four pack','processing',
     'Picked in the warehouse, not yet shipped.',        DATE '2026-08-28', DATE '2026-09-04'),
    ('58129','AH-7104','Outdoor Camera Mount',  'delivered',
     'Signed for at the front door.',                    DATE '2026-08-14', DATE '2026-08-20'),
    ('58140','AH-8230','Aria Floodlight Cam',  'shipped',
     'Left the Dallas facility this morning.',           DATE '2026-08-27', DATE '2026-09-01'),
    ('58139','AH-8230','Aria Thermostat',      'delivered',
     'Delivered to the front porch.',                    DATE '2026-08-05', DATE '2026-08-09')
) AS o(order_id, acct, item, status, detail, placed_on, delivers_on) ON o.acct = c.account_number;

COMMIT;
