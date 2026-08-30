"""Findings from the hiring-manager / LiveKit-specialist review, pinned as tests.

Each test is one finding. If it fails, the demo has the flaw the review found.
Offline — instructions, options and seed data only.
"""

import re

import pytest
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
    "my_devices",
    "find_my_device",
    "my_recent_order",
    "my_order",
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
    assert "find_my_device" in text and "my_devices" in text


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


# ── Findings from the live call review (30 Aug) ─────────────────────────────


def test_empty_mcp_result_becomes_a_spoken_not_found():
    """A SQL query matching nothing is an answer, not a ToolError to retry on."""
    import json
    from types import SimpleNamespace

    from agent import _mcp_result

    out = json.loads(_mcp_result(SimpleNamespace(result=SimpleNamespace(content=[]))))
    assert out["found"] is False and "say" in out


@pytest.mark.asyncio
async def test_end_call_is_refused_once_a_specialist_has_the_call():
    a = Assistant()
    a._handed_off = True
    out = await a.end_call(None)
    assert out["ok"] is False and "specialist" in out["say"].lower()


def test_prompt_fetches_devices_once_and_rags_once():
    text = Assistant().instructions
    assert "scoped to" in text and "them automatically" in text
    assert "call it once per question" in text
    assert "Never end the call after a transfer" in text


def test_tool_step_budget_covers_the_device_chain():
    """identify → list_devices → find_device → get_device_state = 4 steps."""
    src = Path(agent_mod.__file__).read_text()
    m = re.search(r"max_tool_steps=(\d+)", src)
    assert m and int(m.group(1)) >= 4


def test_agent_exposes_at_most_the_documented_tool_budget():
    """LiveKit guidance: aim for 5-10 tools; beyond ~13 selection degrades."""
    src = Path(agent_mod.__file__).read_text()
    local_tools = src.count("@function_tool")
    toolbox = src[
        src.index("allowed_tools=[") : src.index("]", src.index("allowed_tools=["))
    ].count('"')
    mcp_custom = 3  # get_device_state, get_device_history, search_knowledge
    total = local_tools + toolbox // 2 + mcp_custom
    assert total <= 16, f"{total} tools exposed — trim or split agents"
