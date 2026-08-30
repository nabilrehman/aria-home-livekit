"""Findings from the hiring-manager / LiveKit-specialist review, pinned as tests.

Each test is one finding. If it fails, the demo has the flaw the review found.
Offline — instructions, options and seed data only.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import agent as agent_mod  # noqa: E402
import store  # noqa: E402
from agent import SESSION_OPTIONS, Assistant  # noqa: E402

REAL_TOOLS = {
    # Toolbox (Cloud SQL)
    "lookup_account_by_phone",
    "lookup_account_by_number",
    "list_devices",
    "find_device",
    "file_ticket",
    # plain HTTP function tools in the agent (orders are a REST call, not MCP)
    "get_recent_order",
    "lookup_order",
    # custom MCP (Firestore + RAG)
    "get_device_state",
    "get_device_history",
    "search_knowledge",
}
RETIRED_TOOLS = {"lookup_account", "get_room_temperature"}


# ── Finding 1: the prompt named tools that no longer exist ──────────────────


def test_prompt_names_only_tools_that_exist():
    text = Assistant().instructions
    for name in RETIRED_TOOLS:
        # whole-word: "lookup_account_by_phone" must not count as "lookup_account"
        assert not re.search(rf"\b{name}\b(?!_)", text), (
            f"prompt still references retired tool {name!r}"
        )


def test_prompt_teaches_the_two_step_device_lookup():
    """Device state needs a device_id from the registry first. The prompt must say so."""
    text = Assistant().instructions
    assert "find_device" in text and "get_device_state" in text
    assert "device_id" in text


def test_signed_in_prompt_uses_the_real_lookup_tool():
    text = Assistant(known_account="AH-7104", known_name="Nabil Rehman").instructions
    assert "lookup_account_by_number" in text
    assert "AH-7104" in text
    for name in RETIRED_TOOLS:
        assert not re.search(rf"\b{name}\b(?!_)", text)


# ── Finding 2: the policy corpus says "AnyCompany"; the agent must not ───────


def test_prompt_tells_the_agent_never_to_say_anycompany():
    text = Assistant().instructions
    assert "AnyCompany" in text and "Aria Home" in text
    assert "never say" in text.lower() or "always say aria home" in text.lower()


# ── Finding 3: legacy in-memory tools disagreed with Cloud SQL ──────────────


def test_local_store_knows_every_seeded_order():
    """request_refund / track_package read store.py. It must carry the same orders
    as Cloud SQL, or "track my package" fails for the signed-in demo account."""
    for order_id in ("58120", "58121", "58129", "58130", "58131"):
        assert store.get_order(order_id) is not None, (
            f"store.py missing order {order_id}"
        )


# ── Finding 4: no way to end the call, no idle handling ─────────────────────


def test_agent_can_end_the_call():
    assert hasattr(Assistant, "end_call"), "no end_call tool — 'goodbye' would hang"


def test_session_options_handle_silence_and_false_interruptions():
    """A caller who goes quiet gets checked on; a cough does not derail a sentence."""
    assert SESSION_OPTIONS.get("user_away_timeout"), "no user_away_timeout"
    assert 10 <= SESSION_OPTIONS["user_away_timeout"] <= 30
    th = SESSION_OPTIONS["turn_handling"]  # the 1.7 API: nested, not session-level
    assert th["interruption"]["mode"] == "adaptive"
    assert th["interruption"]["resume_false_interruption"] is True
    assert th["interruption"]["false_interruption_timeout"]
    assert th["preemptive_generation"]["enabled"] is True


def test_session_options_are_what_the_entrypoint_uses():
    """Guards against the options dict drifting from the real AgentSession call."""
    src = Path(agent_mod.__file__).read_text()
    assert "**SESSION_OPTIONS" in src
