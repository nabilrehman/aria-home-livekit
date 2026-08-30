"""
sim_refund.py — run the refund conversation without a microphone, twice.

Drives the agent through LiveKit's own testing harness (`session.run(...)`),
once with the blocking refund and once with progress updates, and prints a
timeline of both so you can see where the silence is.

There is no audio here — the harness runs the same agent, the same tools and
the same LLM, just with text in place of speech. So the *shape* of the
conversation is real even though the voice isn't.

Run:
    uv run python sim_refund.py
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from dataclasses import dataclass

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

TEAL = "\033[36m"
RUST = "\033[33m"
GREY = "\033[90m"
RED = "\033[31m"
GREEN = "\033[32m"
BOLD = "\033[1m"
RESET = "\033[0m"


@dataclass
class Beat:
    at: float           # seconds since the request
    kind: str           # "agent" | "tool" | "tool-done"
    text: str


async def simulate(mode: str) -> list[Beat]:
    """Run one refund request end to end and record when things happened."""
    os.environ["REFUND_MODE"] = mode

    # Import late, and fresh, so the module-level REFUND_MODE is re-read.
    for m in ("agent", "store"):
        sys.modules.pop(m, None)
    from livekit.agents import AgentSession  # noqa: PLC0415
    from agent import Assistant  # noqa: PLC0415

    beats: list[Beat] = []
    started = time.monotonic()

    async with AgentSession() as session:
        @session.on("conversation_item_added")
        def _on_item(ev) -> None:
            item = ev.item
            if getattr(item, "role", None) != "assistant":
                return
            text = getattr(item, "text_content", None) or str(getattr(item, "content", ""))
            text = " ".join(str(text).split())
            if text:
                beats.append(Beat(time.monotonic() - started, "agent", text))

        @session.on("function_tools_executed")
        def _on_tools(ev) -> None:
            for call in getattr(ev, "function_calls", []) or []:
                beats.append(
                    Beat(time.monotonic() - started, "tool", f"{call.name}({call.arguments})")
                )

        await session.start(Assistant())

        # Turn 1: ask. The agent is instructed to confirm the number first,
        # so this alone never reaches the tool.
        await session.run(user_input="I want a refund on order four four seven two one.")

        # Turn 2: confirm. This is the turn that actually runs the refund, so
        # the clock starts here.
        started = time.monotonic()
        beats.clear()
        await session.run(user_input="Yes, that is correct. Please go ahead.")

        # An async tool hands the turn back immediately, so its progress
        # updates land *after* run() returns. Wait them out.
        await asyncio.sleep(9)

    return beats


def render(mode: str, beats: list[Beat]) -> float:
    """Print the timeline and return the longest silent gap."""
    label = "BLOCKING — no progress updates" if mode == "blocking" else "ASYNC — update() + with_filler()"
    colour = RED if mode == "blocking" else GREEN
    print(f"\n{colour}{BOLD}  {label}{RESET}")
    print(f"  {GREY}{'─' * 66}{RESET}")

    if not beats:
        print(f"  {GREY}(nothing recorded){RESET}")
        return 0.0

    worst = 0.0
    previous = 0.0  # last moment the caller heard something
    for b in beats:
        gap = b.at - previous
        if b.kind == "agent" and gap > worst:
            worst = gap

        marker = f"{TEAL}◆{RESET}" if b.kind == "agent" else f"{GREY}·{RESET}"
        gap_note = ""
        if b.kind == "agent" and gap >= 1.0:
            gc = RED if gap >= 3 else RUST
            gap_note = f"  {gc}({gap:.1f}s of silence before this){RESET}"

        text = b.text if len(b.text) <= 78 else b.text[:75] + "…"
        print(f"  {GREY}{b.at:5.1f}s{RESET} {marker} {text}{gap_note}")
        # A tool call makes no sound, so it does not break the silence.
        if b.kind == "agent":
            previous = b.at

    print(f"  {GREY}{'─' * 66}{RESET}")
    verdict = f"{RED}unacceptable on a phone call{RESET}" if worst >= 3 else f"{GREEN}fine{RESET}"
    print(f"  longest silence: {BOLD}{worst:.1f}s{RESET}  →  {verdict}")
    return worst


async def main() -> None:
    print(f"\n{BOLD}Refund simulation — same agent, same tools, no microphone{RESET}")
    print(f"{GREY}The fake backend takes 6.2s: eligibility 1.6 + processor 3.2 + ledger 1.4{RESET}")

    results: dict[str, float] = {}
    for mode in ("blocking", "async"):
        beats = await simulate(mode)
        results[mode] = render(mode, beats)

    print(f"\n{BOLD}  Verdict{RESET}")
    print(f"  {GREY}{'─' * 66}{RESET}")
    print(f"  blocking   longest silence  {RED}{results['blocking']:.1f}s{RESET}")
    print(f"  async      longest silence  {GREEN}{results['async']:.1f}s{RESET}")
    saved = results["blocking"] - results["async"]
    print(f"\n  {BOLD}{saved:.1f} seconds{RESET} of dead air removed — same 6.2s of backend work.\n")


if __name__ == "__main__":
    asyncio.run(main())
