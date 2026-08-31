# Aria Home architecture slide — FINAL spec + value narrative
(Exec audience: Head of AI, Head of CX, CFO — with architect footnotes.
Verified against the code on 2026-08-31.)

## Layout (three panels + two seams)

LEFT — CALLERS: photoreal thumbnails 'App (signed in)', 'Web (guest)',
'Phone'; caption 'every channel, one front door'.
SEAM 1 (callers → LiveKit): small lock/badge glyph on the arrows,
micro-label 'verified first'. (Covers Firebase login AND the in-call
security question; no box, no product name.)

CENTER — LIVEKIT CLOUD: Ember avatar · 'listens · thinks · speaks' ·
shield 'guarded' · strip: 'answers in under a second · keeps talking
through outages · tested by simulated customers'.
BELOW-LEFT: photoreal Support specialist. ONE orange arrow, tail at the
LiveKit panel, head at the specialist, label 'warm transfer
(SIP / WebRTC)'. Orange cloud bubble at the SPECIALIST (never touching
the LiveKit panel): 'INCOMING CALL / Nabil — frustrated / Order hasn't
shipped yet / Next: approve the refund'.

SEAM 2 (Ember → data): slim vertical GATE STRIP fused to the Google
panel's left edge; all four arrows pierce it; micro-label
'identity-checked gateway', tiny grey 'Cloud Run'.

RIGHT — GOOGLE CLOUD: four cards + grey product sublabels + arrow tags:
- 'Your orders & account' / Cloud SQL — arrow tag: REST
- 'User device data — live' / Firestore — arrow tag: REST · MCP
- 'Product & policy answers' / Vertex AI RAG Engine — arrow tag: MCP
- 'Remembers you — pets, preferences' / Vertex AI Memory Bank — MCP
Caption: 'each customer sees only their own data'.

FOOTER: 'Runs on the systems you already have — every transfer arrives
fully briefed.'

## Why each element is true (code receipts)
- verified first: /token (Firebase), IdentifyCallerTask + /api/verify (KBA)
- gate strip: every arrow lands on Cloud Run; X-Account injected
  server-side; DB enforces via parameterized secure views (role has no
  base-table access)
- REST·MCP split: /api/my/* = REST; get_device_state/history,
  search_knowledge, remember/recall = MCP; account lookups = MCP Toolbox
- under a second: measured turns 0.6–1.2s; backend calls 26–265 ms
- keeps talking through outages: STT/LLM/TTS failover in-session
- simulated customers: Coval simulations against the live agent
- fully briefed transfer: LLM brief (summary/mood/next step), PII-masked

## The value, per seat (say these, in this order)
- CFO: "No new platform. It's Cloud Run, Cloud SQL, Firestore — systems
  you already pay for — plus LiveKit for the realtime layer. A transfer
  is a person joining a call, not a second stack."
- Head of CX: "Callers are verified before anything is revealed, never
  repeat themselves — the human picks up already knowing Nabil is
  frustrated and why — and she remembers the dog's name next month."
- Head of AI: "The model is a bounded participant: identity gates the
  tools, the database enforces isolation, guardrails sit between the
  model and the voice, and simulated customers regression-test every
  change. The clever parts are structural, not prompt hopes."

## One-line thesis
"Identity is pluggable, everything after it is one guarded path —
on infrastructure you already own."
