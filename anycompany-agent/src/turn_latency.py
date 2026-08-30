"""
turn_latency.py — print the one-second budget, per turn, as it happens.

Experiment 5 of the observation lab.

Every time the agent finishes a reply, LiveKit attaches a MetricsReport to the
assistant's ChatMessage. That report already contains the whole per-turn
breakdown, including a real measured end-to-end number — so there's nothing to
correlate or reassemble, just read and print.

    turn 3   EOU  312ms │ TTFT  288ms │ TTFB  141ms │ e2e  741ms  ▏▏▏▏▏▏▏░░░  good

At shutdown it prints a median summary against the published budget.

Usage, inside your entrypoint after creating the session:

    from turn_latency import TurnLatency
    TurnLatency().attach(session, ctx)
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

from livekit.agents import ConversationItemAddedEvent, JobContext

GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
GREY = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"


@dataclass
class Turn:
    """One agent reply, as measured by LiveKit itself."""

    eou_ms: float
    ttft_ms: float
    ttfb_ms: float
    e2e_ms: float
    transcription_ms: float


def _ms(value: float | None) -> float:
    """Reports are in seconds; None means the stage didn't run this turn."""
    return (value or 0.0) * 1000


def _bar(total_ms: float, width: int = 10, ceiling_ms: float = 1000.0) -> str:
    filled = min(width, max(0, round(total_ms / ceiling_ms * width)))
    return "▏" * filled + "░" * (width - filled)


def _verdict(total_ms: float) -> str:
    if total_ms < 800:
        return f"{GREEN}good{RESET}"
    if total_ms < 1000:
        return f"{YELLOW}ok{RESET}"
    return f"{RED}slow{RESET}"


class TurnLatency:
    def __init__(self) -> None:
        self._turns: list[Turn] = []
        # EOU and transcription are reported on the *user* message, TTFT/TTFB/e2e on the
        # assistant reply that follows it — so we hold the user half until the pair lands.
        self._pending_user: dict = {}

    # ---------- wiring ----------

    def attach(self, session, ctx: JobContext) -> None:
        @session.on("conversation_item_added")
        def _on_item(ev: ConversationItemAddedEvent) -> None:
            item = ev.item
            role = getattr(item, "role", None)
            # MetricsReport is a TypedDict, not an object — read it with .get(), never
            # getattr(), which silently returns None for every field and prints 0 ms.
            report = getattr(item, "metrics", None) or {}
            if role == "user":
                self._pending_user = report
                return
            if role != "assistant":
                return
            self.record(report, self._pending_user)
            self._pending_user = {}

        async def _summary() -> None:
            self.print_summary()

        ctx.add_shutdown_callback(_summary)

    # ---------- collection ----------

    def record(self, report, user_report=None) -> None:
        user_report = user_report or {}
        turn = Turn(
            eou_ms=_ms(user_report.get("end_of_turn_delay")),
            ttft_ms=_ms(report.get("llm_node_ttft")),
            ttfb_ms=_ms(report.get("tts_node_ttfb")),
            e2e_ms=_ms(report.get("e2e_latency")),
            transcription_ms=_ms(user_report.get("transcription_delay")),
        )
        # An interrupted or tool-only reply reports nothing; recording it would drag
        # every median toward zero.
        if not (turn.ttft_ms or turn.ttfb_ms or turn.e2e_ms):
            return
        self._turns.append(turn)
        self._print(turn, len(self._turns))

    # ---------- output ----------

    def _print(self, t: Turn, n: int) -> None:
        total = t.e2e_ms or (t.eou_ms + t.ttft_ms + t.ttfb_ms)
        print(
            f"{CYAN}turn {n:<3}{RESET} "
            f"EOU {t.eou_ms:>5.0f}ms {GREY}│{RESET} "
            f"TTFT {t.ttft_ms:>5.0f}ms {GREY}│{RESET} "
            f"TTFB {t.ttfb_ms:>5.0f}ms {GREY}│{RESET} "
            f"e2e {total:>5.0f}ms  {_bar(total)}  {_verdict(total)}",
            flush=True,
        )

    def print_summary(self) -> None:
        if not self._turns:
            print(f"\n{GREY}no turns recorded{RESET}\n", flush=True)
            return

        def med(vals: list[float]) -> float:
            vals = [v for v in vals if v > 0]
            return statistics.median(vals) if vals else 0.0

        eou = med([t.eou_ms for t in self._turns])
        ttft = med([t.ttft_ms for t in self._turns])
        ttfb = med([t.ttfb_ms for t in self._turns])
        e2e_vals = [t.e2e_ms for t in self._turns if t.e2e_ms > 0]
        e2e = med([t.e2e_ms for t in self._turns])

        print(f"\n{BOLD}  Your latency budget{RESET}", flush=True)
        print(f"  {GREY}{len(self._turns)} turns{RESET}\n", flush=True)
        print(f"  {'Stage':<20}{'Published':<15}{'Yours (median)'}", flush=True)
        print(f"  {'-' * 52}", flush=True)
        for name, published, value in (
            ("End-of-turn", "~300 ms", eou),
            ("LLM first token", "200-400 ms", ttft),
            ("TTS first audio", "100-300 ms", ttfb),
        ):
            print(f"  {name:<20}{published:<15}{value:>6.0f} ms", flush=True)
        print(f"  {'-' * 52}", flush=True)

        p95 = ""
        if len(e2e_vals) >= 3:
            p95_val = sorted(e2e_vals)[max(0, int(len(e2e_vals) * 0.95) - 1)]
            p95 = f"   {GREY}(p95 {p95_val:.0f} ms){RESET}"
        print(f"  {'End to end':<20}{'< 1000 ms':<15}{e2e:>6.0f} ms{p95}", flush=True)

        print(
            f"\n  {GREY}e2e is measured by LiveKit, not summed — with preemptive"
            f"\n  generation the stages overlap, so it can be lower than the parts."
            f"\n  Transport (<50ms) isn't here: read currentRoundTripTime from"
            f"\n  chrome://webrtc-internals and add it yourself.{RESET}\n",
            flush=True,
        )
