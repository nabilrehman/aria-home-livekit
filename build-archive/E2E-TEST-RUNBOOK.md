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
| Login | Firebase Auth (email/password + Google) | `johndoe@gmail.com` exists; your Gmail signs in with Google |

**Two demo callers, on purpose.** The panel sees two unrelated customers come out of one system:

| | John Doe | You (Nabil Rehman) |
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

## 2 · The demo — one call, seven minutes, every graded beat once

Two browser tabs before you start: the **store** (signed in with your Gmail, on the Support page) and the **Specialist Desk** (`/desk`, PIN 8616, name "Ahmad"). Warm-up from §1 done. Say each "watch for" line *before* the beat.

### Prologue · John, by phone (75 s) — requirement 1b, the guest path
Click **Call as a guest → Start call**.

| You say | Must happen | To the panel |
|---|---|---|
| "Hi, I need help with my account." | She **asks** for phone or account number. | "No caller ID on this path — same as an unknown phone." |
| "A H four eight two one." | "Hi John… I can see your account." | "Digits-only match on Cloud SQL, through Google's MCP Toolbox. 'AH 4821', '4821', 'ah-4821' all resolve." |
| "What's the status of order five eight one two one?" | "Your Indoor Camera two pack is **processing** — still in the warehouse, delivers September third." | "Order by number — one scoped call, account pinned by the identification step." |
| "And order five eight one three one?" | "**No order with that number on this account.**" | **Mike:** "Same tool, same second. That one is Nabil's. She can't see it — the database won't return it. Parameterized secure views, a role with no base-table access, and the account never comes from the model." |
| "Okay, bye." | goodbye, call closes | — |

### Act 1 · You, signed in (90 s) — requirement 1a
Switch tab → **Start call with Ember**.

| You say | Must happen | To the panel |
|---|---|---|
| *(nothing)* | "**Hi Nabil**, I can see your account." No question. | **Ahmad:** "Firebase verified him; the account rides on the LiveKit token. Nobody recites an account number to a machine." |
| "What do you know about my hallway sensor?" | "It's not reporting — **needs a battery**… and I have a note your dog **Biscuit** sets it off." | **Mike:** "Two stores in one answer: live telemetry from Firestore, and a fact from Vertex AI Memory Bank. Both were preloaded in parallel with the session start — zero tool calls for that answer." |

### Act 2 · The three graded questions (90 s) — requirement 2

| You say | Must happen | To the panel |
|---|---|---|
| "What's the status of my most recent order?" | Smart Sensor four pack, processing, September fourth. | **Varun:** "A plain REST call into an order API — the kind you already have. Not everything needs a protocol." |
| "Is my living room thermostat on, and what's it set to?" | On, sixty-nine degrees, cooling. | "Registry in Postgres, state in Firestore, joined on device id — a thermostat and a lock don't share a schema." |
| "How long do I have to return a doorbell camera?" | **Fourteen days.** | "That number exists only in your policy PDF. Right answer = retrieval, not memory." |

### Act 3 · Memory (45 s) — requirement 4, and the differentiator

| You say | Must happen | To the panel |
|---|---|---|
| "Remember that my back door lock sticks when it's cold." | "I'll remember that." | **Ahmad:** "That's a customer preference stored in Memory Bank, scoped to his account. Next call, any agent — human or Ember — knows it. Contradict it later and it's *updated*, not duplicated." |

### Act 4 · Transfer with a summary (2 min) — requirement 3
Move the **desk** tab into view.

| You say | Must happen | To the panel |
|---|---|---|
| "I want a refund on order five eight one three zero, it arrived damaged. Put me through to someone." | Ember: "connecting you now, I've passed along a summary." **Desk rings**: Nabil · refunds · summary · mood · urgency · next steps. | **Ahmad:** "Look at the desk before anyone picks up. This is the beat where CSAT normally dies — here the human starts briefed. Stop talking. Let them read it." |
| Click **Accept call** (as Ahmad) | Ember: "a specialist has joined…" and goes silent. You (Ahmad) say "Hi Nabil, I've got the damaged sensor pack here — I can refund that now." | **Mike:** "The specialist is just another participant in the same LiveKit room. No new subsystem. The phone version is the same tool with a SIP trunk." |
| Click **End call** | Call ends. Desk keeps the case summary under Recent. | **Varun:** "Every transferred call is a record — brief, outcome, transcript — masked, in Firestore. That's your QA dataset for free." |

### Epilogue (20 s) — memory across calls
**Start call** again. Say: "Anything I told you about my back door?" → "Your back door lock sticks when it's cold." → "Thanks, bye."
> "Same customer, fresh session, no login screen twice. That's the difference between a bot and a support line."

### Timing guard
Prologue 1:15 · Act 1 1:30 · Act 2 1:30 · Act 3 0:45 · Act 4 2:00 · Epilogue 0:20 = **7¼ min**. If running long, drop the Epilogue; never drop Act 4.

### If the panel takes the wheel
Invite it after Act 2. Good probes: "Is my garage camera recording?" (no such device — she says so); "What does error E four mean on my thermostat?" (no C-wire — from that model's manual); "Will the motion sensor ignore my dog?" (under forty pounds, mounted at seven feet — and she knows about Biscuit); "What's the serial on my lock?" (doesn't know, offers a ticket); talk over her (stops); cough (resumes); silence 15 s (checks in).

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
