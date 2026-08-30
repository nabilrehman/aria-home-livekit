"""Aria Home voice support — authenticated web client.

Flow:
  1. Browser signs in with Firebase Auth and gets a short-lived ID token.
  2. Browser POSTs that ID token to /token as `Authorization: Bearer <id_token>`.
  3. This service verifies the token with the Firebase Admin SDK, maps the user to
     an Aria Home account, and mints a LiveKit access token.
  4. The LiveKit token carries the account number as a participant *attribute*, so
     Ember knows who called before anyone says a word.

The LiveKit API key/secret never leave this service. Participant identity is the
opaque Firebase uid — never an email or phone — because LiveKit records identity
and room name in infrastructure logs that are not PII-redacted.
"""

import datetime
import os
import pathlib
import uuid

import firebase_admin
from firebase_admin import auth as fb_auth
from flask import Flask, Response, jsonify, request
from livekit import api

app = Flask(__name__)

KEY = os.environ["LIVEKIT_API_KEY"]
SECRET = os.environ["LIVEKIT_API_SECRET"]
URL = os.environ["LIVEKIT_URL"]
AGENT = os.environ.get("AGENT_NAME", "anycompany-agent")

# Firebase *web* config is public by design — it identifies the project, it does not
# grant anything. Access is controlled by Firebase Auth rules, not by hiding this.
FIREBASE_WEB = {
    "apiKey": os.environ.get("FIREBASE_API_KEY", ""),
    "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN", ""),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID", ""),
}

# On Cloud Run the Admin SDK picks up the runtime service account from the metadata
# server — no key file to manage. verify_id_token checks the token's audience against
# the project id, so name it explicitly when Firebase lives in a different project
# from this Cloud Run service.
_fb_project = FIREBASE_WEB["projectId"] or os.environ.get("GOOGLE_CLOUD_PROJECT")
firebase_admin.initialize_app(
    options={"projectId": _fb_project} if _fb_project else None
)

from data import DataUnavailable, repo  # noqa: E402  (after env is read)


def _customer_for(decoded: dict) -> dict | None:
    """Resolve a verified Firebase user to their Aria Home customer row.

    The join key is the email on the account — customers.email in Postgres. No
    mapping table in the app: if you are not a customer, you are not a customer,
    and the call falls through to the guest path where Ember asks who you are.
    """
    email = (decoded.get("email") or "").strip()
    if not email:
        return None
    return repo.find_customer(email=email)


def _verified(request) -> dict | None:
    """Return the decoded Firebase claims, or None if the caller isn't signed in."""
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    try:
        return fb_auth.verify_id_token(header.removeprefix("Bearer ").strip())
    except Exception:
        return None


def _mint(identity: str, display_name: str, account_number: str = "") -> dict:
    """Build a LiveKit access token. `account_number` empty = caller not yet known."""
    grant = api.VideoGrants(
        room_join=True,
        room=f"web-{uuid.uuid4().hex[:8]}",
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True,
    )
    room_config = api.RoomConfiguration(
        agents=[api.RoomAgentDispatch(agent_name=AGENT)],
        empty_timeout=120,
        max_participants=3,
    )
    builder = (
        api.AccessToken(KEY, SECRET)
        .with_identity(identity)
        .with_name(display_name)
        .with_grants(grant)
        .with_room_config(room_config)
        .with_ttl(datetime.timedelta(minutes=15))
    )
    if account_number:
        builder = builder.with_attributes({"aria_account": account_number})
    return {
        "token": builder.to_jwt(),
        "url": URL,
        "room": grant.room,
        "name": display_name,
    }


@app.post("/token/guest")
def token_guest():
    """Unauthenticated call — the phone caller's experience.

    A SIP caller has no login, so the agent has to ask who they are and look them
    up by phone or account number. This endpoint reproduces that on the web so the
    identification beat can be demonstrated without dialling in. No account rides
    on the token, so the agent falls through to asking.
    """
    return jsonify(_mint(f"guest-{uuid.uuid4().hex[:8]}", "Caller"))


@app.post("/token")
def token():
    decoded = _verified(request)
    if decoded is None:
        return jsonify({"error": "Sign in to start a call."}), 401

    uid = decoded["uid"]
    try:
        cust = _customer_for(decoded)
    except DataUnavailable as err:
        app.logger.error(f"customer lookup failed: {err}")
        return jsonify(
            {"error": "Account system is unavailable. Try again shortly."}
        ), 503

    if cust is None:
        # Signed in, but not a customer of ours. Let them talk to Ember anyway —
        # she will ask for a phone or account number like any other caller.
        app.logger.info(
            f"signed-in user {decoded.get('email')} has no Aria Home account"
        )
        return jsonify(_mint(uid, decoded.get("name") or "Caller"))

    # Identity is the opaque Firebase uid — never an email or phone, because LiveKit
    # writes identity and room name into logs that are not PII-redacted. Only the
    # account NUMBER rides along; the profile stays server-side.
    return jsonify(_mint(uid, cust["name"], cust["account_number"]))


@app.get("/me")
def me():
    """The signed-in customer's system and order history. Never public.

    Devices come from Postgres (the registry) and their readings from Firestore
    (telemetry), joined on device_id — the same two-store path the agent uses.
    """
    decoded = _verified(request)
    if decoded is None:
        return jsonify({"error": "Sign in to see your system."}), 401

    try:
        cust = _customer_for(decoded)
        if cust is None:
            return jsonify({"error": "no_account", "email": decoded.get("email")}), 404

        cid = cust["customer_id"]
        devices = []
        for d in repo.devices_for(cid):
            state = repo.device_state(d["device_id"])
            devices.append(
                repo.with_product(
                    {
                        "device_id": d["device_id"],
                        "device": d["name"],
                        "type": d["device_type"],
                        "room": d["room"].title(),
                        "sku": d.get("sku"),
                        "state": state.get("reading", "no signal"),
                        "on": bool(state.get("active")),
                        "battery_pct": state.get("battery_pct"),
                    }
                )
            )
        orders = [repo.with_product(o) for o in repo.orders_for(cid)]
    except DataUnavailable as err:
        app.logger.error(f"/me failed: {err}")
        return jsonify({"error": "Your system is unreachable right now."}), 503

    sub = cust["subscription"]
    return jsonify(
        {
            "name": cust["name"],
            "first_name": cust["first_name"],
            "account": cust["account_number"],
            "plan": sub["tier"],
            "plan_status": sub["status"],
            "renews_on": sub["renews_on"],
            "devices": devices,
            "orders": orders,
        }
    )


# ── Orders API — a plain REST surface for the voice agent ──────────────────
#
# Order status is a one-line lookup, so the agent calls it as an ordinary HTTP
# function tool rather than through MCP. MCP earns its place for the device cloud
# and the knowledge base (many tools, external systems); a REST call is the right
# weight for this. Shared key, because this is not a browser endpoint.
ORDERS_API_KEY = os.environ.get("ORDERS_API_KEY", "")


def _api_key_ok(request) -> bool:
    return (
        bool(ORDERS_API_KEY) and request.headers.get("X-Api-Key", "") == ORDERS_API_KEY
    )


@app.get("/api/orders")
def api_orders():
    """Orders for an account, newest first. ?account=AH-7104"""
    if not _api_key_ok(request):
        return jsonify({"error": "unauthorized"}), 401
    account = request.args.get("account", "")
    try:
        cust = repo.find_customer(account_number=account)
        if cust is None:
            return jsonify({"found": False, "error": "no_such_account"}), 404
        orders = [repo.with_product(o) for o in repo.orders_for(cust["customer_id"])]
    except DataUnavailable as err:
        app.logger.error(f"/api/orders failed: {err}")
        return jsonify({"error": "orders_unavailable"}), 503
    return jsonify({"found": True, "account": cust["account_number"], "orders": orders})


@app.get("/api/orders/<order_id>")
def api_order(order_id: str):
    if not _api_key_ok(request):
        return jsonify({"error": "unauthorized"}), 401
    try:
        order = repo.get_order(order_id)
    except DataUnavailable as err:
        app.logger.error(f"/api/orders/{order_id} failed: {err}")
        return jsonify({"error": "orders_unavailable"}), 503
    if order is None:
        return jsonify({"found": False}), 404
    return jsonify({"found": True, **repo.with_product(order)})


# ── Product images ─────────────────────────────────────────────────────────
# The org forbids public buckets, so the store serves catalogue images from the
# private bucket through this route. Firestore `products.image_url` points here.
ASSETS_BUCKET = os.environ.get("ASSETS_BUCKET", "aria-home-assets-bq-demos-469816")
_gcs = None


@app.get("/assets/products/<path:name>")
def product_image(name: str):
    global _gcs
    if not name.endswith(".png") or "/" in name:
        return Response(status=404)
    try:
        if _gcs is None:
            from google.cloud import storage

            _gcs = storage.Client()
        data = _gcs.bucket(ASSETS_BUCKET).blob(f"products/{name}").download_as_bytes()
    except Exception as err:
        app.logger.warning(f"asset {name} unavailable: {err}")
        return Response(status=404)
    return Response(
        data,
        mimetype="image/png",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@app.get("/api/products")
def api_products():
    """The catalogue, for the storefront grid."""
    try:
        return jsonify(repo.products())
    except DataUnavailable as err:
        app.logger.error(f"/api/products failed: {err}")
        return jsonify({"error": "catalogue_unavailable"}), 503


# ── Specialist desk: warm handoff without a carrier ───────────────────────────
#
# The agent posts a brief here when it decides to transfer. The desk page
# (/desk) rings, shows the brief, and on Accept joins the caller's LiveKit room
# as a WebRTC participant — the human is just another participant, exactly as a
# SIP dial-out would be. Single-instance in-memory queue: this service runs with
# min-instances=1 and the queue is demo state, not a system of record.
import threading
import time

DESK_PIN = os.environ.get("DESK_PIN", "")
_handoffs: dict[str, dict] = {}
_handoffs_lock = threading.Lock()


def _desk_ok(request) -> bool:
    return bool(DESK_PIN) and request.headers.get("X-Desk-Pin", "") == DESK_PIN


@app.post("/api/handoffs")
def handoff_create():
    """Agent → desk. Body: room, department, brief{summary,next_steps,mood,urgency}, caller{}."""
    if not _api_key_ok(request):
        return jsonify({"error": "unauthorized"}), 401
    body = request.get_json(silent=True) or {}
    hid = uuid.uuid4().hex[:10]
    item = {
        "id": hid,
        "room": body.get("room") or "",
        "department": body.get("department") or "the support team",
        "brief": body.get("brief") or {},
        "caller": body.get("caller") or {},
        "status": "ringing",
        "created_at": time.time(),
    }
    with _handoffs_lock:
        _handoffs[hid] = item
    app.logger.info(f"handoff {hid} ringing for room {item['room']}")
    return jsonify(item), 201


@app.get("/api/handoffs")
def handoff_list():
    """Desk polls this. Ringing first, then the last few resolved."""
    if not _desk_ok(request):
        return jsonify({"error": "unauthorized"}), 401
    with _handoffs_lock:
        items = sorted(_handoffs.values(), key=lambda h: h["created_at"], reverse=True)
    return jsonify({"handoffs": items[:20]})


@app.get("/api/handoffs/<hid>")
def handoff_get(hid):
    """Agent polls this to learn whether the specialist accepted or declined."""
    if not (_api_key_ok(request) or _desk_ok(request)):
        return jsonify({"error": "unauthorized"}), 401
    with _handoffs_lock:
        item = _handoffs.get(hid)
    return (jsonify(item), 200) if item else (jsonify({"error": "not_found"}), 404)


@app.post("/api/handoffs/<hid>/accept")
def handoff_accept(hid):
    """Desk accepts: mint a token so the specialist joins the caller's room."""
    if not _desk_ok(request):
        return jsonify({"error": "unauthorized"}), 401
    body = request.get_json(silent=True) or {}
    name = (body.get("name") or "Specialist").strip()[:40]
    with _handoffs_lock:
        item = _handoffs.get(hid)
        if not item:
            return jsonify({"error": "not_found"}), 404
        item["status"] = "accepted"
        item["specialist"] = name
        item["resolved_at"] = time.time()
    identity = f"specialist-{uuid.uuid4().hex[:6]}"  # the agent steps back on "specialist"
    grant = api.VideoGrants(
        room_join=True, room=item["room"], can_publish=True,
        can_subscribe=True, can_publish_data=True,
    )
    jwt = (
        api.AccessToken(KEY, SECRET)
        .with_identity(identity)
        .with_name(name)
        .with_grants(grant)
        .with_ttl(datetime.timedelta(minutes=30))
        .to_jwt()
    )
    return jsonify({"token": jwt, "url": URL, "room": item["room"], "identity": identity})


@app.post("/api/handoffs/<hid>/decline")
def handoff_decline(hid):
    if not _desk_ok(request):
        return jsonify({"error": "unauthorized"}), 401
    body = request.get_json(silent=True) or {}
    with _handoffs_lock:
        item = _handoffs.get(hid)
        if not item:
            return jsonify({"error": "not_found"}), 404
        item["status"] = "declined"
        item["reason"] = (body.get("reason") or "")[:200]
        item["resolved_at"] = time.time()
    return jsonify(item)


# ── Call memory: the agent writes a record at hang-up; reads happen via MCP ──
@app.post("/api/calls")
def call_save():
    if not _api_key_ok(request):
        return jsonify({"error": "unauthorized"}), 401
    body = request.get_json(silent=True) or {}
    account = (body.get("account_number") or "").strip().upper()
    if not account:
        return jsonify({"error": "account_number required"}), 400
    record = {
        "room": body.get("room", ""),
        "summary": body.get("summary", ""),
        "next_steps": body.get("next_steps", []),
        "mood": body.get("mood"),
        "urgency": body.get("urgency"),
        "outcome": body.get("outcome", "completed"),
        "transcript": (body.get("transcript") or [])[:400],
    }
    try:
        cid = repo.save_call(account, record)
    except DataUnavailable as err:
        app.logger.error(f"call save failed: {err}")
        return jsonify({"error": "history_unavailable"}), 503
    app.logger.info(f"call saved for {account}: {cid}")
    return jsonify({"call_id": cid}), 201


@app.get("/api/calls")
def call_list():
    if not _api_key_ok(request):
        return jsonify({"error": "unauthorized"}), 401
    account = (request.args.get("account") or "").strip().upper()
    try:
        return jsonify({"calls": repo.recent_calls(account, limit=3)})
    except DataUnavailable as err:
        app.logger.error(f"call list failed: {err}")
        return jsonify({"error": "history_unavailable"}), 503


@app.get("/desk")
def desk():
    return Response(
        (pathlib.Path(__file__).parent / "desk.html").read_text(), mimetype="text/html"
    )


@app.get("/config")
def config():
    return jsonify(FIREBASE_WEB)


@app.get("/")
def index():
    return Response(
        (pathlib.Path(__file__).parent / "index.html").read_text(),
        mimetype="text/html",
    )
