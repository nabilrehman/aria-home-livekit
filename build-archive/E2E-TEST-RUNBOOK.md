# Aria Home · End-to-end test runbook

The goal is 10/10 on the four graded requirements, in the room, live. This is the
exact sequence to prove the system before the panel and the exact script to run
in front of them. Every step has a pass condition. Do not skip the pre-flight.

---

## 0 · What is deployed (verify, don't assume)

| Piece | Where | Check |
|---|---|---|
| Voice agent **Ember** | LiveKit Cloud `anycompany-agent` (CA_gBWxTuDrRTNu, us-east) | `lk agent status` → **Running** |
| Web console | https://aug24-web-549403515075.us-central1.run.app | opens, title "Aria Home · Support" |
| Identity + device registry (Cloud SQL) | Google **MCP Toolbox** → https://aria-toolbox-549403515075.us-central1.run.app/mcp | tool list has `lookup_account_by_phone` |
| Live telemetry + policy RAG | custom MCP → https://aug24-mcp-549403515075.us-central1.run.app/mcp | tool list has `get_device_state`, `search_knowledge` |
| Orders | REST on the web service `/api/orders` (key-protected) | 401 without key |
| Data | Cloud SQL `aria-home` · Firestore `aug24` | `seed.py --check` prints 5 customers |
| Login | Firebase Auth (email/password + Google) | `sarah@example.com` exists; your Gmail signs in with Google |

**Two demo callers, on purpose.** The panel sees two unrelated customers come out of one system:

| | Sarah Chen | You (Nabil Rehman) |
|---|---|---|
| Account | AH-4821 · Video Plus | AH-7104 · Video Plus |
| Phone | +1 512 555 1188 | **+1 737 205 9240** |
| Path | Guest / phone — Ember must *ask* who you are | Signed in with Google — Ember already knows |
| Devices | Living Room Thermostat 71°, Front Door Camera, Backyard Camera, Front Door Lock | Aria Thermostat 69°, Aria Doorbell Cam, Aria Floodlight Cam, Aria Smart Lock, Aria Motion Sensor (**needs battery**) |
| Most recent order | **58121** Indoor Camera two pack · processing · due 3 Sep | **58131** Smart Sensor four pack · processing · due 4 Sep |

---

## 1 · Pre-flight — 10 minutes before the panel

Run these in order. Each must pass.

```bash
cd ~/Downloads/livekit/anycompany-agent

# 1. Agent is live on LiveKit Cloud with today's build
lk agent status                                  # Status: Running, Deployed At = today

# 2. Warm every Cloud Run service (they scale to zero; a cold start mid-demo is a 10s silence)
for u in https://aria-toolbox-549403515075.us-central1.run.app/mcp \
         https://aug24-mcp-549403515075.us-central1.run.app/mcp \
         https://aug24-web-549403515075.us-central1.run.app/ ; do
  curl -s -o /dev/null -w "$u %{http_code} %{time_total}s\n" -m 30 "$u"; done
# expect 200/405/406 style codes and <1s on the SECOND run — run it twice

# 3. Data is there — and refresh telemetry so readings say "just now", not "10 hours ago"
(cd ../build-archive/deploy/aug24-mcp-server && FIRESTORE_DB=aug24 ../../../anycompany-agent/.venv/bin/python seed.py --telemetry)
set -a; . ./.env.local; set +a
.venv/bin/python -m pytest tests/test_assignment_answers.py -q     # 20 passed

# 4. The four graded beats, live, against the real stack
.venv/bin/python -m pytest tests/test_assignment_beats.py -q       # 13 passed

# 5. Web console end-to-end (Playwright, real endpoints)
#   open the URL, click "Call as a guest" → "Start call" → hear Ember within ~2s
```

**If step 4 shows a failure**, read the judge message — it is a sentence explaining what Ember said wrong. Nine times out of ten it is a phrasing drift, not a broken tool.

Also before the room: **laptop on power, wired headphones or a quiet mic, Chrome, mic permission already granted to the site, phone on silent.** Have `chrome://webrtc-internals` open in a second tab for Mike.

---

## 2 · The live script — what you say, what must happen

Timing: **6 minutes total** for the demo. Say each "watch for" line *before* the beat.

### Call 1 — Guest (the phone experience) · Sarah · ~3 min

Open the console → **Call as a guest** → **Start call**.

| # | Requirement | You say | Must happen | Say to the panel |
|---|---|---|---|---|
| 1a | Greet + look up | *(Ember opens)* "Hi, I'm calling from 512 555 1188." | "Hi **Sarah**… I can see your account." No account-number question. | "That was caller-ID → Cloud SQL through Google's MCP Toolbox. She never asked me who I am." |
| 1b | Ask for account # if no phone | *(second run, later, optional)* "Hi, I need help with my account." | She **asks** for phone or account number. Say "A H four eight two one." → "Hi Sarah." | "Same lookup, digits-only match — 'A H 4821', '4821', 'ah-4821' all resolve." |
| 2a | Most recent order | "What's the status of my most recent order?" | "Your Indoor Camera two pack is **processing**… due **September third**." | "Orders are a plain REST call — not everything needs MCP. Newest by *date*, not by number." |
| 2b | Thermostat active | "Is my thermostat active?" | "Yes, your living room thermostat is **on**…" | "Two stores, one answer: Postgres found the device, Firestore said what it's doing." |
| 2c | Temperature | "What's the temperature in my living room?" | "**Seventy-one degrees**." | "Live telemetry, read just now — she'll tell you *when* it reported if you ask." |
| 4 | Grounded policy | "How long do I have to return a doorbell camera?" | "**Fourteen days**" (not thirty). | "That number exists only in Aria Home's policy PDF. Correct answer = retrieval, not memory." |
| 3 | Transfer + summary | "I need to change the delivery address — can I speak to a person?" | She says she's connecting you and **has passed a summary**. The **"Handed to a person"** panel appears with a 2–3 sentence brief naming Sarah, the order, and why. | "This is the beat where CSAT normally dies — the human picks up already briefed. Stop talking; let them read it." |
| — | End | "That's all, thanks." | She says goodbye; the call closes itself a few seconds later. | — |

### Call 2 — Signed in (the web experience) · you · ~2 min

**Sign in first → Continue with Google** (your Gmail) → the right rail fills: **4/5 reporting**, motion sensor amber "needs battery", order history with **#58131 MOST RECENT ORDER** on top → **Start call**.

| # | You say | Must happen | Say to the panel |
|---|---|---|---|
| 1 | *(nothing — let her open)* | "**Hi Nabil**, I can see your account…" — **no** phone/account question. | "Firebase verified me; the account rides on the LiveKit token as an attribute. Identity is the opaque uid — never email or phone in LiveKit's logs." |
| 2 | "Where's my order?" | "Smart Sensor four pack, processing, due September fourth." → point at #58131 on screen | "Screen and voice read the same row." |
| 3 | "Is my hallway sensor okay?" | "It's **not reporting — needs a battery**, about six percent." | "An honest 'off' with a reason, not a guess. Amber on screen, amber in her answer." |
| 4 | "Is my back door locked?" | "Yes, locked, battery ninety-one percent." | — |
| 5 | "Bye." | Goodbye → room closes. | — |

### If the panel takes the wheel ("can we ask it things?")

Yes — that is requirement 4. Good ones to invite:
- "Which plan am I on?" → Video Plus
- "What devices do I have?" → lists them
- "Is my garage camera recording?" (Sarah has none) → "There's no garage camera on this account — you have…" **never** a state for a device that doesn't exist
- "What's the serial number on my lock?" → admits it doesn't have that **and offers a ticket or a person** (no dead ends)
- Talk over her mid-sentence → she stops (adaptive interruption). Cough/"mm-hm" → she **resumes** where she was (false-interruption resume).
- Go silent 15s → she checks in ("Are you still there?").

---

## 3 · Robustness you can demonstrate on request

| Ask | What happens | Why it matters |
|---|---|---|
| Kill nothing, just wait 15 s silent | Ember checks on you | `user_away_timeout=15` |
| Cough while she's speaking | She keeps going / resumes | `resume_false_interruption`, adaptive interruption mode |
| Read an order number "5, 8, 1, 3, 0" with pauses | Turn detector waits; no cut-off | semantic + acoustic end-of-turn model |
| Ask about an order that doesn't exist ("4472") | "No order with that number" — **never padded** to 5 digits | regression test for the padding bug |
| Ask for a person twice (retry) | One ticket, not two | partial unique index + idempotent insert (the retry-storm fix — tell this story) |
| Device cloud down (don't do live) | "I can't reach the device cloud right now" — never a guessed temperature | `DataUnavailable` → escalate, tested |

---

## 4 · Scoring self-check (do this the night before)

| Graded item | Evidence you'll show | Pass? |
|---|---|---|
| 1. Greet by name + look up (phone) | Call 1 step 1a | ☐ |
| 1. Ask for account # if not by phone | Call 1 step 1b | ☐ |
| 2. 2–3 smart-home questions | 2a, 2b, 2c (+ 4) | ☐ |
| 3. Transfer to another number **with summary** | Call 1 step 3 — summary panel | ☐ |
| 4. Answer customer questions | policy, plan, devices, unknowns | ☐ |
| Architecture slide | slide 5 (+5B gateway, 6 platform) | ☐ |
| Data flows to external systems | Cloud SQL (Toolbox MCP) · Firestore (MCP) · Orders (REST) · Vertex RAG · Firebase | ☐ |
| Tailored to Mike / Ahmad / Varun | speaker notes per slide | ☐ |
| Under 30 min including Q&A | rehearse with a timer — twice | ☐ |

**Honest gap to own, not hide:** "transfer to another number" is an in-room warm handoff (summary delivered, specialist joins the same room). There is no outbound SIP trunk on the LiveKit project, so it does not dial a PSTN number. If asked: *"The transfer tool already calls `create_sip_participant`; it needs an outbound trunk — a Twilio/Telnyx credential — to dial out. I left it as the in-room handoff so nothing in the demo depends on a carrier."* To make it real before the panel: buy a number in LiveKit Cloud → Telephony, create an outbound trunk, set `SIP_OUTBOUND_TRUNK_ID` and `TRANSFER_TO_NUMBER` (+17372059240) as agent secrets.

---

## 5 · Automated suites (what they prove)

| Suite | Count | Needs | Proves |
|---|---|---|---|
| `test_assignment_answers.py` | 20 | offline | the data supports a correct answer to every graded question, for all 5 accounts |
| `test_device_data.py` | 40 | offline | registry/telemetry split; spoken account & phone formats; retry-safe tickets; outages raise |
| `test_web_auth.py` | 22 | offline | no token without Firebase; opaque identity; no PII in JWT; guest path; `/me` |
| `test_order_tools.py` | 6 | offline | REST order tools: found / missing / outage; no duplicate MCP tools |
| `test_review_findings.py` | 8 | offline | prompt names real tools; never says "AnyCompany"; end_call; silence & false-interruption options |
| `test_turn_latency.py` | 4 | offline | metrics read correctly (the 0 ms bug can't return) |
| `test_agent.py`, `test_store.py` | 27 | offline | greeting; legacy store parity |
| **`test_assignment_beats.py`** | **13** | live stack | **the four requirements, verbatim, judged by an LLM** |
| `test_demo_beats.py` | 3 | live stack | the whole hero-journey call |
| Playwright `qa_site.py` | 37 | local server | console states, order rail, focus, mobile, no console errors |

```bash
.venv/bin/python -m pytest -q --ignore=tests/test_assignment_beats.py --ignore=tests/test_demo_beats.py   # 133 offline
set -a; . ./.env.local; set +a; .venv/bin/python -m pytest tests/test_assignment_beats.py tests/test_demo_beats.py -q   # 16 live
```

---

## 6 · Talking points that separate a 10 from an 8

- **"Not everything is MCP."** Identity, device registry: Google's MCP Toolbox, declarative SQL, zero data-API code. Device telemetry + RAG: our MCP server, because those aren't SQL. Orders: a plain REST function tool, because a one-line lookup doesn't need a protocol. Choosing per system is the senior answer.
- **The registry is relational, the state is not.** A thermostat reports degrees, a lock reports a bolt; no shared column set → Firestore. `device_id` is the join. "Is my thermostat active?" crosses both.
- **The retry storm.** Your own incident: tool timeout → model retried → four tickets. Fixed structurally (partial unique index), not with prompt-begging. Then: "that's why the API gateway/quota belongs at the boundary."
- **PII stays off the token.** Firebase uid as LiveKit identity; account *number* only as an attribute; profile fetched server-side.
- **Agent is a participant.** The specialist *joins the room*; that's why handoff needs no new subsystem.
- **Cold starts.** MCP session timeout raised 5→20 s; services pre-warmed. Say it before Mike asks about scale-to-zero.

---

## 7 · Recovery, if something breaks live

| Symptom | Do |
|---|---|
| Ember silent after "Start call" >5 s | say "cold start — give it a second"; if >15 s, End call → Start call |
| "I can't reach the account system" | Toolbox cold; retry the question once; it's the honest failure mode — narrate it |
| Google sign-in popup blocked | use **Call as a guest** — every graded beat is in Call 1 |
| Summary panel doesn't appear | the transfer still happened (check her words); show `lk room participants list` if pressed |
| Total audio failure | fall back to the recorded run + screenshots; keep narrating the architecture |

Finishing early is fine. Going over is not.
