# Panel Demo — Build Plan (finalized 2026-08-28)

Second interview: Solutions Architect panel (mock customer meeting), 30 min, 3 personas (Mike=technical, Ahmad=support, Varun=finance). Customer = a smart-home company (demo name "Aria Home"). Build the voice agent + a 3–5 slide deck.

**Decisions made:** Interface = **Both** (web primary for reliability + real SIP transfer). Data = **keep MCP/CRM on GCP** (extend the deployed store — preserves the "external systems / data flows" story).

## Feasibility
Agent already uses the LiveKit Cloud pattern (`AgentServer` + `@server.rtc_session` + `cli.run_app`) → GKE→LiveKit is a deploy change, not a rewrite. Moving to LiveKit Cloud removes the agent↔inference cross-cloud hop and gives autoscale + graceful drain + built-in observability for free. Data (MCP/CRM, RAG) stays on GCP.

## Revised architecture
Caller (phone SIP / web WebRTC) → **LiveKit Cloud** (Room/SFU + Inference + **Agent, co-located**) → **GCP**: Account+Device CRM via MCP · RAG policies · warm transfer to a human number (with summary).

## Phase 1 — Move agent to LiveKit Cloud
- Confirm creds; `lk agent create` (region US East) → build image, deploy, register `anycompany-agent`, write `livekit.toml`.
- Enable Agent Observability (project level). Test via Sandbox web voice agent. Decommission GKE (keep yaml archived).

## Phase 2 — Extend MCP/CRM (covers brief #1, #2, #4)
- Account model: name, phone, account_number, subscription{tier,status}, devices[], orders[].
- Device model: name, type, room, state{active, reading}.
- Tools (MCP): `lookup_account(phone|account_number)` (greet by name) · `get_device_state(room_or_device)` · `get_room_temperature(room)` · order status (existing) · RAG `search_knowledge` (subscription/policy).
- Seed data: Sarah Chen (+1…, acct #, video plan, thermostat + 2 cameras + lock), plus 2–3 more accounts.

## Phase 3 — Transfer-to-number WITH summary (brief #3)
- `transfer_to_human(reason)`: (1) generate a short conversation summary, (2) warm SIP transfer to another number (trunk + `publish SIP participant`), pass summary to the human (spoken on bridge + shown on screen).
- Web fallback: bring a "human" participant into the room (existing escalate pattern) + display the generated summary.
- Build summary first (reliable), then layer transfer.

## Phase 4 — Slides + rehearsal
- Slide prompt: DONE — `presentation/slide-prompt.md`, xAI-deck aesthetic (near-black, big Helvetica, mono eyebrows, bordered/stat cards, demo-timeline slide), updated for the smart-home brief + 3 personas + new architecture. User generates the deck in Claude Code.
- Rehearse 30-min flow vs the Panel Meeting Primer; test demo end-to-end with seeded data.

## Companion artifacts
- Panel Meeting Primer: https://claude.ai/code/artifact/66eec542-8121-4f15-b62e-433eec6a8469
- The AnyCompany Build (deep doc): https://claude.ai/code/artifact/c0d8cb95-17f0-40da-b0ce-c82ed69dfce4
- The LiveKit Side (cheatsheet): https://claude.ai/code/artifact/a4a6e277-1c92-474a-868c-7bd3126f4645

## Naming
Demo customer = "Aria Home" (swappable). Update agent instructions from "AnyCompany Smart Home" → the demo name for consistency.

---

## Deploy commands (user runs — needs interactive TTY auth)

The agent is already coded to the LiveKit Cloud pattern (`AgentServer` + `@server.rtc_session` + `cli.run_app`) and has a working `Dockerfile`. To move it off GKE onto LiveKit Cloud hosting:

```bash
cd /Users/nabilrehman/Downloads/livekit/anycompany-agent

# 1. Authenticate the CLI (needs a TTY — run it yourself)
lk cloud auth

# 2. Create + deploy the agent to LiveKit Cloud (builds the Docker image on their build service)
lk agent create        # region: US East. Writes livekit.toml, uploads code, builds, deploys.
#   When prompted for secrets, provide the SAME ones from .env.local:
#     LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
#   Plus (optional, for the transfer beat):
#     TRANSFER_TO_NUMBER      = +1XXXXXXXXXX   (point at your own phone for the demo)
#     SIP_OUTBOUND_TRUNK_ID   = <trunk id>     (leave unset to use the in-room fallback)

# 3. Later, to push changes:
lk agent deploy

# 4. Enable Agent Observability: LiveKit Cloud dashboard -> Settings -> Project ->
#    Data and privacy -> Agent Observability -> on.  (Great for the live demo.)

# 5. Once verified on LiveKit Cloud, decommission GKE:
kubectl delete -f /Users/nabilrehman/Downloads/livekit/build-archive/deploy/aug24-agent-gke.yaml
```

The web app + MCP stay on Cloud Run (already redeployed); Firestore + Vertex RAG stay on GCP. Only the AGENT moves — which removes the agent<->inference cross-cloud hop.

### Transfer beat — enabling real SIP dial-out (optional)
Without a trunk, `transfer_to_human` still (a) generates the summary, (b) shows it in the web summary panel, (c) speaks the handoff — and a specialist can join the room manually (`lk room join --identity human-agent <room>`). For real dial-out to a phone, create an outbound SIP trunk and set `SIP_OUTBOUND_TRUNK_ID` + `TRANSFER_TO_NUMBER`.
