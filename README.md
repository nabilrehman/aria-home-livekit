# The Observation Lab

A guided way to *see* the architecture you'll be drawing, instead of taking it on
faith. Each experiment makes one invisible thing visible, then tells you what it
proves and what to say about it in the interview.

Companion to the [playbook](https://claude.ai/code/artifact/280e533f-f812-4e14-b135-cf8bb95adba2)
and the [primer](https://claude.ai/code/artifact/eca37b35-b278-4b09-b3ac-4571b3660c64).

---

## Setup

Already done for you:

- `lk` CLI 2.18.2 (Homebrew)
- `.venv/` on Python 3.12 with `livekit-api` 1.2.0
- `observe/watch_room.py` — the room monitor

- `anycompany-agent/` — the agent, on `livekit-agents` 1.7.0, Python pinned to 3.12
- `.env.local` — credentials for project `personal`, in both the root and the agent dir
- `anycompany-agent/src/turn_latency.py` — per-turn latency instrumentation (experiment 5), already wired into `agent.py`

**Everything is set up and smoke-tested.** The worker registers, the observer
connects. Nothing left to configure.

Your agent's pipeline, as generated:

| Stage | Model |
|---|---|
| STT | `assemblyai/universal-3-5-pro` |
| LLM | `google/gemma-4-31b-it` |
| TTS | `fishaudio/s2.1-pro` |
| Turn detection | `inference.TurnDetector()` — audio-based, semantic + acoustic |

It also ships with **adaptive interruptions** (tells a real interruption from an
"mhm") and **preemptive generation** (starts generating before end-of-turn is
confirmed). Both are relevant to experiments 6 and 7 — and worth mentioning in
the interview, because they're the refinements past the textbook answer.

---

## How to run these

Use **two terminal panes side by side**. Left pane is the observer and stays
running the whole time. Right pane is where you do things.

```
┌─────────────────────────┬─────────────────────────┐
│ watch_room.py           │ lk agent dev            │
│ (leave this running)    │ (and everything else)   │
└─────────────────────────┴─────────────────────────┘
```

Almost all the learning is in watching the left pane react to what you do in the
right one.

---

## 1 · The room is real

**Architecture part:** the room — §01 and §06 of the playbook.

Left pane:

```bash
.venv/bin/python observe/watch_room.py
```

Right pane: start the agent and open the console it prints.

```bash
cd anycompany-agent && lk agent dev
```

Use `lk agent dev`, not `uv run src/agent.py dev` — the latter is deprecated in
1.7.0 and has no hot reload.

Click **Start a session** in the browser, and watch the left pane.

**What you should see:** a room open, then a participant join, then a second
participant join a moment later.

**What it proves:** a room isn't a metaphor. It's a server-side object with a
membership list, and it came into existence the moment somebody needed one.
Notice it also *closes* on its own when the last person leaves — rooms are
sessions, not infrastructure you provision.

---

## 2 · The agent is a participant

**Architecture part:** the single most important claim you'll make on the
whiteboard — §02, "the insight that separates candidates."

Look again at the join lines from experiment 1. There are two participants, and
one of them is the agent. Now run:

```bash
lk room list
lk room participants list --room <the-room-name-from-the-watcher>
```

**What you should see:** the AI agent listed exactly like the human — same
structure, same fields, same kind of object. Nothing marks it as special.

**What it proves:** the agent joined the room; the audio was not piped to it by a
backend. This is why handoff, recording and supervision need no new machinery —
they're all just more participants.

> **Say it:** "The AI isn't a service the audio gets piped to — it's a
> participant that joins the room and subscribes to the customer's audio. Which
> is why putting a human into the call later doesn't need a new subsystem."

---

## 3 · Tracks, flowing both ways

**Architecture part:** rooms / participants / tracks — §02.

With a session live, watch the `♪` lines in the observer, then:

```bash
lk room participants list --room <room> --json | grep -iE "track|source|muted"
```

**What you should see:** each participant publishing an audio track, and each
subscribing to the other's.

**What it proves:** media is per-participant and stays separate. That separation
is exactly why an SFU is the right choice and an MCU is not — the AI needs one
speaker's clean audio, not a mix.

---

## 4 · Look at the actual WebRTC connection

**Architecture part:** WebRTC, ICE, the SFU — §02. This is the one that makes
transport stop being abstract.

While a session is live, open a new Chrome tab:

```
chrome://webrtc-internals
```

Find your active connection and look for these five things:

| Look for | What it tells you |
|---|---|
| `ICE candidate pair` — `succeeded` | The path ICE actually chose. `host`/`srflx` means a direct route; `relay` means it fell back to TURN. |
| `currentRoundTripTime` | Your real RTT to the edge. This is the "under 50 ms transport" line in the latency budget, measured. |
| `jitter` | How unevenly packets are arriving. The jitter buffer is absorbing this for you. |
| `packetsLost` | Nonzero is normal and inaudible. This is the whole UDP-over-TCP argument, live. |
| `codec` — `opus` | 48 kHz. Compare later against a phone call at 8 kHz G.711. |

**Then break it deliberately.** Turn off Wi-Fi for two seconds and turn it back
on. Watch `packetsLost` jump and the call recover without falling behind. That is
the difference from TCP, and you'll have seen it rather than read it.

> **Say it:** "Transport is usually under fifty milliseconds to the edge. And
> when the network drops packets, we lose twenty milliseconds of audio nobody
> hears — instead of TCP stopping to retransmit and putting the whole call
> permanently behind."

---

## 5 · Where the second actually goes

**Architecture part:** the latency budget — §03. **This is the highest-value
experiment in the lab.**

**This is already wired up.** `src/turn_latency.py` is attached to the session,
so you don't need to do anything but talk. Every time the agent replies you get:

```
turn 3   EOU  312ms │ TTFT  288ms │ TTFB  141ms │ ≈ 741ms  ▏▏▏▏▏▏▏░░░  good
```

Have a twenty-turn conversation, then stop the agent with `ctrl-c`. It prints a
summary table on shutdown:

```
  Your latency budget
  20 complete turns

  Stage             Published     Yours (median)
  ----------------------------------------------
  End-of-turn       ~300 ms          312 ms
  LLM first token   200-400 ms       288 ms
  TTS first audio   100-300 ms       141 ms
  ----------------------------------------------
  Total             < 1000 ms        741 ms   (p95 934 ms)
```

Write those numbers down. Transport isn't in the table — read it off
`chrome://webrtc-internals` as `currentRoundTripTime` from experiment 4 and add
it yourself.

One thing to watch for: your agent has **preemptive generation** enabled, which
starts the LLM before end-of-turn is confirmed. So the real perceived latency can
be *better* than EOU + TTFT + TTFB suggests, because those stages overlap. If
your measured total feels lower than the arithmetic, that's why — and it's a good
detail to raise unprompted.

**What it proves:** you can quote your own numbers. "When I built this, my
end-of-turn sat around 340 ms and first token was what surprised me" is a
completely different sentence from reciting a docs table, and nobody can fake it.

---

## 6 · Make it interrupt you

**Architecture part:** turn detection — §04.

Say, out loud, with a real pause in the middle:

> "My order number is… uh… four four seven two one."

**What you should see:** with a good turn detector it waits. Now shorten the
endpointing threshold in the agent config and try again — it will cut you off
after "is," and answer a question you never finished asking.

**What it proves:** the trade-off is real and it has no solution, only a curve.
You'll have personally experienced the failure mode you're describing.

> **Say it:** "VAD alone cuts people off, because a pause while you're
> remembering your order number looks exactly like being finished. There's no
> setting that removes that trade-off — you tune it per use case, depending on
> whether your customers are reading out account numbers or saying yes and no."

---

## 7 · Barge-in

**Architecture part:** turn detection, the other half — §04.

Let the agent start a long answer, then talk over it.

**What you should see:** it stops almost immediately. Then check whether it
*knows* it was cut off — ask "what did you just say?" A good implementation
truncated its own conversation history at the interruption point. A naive one
will reference the whole reply you never heard.

**What it proves:** barge-in is three jobs, not one — stop playback, discard the
rest, and correct the transcript. The third is the one people skip.

---

## 8 · Watch a handoff happen

**Architecture part:** human handoff — §07. The payoff of experiment 2.

With a session live, open the same room in a **second browser window** as a
different identity.

**What you should see:** the observer prints a third join, and the room now holds
three participants — customer, agent, specialist.

**What it proves:** escalation is an arrival, not a transfer. Nothing was routed
anywhere; a third participant simply appeared in a conversation already in
progress, with the whole history intact.

> **Say it:** "When it can't resolve, a specialist joins this same room. They
> arrive already briefed, so the customer doesn't repeat themselves — that's
> really the whole point."

---

## 9 · Break it on purpose

**Architecture part:** reliability — §08. Do this one last.

With a live call, kill the agent process in the right pane (`ctrl-c`).

**What you should see:** the observer prints the agent leaving. In the browser,
you're still connected — the room is fine, your audio still flows. There's just
nobody listening.

**What it proves:** the failure is scoped to the agent, not the session. That's
process isolation, and it's why "a worker crashed" degrades one call rather than
dropping it. Restart the agent and watch it rejoin.

> **Say it:** "If a worker dies it's process-isolated, so it only affects that one
> call, and it's replaced in about fifteen seconds. I'd be honest that the call in
> progress is degraded — that's the one I'd design around rather than paper over."

---

## Later: the phone

Experiment 10 is telephony — buy a number, configure an inbound trunk and a
dispatch rule, then call your own agent. It costs a few dollars and it's the best
money in this lab, because SIP stops being abstract the instant your phone rings
and the observer prints a `sip_` participant joining the same room as everything
else.

Ask me when you're ready and I'll walk it through.

---

## Files

```
.venv/                    Python 3.12 + livekit-api
observe/watch_room.py     live room + participant + track monitor
anycompany-agent/         created by `lk agent init` (after you auth)
.env.local                your project credentials (never commit)
```

## Troubleshooting

**`Missing: LIVEKIT_URL...`** — you haven't copied `.env.local` to the project
root yet. It's written by `lk agent init` into the agent directory.

**Watcher shows nothing while a session is live** — check you're on the right
project with `lk project list`. The watcher reads whichever credentials are in
`.env.local`.

**Agent won't start on Python 3.14** — it shouldn't; `uv` pins 3.12 for this
project. If `uv sync` picked something else, `uv python pin 3.12` in the agent
directory and re-sync.
