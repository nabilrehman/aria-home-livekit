#!/usr/bin/env python3
"""
protocol_probe.py — watch the room from inside it, at the protocol level.

watch_room.py polls the REST API and tells you what the room looks like *now*.
This is different: it joins the room as a real participant over the signaling
WebSocket, and prints every push event the SFU sends it, as it arrives.

That distinction is the point. Polling shows you state. This shows you the
protocol — the SFU actively telling every participant "somebody joined",
"a track was published", "here is the new membership list". It is the same
channel your browser and the agent are on.

The probe joins `hidden: true`, so nobody else in the room can see it and the
agent will not try to talk to it. You are observing without perturbing.

Usage:
    python observe/protocol_probe.py --room my-room
    python observe/protocol_probe.py --room my-room --subscribe   # also pull audio

Reads LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET from .env.local.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from livekit import api, rtc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env.local"))
load_dotenv(os.path.join(ROOT, ".env"))

BOLD = "\033[1m"
DIM = "\033[2m"
TEAL = "\033[36m"
RUST = "\033[33m"
GREY = "\033[90m"
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"

# Participant kinds, as the protocol defines them. This enum is the closest the
# system comes to admitting that participants differ at all — and note that an
# agent is a *kind*, not a different class of object.
KIND_NAMES = {
    0: "STANDARD",
    1: "INGRESS",
    2: "EGRESS",
    3: "SIP",
    4: "AGENT",
}

SOURCE_NAMES = {
    0: "UNKNOWN",
    1: "CAMERA",
    2: "MICROPHONE",
    3: "SCREENSHARE",
    4: "SCREENSHARE_AUDIO",
}


def ts() -> str:
    return f"{GREY}{datetime.now().strftime('%H:%M:%S.%f')[:-3]}{RESET}"


def ev(name: str, colour: str = TEAL) -> str:
    """Left-aligned event name, so the log reads as a protocol trace."""
    return f"{colour}{name:<28}{RESET}"


def emit(name: str, detail: str, colour: str = TEAL) -> None:
    print(f"{ts()}  {ev(name, colour)} {detail}", flush=True)


def kind_of(p) -> str:
    raw = int(getattr(p, "kind", 0) or 0)
    return KIND_NAMES.get(raw, f"KIND_{raw}")


def describe_participant(p, indent: str = "") -> str:
    kind = kind_of(p)
    colour = RUST if kind == "AGENT" else TEAL if kind == "SIP" else ""
    return (
        f"{indent}{BOLD}{p.identity}{RESET}\n"
        f"{indent}  {GREY}sid{RESET}         {p.sid}\n"
        f"{indent}  {GREY}kind{RESET}        {colour}{kind}{RESET}\n"
        f"{indent}  {GREY}name{RESET}        {p.name or GREY + '(none)' + RESET}\n"
        f"{indent}  {GREY}state{RESET}       {p.state}\n"
        f"{indent}  {GREY}metadata{RESET}    {p.metadata or GREY + '(empty)' + RESET}"
    )


def describe_publication(pub) -> str:
    source = SOURCE_NAMES.get(int(getattr(pub, "source", 0) or 0), "?")
    return (
        f"{GREY}track sid{RESET} {pub.sid}  "
        f"{GREY}kind{RESET} {pub.kind}  "
        f"{GREY}source{RESET} {source}  "
        f"{GREY}mime{RESET} {pub.mime_type or '?'}  "
        f"{GREY}muted{RESET} {pub.muted}"
    )


class Probe:
    def __init__(self, room_name: str, subscribe: bool) -> None:
        self.room_name = room_name
        self.subscribe = subscribe
        self.room = rtc.Room()
        self._wire()

    # ---------- token ----------

    def token(self) -> str:
        grants = api.VideoGrants(
            room_join=True,
            room=self.room_name,
            can_subscribe=self.subscribe,
            can_publish=False,
            can_publish_data=False,
            # Invisible to everyone else — observe without being observed.
            hidden=True,
        )
        return (
            api.AccessToken()
            .with_identity("protocol-probe")
            .with_name("protocol probe")
            .with_grants(grants)
            .to_jwt()
        )

    # ---------- event wiring ----------

    def _wire(self) -> None:
        room = self.room

        @room.on("connected")
        def _connected():
            emit("connected", "signaling channel established", GREEN)

        @room.on("connection_state_changed")
        def _state(state):
            emit("connection_state_changed", f"{state}", GREY)

        @room.on("participant_connected")
        def _joined(p: rtc.RemoteParticipant):
            kind = kind_of(p)
            colour = RUST if kind == "AGENT" else TEAL
            emit("participant_connected", "", colour)
            print(describe_participant(p, indent="    "), flush=True)
            if kind == "AGENT":
                print(
                    f"    {RUST}↑ this is the AI. Same message type, same fields,"
                    f" same room as a human.{RESET}",
                    flush=True,
                )
            self.headcount()

        @room.on("participant_disconnected")
        def _left(p: rtc.RemoteParticipant):
            emit("participant_disconnected", f"{BOLD}{p.identity}{RESET} ({kind_of(p)})", RUST)
            self.headcount()

        @room.on("track_published")
        def _published(pub, p):
            emit("track_published", f"{BOLD}{p.identity}{RESET}  {describe_publication(pub)}")

        @room.on("track_unpublished")
        def _unpublished(pub, p):
            emit("track_unpublished", f"{p.identity}  {GREY}{pub.sid}{RESET}", RUST)

        @room.on("track_subscribed")
        def _subscribed(track, pub, p):
            emit("track_subscribed", f"{p.identity}  {GREY}now receiving media{RESET}", GREEN)

        @room.on("track_muted")
        def _muted(p, pub):
            emit("track_muted", f"{BOLD}{p.identity}{RESET}  {GREY}{pub.sid}{RESET}", RUST)

        @room.on("track_unmuted")
        def _unmuted(p, pub):
            emit("track_unmuted", f"{BOLD}{p.identity}{RESET}  {GREY}{pub.sid}{RESET}")

        @room.on("active_speakers_changed")
        def _speakers(speakers):
            names = ", ".join(s.identity for s in speakers) or GREY + "silence" + RESET
            emit("active_speakers_changed", names, GREY)

        @room.on("connection_quality_changed")
        def _quality(p, quality):
            emit("connection_quality_changed", f"{p.identity}  {quality}", GREY)

        @room.on("participant_attributes_changed")
        def _attrs(changed, p):
            emit("participant_attributes_changed", f"{p.identity}  {changed}", GREY)

        @room.on("transcription_received")
        def _transcript(segments, p, pub):
            for seg in segments:
                if seg.final:
                    who = p.identity if p else "?"
                    emit("transcription_received", f"{who}: {BOLD}{seg.text}{RESET}", GREY)

        @room.on("data_received")
        def _data(packet):
            emit("data_received", f"{len(packet.data)} bytes from {packet.participant.identity if packet.participant else '?'}", GREY)

        @room.on("sip_dtmf_received")
        def _dtmf(dtmf):
            emit("sip_dtmf_received", f"digit {BOLD}{dtmf.digit}{RESET}", RUST)

        @room.on("disconnected")
        def _disconnected(reason=None):
            emit("disconnected", f"{reason}", RUST)

        @room.on("reconnecting")
        def _reconnecting():
            emit("reconnecting", "lost the signaling channel", RUST)

        @room.on("reconnected")
        def _reconnected():
            emit("reconnected", "signaling channel restored", GREEN)

    # ---------- helpers ----------

    def headcount(self) -> None:
        people = list(self.room.remote_participants.values())
        if not people:
            print(f"    {GREY}room is now empty{RESET}", flush=True)
            return
        summary = ", ".join(f"{p.identity}[{kind_of(p)}]" for p in people)
        print(f"    {GREY}membership: {summary}{RESET}", flush=True)

    def dump_join_state(self) -> None:
        """
        What the server told us the moment we joined.

        This is the JoinResponse: the room, our own identity within it, and the
        full existing membership. Everything after this arrives as an incremental
        update — which is exactly how the SFU keeps every participant's view of
        the room consistent.
        """
        room = self.room
        print(f"\n{BOLD}  ── join response ──{RESET}", flush=True)
        print(f"  {GREY}room name{RESET}   {room.name}", flush=True)
        print(f"  {GREY}room sid{RESET}    {room.sid if isinstance(room.sid, str) else '(async)'}", flush=True)
        lp = room.local_participant
        print(f"  {GREY}you{RESET}         {lp.identity}  {GREY}sid{RESET} {lp.sid}", flush=True)

        people = list(room.remote_participants.values())
        print(f"\n  {GREY}already here: {len(people)}{RESET}", flush=True)
        for p in people:
            print(describe_participant(p, indent="    "), flush=True)
            for pub in p.track_publications.values():
                print(f"      {describe_publication(pub)}", flush=True)
        print(flush=True)

    async def run(self) -> None:
        url = os.environ["LIVEKIT_URL"]
        emit("connecting", f"{url}  room={BOLD}{self.room_name}{RESET}", GREY)

        await self.room.connect(url, self.token(), options=rtc.RoomOptions(auto_subscribe=self.subscribe))
        self.dump_join_state()
        print(f"{GREY}  watching for protocol events — ctrl-c to stop{RESET}\n", flush=True)

        # Room sid resolves asynchronously; fetch it once for completeness.
        try:
            sid = await self.room.sid
            print(f"{ts()}  {ev('room_sid_resolved', GREY)} {sid}\n", flush=True)
        except Exception:
            pass

        while True:
            await asyncio.sleep(3600)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Join a LiveKit room as a hidden observer and print protocol events."
    )
    parser.add_argument("--room", required=True, help="room name to join")
    parser.add_argument(
        "--subscribe",
        action="store_true",
        help="also subscribe to audio tracks (off by default to stay light)",
    )
    args = parser.parse_args()

    missing = [
        v
        for v in ("LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET")
        if not os.environ.get(v)
    ]
    if missing:
        print(f"{RED}Missing: {', '.join(missing)}{RESET}", file=sys.stderr)
        return 1

    probe = Probe(args.room, args.subscribe)
    try:
        asyncio.run(probe.run())
    except KeyboardInterrupt:
        print(f"\n{GREY}stopped{RESET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
