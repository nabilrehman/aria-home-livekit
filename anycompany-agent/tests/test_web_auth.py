"""Auth tests for the web token endpoint (build-archive/deploy/aug24-webapp/main.py).

The rule these pin down: no verified Firebase ID token, no LiveKit room. And when a
token IS verified, the minted LiveKit JWT must carry an opaque identity, the right
grants, and no PII.

firebase_admin is stubbed, so these run offline with no credentials.
"""

import asyncio
import base64
import importlib.util
import json
import os
import sys
import types
from pathlib import Path

import pytest

from tests.test_device_data import FakeRepo

WEBAPP = (
    Path(__file__).resolve().parents[2]
    / "build-archive"
    / "deploy"
    / "aug24-webapp"
    / "main.py"
)

API_KEY = "APIdevkey"
API_SECRET = "devsecret0123456789devsecret0123456789"


class _StubVerifyError(Exception):
    pass


def _load_webapp():
    """Import main.py with firebase_admin stubbed and test env applied.

    main.py reads its config at import time, so the env has to be in place for the
    load — but only for the load. The real LIVEKIT_* credentials from .env.local are
    restored immediately afterwards, or every other test in the suite would try to
    reach LiveKit with this fake key.
    """
    fake_env = {
        "LIVEKIT_API_KEY": API_KEY,
        "LIVEKIT_API_SECRET": API_SECRET,
        "LIVEKIT_URL": "wss://test.livekit.cloud",
        "AGENT_NAME": "anycompany-agent",
        "FIREBASE_PROJECT_ID": "aria-home-test",
        "FIREBASE_API_KEY": "web-api-key",
        "FIREBASE_AUTH_DOMAIN": "aria-home-test.firebaseapp.com",
    }
    saved = {k: os.environ.get(k) for k in fake_env}
    os.environ.update(fake_env)

    auth_stub = types.SimpleNamespace(
        verify_id_token=lambda tok: (_ for _ in ()).throw(
            _StubVerifyError("not configured")
        )
    )
    fb = types.ModuleType("firebase_admin")
    fb.initialize_app = lambda *a, **k: None
    fb.auth = auth_stub
    sys.modules["firebase_admin"] = fb
    sys.modules["firebase_admin.auth"] = auth_stub

    try:
        spec = importlib.util.spec_from_file_location("aria_webapp", WEBAPP)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        for key, was in saved.items():
            if was is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = was
    return mod


main = _load_webapp()


@pytest.fixture
def client(monkeypatch):
    """Real Flask app, real token minting, both data stores faked."""
    monkeypatch.setattr(main, "repo", FakeRepo())
    main.app.config["TESTING"] = True
    with main.app.test_client() as c:
        yield c


def signed_in_as(monkeypatch, *, uid: str, email: str, name: str = "") -> None:
    """Make verify_id_token succeed for this user."""
    claims = {"uid": uid, "email": email}
    if name:
        claims["name"] = name
    monkeypatch.setattr(main.fb_auth, "verify_id_token", lambda tok: claims)


def signed_out(monkeypatch) -> None:
    """Make verify_id_token reject anything it is given."""

    def _reject(tok):
        raise _StubVerifyError("invalid or expired")

    monkeypatch.setattr(main.fb_auth, "verify_id_token", _reject)


def claims_of(jwt_str: str) -> dict:
    payload = jwt_str.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload))


# --------------------------------------------------------------- logged OUT


def test_no_header_is_rejected(client):
    r = client.post("/token")
    assert r.status_code == 401
    assert "token" not in r.get_json()


def test_bare_token_without_bearer_is_rejected(client):
    r = client.post("/token", headers={"Authorization": "some-raw-id-token"})
    assert r.status_code == 401


def test_expired_or_forged_token_is_rejected(client, monkeypatch):
    signed_out(monkeypatch)
    r = client.post("/token", headers={"Authorization": "Bearer tampered.token.here"})
    assert r.status_code == 401
    assert "token" not in r.get_json()


def test_get_is_not_allowed(client):
    """Tokens in URLs land in logs and browser history — POST only."""
    assert client.get("/token").status_code == 405


# ---------------------------------------------------------------- logged IN


def test_known_user_gets_their_own_account(client, monkeypatch):
    signed_in_as(monkeypatch, uid="firebase-uid-sarah", email="sarah@example.com")
    r = client.post("/token", headers={"Authorization": "Bearer good"})

    assert r.status_code == 200
    body = r.get_json()
    assert body["name"] == "Sarah Chen"

    c = claims_of(body["token"])
    assert c["sub"] == "firebase-uid-sarah"
    assert c["attributes"]["aria_account"] == "AH-4821"


def test_second_user_gets_a_different_account(client, monkeypatch):
    """Identity must actually follow the signed-in user, not a hardcoded demo."""
    signed_in_as(monkeypatch, uid="firebase-uid-marcus", email="marcus@example.com")
    c = claims_of(
        client.post("/token", headers={"Authorization": "Bearer good"}).get_json()[
            "token"
        ]
    )

    assert c["sub"] == "firebase-uid-marcus"
    assert c["attributes"]["aria_account"] == "AH-3390"


def test_a_signed_in_non_customer_gets_no_account(client, monkeypatch):
    """Signing in does not make you a customer. Ember still has to ask."""
    signed_in_as(
        monkeypatch, uid="uid-newcomer", email="someone@gmail.com", name="Jane Roe"
    )
    body = client.post("/token", headers={"Authorization": "Bearer good"}).get_json()
    c = claims_of(body["token"])

    assert c["sub"] == "uid-newcomer"
    assert not c.get("attributes"), "a non-customer must not be handed an account"


def test_the_demo_google_account_resolves_to_its_own_customer(client, monkeypatch):
    """nabilrehman8@gmail.com is a real row in customers, not a mapping table entry."""
    signed_in_as(monkeypatch, uid="uid-nabil", email="nabilrehman8@gmail.com")
    body = client.post("/token", headers={"Authorization": "Bearer good"}).get_json()
    c = claims_of(body["token"])

    assert body["name"] == "Nabil Rehman"
    assert c["attributes"]["aria_account"] == "AH-7104"


def test_me_returns_devices_and_order_history(client, monkeypatch):
    signed_in_as(monkeypatch, uid="uid-nabil", email="nabilrehman8@gmail.com")
    r = client.get("/me", headers={"Authorization": "Bearer good"})
    body = r.get_json()

    assert r.status_code == 200
    assert body["account"] == "AH-7104" and body["first_name"] == "Nabil"
    assert len(body["devices"]) == 5
    assert {d["device"] for d in body["devices"]} >= {
        "Aria Thermostat",
        "Aria Doorbell Cam",
        "Aria Smart Lock",
    }
    # order history, newest first, each with its catalogue image
    assert [o["order_id"] for o in body["orders"]] == ["58131", "58130", "58129"]
    assert all(o["image_url"].endswith(".png") for o in body["orders"])
    assert all(d["image_url"].endswith(".png") for d in body["devices"])
    assert body["orders"][0]["status"] == "processing"


def test_me_marks_a_device_that_needs_attention(client, monkeypatch):
    signed_in_as(monkeypatch, uid="uid-nabil", email="nabilrehman8@gmail.com")
    devices = client.get("/me", headers={"Authorization": "Bearer good"}).get_json()[
        "devices"
    ]
    sensor = next(d for d in devices if d["type"] == "sensor")

    assert sensor["on"] is False
    assert sensor["battery_pct"] == 6


def test_me_needs_a_signed_in_user(client):
    assert client.get("/me").status_code == 401


# ------------------------------------------------------------------ privacy


def test_identity_and_room_are_opaque(client, monkeypatch):
    """LiveKit writes identity and room name to logs that are not PII-redacted."""
    signed_in_as(monkeypatch, uid="uid-sarah", email="sarah@example.com")
    body = client.post("/token", headers={"Authorization": "Bearer good"}).get_json()
    c = claims_of(body["token"])

    leaks = ("sarah@example.com", "example.com", "Sarah", "+1512")
    for field in (c["sub"], c["video"]["room"], body["room"]):
        for leak in leaks:
            assert leak not in field, f"{leak!r} leaked into {field!r}"


def test_attributes_carry_the_account_number_and_nothing_personal(client, monkeypatch):
    """A JWT is base64, not encrypted, and this one is handed to the browser."""
    signed_in_as(monkeypatch, uid="uid-sarah", email="sarah@example.com")
    c = claims_of(
        client.post("/token", headers={"Authorization": "Bearer good"}).get_json()[
            "token"
        ]
    )

    assert c["attributes"] == {"aria_account": "AH-4821"}
    blob = json.dumps(c["attributes"])
    for leak in ("Sarah", "sarah@example.com", "+1512", "Video Plus", "thermostat"):
        assert leak not in blob


def test_no_api_secret_anywhere_in_the_response(client, monkeypatch):
    signed_in_as(monkeypatch, uid="uid-sarah", email="sarah@example.com")
    raw = client.post("/token", headers={"Authorization": "Bearer good"}).get_data(
        as_text=True
    )
    assert API_SECRET not in raw


# ------------------------------------------------------------------- grants


def test_grants_allow_a_call_but_not_administration(client, monkeypatch):
    signed_in_as(monkeypatch, uid="uid-sarah", email="sarah@example.com")
    v = claims_of(
        client.post("/token", headers={"Authorization": "Bearer good"}).get_json()[
            "token"
        ]
    )["video"]

    assert v["roomJoin"] is True
    assert v["canPublish"] is True
    assert v["canSubscribe"] is True
    assert v.get("roomAdmin") is not True
    assert v.get("hidden") is not True


def test_issuer_and_ttl_are_within_policy(client, monkeypatch):
    signed_in_as(monkeypatch, uid="uid-sarah", email="sarah@example.com")
    c = claims_of(
        client.post("/token", headers={"Authorization": "Bearer good"}).get_json()[
            "token"
        ]
    )

    assert c["iss"] == API_KEY
    ttl_minutes = (c["exp"] - c["nbf"]) / 60
    assert 10 <= ttl_minutes <= 60, f"TTL {ttl_minutes} min is outside policy"


def test_room_config_dispatches_the_agent_and_bounds_the_room(client, monkeypatch):
    signed_in_as(monkeypatch, uid="uid-sarah", email="sarah@example.com")
    c = claims_of(
        client.post("/token", headers={"Authorization": "Bearer good"}).get_json()[
            "token"
        ]
    )

    rc = c["roomConfig"]
    assert rc["agents"][0]["agentName"] == "anycompany-agent"
    assert int(rc["emptyTimeout"]) == 120  # a room nobody joins closes itself
    assert int(rc["maxParticipants"]) == 3  # caller + Ember + one specialist


# -------------------------------------------------------- agent-side pairing


def test_agent_skips_identification_for_an_authenticated_caller():
    """The attribute the token carries is the one the agent branches on."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from agent import Assistant

    attrs = {"aria_account": "AH-4821"}  # what the web token delivers
    known = Assistant(known_account=attrs["aria_account"], known_name="Sarah Chen")
    anon = Assistant()

    assert "Do NOT ask for a phone number" in known.instructions
    assert "AH-4821" in known.instructions
    # Guests are identified by IdentifyCallerTask, which owns the asking.
    assert "already identified" not in anon.instructions
    assert "Do NOT ask" not in anon.instructions
    assert "already identified" not in anon.instructions


def test_phone_caller_without_attributes_still_gets_identified_normally():
    """SIP callers have no token attributes — they must keep the ANI path."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from agent import Assistant

    anon = Assistant(known_account="", known_name="")
    assert "Do NOT ask" not in anon.instructions
    # The asking lives in the identification task's prompt now.
    from tasks import IdentifyCallerTask

    async def _dummy_verify(account, email="", phone=""):
        return True

    async def _task_text():
        return IdentifyCallerTask([], _dummy_verify).instructions

    text = asyncio.run(_task_text())
    assert "phone number" in text and "lookup_account_by_phone" in text


# ---------------------------------------------------- guest = the phone caller


def test_guest_call_needs_no_sign_in(client):
    """A SIP caller has no login. The guest path reproduces that on the web."""
    r = client.post("/token/guest")
    assert r.status_code == 200
    assert r.get_json()["token"]


def test_guest_token_carries_no_account_so_the_agent_must_ask(client):
    """Assignment requirement 1: look the caller up by phone or account number."""
    c = claims_of(client.post("/token/guest").get_json()["token"])

    assert not c.get("attributes"), "a guest must arrive unidentified"
    assert c["sub"].startswith("guest-")
    assert c["roomConfig"]["agents"][0]["agentName"] == "anycompany-agent"


def test_guest_still_gets_the_same_room_bounds(client):
    rc = claims_of(client.post("/token/guest").get_json()["token"])["roomConfig"]
    assert int(rc["emptyTimeout"]) == 120
    assert int(rc["maxParticipants"]) == 3


def test_second_google_account_resolves_to_her_own_home(client, monkeypatch):
    """Identity follows the login: a different Gmail lands on a different customer."""
    signed_in_as(monkeypatch, uid="uid-anam", email="anam.nabil1@gmail.com")
    body = client.get("/me", headers={"Authorization": "Bearer good"}).get_json()

    assert body["first_name"] == "Anam" and body["account"] == "AH-8230"
    assert body["plan"] == "Video Basic"
    assert {d["device"] for d in body["devices"]} == {
        "Aria Doorbell Cam",
        "Aria Thermostat",
        "Aria Smart Lock",
    }
    assert [o["order_id"] for o in body["orders"]] == ["58140", "58139"]


# ---------------------------------------------------- KBA verification endpoint


def test_verify_endpoint_compares_in_code_and_never_leaks():
    c = main.app.test_client()
    hdr = {"X-Api-Key": "test-orders-key"}
    # right email -> verified
    r = c.post(
        "/api/verify",
        json={"account": "AH-4821", "email": " Sarah@Example.com "},
        headers=hdr,
    )
    assert r.get_json() == {"verified": True}
    # right phone tail -> verified
    r = c.post(
        "/api/verify", json={"account": "AH-4821", "phone": "512 555 1188"}, headers=hdr
    )
    assert r.get_json() == {"verified": True}
    # wrong answer -> false, and the response must not contain the real values
    r = c.post(
        "/api/verify", json={"account": "AH-4821", "email": "nope@x.com"}, headers=hdr
    )
    body = r.get_data(as_text=True)
    assert r.get_json() == {"verified": False}
    assert "sarah@example.com" not in body and "1188" not in body
    # unknown account -> false, same shape (no user enumeration)
    r = c.post(
        "/api/verify", json={"account": "AH-0000", "email": "a@b.com"}, headers=hdr
    )
    assert r.get_json() == {"verified": False}
    # short/empty answers never pass
    r = c.post("/api/verify", json={"account": "AH-4821", "phone": "88"}, headers=hdr)
    assert r.get_json() == {"verified": False}
    # no service key -> unauthorized
    r = c.post("/api/verify", json={"account": "AH-4821", "email": "sarah@example.com"})
    assert r.status_code == 401
