"""Aria Home data layer — one seam, two stores.

    RELATIONAL (Cloud SQL / Postgres)   the system of record
        customers, subscriptions, orders, the device REGISTRY, tickets.
        Relationships and transactions: "which devices does this customer own" is
        a join, and an order status change is an atomic write. See schema.sql.

    DOCUMENT (Firestore)                device TELEMETRY
        What each device is reporting right now. High write volume, and the shape
        differs per device type — a thermostat reports degrees and a mode, a lock
        reports a bolt position and a battery level, a camera reports a stream.
        You almost always want only the newest reading. Columns would fight that.

The registry is relational, the state is not, and `device_id` is the join key
across the boundary. "Is my thermostat active?" is one Postgres read to find the
device and one Firestore read to see what it's saying.

Both stores are required. Run seed.py once to populate them.
"""

from __future__ import annotations

import logging
import os
import re

log = logging.getLogger("aria.data")

CLOUD_SQL_INSTANCE = os.environ.get("CLOUD_SQL_INSTANCE", "")
# The view-only role for per-customer reads (parameterized secure views).
DB_APP_USER = os.environ.get("DB_APP_USER", "aria_app")
DB_APP_PASS = os.environ.get("DB_APP_PASS", "")
FIRESTORE_DB = os.environ.get("FIRESTORE_DB", "aug24")
TELEMETRY_COLLECTION = "device_telemetry"
PRODUCTS_COLLECTION = "products"
CALLS_COLLECTION = "call_history"
# Vertex AI Agent Engine Memory Bank — distilled, consolidated facts per account.
MEMORY_BANK = os.environ.get("MEMORY_BANK", "")


def digits(s) -> str:
    return re.sub(r"\D", "", str(s or ""))


class DataUnavailable(RuntimeError):
    """A backing store could not be reached. Surfaced so the agent escalates
    honestly instead of inventing a temperature."""


class Repo:
    """Every tool reads through this. Connections are built once and reused."""

    def __init__(self) -> None:
        self._pool = None
        self._fs = None

    # ── connections ─────────────────────────────────────────────────────────

    def _engine(self):
        if self._pool is None:
            import sqlalchemy
            from google.cloud.sql.connector import Connector

            if not CLOUD_SQL_INSTANCE:
                raise DataUnavailable("CLOUD_SQL_INSTANCE is not set")
            connector = Connector()
            self._pool = sqlalchemy.create_engine(
                "postgresql+pg8000://",
                creator=lambda: connector.connect(
                    CLOUD_SQL_INSTANCE,
                    "pg8000",
                    user=os.environ.get("DB_USER", "aria"),
                    password=os.environ.get("DB_PASS", ""),
                    db=os.environ.get("DB_NAME", "aria"),
                ),
                pool_size=2,
                max_overflow=2,
                pool_pre_ping=True,  # Cloud Run idles; don't hand out dead sockets
                pool_recycle=1800,
            )
        return self._pool

    def _rows(self, sql: str, **params) -> list[dict]:
        import sqlalchemy

        try:
            with self._engine().connect() as conn:
                result = conn.execute(sqlalchemy.text(sql), params)
                return [dict(r) for r in result.mappings()]
        except DataUnavailable:
            raise
        except Exception as err:
            raise DataUnavailable(f"Cloud SQL read failed: {err}") from err

    def firestore(self):
        if self._fs is None:
            from google.cloud import firestore

            self._fs = firestore.Client(database=FIRESTORE_DB)
        return self._fs

    # ── per-customer reads through parameterized secure views ─────────────
    #
    # These run as `aria_app`, a role that cannot see the base tables at all.
    # The only way it can read a device or an order is through a view that is
    # filtered by $@account — and the caller of these methods supplies the
    # account from verified identity, never from the model.

    _app_pool = None

    def _app_engine(self):
        if self._app_pool is None:
            import sqlalchemy
            from google.cloud.sql.connector import Connector

            if not (CLOUD_SQL_INSTANCE and DB_APP_PASS):
                raise DataUnavailable("secure-view role not configured")
            connector = Connector()
            self._app_pool = sqlalchemy.create_engine(
                "postgresql+pg8000://",
                creator=lambda: connector.connect(
                    CLOUD_SQL_INSTANCE, "pg8000", user=DB_APP_USER,
                    password=DB_APP_PASS, db=os.environ.get("DB_NAME", "aria"),
                ),
                pool_size=2, max_overflow=2, pool_pre_ping=True, pool_recycle=1800,
            )
        return self._app_pool

    def _secure_rows(self, view_sql: str, account: str) -> list[dict]:
        """Run a SELECT over a secure view with $@account bound server-side."""
        import sqlalchemy

        try:
            with self._app_engine().connect() as conn:
                result = conn.execute(
                    sqlalchemy.text(
                        "SELECT * FROM parameterized_views.execute_parameterized_query("
                        "query => :q, param_names => ARRAY['account'], "
                        "param_values => ARRAY[:account])"
                    ),
                    {"q": view_sql, "account": account},
                )
                # rows come back as a single json_results column per row
                return [dict(r["json_results"]) for r in result.mappings()]
        except DataUnavailable:
            raise
        except Exception as err:
            raise DataUnavailable(f"secure view read failed: {err}") from err

    def my_devices(self, account: str) -> list[dict]:
        return self._secure_rows(
            "SELECT device_id, name, device_type, room, sku FROM secure.my_devices ORDER BY device_id",
            account,
        )

    def my_orders(self, account: str) -> list[dict]:
        rows = self._secure_rows(
            "SELECT order_id, item, sku, status, detail, placed_on, delivers_on "
            "FROM secure.my_orders ORDER BY placed_on DESC LIMIT 10",
            account,
        )
        return [self._shape_order(r) for r in rows]

    # ── customers ───────────────────────────────────────────────────────────

    _CUSTOMER_COLS = """
        c.customer_id, c.account_number, c.first_name, c.last_name,
        c.email, c.phone_e164,
        s.tier, s.status AS sub_status, s.renews_on, s.monthly_usd
    """

    def _shape_customer(self, r: dict) -> dict:
        return {
            "customer_id": r["customer_id"],
            "account_number": r["account_number"],
            "first_name": r["first_name"],
            "last_name": r["last_name"],
            "name": f"{r['first_name']} {r['last_name']}",
            "email": r.get("email"),
            "phone_e164": r.get("phone_e164"),
            "subscription": {
                "tier": r.get("tier"),
                "status": r.get("sub_status"),
                "renews_on": str(r["renews_on"]) if r.get("renews_on") else None,
                "monthly_usd": float(r["monthly_usd"])
                if r.get("monthly_usd")
                else None,
            },
        }

    def find_customer(
        self, phone: str = "", account_number: str = "", email: str = ""
    ) -> dict | None:
        """Account number first, then email, then the last ten digits of the phone.

        Callers read account numbers back however they like — "AH 4821", "ah-4821",
        or just "4821" — so the digits are what we actually compare. Inbound caller
        ID has no formatting agreement either, hence the ten-digit tail.
        """
        if account_number:
            want = digits(account_number)
            if want:
                rows = self._rows(
                    f"""SELECT {self._CUSTOMER_COLS}
                        FROM customers c LEFT JOIN subscriptions s USING (customer_id)
                        WHERE regexp_replace(c.account_number, '\\D', '', 'g') = :want
                        LIMIT 1""",
                    want=want,
                )
                if rows:
                    return self._shape_customer(rows[0])

        if email:
            rows = self._rows(
                f"""SELECT {self._CUSTOMER_COLS}
                    FROM customers c LEFT JOIN subscriptions s USING (customer_id)
                    WHERE LOWER(c.email) = LOWER(:email)
                    LIMIT 1""",
                email=email.strip(),
            )
            if rows:
                return self._shape_customer(rows[0])

        if phone:
            tail = digits(phone)[-10:]
            if tail:
                rows = self._rows(
                    f"""SELECT {self._CUSTOMER_COLS}
                        FROM customers c LEFT JOIN subscriptions s USING (customer_id)
                        WHERE RIGHT(regexp_replace(c.phone_e164, '\\D', '', 'g'), 10) = :tail
                        LIMIT 1""",
                    tail=tail,
                )
                if rows:
                    return self._shape_customer(rows[0])
        return None

    # ── devices: registry in Postgres, state in Firestore ───────────────────

    def devices_for(self, customer_id: int) -> list[dict]:
        return self._rows(
            """SELECT device_id, name, device_type, room, sku
               FROM devices WHERE customer_id = :cid ORDER BY device_id""",
            cid=customer_id,
        )

    def find_device(self, customer_id: int, needle: str) -> dict | None:
        """Match on room, type, or name — however the caller happened to say it."""
        n = (needle or "").strip().lower()
        if not n:
            return None
        rows = self._rows(
            """SELECT device_id, name, device_type, room, sku
               FROM devices
               WHERE customer_id = :cid
                 AND (LOWER(room) LIKE :like
                      OR LOWER(device_type) LIKE :like
                      OR LOWER(name) LIKE :like)
               ORDER BY device_id LIMIT 1""",
            cid=customer_id,
            like=f"%{n}%",
        )
        return rows[0] if rows else None

    def find_thermostat(self, customer_id: int, room: str = "") -> dict | None:
        n = (room or "").strip().lower()
        rows = self._rows(
            """SELECT device_id, name, device_type, room, sku
               FROM devices
               WHERE customer_id = :cid AND device_type = 'thermostat'
                 AND (:n = '' OR LOWER(room) LIKE :like)
               ORDER BY device_id LIMIT 1""",
            cid=customer_id,
            n=n,
            like=f"%{n}%",
        )
        return rows[0] if rows else None

    def device_state(self, device_id: str) -> dict:
        """Latest telemetry for one device, straight out of Firestore.

        A device that has never reported returns {} — that's not an error, it's an
        unknown, and the agent should say so rather than guess.
        """
        try:
            doc = (
                self.firestore()
                .collection(TELEMETRY_COLLECTION)
                .document(device_id)
                .get()
            )
        except Exception as err:
            raise DataUnavailable(
                f"telemetry read failed for {device_id}: {err}"
            ) from err
        if not doc.exists:
            log.warning(f"no telemetry document for {device_id}")
            return {}
        return doc.to_dict() or {}

    def device_history(self, device_id: str, limit: int = 10) -> list[dict]:
        """Recent readings, newest first — for "has it been doing this all day?"."""
        try:
            from google.cloud import firestore as fs

            snaps = (
                self.firestore()
                .collection(TELEMETRY_COLLECTION)
                .document(device_id)
                .collection("history")
                .order_by("reported_at", direction=fs.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            return [s.to_dict() for s in snaps]
        except Exception as err:
            raise DataUnavailable(
                f"history read failed for {device_id}: {err}"
            ) from err

    # ── orders ──────────────────────────────────────────────────────────────

    _ORDER_COLS = "order_id, item, sku, status, detail, placed_on, delivers_on"

    def _shape_order(self, r: dict) -> dict:
        return {
            "order_id": r["order_id"],
            "item": r["item"],
            "sku": r.get("sku"),
            "status": r["status"],
            "detail": r.get("detail"),
            "placed_on": str(r["placed_on"]) if r.get("placed_on") else None,
            "delivers_on": str(r["delivers_on"]) if r.get("delivers_on") else None,
        }

    def orders_for(self, customer_id: int) -> list[dict]:
        rows = self._rows(
            f"""SELECT {self._ORDER_COLS} FROM orders
                WHERE customer_id = :cid ORDER BY placed_on DESC""",
            cid=customer_id,
        )
        return [self._shape_order(r) for r in rows]

    def most_recent_order(self, customer_id: int) -> dict | None:
        rows = self.orders_for(customer_id)
        return rows[0] if rows else None

    def get_order(self, order_id: str) -> dict | None:
        rows = self._rows(
            f"""SELECT {self._ORDER_COLS} FROM orders WHERE order_id = :oid LIMIT 1""",
            oid=digits(order_id),
        )
        return self._shape_order(rows[0]) if rows else None

    # ── product catalogue (Firestore) ───────────────────────────────────────

    _products_cache: dict = {}

    def products(self) -> dict:
        """The catalogue, keyed by SKU: name, category, price, image_url.

        Small and static, so it is read once per process and cached. This is
        where every picture on the site comes from — nothing matches on names.
        """
        if not self._products_cache:
            try:
                docs = self.firestore().collection(PRODUCTS_COLLECTION).stream()
                self._products_cache = {d.id: d.to_dict() for d in docs}
            except Exception as err:
                raise DataUnavailable(f"products read failed: {err}") from err
        return self._products_cache

    def with_product(self, row: dict) -> dict:
        """Attach image_url / price / category to a device or order row by its sku."""
        prod = self.products().get(row.get("sku") or "", {})
        return {
            **row,
            "image_url": prod.get("image_url"),
            "price_usd": prod.get("price_usd"),
            "category": prod.get("category"),
        }

    # ── call memory (Firestore) ─────────────────────────────────────────────
    #
    # LiveKit keeps a conversation only for the length of a call. Anything Ember
    # should remember next time — what the customer called about, how it ended —
    # is written here at hang-up and read back at the next greeting.

    def save_call(self, account_number: str, call: dict) -> str:
        """Append one call record under the account. Returns the document id."""
        try:
            from datetime import datetime, timezone

            doc = {**call, "account_number": account_number,
                   "ended_at": datetime.now(timezone.utc)}
            ref = (self.firestore().collection(CALLS_COLLECTION)
                   .document(account_number).collection("calls").document())
            ref.set(doc)
            return ref.id
        except Exception as err:
            raise DataUnavailable(f"call save failed: {err}") from err

    def recent_calls(self, account_number: str, limit: int = 3) -> list[dict]:
        """Newest first. Transcripts are excluded; the brief is what the agent needs."""
        try:
            from google.cloud import firestore as fs

            snaps = (self.firestore().collection(CALLS_COLLECTION)
                     .document(account_number).collection("calls")
                     .order_by("ended_at", direction=fs.Query.DESCENDING)
                     .limit(limit).stream())
            out = []
            for sn in snaps:
                d = sn.to_dict() or {}
                when = d.get("ended_at")
                out.append({
                    "call_id": sn.id,
                    "ended_at": when.isoformat() if hasattr(when, "isoformat") else str(when),
                    "summary": d.get("summary", ""),
                    "next_steps": d.get("next_steps", []),
                    "mood": d.get("mood"),
                    "outcome": d.get("outcome"),
                })
            return out
        except Exception as err:
            raise DataUnavailable(f"call history read failed: {err}") from err

    # ── long-term memory (Vertex AI Memory Bank) ────────────────────────────
    #
    # Memory Bank keeps *facts* about a customer, consolidated by an LLM across
    # calls: a new fact that contradicts an old one updates it rather than piling
    # up. Firestore call_history remains the full transcript record. Scope is the
    # account number, so one customer can never read another's memories.

    _mb = None

    def _memory_client(self):
        if not MEMORY_BANK:
            raise DataUnavailable("MEMORY_BANK is not set")
        if self._mb is None:
            import vertexai

            project, location = MEMORY_BANK.split("/")[1], MEMORY_BANK.split("/")[3]
            self._mb = vertexai.Client(project=project, location=location)
        return self._mb

    def memories(self, account_number: str, query: str = "", top_k: int = 5) -> list[dict]:
        """All facts for an account, or the top_k most relevant to a question."""
        try:
            kw = {"name": MEMORY_BANK, "scope": {"user_id": account_number}}
            if query:
                kw["similarity_search_params"] = {"search_query": query, "top_k": top_k}
            page = self._memory_client().agent_engines.memories.retrieve(**kw).page
            return [{"fact": m.memory.fact,
                     "updated": str(getattr(m.memory, "update_time", "") or "")[:10]}
                    for m in page]
        except Exception as err:
            raise DataUnavailable(f"memory retrieve failed: {err}") from err

    def remember(self, account_number: str, fact: str) -> None:
        """Store one explicit fact now (sub-second)."""
        try:
            self._memory_client().agent_engines.memories.create(
                name=MEMORY_BANK, fact=fact, scope={"user_id": account_number}
            )
        except Exception as err:
            raise DataUnavailable(f"memory create failed: {err}") from err

    def generate_memories(self, account_number: str, transcript: list[dict]) -> None:
        """Extract + consolidate facts from a whole call. Takes ~20 s — never wait."""
        events = [
            {"content": {"role": "model" if t.get("role") == "assistant" else "user",
                         "parts": [{"text": str(t.get("text", ""))}]}}
            for t in transcript if t.get("text")
        ]
        if not events:
            return
        try:
            self._memory_client().agent_engines.memories.generate(
                name=MEMORY_BANK,
                direct_contents_source={"events": events},
                scope={"user_id": account_number},
                config={"wait_for_completion": False},
            )
        except Exception as err:
            raise DataUnavailable(f"memory generate failed: {err}") from err

    # ── tickets ─────────────────────────────────────────────────────────────

    def open_ticket(
        self, customer_id: int | None, order_id: str | None, summary: str
    ) -> dict:
        """Idempotent while a matching ticket is still open.

        The model retries on a tool timeout. Without the ON CONFLICT this becomes
        four identical tickets for one customer, which is what happened in testing.
        The partial unique index in schema.sql is what makes this safe.
        """
        rows = self._rows(
            """INSERT INTO support_tickets (customer_id, order_id, summary)
               VALUES (:cid, :oid, :summary)
               ON CONFLICT (customer_id, order_id, summary)
                   WHERE status = 'open'
                   DO UPDATE SET summary = EXCLUDED.summary
               RETURNING ticket_id, status,
                         (xmax <> 0) AS was_existing""",
            cid=customer_id,
            oid=order_id,
            summary=summary,
        )
        r = rows[0]
        return {
            "ticket_id": r["ticket_id"],
            "status": r["status"],
            "duplicate": bool(r["was_existing"]),
        }


repo = Repo()
