# Aria Home deck — build brief v2

**For:** the designer building the deck · **From:** Nabil (presenting) · **Date:** 29 Aug 2026
**Supersedes:** `slide-prompt.md` (v1, 9 slides). Keep v1 for reference; this is what to build.

**The meeting:** 30 minutes, live, in front of three buyers. I present, break to a live voice-agent
demo around the 14-minute mark, come back for the numbers. The deck is projected and I drive it
from the keyboard.

**Read this section first, designer:** every slide below has three parts — **COPY** (the words,
final, don't rewrite them without asking me), **DATA** (numbers with their sources — these are
cited and must not be rounded or "improved"), and **DESIGN INTENT** (what the slide has to *do* in
the room, which is what should drive your layout choices). Where I've specified something visually
it's because the room constrains it, not because I'm art-directing you. Everything not specified
is yours.

---

## 1 · What changed from v1, and why

v1 was a solid presales structure but it was missing five things. Four of them are the things a
technical panel actually probes, and the fifth is the thing that wins finance buyers. All five are
now in.

| # | What was missing in v1 | Why it matters | Now |
|---|---|---|---|
| 1 | **No platform slide.** v1 showed an architecture diagram but never showed what LiveKit actually ships. | The technical buyer's real question isn't "how does it work", it's "what am I signing up to maintain". An architecture diagram doesn't answer that; a list of what he *doesn't* build does. Voice projects don't die at the demo, they die in month three on telephony edge cases, autoscaling, and having no way to see what the agent said. | **Slide 6** |
| 2 | **No LiveKit customer proof.** v1's proof strip used PAL Airlines and an unnamed Bangkok retailer — third-party voice-AI vendor blog stats, nothing to do with LiveKit. | Weakest kind of evidence: unverifiable, and it implicitly admits we have no customer like theirs. We do. **Assort Health** is LiveKit's own published case study and is structurally near-identical to Aria Home — high inbound volume, caller identified on arrival, routine handled, rest handed off warm. With real numbers, including a revenue number. | **Slide 9** |
| 3 | **No calculator, just a static worked example.** v1 asserted "$0.50–2.00 per AI resolution" from a third-party blog and a fixed "$2.5M/year". | A static number on a slide is a claim. A number the CFO watches you compute from *his* inputs is a finding. And we can do better than the blog figure: LiveKit publishes its actual per-minute rates, so the cost side is auditable line by line — and it comes out around **$0.25 for a four-minute call**, well under the industry's $0.50–2.00. | **Slide 10** |
| 4 | **No security or compliance beat.** | They sell cameras and door locks. The technical buyer *will* ask where customer data goes, and "our customer data stays in our cloud" is only half an answer without the certifications and the self-host escape hatch behind it. | **Slide 6**, security band |
| 5 | **Latency never quantified.** v1 talked about realtime but gave no numbers. | I have per-turn instrumentation on my own build. Quoting measurements off the thing they just watched run is a completely different kind of credibility from reciting a docs table, and it cannot be faked. | **Slide 8** |

**Result: 9 slides → 12.** That still fits 30 minutes because four of them are fast (title, agenda,
demo bridge, close) and the demo eats six.

**On the xAI comparison:** what makes that deck work isn't the near-black — it's the *restraint*.
One idea per slide, type doing all the work, hairline rules instead of boxes-within-boxes, and
numbers set enormous. What we should not copy is the palette; a near-black deck with a single acid
accent is now the default look of every AI company deck and reads as generic. See §4.

---

## 2 · The room

Three buyers. Every content slide serves exactly one of them, and that should be **visible on the
slide** — I need to be able to see whose slide I'm on without reading my notes, and they should
each notice when it's their turn.

| Buyer | Role | Cares about | Their fear |
|---|---|---|---|
| **Mike** | Director of AI Platform — technical | Architecture, integration, latency, security, maintenance burden | "This becomes my team's problem to keep alive." |
| **Ahmad** | Director of Customer Support — operational | Customer experience, his agents' jobs, daily workflows | "This is a headcount reduction plan with a friendly name." |
| **Varun** | VP of Finance — economic | Cost per outcome, ROI, and — subscription business — protected recurring revenue | "The savings are hypothetical and the costs are real." |

**Designer:** I need a small persistent buyer tag in the slide chrome (top rail is fine) reading
e.g. `FOR MIKE`. Keep it quiet — it's a wayfinding device, not a headline. Don't colour-code the
three buyers; three extra colours will fight the palette for no gain.

---

## 3 · Principles that override everything

These matter more than any visual decision. If a layout choice conflicts with one of these, the
principle wins.

1. **Customer-first.** Every slide is about Aria Home, in their words. Their situation before our
   solution — that's why the agenda spends the first third on them.
2. **Outcomes, never features.** No capability appears without the outcome for a named person.
3. **Two value levers, not one.** This is a subscription business. Sell **(a) protect and grow
   recurring revenue** — better support cuts churn and creates renewal moments in-call; a saved
   subscriber is worth far more than a saved call — *and* **(b) cut the cost of the routine.**
   Cost-only is the weak half of the story and it's the half every competitor leads with.
4. **Quantify pain, then value.** Number it, scale it, then ROI = (value − cost) ÷ cost. Benchmarks
   now, their real numbers proven in a pilot. Never blur that line.
5. **Why now.** Rising device volume, longer waits, churn, competitors already shipping voice AI.
6. **One buyer per slide,** labelled, with notes on how to pivot it if someone else bites.
7. **The demo is a hero's journey.** Sarah is the hero, the agent is the guide, pain → resolution.
8. **Augment, don't replace.** Say it before Ahmad has to ask, or he spends the rest of the meeting
   defending his team instead of listening.
9. **Trust and safety is a business argument.** Cameras and door locks: a wrong or unavailable
   answer is a safety failure on a security product, not a CSAT dip.
10. **De-risk the decision.** Pilot metrics agreed up front, explicit yes/no gate, crawl→walk→run.
11. **Land and expand.** Support is the beachhead; outbound, renewals and onboarding come later.
12. **Proof beats claims.** Cited numbers with sources on the slide. No adjectives doing a
    number's job.

---

## 4 · Design direction

**The read:** this is editorial, not utilitarian. It's the highest-stakes 30 minutes of a sales
cycle and it should look like someone made deliberate choices. But it is also a *working* document
projected in a lit room — legibility beats atmosphere every time.

### Hard constraints (these come from the room, not from taste)

- **16:9, fixed.** Build to a 1280×720 base and scale to fit the viewport rather than reflowing;
  the deck must look identical on my laptop and on whatever projector is in the room. No surprises
  at presentation time.
- **Minimum type size 12px at the 1280 base** (≈ 22pt projected). Nothing smaller, including
  captions and sources. If content doesn't fit above that floor, the content is too long — tell me
  and I'll cut it.
- **Commit to one theme.** Don't build light/dark switching. A projected deck must render the same
  regardless of the presenter's OS setting, so paint every colour explicitly and skip
  `prefers-color-scheme` entirely. Make that a stated choice in the CSS, not an omission.
- **No horizontal scroll ever**, at any window size.
- **Respect `prefers-reduced-motion`.** Transitions between slides only; no ambient animation. A
  moving background during a live demo is a liability.

### Palette

Dark ground is right — it's a voice/infrastructure subject and it keeps the projector from washing
out. What's *not* right is the default AI-deck dark: near-black plus one acid green or electric
purple. Suggested direction, take it or replace it with something equally specific:

| Token | Value | Role |
|---|---|---|
| ground | `#0B0F12` | Near-black with a slight cool bias. Not pure black — pure black on a projector kills the hairlines. |
| surface | `#12181C` | Raised cards |
| hairline | `#1F2A30` / `#2C3A42` | Rules and card edges. Hairlines, not borders — this is the main structural device. |
| text | `#E8EDEF` → `#7E8F98` | Three steps of text, not two |
| **accent** | `#F2A93B` — signal amber | One accent, used sparingly. The rationale: it's the colour of a status LED in a dark house, which is literally the subject. It also isn't the acid green / vermilion / purple that everything else in this category uses. |
| good | `#56C79A` | **Semantic only** — savings, wins, retained subscribers. Kept separate from the accent so a green number always means "this is money you keep". |
| warn | `#E2705F` | **Semantic only** — cost, pain, what's being removed |

Spend the boldness in one place per slide and keep everything around it quiet. If the amber fights
a surface, drop its saturation rather than swapping the hue.

### Typography

Three roles. **Avoid Inter and Space Grotesk** — they're the safe defaults and read as unconsidered.

- **Display** (headlines, big numbers): an industrial grotesque with tight negative tracking at
  size. `Archivo` at 700–800, tracking around `-0.03em`, works well. Headlines want
  `text-wrap: balance`.
- **Body**: something engineered rather than neutral — `IBM Plex Sans` pairs well against Archivo
  and reads as instrumentation rather than marketing.
- **Utility / mono** (eyebrows, data labels, per-minute rates, the ledger): `IBM Plex Mono`, ~10px,
  `letter-spacing: 0.16em`, uppercase. Same superfamily as the body face so it's cohesive rather
  than arbitrary.

Every column of digits gets `font-variant-numeric: tabular-nums`. This deck is mostly numbers and
misaligned digits will be visible from the back of the room.

### Layout

Persistent chrome: a hairline top rail carrying the slide's eyebrow (left) and the buyer tag
(right), and a bottom bar with a slide counter, thin progress bar, prev/next buttons, and the
keyboard hint. Content sits between them on a strict grid with generous margins (≈64px at base).

Structural devices should encode something true. Two places where numbering is genuinely earned:
the **agenda uses real minute marks** (0–3, 3–8, …) because I need to know if I'm running long, and
the **demo timeline uses real elapsed times** (0:00, 0:20, 0:40, 1:00) because it's an actual
sequence. Don't add 01/02/03 markers anywhere they aren't a real sequence.

### Interaction

- `←` / `→` / `Space` / `PageUp` / `PageDown` navigate; `Home` / `End` jump to ends.
- `S` toggles a **speaker-notes panel** — an overlay across the bottom, outside the scaled stage,
  scrollable, showing the notes written for each slide below. This is the single most important
  non-visual feature; I rehearse from it.
- `F` toggles fullscreen.
- **Critical:** slide 10's calculator has range sliders. When focus is inside an input, arrow keys
  must go to the slider, not the deck. Guard the keyboard handler on `event.target`. Same for
  `Space` when a button or input has focus.
- Visible keyboard focus states throughout.

### Copy

The words below are final. They're written to be *said*, not read — short, active, specific. Where
a line looks awkward on the page it's usually because it's shaped for the mouth. Check with me
before rewriting. No emoji anywhere.

---

## 5 · The twelve slides

Timings total 30 minutes with the demo at six.

---

### Slide 1 — Title · everyone · ~2 min

**COPY**
- Eyebrow / wordmark: `LiveKit · Solutions Architecture`
- Headline: **A support line that already knows your customer.**
- Subline: Voice AI customer support for Aria Home — built on LiveKit.
- Footer left: `Nabil Rehman · Solutions Architect, LiveKit`
- Footer right: `Prepared for Aria Home · August 2026`

**DESIGN INTENT** — The headline is an outcome for them, not a product name, and it should be the
largest type in the whole deck. This slide is up on screen while people file in and while
introductions happen, so it carries more dwell time than any other; it should reward being looked
at for three minutes. No hero image, no gradient — the sentence is the hero.

**SPEAKER NOTES** — One line on who I am and why we're here, then hand the floor over: *"Before I
show you anything, I'd like each of you to tell me what you'd want to walk out of this room with."*
Their answers decide which slides I lean on and which I skip. Mike will say architecture and
integration; Ahmad will say his team and his queue; Varun will say cost and payback. Write those
three words down and call back to them by name later.

---

### Slide 2 — Agenda · everyone · ~1 min

**COPY** — Headline: **Your situation first.** Sub: Then what we'd build, then a live call, then
the numbers.

| Time | Item | Right-hand note |
|---|---|---|
| 0 – 3 | Introductions | What each of you needs from today |
| 3 – 8 | Where you are today | The volume problem, quantified |
| 8 – 14 | What we'd build | Four jobs · architecture · platform |
| **14 – 20** | **Live demo** | One caller, start to handoff |
| 20 – 27 | The business case | Your numbers, calculated live |
| 27 – 30 | Next steps | A two-week pilot with a yes/no gate |

**DESIGN INTENT** — A three-column table: time (mono, accent), item (display), note (small, muted,
right-aligned). Hairline between rows, no card. **Emphasise the demo row** — accent on the item
text is enough. The minute marks are a real presenter tool, not decoration.

**SPEAKER NOTES** — Point at the order deliberately: *"Notice we spend the first third on your
situation, not our product. If I get your situation wrong, nothing after it matters."* Then give
explicit permission to interrupt: *"Please cut in. A question in the moment is worth more to me
than a clean run-through."* If we're running long, the slides I cut are 8 and 11, never the demo.

---

### Slide 3 — Where you are today · **Ahmad & Varun** · ~4 min

**COPY** — Eyebrow `WHERE YOU ARE TODAY`. Headline: **Every device sold is a support call
waiting.** Dek: You've built a business that ships more support volume every quarter — and the
calls arrive on the channel that costs the most to staff.

**DATA — four stat cards, in this order.** Order matters: slide 4 mirrors it exactly.

| Big number | Label | Supporting line | Source |
|---|---|---|---|
| **16** | Devices per home | Average US connected household. **52%** hit a technical problem last year; 38% hit two or more. | Parks Associates |
| **63%** | Still call in | Of consumers prefer to handle technical support over the phone — the channel you can least afford to scale linearly. | Parks Associates |
| **45–60%** | Deflectable today | Of tier-1 contacts are resolvable by voice AI. Routine intents — order status, resets, device state — run above 70%. | Fin AI / industry 2026 |
| **24/7** | Expected coverage | On cameras and door locks, a call that goes unanswered at 11pm isn't a queue problem. It's a trust problem. | — |

**Footer (the why-now, must appear):** Connected devices pass 32 billion by 2030, and on a
subscription base every extra minute of wait is churn risk rather than just cost. This compounds in
one direction — and your competitors are already deploying voice AI. `Parks Associates · Gartner ·
Statista`

**DESIGN INTENT** — Numbers enormous, labels tiny. The four cards read as one unit: a single
bordered block divided by hairlines, not four floating cards with gaps. Sources visible but quiet —
they're doing credibility work just by being present, they don't need to be read. `45–60%` will set
narrower than the others; size it down slightly so the four numbers hold a common optical weight
rather than a common point size.

**SPEAKER NOTES** — These are industry benchmarks, not claims about Aria Home — say that out loud,
it buys credibility. Land the compounding: every device you ship is a support call you haven't
received yet, and you're shipping more every quarter. Then the subscription twist for Varun: *"On a
hardware-only business a long hold is an annoyance. On a subscription business it's a
cancellation."* **Then stop and ask:** *"Does this match what you're seeing? What's your current
average wait?"* Whatever number Ahmad says, write it down — it goes into the calculator on slide 10
and that's the moment the deck becomes theirs.

---

### Slide 4 — What we'd build · **Ahmad** · ~3 min

**COPY** — Eyebrow `WHAT WE'D BUILD`. Headline: **One voice agent, four jobs.** Dek: Each one
answers something from the previous slide, in the same order.

Four cards. Each is `LABEL` / outcome headline / description / **Removes:** line.

1. **IDENTIFY — "Knows who's calling."**
   Greets by name and pulls the account — subscription tier, registered devices, order history —
   from the phone number, or an account number if they're calling from elsewhere.
   *Removes:* Reciting account details to a machine before reaching a person.
2. **RESOLVE — "Answers the routine."**
   Order status, is the thermostat active, what's the living room reading, when does my plan renew,
   what does the return policy say.
   *Removes:* The 45–60% of contacts that never needed a person — freeing your team for the complex
   and the safety-critical.
3. **HAND OFF WARM — "Escalates without the restart."**
   Writes a summary of the call, then transfers to a person — by phone, or by bringing a specialist
   into the same live conversation.
   *Removes:* The customer repeating the whole story; the agent picking up cold.
4. **STAY GROUNDED — "Accurate, or it escalates."**
   Every fact comes from your systems or your policy documents. It has no authority to guess a
   date, a temperature, or a warranty term.
   *Removes:* Brand risk. On security hardware, a wrong answer is a trust failure.

**DESIGN INTENT** — Same four-across structure as slide 3, deliberately, so the mirroring is felt
rather than just claimed. The **Removes:** line is the payload of each card — it should sit at the
bottom, separated by a hairline, with its label in the `warn` semantic colour. That's the one place
warn appears on this slide and it should read as "this is the pain being deleted".

**SPEAKER NOTES** — The four cards mirror slide 3 in the same order — say that; it shows the
solution was derived from their problem rather than pre-packaged. Two lines matter most: on
RESOLVE, pre-empt Ahmad's fear before he raises it — *"This takes the calls your people don't want,
not the calls they're good at."* On STAY GROUNDED, escalate past accuracy — *"You sell door locks.
A confidently wrong answer isn't a bad CSAT score, it's a safety claim you didn't mean to make."*
For Mike: every one of these four is a tool call into a system he already owns. Nothing here asks
him to move data.

---

### Slide 5 — How it works · **Mike** · ~4 min

**COPY** — Eyebrow `HOW IT WORKS`. Headline: **Where your data flows.**

**THE DIAGRAM — inline SVG, left to right, three zones:**

- **CALLER** (left): `Phone · SIP` / `Web · WebRTC` / caption "Same agent, either way"
- **LIVEKIT CLOUD** (centre, visually emphasised — this is the only box with an accent border),
  containing three stacked inner boxes:
  - `Room / SFU` — Media transport, per-participant tracks
  - `Inference` — STT · LLM · TTS · turn detection
  - `The agent` — Joins the room as a participant — co-located with the models, one hop
- **YOUR CLOUD** (right), three stacked inner boxes:
  - `Account & device CRM` — Behind an MCP boundary
  - `Policy knowledge` — Retrieval over your documents
  - `Warm transfer` — Dials a person, hands over the summary
- **HUMAN SPECIALIST** (below right): "Arrives already briefed"

**Three edge types, each visually distinct, with a legend:**

| Edge | Style | Route | Label |
|---|---|---|---|
| Realtime voice · WebRTC | solid, neutral | Caller → LiveKit | "realtime audio" |
| Data / tool call | **dashed**, info blue | LiveKit → Your cloud | "tool call" |
| Human transfer, with summary | solid, **accent** | Warm transfer → Human, then Human → back into the Room | "joins the same room" |

**Footer:** The agent runs on LiveKit, co-located with the models. Your account records, device
state and policy documents stay in your cloud — what crosses the line is a scoped tool call and its
answer, not your customer database.

**DESIGN INTENT** — This diagram makes three arguments and the visual language has to carry all
three without me narrating: (1) the LiveKit box is emphasised because the whole latency argument is
that media, models and agent logic are in one place; (2) the dashed edge is thin and singular
because the point is how *little* crosses the boundary; (3) the accent edge loops the human back
into the Room rather than terminating at a "transfer" box, because the actual claim is that a
specialist *joins the existing conversation* rather than receiving a routed call. That loop is the
slide's whole insight — make sure it reads. Three edge types is the maximum; don't add a fourth.

**SPEAKER NOTES** — Three claims, in this order. **1. The agent is a participant, not a backend
service.** It joins the room and subscribes to the caller's audio the way a human would. That's why
a specialist joining later needs no new subsystem — they just arrive. **2. The agent is co-located
with the models.** No cross-cloud hop in the latency path; numbers on slide 8. **3. Your customer
data never moves.** Account records, device state and policy documents stay in your cloud behind
the MCP boundary; what crosses is a scoped tool call and its answer. Integration and security are
the same picture. *Offer to go deeper on any single box and let him pick — the box he picks tells
you what he's actually worried about.*

---

### Slide 6 — What you don't have to build · **Mike** · ~3 min · **NEW**

**COPY** — Eyebrow `WHAT YOU DON'T HAVE TO BUILD`. Headline: **The parts that usually sink month
three.** Dek: A voice demo takes a weekend. What follows is the platform underneath it — and it
ships with the product.

**Eight cells, 4 × 2:**

| | |
|---|---|
| **Agents SDK** — Agent logic in Python or TypeScript. Your code, your control flow, your tools. | **Inference** — 50+ STT, LLM and TTS models routed for low latency. Swap any of them without touching the agent. |
| **Telephony** — Native SIP in and out. Numbers, trunks, transfers and DTMF, without a separate telephony stack. | **Cloud deployment** — Versioned rollouts, autoscaling and graceful drain on the same global edge as the media. |
| **Observability** — Session replay, full transcripts, trace spans and runtime logs for every call. | **Testing & evals** — Run and stress-test real scenarios before they reach a customer. |
| **Recording & egress** — Export audio and transcripts straight to your own storage for QA and compliance. | **Speech quality** — Built-in noise cancellation, end-of-turn detection and interruption handling. |

**Security band** (full width, beneath the grid, visually distinct):
`SECURITY` · SOC 2 Type II · HIPAA · GDPR & CCPA · End-to-end encryption · Regional data residency ·
**Same APIs self-hosted or in your own cloud — not a one-way door**

**Footer:** 300,000+ developers, billions of calls a year, thousands of concurrent agent sessions —
and roughly a quarter of US 911 dispatch centres run on the same transport.
`livekit.com/products/agent-platform · livekit.com/security`

**DESIGN INTENT** — Eight cells is a lot; keep each one to a bold noun and two lines and let the
grid do the work. This slide should feel like a *checklist being ticked*, not a feature brochure —
the emotional beat is relief, not excitement. The security band is deliberately a different
treatment from the grid because it answers a different question; give the last item (the self-host
escape hatch) the accent, because it's the line that defuses lock-in and it's the one Mike will
remember.

**SPEAKER NOTES** — Frame it as subtraction, not features: *"Here's the list of things a team
normally builds for a voice product, and doesn't have to here."* Most voice-AI projects don't die
on the demo, they die in months two through six — telephony edge cases, autoscaling, and having no
way to see what the agent actually said. **Land observability hardest** — session replay,
transcripts and trace spans are what turn "a customer complained" into a fix. Ahmad cares about
this too; it's his QA process. **No model lock-in** is the strategic line: pick STT, LLM and TTS
per workload and swap them as the market moves without touching the agent or the transport. If he
asks about security, the band is the answer, and the escape hatch is real — same APIs self-hosted
or in your own cloud, so this is not a one-way door.

---

### Slide 7 — Live demo · everyone · ~6 min

**COPY** — Eyebrow `LIVE DEMO`. Headline: **One caller, ninety seconds.**
Caller chip: `Sarah Chen` · Video Plus plan · thermostat, two cameras, one door lock

**Horizontal timeline, four beats.** Above the axis: time, the line Sarah says, what happens.
Below the axis: the "Watch for" cue.

| | 0:00 | 0:20 | 0:40 | 1:00 |
|---|---|---|---|---|
| **She says** | "Hi Sarah." | "Is my thermostat on?" | "Where's my order?" | "I need a person." |
| **What happens** | Recognised from the number she's calling on. Account, plan and devices already on screen. | Live device state, read out of your systems: active, living room at 71°. | The specific order, the specific date, said out loud as words rather than read as a record. | A summary is written, appears on screen, and goes with her to the subscription team. |
| **Watch for** | She never says an account number. | A real call into your CRM — not a plausible-sounding guess. | Ask it something it can't know. It says so. | The human arrives already briefed. She doesn't start over. |

**Footer:** Nothing here is scripted. Every step is a tool call into a system you already run — and
if a call fails, the agent says it doesn't know and escalates rather than inventing an answer.

**DESIGN INTENT** — A real horizontal axis with dots at each beat, not four cards in a row: the
elapsed times are true and the left-to-right reading *is* the argument. The "Watch for" cues sit
below the axis in the `good` semantic colour and quieter type — they're a second layer I read out
before the demo, so they must be visually subordinate but individually scannable. The caller chip
wants a small live-status dot; this slide is on screen while I dial.

**SPEAKER NOTES** — **Prime before you dial.** Read the four "watch for" cues out loud first. An
unprimed demo looks like a chatbot; a primed one looks like engineering, because they're now
watching for the specific thing you said would happen. Sarah is the hero, the agent is the guide.
Narrate what's happening underneath as it happens — *"that was a live call into the CRM, not a
cached answer"* — and when the handoff summary lands on screen, **stop talking and let them read
it.** That silence is the most persuasive four seconds in the meeting. **If something breaks:**
don't apologise or restart. Say what you expected, what you saw, and what you'd check — this is a
panel of engineers and operators, and diagnosing calmly in front of them scores higher than a clean
run.

---

### Slide 8 — Measured, not quoted · **Mike** · ~3 min · **NEW**

**COPY** — Eyebrow `MEASURED, NOT QUOTED`. Headline: **The one-second budget, on this build.** Dek:
Per-turn instrumentation on the agent you just watched — not a published table.

**Left: the budget table.** Three columns — Stage / Published budget / **This build**.

| Stage | Published budget | This build |
|---|---|---|
| End of turn detected | ~300 ms | **312 ms** |
| LLM first token | 200–400 ms | **288 ms** |
| Speech first byte | 100–300 ms | **141 ms** |
| **Perceived response** | **< 1000 ms** | **741 ms** |

Caption beneath: Median over a twenty-turn conversation; p95 at 934 ms. Transport sits outside the
table — about 40 ms to the nearest edge, read live off the WebRTC connection. Stages overlap
because generation starts before end-of-turn is confirmed, so the total lands under the sum of its
parts.

> ⚠️ **Designer: treat these three numbers as placeholders.** They come from my own instrumented
> run and I re-run it before the meeting; I'll hand you final figures. Build the table so swapping
> them is a one-line edit.

**Right: the grounding proof panel.** Header `GROUNDING, PROVED`.

- *"How long do I have to return a doorbell camera?"* → **14 days** — Not 30. That exception exists
  only in your returns policy.
- *"How quickly must I report a damaged device?"* → **48 hours** — Retrieved from the document, not
  recalled by the model.
- Closing line: Both answers are unique to your policy document, so a correct answer is evidence of
  retrieval rather than a lucky guess. Ask it something the document doesn't cover and it will tell
  you it doesn't know.

**DESIGN INTENT** — The "This build" column is the entire point of the slide: set it in the mono
face, in the `good` semantic colour, heavier than the published column, tabular figures. The eye
should land there first and read down. Two-column split, roughly 55/45 — the table is the hero and
the proof panel is a bordered aside. This is the most technical slide in the deck and it should
look like an instrument readout rather than a marketing claim.

**SPEAKER NOTES** — This is the credibility slide. Anyone can recite a docs table; these are
numbers off the build they just watched, measured per turn by instrumentation wired into the
session. Two things to say: transport is missing from the table **on purpose** — it's roughly 40 ms
to the edge, read off the live WebRTC stats, and I'll add it rather than hide it. And preemptive
generation means the stages overlap, so perceived latency beats the arithmetic — which is why the
total is under the sum of its parts. **The grounding proof is the sharper half.** Those two answers
appear nowhere except Aria Home's own returns policy, so a correct answer proves retrieval rather
than a model that happens to know a plausible number. Offer to ask a question with no answer in the
corpus and let them watch it decline. *Volunteering the failure mode is what separates this from a
vendor demo.*

---

### Slide 9 — Someone already did this · **Ahmad & Varun** · ~3 min · **NEW**

**COPY** — Eyebrow `SOMEONE ALREADY DID THIS`. Headline: **Different industry. Same call.** Dek:
Assort Health runs patient phone lines on LiveKit — high inbound volume, callers identified on
arrival, the routine handled and the rest passed to a person.

**Left column — `ASSORT HEALTH, ON LIVEKIT`** — four metrics in a 2×2:

| Number | Label |
|---|---|
| **20M+** | Patient interactions carried on LiveKit |
| **90%** *(good colour)* | Of inbound calls handled by the agent — 10% handed to staff |
| **4.3/5** | Average caller satisfaction |
| **99%+** *(good colour)* | Accuracy across interactions |

Pull quote beneath: *"When someone calls their doctor, they shouldn't be stuck on hold. Our agent
greets them immediately and handles the interaction from the very beginning, with 99%+ accuracy."*
— **Jeffery Liu · Founder & Co-CEO, Assort Health**

**Right column — `ONE OF THEIR CUSTOMERS · CHESAPEAKE HEALTH CARE`**

| Number | Label |
|---|---|
| **−89%** *(good)* | Hold time, across 150+ providers |
| **2.6 → 4.4** | Satisfaction, out of 5 |
| **$1M+** *(good, given its own emphasised block)* | New revenue captured from bookings taken **after hours** — demand that used to hang up. This is the revenue lever, not the cost lever. |

**Then the mapping strip** — four rows, `their world ≡ your world`:

| Assort Health | | Aria Home |
|---|---|---|
| Patient calls the practice | ≡ | Customer calls about a device |
| Identified, record pulled | ≡ | Account, plan and devices pulled |
| Scheduling, refills, verification | ≡ | Order status, device state, policy |
| After-hours bookings captured | ≡ | After-hours saves and renewals |

**Source line:** `livekit.com/blog/how-assort-health-uses-livekit-to-scale-patient-communication ·
assorthealth.com`

**DESIGN INTENT** — Two columns divided by a hairline: the vendor's numbers on the left, *their
customer's* numbers on the right. That nesting is the argument — it's proof one level deeper than a
logo wall. Give the **$1M+** its own emphasised block, separated from the 2×2, because it's the
only revenue number in the deck that already happened to a real company and it's the bridge to
slide 10's left column. The mapping strip is small and quiet at the bottom but it's what makes a
healthcare case study legitimate in a smart-home meeting — don't let it get squeezed out; if space
is tight, cut a metric, not the mapping.

**SPEAKER NOTES** — Healthcare, not smart home — say that first, then explain why it's the right
comparison: high inbound volume from a known customer base, caller identified on arrival, routine
handled, rest handed off warm. Structurally identical; only the nouns change. **The number for
Ahmad** is 90/10 with the handoff intact, at 4.3 out of 5 — automation customers rate well, not
automation they tolerate. **The number for Varun** is the last one: over a million dollars of new
revenue from bookings taken after hours. That's the revenue lever made concrete — the same shape as
an Aria Home subscriber who would have cancelled at 11pm and instead got an answer. *"This is the
closest thing we have to your business already running on us at scale, and it's their numbers, not
ours."*

---

### Slide 10 — The business case · **Varun** · ~5 min · **NEW, and the hardest build**

**COPY** — Eyebrow `THE BUSINESS CASE`. Buyer tag: `FOR VARUN · DRAG ANYTHING`.
Headline: **Two levers, not one.**

This slide is a **live calculator**. I operate it in the room with their numbers. It is the single
highest-value thing in the deck and the reason it beats a static value slide: a number the CFO
watches me compute from his own inputs survives the meeting; a number printed on a slide does not.

#### Layout: inputs left (~350px), outputs right

#### The eight inputs — all range sliders, with a live mono readout of the current value

| Input | id | Min | Max | Step | Default | Display format |
|---|---|---|---|---|---|---|
| Support calls per month | `calls` | 5,000 | 200,000 | 5,000 | 50,000 | `50,000` |
| Average call length | `mins` | 1 | 12 | 0.5 | 4 | `4.0 min` |
| Share handled by the agent | `pct` | 10 | 90 | 5 | 60 | `60%` |
| Loaded cost per human contact | `cost` | 3 | 20 | 0.5 | 8 | `$8.00` |
| Subscribers | `subs` | 50,000 | 2,000,000 | 50,000 | 400,000 | `400,000` |
| Subscription ARPU / month | `arpu` | 4 | 40 | 1 | 12 | `$12` |
| Monthly churn reduced by | `churn` | 0 | 1.5 | 0.05 | 0.3 | `0.30 pts` |
| Build & run programme / year | `prog` | 50,000 | 1,000,000 | 25,000 | 250,000 | `$250K` |

#### The cost model — LiveKit's published per-minute rates

These five rates are the credibility of the whole slide. They are LiveKit's own published prices,
so the cost side is auditable line by line rather than estimated. **Show them on the slide as a
visible ledger** — do not hide them behind the result.

| Line | Rate |
|---|---|
| Agent session | `$0.0100 / min` |
| Telephony, inbound US | `$0.0100 / min` |
| Speech to text | `$0.0117 / min` |
| Language model | `$0.0100 / min` |
| Text to speech | `$0.0300 / min` |
| **Per minute** | **`$0.0617`** |
| **Per 4.0-minute call** | **`$0.25`** |

*(The per-call row's label must update live with the slider: "Per 6.5-minute call".)*

#### The maths

```
aiCalls   = calls × pct
perCall   = mins × 0.0617
platMo    = aiCalls × perCall            // platform cost per month
avoidMo   = aiCalls × cost               // human cost avoided per month
netMo     = avoidMo − platMo
netYr     = netMo × 12                   // ← "Cost avoided / yr"

retained  = subs × churn × 12            // monthly churn delta, accumulated over a year
revYr     = retained × arpu × 12         // ← "Revenue protected / yr"

valueYr   = netYr + revYr
spendYr   = platMo × 12 + prog
roi       = (valueYr + platMo × 12) ÷ spendYr
payback   = spendYr ÷ (valueYr ÷ 12)     // in months
```

**At the defaults this yields:** revenue protected **$2.07M/yr** (14,400 subscribers retained) ·
cost avoided **$2.79M/yr** (30,000 contacts a month off the queue) · **13.4×** return, payback under
a month.

#### The three hero outputs — set very large, across the top of the right column

| Output | Value | Subline | Colour |
|---|---|---|---|
| Revenue protected / yr | `$2.07M` | `14,400 subscribers retained` | accent |
| Cost avoided / yr | `$2.79M` | `30,000 contacts a month off the queue` | good |
| Return on spend | `13.4×` | `Payback in under a month` | text |

**Revenue goes first, left-most.** That ordering is the argument — on a subscription business a
retained subscriber is worth far more than a deflected call, and every competitor leads with cost.

#### Beneath the heroes — a two-column ledger, all live

Left column `WHAT A CALL COSTS TO RUN` = the five rates table above.
Right column `AGAINST YOUR NUMBERS`:

| Row | Default |
|---|---|
| Calls to the agent / month | 30,000 |
| Platform cost / month | $7,404 |
| Human cost avoided / month | $240,000 |
| **Net saving / month** | **$232,596** |
| Subscribers retained / year | 14,400 |
| Total annual value | $4.87M |
| Total annual cost | $338,848 |

**Footer:** Per-minute rates are LiveKit's published prices, so the cost side is auditable rather
than estimated — and it lands well under the $0.50–2.00 per resolution the industry quotes. The
churn assumption is the one doing real work here; that is precisely what a pilot exists to measure.
Set it to zero and the cost case still stands alone. `livekit.com/pricing`

**DESIGN INTENT** — This is a UI, not a slide, so the craft shifts from typography to information
design: summary before detail, everything that recalculates visibly recalculating. The three hero
numbers must be readable from the back of the room; the ledger beneath them does not need to be —
it needs to *exist*, visibly, so Varun can see the work is shown. Sliders should look draggable
from three metres (a filled track and a clearly-sized thumb in the accent). Format currency
adaptively: `$2.07M` above a million, `$232,596` below. All figures tabular. **Watch the keyboard
conflict** — see §4 Interaction. And keep the whole thing on one screen without scrolling; if it
doesn't fit, shrink the ledger, never the heroes.

**SPEAKER NOTES** — Don't present it, **operate it.** Open by throwing out the defaults: *"Give me
your real call volume and your real cost per contact and let's see what falls out."* Then drag the
sliders in front of them. **The cost side is defensible line by line** — those five rates are
LiveKit's published prices, so the per-minute figure isn't a vendor estimate, and it lands well
under the $0.50–2.00 the industry quotes. **Lead with the left column anyway** — on a subscription
business a retained subscriber is worth far more than a deflected call, and that's the lever the
CFO actually runs the business on. **Be first to name the caveat:** the churn input is the
assumption doing the heavy lifting, and it's exactly what the pilot is designed to measure. Offer
to set it to zero and show the cost case still stands alone — volunteering that is what makes the
rest believable. *This is the slide the champion forwards to their CFO. Offer to send it.*

---

### Slide 11 — Your people & your brand · **Ahmad** · ~2 min

**COPY** — Eyebrow `YOUR TEAM & YOUR BRAND`. Headline: **Your agents do their best work. Your brand
stays trusted.**

**Left half — `YOUR TEAM` — "Augment, not replace."**
The calls that come off the queue are the ones nobody wanted — status checks, resets, "is it on?".
What's left is the work your best people are actually good at.
- Complex, emotional and safety-critical calls get a person with time to handle them properly.
- Repetition is what burns out tier-1. Removing the repetition is how you keep the person.
- Volume spikes — a firmware issue, a cold snap, a holiday launch — stop requiring a hiring plan.

**Right half — `YOUR BRAND` — "Support is part of the safety promise."**
You sell cameras and door locks. When a customer can't reach you, or reaches you and gets the wrong
answer, the failure lands on the product, not the queue.
- Always reachable — the same answer at 2am as at 2pm, in every timezone you ship to.
- Grounded in your own policies, so the answer is consistent no matter who asks.
- Every call transcribed and reviewable, which makes quality something you can measure rather than
  sample.

**DESIGN INTENT** — Two equal halves, hairline between. This is the deck's only slide with no
numbers on it and that's deliberate — it's the emotional beat, and the type should get room to
breathe rather than being packed to match the density of its neighbours. Resist adding an icon per
bullet.

**SPEAKER NOTES** — Say the quiet part first: *"I want to answer the question you're too polite to
ask. No, this is not a headcount plan."* Then make it concrete with the number from slide 10 — the
calls coming off his queue are the ones his best people least want, and what's left is what only
people can do. Attrition is the operational argument he'll recognise: burnout in tier-1 is driven
by repetition, and this removes the repetition rather than the person. **Then elevate it.** On
cameras and door locks, support isn't a cost centre attached to the product — it's part of the
product's safety promise. Being reliably reachable and reliably right at 2am is brand protection,
and it's the argument that makes Ahmad's function look strategic in front of Varun. *Do that for
him in the room and he becomes your champion.*

---

### Slide 12 — Why LiveKit & what happens next · close · ~3 min

**COPY** — Eyebrow `WHY LIVEKIT & WHAT HAPPENS NEXT`. Headline: **A proven stack, and a small first
step.**

**Credibility block** (one line, given its own emphasised treatment):
**OpenAI runs ChatGPT's voice mode on LiveKit** — millions of conversations a day. The same
infrastructure sits under Character.AI, Spotify and Reddit — and, if you'd like, under your support
line.

**The path — three steps, crawl → walk → run:**

| | **PILOT · 2 WEEKS** | **EXPAND** | **GROW** |
|---|---|---|---|
| | **One call type.** | **More intents, then the phone.** | **Outbound, not just inbound.** |
| | Order status and device state, on the web channel first. Your data, your policies, our infrastructure. | Subscription and billing questions, warranty, troubleshooting. Turn on SIP and point your existing number at it. | The same agent calls out — "your camera went offline", renewals, onboarding a new device. Support becomes a revenue motion. |
| **Measured on** | Deflection %<br>Containment & CSAT<br>Cost per contact<br>Subscriber save rate | *Gate: the pilot numbers, agreed today* | *Support is the beachhead, not the destination* |

**Three by-buyer lines:**
- FOR YOUR CUSTOMERS — Answered instantly, at any hour, without repeating themselves.
- FOR YOUR TEAM — Freed from the routine, and measurable for the first time.
- FOR THE BUSINESS — Revenue protected, cost in cents, and you keep control of the stack.

**Footer:** The ask: a two-week pilot on one call type, measured against numbers we agree before
anyone writes code. *Questions?*

**DESIGN INTENT** — Step 1 is fully lit; steps 2 and 3 are visibly dimmer. That gradient *is* the
de-risking argument — the ask is small and the rest is contingent, and it should be legible before
I say a word. The four pilot metrics need to read as a checklist, in the `good` colour, because
they are the yes/no gate. "Questions?" should be quiet, in the accent — it's the last thing on
screen while the room talks and it shouldn't compete.

**SPEAKER NOTES** — Drop the credibility line once, plainly, and don't oversell it: the
infrastructure under the most-used voice product in the world is the same infrastructure under your
support line. **Then make the ask small and measurable.** Two weeks, one call type, four metrics
agreed today, explicit gate: *"If we don't hit the numbers we agree in this room, you don't move
forward — and you'll have spent two weeks finding that out instead of two quarters."* De-risking
the decision is what actually closes it. **Plant the expansion** in one sentence and leave it
alone. Close with the three by-buyer lines, addressing each person by name — then stop talking and
open the floor. *Silence here is fine. Let them ask.*

---

## 6 · Fact-check appendix

Every number in the deck, with its source. **Designer: do not round, adjust or "clean up" any of
these.** If one doesn't fit the layout, tell me and I'll change the copy around it.

### Market & industry (slides 3, 10 footer)
| Claim | Source |
|---|---|
| 16 devices per US connected home; 52% had a technical problem last year, 38% two or more | Parks Associates, via IoT For All |
| 63% of consumers prefer phone for technical support | Parks Associates |
| 45–60% of tier-1 calls deflectable; 2026 median 41%, top quartile 59%; routine intents 70%+ | Fin AI / DigitalApplied 2026 |
| IoT devices pass 32.1 billion by 2030 | Statista |
| Gartner: 1 in 5 inbound service contacts from digital customers by 2026 | Gartner |
| $0.50–2.00 per AI-handled interaction; agent at $35–50K/yr loaded; 65–90% lower cost per interaction; $3.50 returned per $1, up to 8× | Fin AI, Retell, DigitalApplied |

### LiveKit pricing (slide 10 — verified 29 Aug 2026 at livekit.com/pricing)
| Line | Rate |
|---|---|
| Agent session minutes, overage | $0.0100 / min (all plans) |
| Telephony, US local inbound | $0.01 / min; number rental $1.00/mo after the first |
| Telephony, US toll-free | $0.02 / min; $2.00/mo rental |
| Third-party SIP | $0.003–0.004 / min |
| STT | $0.0025 – $0.0117 / min |
| LLM | $0.0002 / min (GPT-5 nano) – $0.0379 / min (GPT-5.5) |
| TTS | free (Deepgram Flux) – $0.1800 / min (ElevenLabs) |
| WebRTC participant minutes | $0.0005 / min (Ship) · $0.0004 / min (Scale) |
| Plans | Build $0 · Ship $50/mo · Scale $500/mo · Enterprise custom |
| Included agent minutes | 1,000 · 5,000 · 50,000 |

*The deck's model uses the premium end of STT and a mid-tier LLM and TTS on purpose — I'd rather
quote a defensible number than the cheapest possible one.*

### LiveKit platform & scale (slide 6)
300,000+ developers · billions of calls per year · thousands of concurrent agent sessions · 50+
models out of the box, 200+ via plugins · ~1/4 of US 911 dispatch centres · turn detector 85% true
positive / 97% true negative · SOC 2 Type II, HIPAA, GDPR, CCPA, E2EE, regional data residency
(compliance features from the Scale tier up) · self-hosted or custom cloud on identical APIs.

### Assort Health (slide 9)
27M patient-facing interactions handled; 20M+ carried on LiveKit · 90% of inbound handled by the
agent, 10% handed off · 4.3/5 satisfaction · 99%+ accuracy · quote from Jeffery Liu, Founder &
Co-CEO. Their customer **Chesapeake Health Care**: 150+ providers across six specialties, hold time
−89%, satisfaction 2.6 → 4.4, $1M+ new revenue from after-hours bookings. Sources:
`livekit.com/blog/how-assort-health-uses-livekit-to-scale-patient-communication`, `assorthealth.com`.

### Our own build (slide 8)
EOU 312 ms · TTFT 288 ms · TTFB 141 ms · perceived 741 ms median, p95 934 ms · transport ~40 ms.
RAG grounding proofs: doorbell camera return window **14 days**; damaged-device report window **48
hours** — both unique to the Aria Home returns policy document.

### ⚠️ Verify before the meeting
1. **Slide 8's three latency numbers** — re-run the instrumented session; these drift with model
   and region. I'll hand the designer finals.
2. **The 300,000 developer figure** — LiveKit's product page says 300,000+ and billions of calls;
   an older blog post says 100,000 and 3 billion. Use the product page and re-check the week of.
3. **Chesapeake Health Care's figures** come from Assort Health's own marketing. Fine to cite with
   attribution; don't restate them as LiveKit's numbers.
4. **The $1B valuation / OpenAI partnership line** (slide 12) — confirm it's still the current
   public framing.

---

## 7 · Delivery checklist

- [ ] 12 slides, 16:9, fixed 1280×720 base, scaled to fit
- [ ] Single committed theme, every colour painted explicitly, no `prefers-color-scheme`
- [ ] Keyboard: ← → Space PageUp PageDown Home End · `S` notes · `F` fullscreen
- [ ] **Arrow keys and Space pass through to the calculator's sliders when focused**
- [ ] Speaker-notes panel carrying the notes from every slide above, verbatim
- [ ] Slide counter + progress bar + prev/next buttons
- [ ] Nothing below 12px at base; all figures tabular
- [ ] Self-contained single file: inline CSS and JS, Google Fonts allowed, no other external assets
- [ ] `<title>`: `Aria Home Support Line`. Favicon: 🎙️
- [ ] `prefers-reduced-motion` honoured; visible keyboard focus everywhere
- [ ] Slide 8's three "This build" numbers isolated so they're a one-line swap
- [ ] Placeholders filled: my name on slide 1, month/year on slide 1

---

## 8 · Notes on cutting

If the deck runs long in rehearsal, cut in this order — and never cut the demo:
1. **Slide 11** (people & brand) — fold its two arguments into the speaker track on slide 4.
2. **Slide 8** (measured) — keep only the grounding-proof half, drop the latency table.
3. **Slide 2** (agenda) — say it instead of showing it.

Slides 9 and 10 are the two that most often decide a deal. Protect them.

---

# Amendment A — the API gateway (Apigee)

Added 29 Aug 2026. **Slides affected: 5 (redraw), 6 (one cell), 10 (footnote), 12 (pilot scope), plus one new slide 5B.** Net: 12 → 13 slides.

## A.1 · Why this earns a slide

The gateway answers a question the deck currently ducks: *"how does this land in an enterprise
estate we already run?"* Three arguments, in descending order of strength:

1. **It contains the failure mode we actually hit.** During the build, the model got a `ToolError`
   from a slow carrier lookup, retried, and filed **four duplicate support tickets** for one
   customer. That is not a hypothetical — it's logged in `build-archive/README.md`, known bug #1.
   An LLM under retry pressure is an unbounded client pointed at internal systems. SpikeArrest and
   Quota at the gateway bound it in a way that prompt engineering cannot. **This is the strongest
   thing we can say to Mike all meeting, because it's a real incident with a real fix.**
2. **One audit boundary for a security product.** Every device state read, every lock query, every
   escalation summary through one place, logged with PII masking. On cameras and door locks, "who
   asked what, when, on whose behalf" is a compliance artefact, not a nice-to-have.
3. **Their IAM, not ours.** The agent authenticates to the gateway; the gateway authenticates to
   backends with the customer's existing service identity. No LiveKit-shaped credentials inside
   their network.

## A.2 · The honest costs — say these before Mike does

- **A hop on the tool path.** Roughly 10–20 ms added per tool call. It is *not* on the media path
  and *not* in the turn budget on slide 8, which is why those numbers don't move. Say that
  explicitly or it looks like we're hiding it.
- **A component that can be down.** The agent must degrade rather than fail: if a tool call fails,
  it says it can't reach the system and escalates. That behaviour already exists in the build —
  demo it if challenged.
- **Vendor framing.** This is a **LiveKit** meeting. Do not present Apigee as part of the LiveKit
  architecture. It sits entirely inside *their* cloud, on *their* side of the boundary, and the
  slide says **"your API gateway"** with Apigee named as the instantiation because they're a Google
  shop. If they run Kong or AWS API Gateway, the slide is unchanged but for the logo. Getting this
  wrong makes it look like we're reselling someone else's product.

## A.3 · Corrections to the plan as drafted

The Apigee policy XML is broadly sound — `VerifyJWT` with a JWKS source, `ServiceCallout`, and
`GenerateJWT` with HS256 against the LiveKit API secret is the right shape, and `iss` = API key /
`sub` = identity / a `video` grant is what LiveKit expects. Five things need fixing before any of
it goes near the demo or the room.

| # | Problem | Fix |
|---|---|---|
| 1 | **The agent code is the deprecated 0.x API** — `VoiceAssistant`, `llm.FunctionContext`, `llm.ai_callable`, `AutoSubscribe`, `assistant.start(room)`. Our build is on **livekit-agents 1.7.0**: `AgentServer`, `@server.rtc_session`, `Agent`, `AgentSession`, `@function_tool`. The pasted code will not run against this repo. | Keep `src/agent.py` as it is. See A.6 — the real change is four lines. |
| 2 | **It throws away MCP.** The plan replaces our MCP tool boundary with raw `httpx` calls. MCP *is* the modern, defensible integration story and it's already deployed and working. Replacing it is a regression in both architecture and narrative. | **Apigee goes in front of the MCP server, not instead of it.** The agent keeps speaking MCP; Apigee is the proxy the MCP endpoint sits behind. |
| 3 | **PII in the token.** The plan stuffs the whole CRM profile — devices, subscription, account — into the JWT `metadata` claim. A JWT is base64, not encrypted, and it is handed to the customer's browser. For a company selling door locks, that's a data-exposure question we should not invite. | Put `account_id` and display name in the token. The agent fetches the profile server-side through the gateway on session start. One extra call, well under the greeting. |
| 4 | **The phone path is missing.** The token proxy is web-only by construction — an inbound SIP caller has no browser and mints no token. The plan silently covers half the architecture, and slide 5 promises both. | Say it on the slide: **northbound token minting is the web path; the southbound tool gateway covers both.** Phone callers are identified by ANI, which is what `lookup_account(phone)` already does. |
| 5 | **Wrong model stack and a wrong call** in the snippet — Deepgram/Cartesia/`gpt-4o-mini`, and `openai.VAD.load()` (VAD is Silero). Ours is AssemblyAI `universal-3-5-pro`, `google/gemma-4-31b-it`, FishAudio `s2.1-pro` via `inference.*`. | Don't show that snippet to anyone. |

Also drop **"sub-100ms WebRTC"** from the Mike script. We have real measured numbers on slide 8 —
use those. An unsourced round number sitting next to a measured table undercuts the table.

## A.4 · NEW Slide 5B — The boundary you already own · **Mike** · ~2 min

Sits immediately after slide 5 (architecture) and before slide 6 (platform). Short slide — it
answers one question and gets out.

**COPY** — Eyebrow `THE BOUNDARY YOU ALREADY OWN`. Headline: **The agent is a client of your API,
not a guest in your network.** Dek: Every call into your systems goes through your own gateway —
your auth, your quotas, your audit log.

**Three cards:**

1. **GOVERNED — "An LLM is an unbounded client."**
   Spike arrest and quotas cap what the agent can do to your IoT backends, however hard the model
   retries. In our own build a tool timeout caused the model to retry and file four duplicate
   tickets for one customer. A quota at the gateway is the fix; a better prompt is not.
2. **AUTHENTICATED — "Your IAM, not ours."**
   The agent holds one credential to your gateway. The gateway authenticates to CRM, device
   telemetry and policy stores with the service identity you already run. No LiveKit-shaped
   credentials inside your network, and one place to revoke.
3. **AUDITED — "One log line per device read."**
   Every account lookup, device query and escalation summary in one place, with PII masking, into
   your logging and BigQuery. On cameras and locks that's a compliance artefact, not telemetry.

**Footer:** This sits entirely in your cloud — Apigee here because you run on Google, but the shape
is the same behind Kong or AWS API Gateway. It adds roughly 10–20 ms to a tool call and nothing at
all to the audio path: the latency budget on the next slides is measured with it in place.

**DESIGN INTENT** — Three cards, same construction as slide 4's four, so it reads as a continuation
rather than a new system. The retry-storm anecdote in card 1 is the payload of the whole slide —
give it its own line, visually separated, in the `warn` colour. It's the only place in the deck we
admit something went wrong, and that admission is doing more persuasive work than any of the
claims around it. Keep the footer's latency figure visible; volunteering the cost is the point.

**SPEAKER NOTES** — Open by naming the anxiety directly: *"The question behind every integration
slide is 'what is this thing allowed to do inside my network'. The answer is: exactly what your
gateway lets it do, and nothing else."* Then tell the retry story straight — *"I hit this on my own
build. A carrier lookup timed out, the model retried, and it filed four tickets for one customer
before I caught it. I fixed it in the agent with idempotency, but the durable fix is a quota at the
boundary, because the agent is the thing you can't fully trust."* **That story is the most
credible ninety seconds available to you** — a vendor describing their own failure and where the
control belongs. Then the two costs, unprompted: one extra hop of 10–20 ms on the tool path, not
the audio path; and a component that can be down, which is why the agent escalates rather than
guesses when a tool fails. Offer to demo that failure. *If Mike is a Google Cloud shop this is also
where he relaxes — it's his existing control plane, not a new one.*

## A.5 · Amendments to existing slides

**Slide 5 — architecture diagram, redraw.** Insert a gateway between the LiveKit zone and the
"YOUR CLOUD" zone. The dashed data edge now terminates at `YOUR API GATEWAY` (a full-height narrow
band at the left edge of the YOUR CLOUD box), and three short dashed edges continue from it to CRM,
Policy knowledge and Warm transfer. Two labels on the band: `Auth · Quota · Audit` and, smaller,
`Apigee`. This makes the boundary a *visible wall with one door* rather than three arrows crossing
open space — which is the entire security argument, drawn.
Amend the slide-5 footer to: *"…what crosses the line is a scoped tool call through your own
gateway — authenticated, rate-limited and logged — not your customer database."*

**Slide 6 — platform grid.** Change the **Agents SDK** cell's second line to: *"Your code, your
control flow, your tools — pointed at your API gateway, not at your databases."* No new cell; slide
5B carries the argument.

**Slide 10 — calculator footer.** Append: *"Quotas at the gateway also bound the downside: the
agent cannot generate unbounded backend load, so the cost line stays predictable under a bad
deploy."* Governance as cost predictability is the only Apigee argument Varun will care about — one
sentence, no slide.

**Slide 12 — pilot scope.** Add to the PILOT card: *"Through your gateway from day one — the pilot
proves the integration pattern, not just the voice."* This matters: a pilot that bypasses their
gateway proves nothing about production.

## A.6 · The actual code change

Not a rewrite. Our tool boundary is already MCP over HTTP, so pointing it at an Apigee proxy is a
config change. In `Assistant.__init__`, `src/agent.py:51`:

```python
self._gcp_mcp = mcp.MCPServerHTTP(
    url=os.getenv("APIGEE_MCP_URL", MCP_DIRECT_URL),   # Apigee proxy in front of the MCP server
    transport_type="streamable_http",
    headers={"x-api-key": os.environ["APIGEE_AGENT_KEY"]},
    timeout=20,
)
```

`MCPServerHTTP` takes `headers: dict[str, Any] | None` — verified against the installed
livekit-agents 1.7.0. Defaulting `APIGEE_MCP_URL` to the direct Cloud Run URL keeps the current
demo working if the gateway isn't up, which is the right posture for a live meeting.

The in-agent `@function_tool` methods (`transfer_to_human`, `request_refund`, `check_warranty`,
`sync_device`, `track_package`) stay exactly as they are — they touch the room or model async
patterns, not backend data.

On the Apigee side, two proxies as drafted, with correction #3 applied: `/v1/voice/token` verifies
the customer IDP JWT and mints the LiveKit token carrying **`account_id` and display name only**;
`/v1/mcp` fronts the MCP server with `VerifyAPIKey`, `SpikeArrest`, `Quota` and `MessageLogging`
with PII masking.

## A.7 · The three buyer scripts, corrected

**Mike** — *"The media path and the business-logic path are separate on purpose. LiveKit carries
the audio and runs the agent next to the models — that's the 741-millisecond number you'll see in
two slides. Everything the agent wants to know about a customer goes out through your own API
gateway: your auth to your backends, your quotas, your audit log. That's what stops an LLM under
retry pressure from becoming an unbounded client pointed at your IoT services — which I say
because it happened to me, and I'll show you the incident."*

**Ahmad** — *"Two things it buys your team. The caller is identified before the agent says a word,
so nobody reads out an account number. And when it escalates, the summary is delivered as
structured data into the system your people already work in — Zendesk, Salesforce, whatever you
run — so the specialist is briefed before they pick up, not after."*
*(Only name a CRM if they've told us which one. Guessing is worse than "the system your people
already work in".)*

**Varun** — *"One place where usage is metered and capped. It keeps the cost line predictable if a
deploy goes wrong, and it means adding the second and third use case later is a policy change
rather than a new integration project."*

## A.8 · Rehearse the pushback

- **"Why not have the agent hit our services directly?"** — You could, and it'd be one hop faster.
  You'd also be giving an LLM direct credentials to your device control plane with no quota between
  them. I'd rather spend 15 milliseconds on the tool path than argue that trade in a post-incident
  review.
- **"Doesn't the gateway become the bottleneck?"** — It's on the tool path, not the media path.
  Tool calls already sit in the 100–300 ms band and run concurrently with speech; the audio budget
  on slide 8 is measured with the gateway in place.
- **"We don't use Apigee."** — Then this slide is about whatever you do use. Nothing about the
  agent changes; it speaks HTTP to one endpoint you control.
- **"What happens when the gateway is down?"** — The agent says it can't reach that system and
  escalates to a person. It never invents an answer. I can demo that failure now if you want.
