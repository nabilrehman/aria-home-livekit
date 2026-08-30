import json as _json
import logging
import os
import urllib.request
from datetime import datetime, timezone

import google.auth
import google.auth.transport.requests
from mcp.server.fastmcp import FastMCP

from data import DataUnavailable, repo

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("aug24-mcp")

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]  # used by the RAG call below

mcp = FastMCP("aria-home-crm")
mcp.settings.host = "0.0.0.0"
mcp.settings.port = int(os.environ.get("PORT", 8080))

# =====================================================================
# Aria Home device cloud + policy knowledge.
#
# This server owns the NON-relational half only:
#   Firestore   — live device telemetry, keyed by device_id
#   Vertex RAG  — the returns/warranty policy corpus
#
# Everything relational — who is calling, what they own, what they bought —
# is served by Google's MCP Toolbox for Databases straight from Cloud SQL
# (see ../aria-toolbox/tools.yaml). The agent attaches both servers.
#
# The two halves join on device_id: Toolbox's find_device returns it from the
# Postgres registry, get_device_state below reads Firestore with it.
# =====================================================================


def _stamp(state: dict) -> str:
    """When the device last reported, said the way a person would say it."""
    when = state.get("reported_at")
    if not hasattr(when, "strftime"):
        return "just now"
    age = (datetime.now(timezone.utc) - when).total_seconds()
    if age < 90:
        return "just now"
    if age < 5400:
        return f"about {max(1, round(age / 60))} minutes ago"
    return f"about {max(1, round(age / 3600))} hours ago"


@mcp.tool()
def get_device_state(device_id: str) -> dict:
    """Read what one device is reporting RIGHT NOW.

    Use this for "is my thermostat on?", "is the front door locked?", "is the
    camera recording?". This is live telemetry, never cached.

    You need the device_id first: call find_device (or list_devices) to turn what
    the customer said — a room, a device type — into a device_id, then pass it here.

    Args:
        device_id: from find_device or list_devices, e.g. "AH4821-D1".
    """
    try:
        state = repo.device_state(device_id)
    except DataUnavailable as err:
        log.error(f"TOOL get_device_state({device_id}) -> STORE DOWN: {err}")
        return {
            "found": False,
            "error": "telemetry_unavailable",
            "say": "Tell them the device cloud is not reachable right now. "
            "Do not guess whether the device is on.",
        }

    if not state:
        log.info(f"TOOL get_device_state({device_id}) -> never reported")
        return {
            "found": False,
            "reported": False,
            "say": "That device has not reported in. Say so plainly and offer "
            "to have someone look into it.",
        }

    log.info(f"TOOL get_device_state({device_id}) -> {state.get('reading')}")
    return {
        "found": True,
        "reported": True,
        "device_id": device_id,
        "active": state.get("active"),
        "reading": state.get("reading"),
        "temperature_f": state.get("temp_f"),
        "mode": state.get("mode"),
        "battery_pct": state.get("battery_pct"),
        "bolt": state.get("bolt"),
        "as_of": _stamp(state),
        "source": "Aria Home device cloud · Firestore via MCP",
    }


@mcp.tool()
def get_device_history(device_id: str, limit: int = 10) -> dict:
    """Recent readings from one device, newest first.

    Only for questions about the PAST — "has the garage camera been offline all
    day?", "when did it last report?". For the current value use get_device_state.

    Args:
        device_id: from find_device or list_devices.
        limit: how many readings to return, at most 20.
    """
    try:
        history = repo.device_history(device_id, limit=min(max(limit, 1), 20))
    except DataUnavailable as err:
        log.error(f"TOOL get_device_history({device_id}) -> STORE DOWN: {err}")
        return {
            "found": False,
            "error": "telemetry_unavailable",
            "say": "Tell them the device history is not reachable right now.",
        }

    log.info(f"TOOL get_device_history({device_id}) -> {len(history)} readings")
    return {
        "found": True,
        "device_id": device_id,
        "readings": [
            {
                "reading": h.get("reading"),
                "active": h.get("active"),
                "at": str(h.get("reported_at")),
            }
            for h in history
        ],
        "source": "Aria Home device cloud · Firestore via MCP",
    }


RAG_REGION = "europe-west3"
RAG_CORPUS = f"projects/{PROJECT}/locations/{RAG_REGION}/ragCorpora/2305843009213693952"


@mcp.tool()
def get_previous_calls(account_number: str) -> dict:
    """What this customer called about before — their last few calls, newest first.

    Call this right after you identify a caller. If the most recent call is
    recent and relevant, acknowledge it in one natural sentence ("last time you
    called about the doorbell order — did that arrive?"). Never recite the list.

    Args:
        account_number: their Aria Home account number, e.g. "AH-4821".
    """
    try:
        calls = repo.recent_calls(account_number.strip().upper(), limit=3)
    except DataUnavailable as err:
        log.error(f"TOOL get_previous_calls -> STORE DOWN: {err}")
        return {"found": False, "error": "history_unavailable",
                "say": "Carry on without history; do not mention it."}
    log.info(f"TOOL get_previous_calls({account_number}) -> {len(calls)} calls")
    if not calls:
        return {"found": False, "say": "This is their first call. Do not mention history."}
    return {"found": True, "calls": calls, "source": "Aria Home call history · Firestore via MCP"}


@mcp.tool()
def remember(account_number: str, fact: str) -> dict:
    """Store something the customer asked you to remember, for future calls.

    Use when they say "remember that…", state a preference ("text me, don't
    call"), or tell you something lasting about their home ("the back door lock
    sticks"). Write the fact as one plain sentence in the third person.

    Args:
        account_number: their Aria Home account number.
        fact: one sentence, e.g. "Prefers to be contacted by text message."
    """
    try:
        repo.remember(account_number.strip().upper(), fact.strip())
    except DataUnavailable as err:
        log.error(f"TOOL remember -> STORE DOWN: {err}")
        return {"ok": False, "say": "Tell them you could not save that just now."}
    log.info(f"TOOL remember({account_number}) -> {fact[:60]}")
    return {"ok": True, "say": "Confirm in a few words that you will remember it."}


@mcp.tool()
def recall(account_number: str, question: str) -> dict:
    """Look up what you know about this customer from previous calls.

    Facts from earlier calls are usually already in your context; use this when
    they ask something like "what did I tell you last time?" or "do you have my
    preferences?" and the answer is not in front of you.

    Args:
        account_number: their Aria Home account number.
        question: what you are trying to find out, in plain words.
    """
    try:
        facts = repo.memories(account_number.strip().upper(), query=question, top_k=5)
    except DataUnavailable as err:
        log.error(f"TOOL recall -> STORE DOWN: {err}")
        return {"found": False, "say": "Say you do not have that on file."}
    log.info(f"TOOL recall({account_number}) -> {len(facts)} facts")
    if not facts:
        return {"found": False, "say": "Nothing on file about that."}
    return {"found": True, "facts": facts, "source": "Vertex AI Memory Bank"}


@mcp.tool()
def search_knowledge(question: str) -> dict:
    """Search Aria Home's policy knowledge base to answer a customer question.

    Use this for ANY policy question: return windows, refund timing, warranty
    coverage, damaged or defective items, subscription terms, who pays return
    shipping. Do not guess policy — always search.

    Args:
        question: the customer's policy question, in their own words.
    """
    log.info(f"TOOL search_knowledge({question!r}) -> RAG")
    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())
    body = _json.dumps(
        {
            "vertex_rag_store": {"rag_resources": {"rag_corpus": RAG_CORPUS}},
            "query": {"text": question, "rag_retrieval_config": {"top_k": 3}},
        }
    ).encode()
    req = urllib.request.Request(
        f"https://{RAG_REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{RAG_REGION}:retrieveContexts",
        data=body,
        headers={
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json",
        },
    )
    data = _json.load(urllib.request.urlopen(req))
    ctx = data.get("contexts", {}).get("contexts", [])
    passages = [c.get("text", "")[:400] for c in ctx[:3]]
    log.info(f"RAG retrieved {len(passages)} passages from Vertex corpus")
    return {
        "found": bool(passages),
        "passages": passages,
        "source": "GCP Vertex AI RAG Engine",
        "say": "Answer using ONLY these passages. If they do not cover it, say you will check.",
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
