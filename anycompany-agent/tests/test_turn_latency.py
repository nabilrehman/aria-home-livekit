"""MetricsReport is a TypedDict. Reading it with getattr() silently yields zeros —
that bug shipped once and printed a 0 ms latency budget. These tests pin the shape.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from turn_latency import TurnLatency

# Field names and owning role come from livekit.agents.llm.chat_context.MetricsReport.
USER_REPORT = {"end_of_turn_delay": 0.312, "transcription_delay": 0.089}
ASSISTANT_REPORT = {
    "llm_node_ttft": 0.288,
    "tts_node_ttfb": 0.141,
    "e2e_latency": 0.741,
}


def test_reads_typed_dict_not_attributes() -> None:
    tl = TurnLatency()
    tl.record(ASSISTANT_REPORT, USER_REPORT)

    assert len(tl._turns) == 1
    t = tl._turns[0]
    assert round(t.ttft_ms) == 288
    assert round(t.ttfb_ms) == 141
    assert round(t.e2e_ms) == 741


def test_eou_comes_from_the_user_turn() -> None:
    """EOU and transcription are reported on the user message, not the reply."""
    tl = TurnLatency()
    tl.record(ASSISTANT_REPORT, USER_REPORT)

    assert round(tl._turns[0].eou_ms) == 312
    assert round(tl._turns[0].transcription_ms) == 89


def test_empty_report_records_nothing() -> None:
    """An interrupted or tool-only reply must not drag the medians to zero."""
    tl = TurnLatency()
    tl.record({}, {})
    tl.record({"llm_node_ttft": 0.0}, {})

    assert tl._turns == []


def test_summary_survives_a_partial_turn() -> None:
    tl = TurnLatency()
    tl.record(ASSISTANT_REPORT, USER_REPORT)
    tl.record({"llm_node_ttft": 0.301, "e2e_latency": 0.688}, {})  # no TTS this turn

    assert len(tl._turns) == 2
    tl.print_summary()  # must not raise on a missing stage
