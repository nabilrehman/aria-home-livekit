# Designer brief — Aria Home end-to-end architecture (one slide)

One horizontal diagram, three zones left → right. Clean enterprise style,
generous whitespace, every arrow labeled. LiveKit purple for the realtime
zone, Google Cloud green/blue for the right zone, neutral for callers.

## Zone 1 — LEFT: "Callers" (three entry points, stacked)

1. **Web app — signed in** (person icon + phone/laptop): "Firebase login →
   account rides the call token". Arrow into the LiveKit room labeled
   *"joins room (token carries account)"*.
2. **Web app — guest** (person icon, dashed outline): "no login — identified
   in conversation (account/phone + security question)". Arrow labeled
   *"joins room (anonymous token)"*.
3. **Phone caller** (telephone icon, slightly faded + note "via SIP trunk —
   ready, pending carrier"): arrow into the same room.

Below the three, one more actor:
4. **Support specialist** (headset icon): arrow into the SAME room labeled
   *"warm transfer — joins with full context (summary, mood, next steps)"*.
   Draw this arrow visually distinct (e.g. red/human color) and entering the
   same room box the callers use — the point is ONE room, humans and agent
   together.

## Zone 2 — MIDDLE: "LiveKit Cloud" (purple zone)

One large **Room** box containing:
- the caller's audio in/out (WebRTC)
- **Ember — the agent** (small flame/portrait mark)
- the voice pipeline as three chips INSIDE the room flow, in order:
  **STT → LLM → TTS**
  (labels: "AssemblyAI · streaming", "Gemma 4 · with failover", "Fish Audio ·
  guarded"). One thin loop arrow: audio in → STT → LLM → TTS → audio out.
- a small shield mark on the TTS edge labeled "speech guardrails"
- note under the room: "turn detection · interruption handling · preemptive
  generation — all inside LiveKit's infrastructure (co-located, lowest
  latency loop)"

## Zone 3 — RIGHT: "Google Cloud" (one bounded zone; ONLY these five)

Stack five boxes; each gets ONE arrow from Ember, labeled with what crosses:

1. **Cloud Run — identity & tokens**: "verifies login, mints call tokens,
   checks the security answer, preloads the customer briefing".
2. **Cloud SQL** — "orders + customer accounts" · sublabel: "per-customer
   isolation enforced IN the database (parameterized secure views)".
3. **Firestore** — "live device state + usage history".
4. **RAG (Vertex AI)** — "product manuals + returns policy — she retrieves,
   never memorizes".
5. **Agent Memory (Vertex AI Memory Bank)** — "long-term facts per customer:
   pet's name, preferences, past issues — consolidated across calls".

NOTHING else in this zone. No GKE, no buckets, no extra services.

## The one motif to make memorable

The specialist's red arrow and the caller's arrow ending in the SAME room —
with a small caption: "a handoff is a person joining the conversation, not a
new system." If only one thing survives simplification, keep that.

## Text hygiene
- Arrow labels ≤ 5 words.
- Zone titles: CALLERS · LIVEKIT CLOUD · GOOGLE CLOUD.
- Footer line: "Identity is pluggable — signed-in, conversational, or SIP —
  everything after it is one shared path."
