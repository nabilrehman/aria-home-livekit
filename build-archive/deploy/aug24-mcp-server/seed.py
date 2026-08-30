#!/usr/bin/env python3
"""Populate both Aria Home stores.

    python3 seed.py --sql          apply schema.sql to Cloud SQL (drops and recreates)
    python3 seed.py --telemetry    write device state into Firestore
    python3 seed.py --all          both
    python3 seed.py --check        read both back and print what the agent would see

Environment:
    CLOUD_SQL_INSTANCE   project:region:instance
    DB_USER DB_PASS DB_NAME
    FIRESTORE_DB         default "aug24"

Telemetry is written twice on purpose: a latest-state document the agent reads on
every call, and one history entry, so "has the garage camera been offline all day?"
has somewhere to look.
"""

import argparse
import pathlib
import sys
from datetime import datetime, timedelta, timezone

import seed_data
from data import PRODUCTS_COLLECTION, TELEMETRY_COLLECTION, repo

HERE = pathlib.Path(__file__).parent


def seed_sql() -> None:
    import sqlalchemy

    ddl = (HERE / "schema.sql").read_text()
    engine = repo._engine()
    with engine.begin() as conn:
        # schema.sql carries its own BEGIN/COMMIT; hand it over as one script.
        conn.exec_driver_sql(ddl)
    with engine.connect() as conn:
        for table in ("customers", "subscriptions", "devices", "orders"):
            n = conn.execute(sqlalchemy.text(f"SELECT count(*) FROM {table}")).scalar()
            print(f"  {table:<16} {n} rows")
    print("Cloud SQL seeded.")


def seed_telemetry() -> None:
    fs = repo.firestore()
    now = datetime.now(timezone.utc)
    batch = fs.batch()

    for i, (device_id, state) in enumerate(seed_data.TELEMETRY.items()):
        reported_at = now - timedelta(
            seconds=17 * (i + 1)
        )  # staggered, like real reports
        doc = {**state, "device_id": device_id, "reported_at": reported_at}

        latest = fs.collection(TELEMETRY_COLLECTION).document(device_id)
        batch.set(latest, doc)
        batch.set(latest.collection("history").document(), doc)

    batch.commit()
    print(
        f"Firestore seeded: {len(seed_data.TELEMETRY)} devices in {TELEMETRY_COLLECTION}."
    )


def seed_products() -> None:
    """The catalogue: sku -> name, category, price, image_url. Every picture on the
    site and every order/device thumbnail resolves through this collection."""
    fs = repo.firestore()
    batch = fs.batch()
    for sku, prod in seed_data.PRODUCTS.items():
        batch.set(
            fs.collection(PRODUCTS_COLLECTION).document(sku), {"sku": sku, **prod}
        )
    batch.commit()
    print(
        f"Firestore seeded: {len(seed_data.PRODUCTS)} products in {PRODUCTS_COLLECTION}."
    )


def check() -> None:
    """Read back through the same path the agent uses, for every seeded customer."""
    for c in seed_data.CUSTOMERS:
        cust = repo.find_customer(account_number=c["account_number"])
        if cust is None:
            print(f"MISSING {c['account_number']}")
            continue

        sub = cust["subscription"]
        print(
            f"\n{cust['name']}  {cust['account_number']}  "
            f"{sub['tier']} ({sub['status']})  {cust['phone_e164']}"
        )

        for d in repo.devices_for(cust["customer_id"]):
            st = repo.device_state(d["device_id"])
            when = st.get("reported_at")
            stamp = when.strftime("%H:%M:%S") if hasattr(when, "strftime") else "—"
            mark = "on " if st.get("active") else "off"
            print(
                f"    [{mark}] {d['device_id']:<11} {d['name']:<24} "
                f"{st.get('reading', 'no telemetry'):<14} @ {stamp}"
            )

        recent = repo.most_recent_order(cust["customer_id"])
        if recent:
            print(
                f"    latest order {recent['order_id']} · {recent['item']} · "
                f"{recent['status']}"
            )

    # Prove the phone path too — that's how a SIP caller is identified.
    by_phone = repo.find_customer(phone="512 555 1188")
    print(
        f"\nphone lookup '512 555 1188' -> "
        f"{by_phone['name'] if by_phone else 'NOT FOUND'}"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sql", action="store_true")
    ap.add_argument("--telemetry", action="store_true")
    ap.add_argument("--products", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if not any((args.sql, args.telemetry, args.products, args.all, args.check)):
        ap.print_help()
        return 1

    if args.all or args.sql:
        seed_sql()
    if args.all or args.telemetry:
        seed_telemetry()
    if args.all or args.products:
        seed_products()
    if args.check:
        check()
    return 0


if __name__ == "__main__":
    sys.exit(main())
