# Slide-deck generation prompt — LiveKit smart-home support agent (presales, principal-level business story)

> Paste the block below into a fresh Claude Code / Claude session to generate the deck.
> Built around how a principal solutions engineer sells business VALUE: customer-first, pain quantified, TWO value levers (protect revenue + cut cost), tailored to each buyer, demo as a hero's journey, de-risked with pilot metrics, and a land-and-expand close. The design is the deck's own — do NOT copy any other company's look.
> Swap "Aria Home" for the customer name you choose.

```
Build me a self-contained, keyboard-navigable SLIDE DECK as a single HTML artifact for a live customer meeting. I am a Solutions Architect at LiveKit presenting a voice customer-support agent to a prospective customer, "Aria Home" — a smart-home company selling connected devices (thermostats, cameras, door locks, sensors) PLUS a subscription tier for cloud video storage and monitoring (recurring revenue). Their customers have accounts with registered devices, a subscription status, and order history. I present these slides live and switch to a live demo in between.

THE ROOM — three buyers; speak to each in their language and LABEL whose slide is whose:
- Mike, Director of AI Platform — TECHNICAL buyer. Architecture, integration, latency, security, maintenance burden.
- Ahmad, Director of Customer Support — USER/operational buyer. Customer experience, his agents' jobs, day-to-day workflows.
- Varun, VP of Finance — ECONOMIC buyer. Cost per outcome, ROI, and — because this is a subscription business — protected recurring revenue.

PRESALES PRINCIPLES TO APPLY THROUGHOUT (this matters more than any visual):
1. Customer-first. Every slide is about THEM. Their name, their world, their words. Recap their situation before proposing.
2. Sell outcomes, not features. Never a capability without the outcome for a real person.
3. TWO value levers, not one. This is a subscription company: sell (a) PROTECT & GROW RECURRING REVENUE — better support cuts churn and creates in-call renewals/upsell; a saved subscriber is worth far more than a saved call — AND (b) CUT COST of the routine. Cost-only is a weak story here.
4. Quantify pain → value. Number the problem, scale it, then show ROI = (value gained − cost) ÷ cost. Benchmarks now; their real numbers proven in a pilot.
5. Why now. Name the cost of the status quo — rising IoT volume, longer waits, churn, competitors deploying voice AI. Give a reason to act now.
6. Tailor to the buyer. Each content slide serves one buyer; speaker notes say which and how to pivot it for the others.
7. The demo is a hero's journey. The caller (Sarah) is the hero; the agent is the guide; arc is pain → resolution; "watch for" cues prime each beat.
8. Augment, don't replace. For the support director: the agent frees his people from tier-1 to handle complex, high-value, safety-critical calls — better jobs, lower attrition. Say this or he resists.
9. Trust & safety is a business value. These are cameras and door locks — a wrong or unavailable answer is a trust/safety failure on a security product. Grounded, accurate, always-on support PROTECTS THE BRAND.
10. De-risk the decision. Define the pilot's success metrics up front (deflection %, containment, CSAT, cost/contact, subscriber save-rate) and a crawl→walk→run path.
11. Land and expand. Support is the beachhead; the same agent later does proactive outbound ("your camera went offline"), renewals, onboarding. Plant it.
12. Proof beats claims. Real cited case studies and benchmarks, not adjectives.

DESIGN DIRECTION (the deck's OWN identity — considered and distinctive, not a template, not a copy of anyone else's deck):
- Commit to ONE clean, confident, modern B2B look and execute it precisely. A deliberate neutral ground (not pure grey) + ONE confident accent used sparingly; a positive/green semantic color for savings & wins, separate from the accent. Light-ground editorial OR a considered dark — pick one and hold it.
- Typography carries it: pair a characterful-but-professional display face with a clean body face (Google Fonts allowed), a real type scale, generous whitespace, one idea per slide. Large readable headlines; small tracked/mono eyebrow labels.
- Data as design: big-number stat treatments for the quantified pain and the ROI; a clean value table; a horizontal timeline for the demo. Charts/numbers get the same care as type.
- Avoid the generic AI-deck look (cream+serif+terracotta, purple gradients, everything centered, emoji headers). Deliberate, subject-specific choices.
- Theme-aware or committed single-theme, but paint background + all colors explicitly. Respect prefers-reduced-motion.

FORMAT:
- 16:9, each slide fills the viewport. Navigate: ← / → arrows, spacebar = next, on-screen prev/next; a "3 / 9" counter + thin progress bar. Press "S" toggles a speaker-notes panel with my talk-track + which buyer each slide serves.
- Self-contained (inline CSS/JS, Google Fonts OK, no external images/scripts). Responsive; never horizontal-scroll. Set <title> + a favicon emoji.

THE SLIDES (9):

1 — TITLE (customer-first)
- Headline names the OUTCOME for them: "A support line that already knows your customer."
- Subline: "Voice AI customer support for Aria Home — built on LiveKit."
- Quiet footer: "[MY NAME] · Solutions Architect, LiveKit  ·  Prepared for Aria Home · [Month Year]".
- Note: I introduce myself + purpose in one line, then invite the panel to introduce themselves so I can tailor.

2 — AGENDA (them before us)
- "What we'll cover": 01 Introductions · 02 Where you are today · 03 What we'd build · 04 Live demo · 05 The business case · 06 Next steps.
- Note: point out the order — their situation before our solution; invite interruptions.

3 — WHERE YOU ARE TODAY (quantify pain + why now — Ahmad's & Varun's slide)
- Eyebrow "WHERE YOU ARE TODAY". Headline: "Every device sold is a support call waiting."
- Four big-number stat cards (REAL cited figures — keep them):
  * "16" — devices per US connected home; 52% hit a technical problem last year.
  * "63%" — of consumers still prefer to handle tech support over the phone.
  * "45–60%" — of tier-1 calls are deflectable by voice AI.
  * "24/7" — customers expect it; and on cameras and locks, an unanswered call is a trust problem.
- Footer (the WHY NOW): "IoT devices pass 32 billion by 2030; every extra minute of wait is churn risk on a subscription. This compounds — and your competitors are already deploying voice AI. (Parks Associates · Gartner)"
- Note: discovery reflected + benchmarks; land the pain, name that it scales AND costs revenue, then earn the right to propose. Ask "does this match what you're seeing?"

4 — WHAT WE'D BUILD (solution mapped 1:1 to the pain; outcomes — Ahmad's slide)
- Eyebrow "WHAT WE'D BUILD". Headline: "One voice agent, four jobs."
- Four cards, each an OUTCOME + the pain it removes (mirror slide 3's order):
  * IDENTIFY — "Knows who's calling." Greets by name, pulls account + devices + subscription (by phone or account #). Removes: repeating account details.
  * RESOLVE — "Answers the routine." Order status, is my thermostat active, living-room temperature. Removes: the 45–60% of calls that never needed a human — freeing your agents for the complex, safety-critical ones.
  * HAND OFF WARM — "Escalates without the restart." Transfers to a person WITH a summary. Removes: customers repeating themselves; agents starting cold.
  * STAY GROUNDED — "Accurate, or it escalates." Answers from your policies (RAG), never guesses — on security devices, a wrong answer is a trust failure. Removes: brand risk.
- Note: each job answers one thing from slide 3; note the RESOLVE card augments agents (not replaces), and STAY GROUNDED is a trust/brand point, not just accuracy.

5 — HOW IT WORKS (architecture as intent → system → output — Mike's slide)
- Eyebrow "HOW IT WORKS". Headline: "Where your data flows."
- Inline SVG, left→right, THREE distinct edge types + legend: solid = realtime voice (WebRTC), dashed = data/tool call, accent = human transfer.
  * CALLER (left): "Phone (SIP) or Web (WebRTC)".
  * LIVEKIT (center, emphasized): Room/SFU (media) + Inference (STT·LLM·TTS·turn) + the Agent — "joins the room as a participant, co-located with the models."
  * YOUR SYSTEMS (right, your cloud): Account & Device CRM (lookup by phone/account #, subscription, device state) behind an MCP boundary; Policy knowledge (RAG); Warm transfer to a human number (with summary).
- Footer: "YOUR SYSTEMS  ·  Account CRM (MCP)  ·  Device state  ·  Policy knowledge (RAG)  ·  Warm transfer".
- Note (Mike): agent is a participant not a backend; runs on LiveKit co-located with inference (one hop) while your customer data stays in YOUR cloud behind the MCP boundary — integration + security in one picture. Offer to go deeper on any box.

6 — LIVE DEMO (hero's journey — prime it, then run the agent)
- Eyebrow "LIVE DEMO". Headline: "One caller, ninety seconds." Caller chip: "Sarah Chen · Aria Home customer · Video Plus plan · thermostat + 2 cameras + lock".
- Horizontal timeline, 4 beats, each a short line + muted "Watch for:" cue (pain → resolution):
  * :00 "Hi Sarah." — identified by number, greeted by name, devices confirmed. Watch for: no account number needed.
  * :20 "Is my thermostat on?" — live device state: active, living room 71°. Watch for: a real tool call, not a guess.
  * :40 "Where's my order?" — order status, specific and grounded. Watch for: it never makes something up.
  * :60 "I need a person." — warm transfer to the subscription team WITH a summary on screen. Watch for: the human is already briefed.
- Footer: "Every step is a tool call into your systems — nothing scripted."
- Note: bridge to the live demo; caller is the hero, agent is the guide; say each "watch for" out loud first.

7 — THE VALUE (TWO levers: protect revenue + cut cost — Varun's slide; REAL cited numbers)
- Eyebrow "THE BUSINESS CASE". Headline: "Two levers, not one."
- Left column — PROTECT & GROW REVENUE (lead with this): "A saved subscriber is worth far more than a saved call." Faster, better support cuts subscription churn and creates renewal/upsell moments in-call. One stat: even a 1–2 point churn reduction on a recurring base dwarfs call-cost savings. (Frame as the CFO's real lever.)
- Right column — CUT COST: "$0.50–2" per AI resolution (vs a $35–50K/yr agent) · "65–90%" lower cost per interaction · "$3.50" returned per $1 (up to 8×). Worked example card: "50,000 calls/month → 60% to AI → ≈ $2.5M/year saved (illustrative; your numbers we prove in a pilot)."
- Footer proof strip: "PROVEN  ·  PAL Airlines: wait < 1 min, cost −30%  ·  a 35-agent retailer: −86% wait, +45% CSAT."
- Note: LEAD with revenue/retention (churn saved), THEN cost. ROI = (value − cost) ÷ cost. This is the slide a champion forwards to their CFO.

8 — WHAT IT MEANS FOR YOUR PEOPLE & BRAND (Ahmad's slide — augment + trust)
- Eyebrow "YOUR TEAM & YOUR BRAND". Headline: "Your agents do their best work. Your brand stays trusted."
- Two halves:
  * YOUR TEAM — the agent handles tier-1 so your people take the complex, emotional, safety-critical calls — better jobs, lower burnout and attrition, no hiring for every volume spike. Augment, not replace.
  * YOUR BRAND — on cameras and door locks, support IS part of the product's safety promise. Always-on, accurate, consistent answers protect customer trust; every call transcribed and reviewable.
- Note: this is Ahmad's slide — pre-empt the "are you replacing my team?" fear directly; elevate support quality to a brand/safety argument.

9 — WHY LIVEKIT + THE PATH FORWARD (trust close + de-risked next step + expand)
- Eyebrow "WHY LIVEKIT". Headline: "The stack behind the world's biggest voice product — and a low-risk path in."
- Credibility line: "OpenAI runs ChatGPT's voice mode on LiveKit — millions of conversations a day. Same infrastructure under Character.AI, Spotify, Reddit — and now your support line."
- THE PATH (crawl→walk→run, with success metrics): "PILOT (2 weeks) — one call type, measured on deflection %, CSAT, cost/contact, and subscriber save-rate → EXPAND — more intents, phone + web → GROW — proactive outbound ('your camera went offline'), renewals, onboarding." Make the success metrics explicit so there's a clear yes/no gate.
- One line by buyer (label by outcome): FOR YOUR CUSTOMERS — instant, 24/7, no repeating. FOR YOUR TEAM — freed for what matters. FOR THE BUSINESS — revenue protected, cost in cents, you own the stack.
- Footer: "NEXT  ·  a two-week pilot on one call type, measured against numbers we agree today." + a quiet "Questions?".
- Note: unifying close; drop the OpenAI credibility line; end on the low-risk, measured next step and the expand vision, then stop and open the floor.

Make it polished and presentation-ready. After building, tell me the keyboard controls and how to present it full-screen.
```
