#!/usr/bin/env python3
"""
watch_room.py — make the room visible.

Polls the LiveKit server API and prints a live event log of what is happening
inside your project: rooms appearing, participants joining and leaving, and the
audio tracks each one publishes.

The point of this script is pedagogical. An SFU and a "room" are abstractions
you cannot see, so this turns them into a stream of lines in your terminal.
Run it in one pane, do something in another, and watch the consequence appear.

Usage:
    python observe/watch_room.py                # watch every room in the project
    python observe/watch_room.py --room my-room # watch one room
    python observe/watch_room.py --interval 0.5 # poll faster

Reads LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET from the environment
or from .env.local in the project root.
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from livekit import api

# .env.local is what `lk agent init` writes, so prefer it, then fall back to .env
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env.local"))
load_dotenv(os.path.join(ROOT, ".env"))

# ---------- terminal colour, kept minimal ----------
DIM = "\033[2m"
BOLD = "\033[1m"
TEAL = "\033[36m"
RUST = "\033[33m"
GREY = "\033[90m"
RED = "\033[31m"
RESET = "\033[0m"


def stamp() -> str:
    return f"{GREY}{datetime.now().strftime('%H:%M:%S.%f')[:-3]}{RESET}"


def log(icon: str, colour: str, message: str) -> None:
    print(f"{stamp()}  {colour}{icon}{RESET}  {message}", flush=True)


def kind_of(identity: str, metadata: str = "") -> str:
    """
    Guess what sort of participant this is, purely from naming convention.

    This is a teaching convenience, not something LiveKit enforces — to the
    server every participant is the same kind of thing, which is exactly the
    point being demonstrated.
    """
    lowered = identity.lower()
    if lowered.startswith("sip_") or "sip" in lowered:
        return "phone caller"
    if "agent" in lowered or lowered.startswith("ag_"):
        return "AI agent"
    if "specialist" in lowered or "human" in lowered:
        return "human specialist"
    return "browser user"


class RoomWatcher:
    """Diffs successive snapshots of the server state and narrates the changes."""

    def __init__(self, room_filter: str | None):
        self.room_filter = room_filter
        # room name -> {participant identity -> set of published track names}
        self.state: dict[str, dict[str, set[str]]] = {}
        self.first_pass = True

    async def snapshot(self, lkapi: api.LiveKitAPI) -> dict[str, dict[str, set[str]]]:
        rooms = await lkapi.room.list_rooms(api.ListRoomsRequest())
        current: dict[str, dict[str, set[str]]] = {}

        for room in rooms.rooms:
            if self.room_filter and room.name != self.room_filter:
                continue
            participants = await lkapi.room.list_participants(
                api.ListParticipantsRequest(room=room.name)
            )
            current[room.name] = {
                p.identity: {t.name or t.sid for t in p.tracks}
                for p in participants.participants
            }
        return current

    def narrate(self, current: dict[str, dict[str, set[str]]]) -> None:
        previous = self.state

        for room_name, participants in current.items():
            if room_name not in previous:
                log("▣", TEAL, f"{BOLD}room opened{RESET}  {room_name}")

            before = previous.get(room_name, {})

            for identity, tracks in participants.items():
                if identity not in before:
                    log(
                        "→",
                        TEAL,
                        f"{BOLD}{identity}{RESET} joined {DIM}{room_name}{RESET}  "
                        f"{GREY}({kind_of(identity)}){RESET}",
                    )
                    self.report_headcount(participants)
                else:
                    new_tracks = tracks - before[identity]
                    for track in new_tracks:
                        log(
                            "♪",
                            TEAL,
                            f"{identity} published a track {GREY}{track}{RESET}",
                        )

            for identity in before:
                if identity not in participants:
                    log("←", RUST, f"{BOLD}{identity}{RESET} left {DIM}{room_name}{RESET}")
                    self.report_headcount(participants)

        for room_name in previous:
            if room_name not in current:
                log("▢", RUST, f"room closed  {room_name}  {GREY}(last participant left){RESET}")

        self.state = current

    def report_headcount(self, participants: dict[str, set[str]]) -> None:
        if not participants:
            return
        names = ", ".join(sorted(participants))
        log("·", GREY, f"{GREY}now in room: {names}{RESET}")

    async def run(self, interval: float) -> None:
        async with api.LiveKitAPI() as lkapi:
            log("✓", TEAL, f"watching {os.environ.get('LIVEKIT_URL', '?')}")
            if self.room_filter:
                log("·", GREY, f"{GREY}filtered to room: {self.room_filter}{RESET}")
            log("·", GREY, f"{GREY}polling every {interval}s — ctrl-c to stop{RESET}")
            print()

            while True:
                try:
                    current = await self.snapshot(lkapi)
                except Exception as exc:  # network blips shouldn't kill the watcher
                    log("!", RED, f"{RED}poll failed: {exc}{RESET}")
                    await asyncio.sleep(interval)
                    continue

                if self.first_pass:
                    if current:
                        log("·", GREY, f"{GREY}already in progress:{RESET}")
                        for room_name, participants in current.items():
                            who = ", ".join(sorted(participants)) or "empty"
                            log("▣", TEAL, f"{room_name}  {GREY}{who}{RESET}")
                    else:
                        log("·", GREY, f"{GREY}no active rooms yet — go start one{RESET}")
                    print()
                    self.state = current
                    self.first_pass = False
                else:
                    self.narrate(current)

                await asyncio.sleep(interval)


def main() -> int:
    parser = argparse.ArgumentParser(description="Watch LiveKit rooms and participants live.")
    parser.add_argument("--room", help="only watch this room")
    parser.add_argument("--interval", type=float, default=1.0, help="poll interval in seconds")
    args = parser.parse_args()

    missing = [
        var
        for var in ("LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET")
        if not os.environ.get(var)
    ]
    if missing:
        print(f"{RED}Missing: {', '.join(missing)}{RESET}", file=sys.stderr)
        print(
            "Run `lk cloud auth`, then `lk agent init`, which writes .env.local "
            "into the project root.",
            file=sys.stderr,
        )
        return 1

    try:
        asyncio.run(RoomWatcher(args.room).run(args.interval))
    except KeyboardInterrupt:
        print(f"\n{GREY}stopped{RESET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
