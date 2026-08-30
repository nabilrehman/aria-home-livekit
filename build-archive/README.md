# AnyCompany Voice Agent — Build Archive

Everything from the LiveKit SE interview prep + the live GCP build. Two goals this serves:
1. **The presentation** — see `presentation/` (published artifacts) + the talk-tracks inside them.
2. **Making the agent work properly** — see `deploy/` (code + config) + the Known Bugs below.

Saved 2026-08-25 after the interview.

---

## 1. The live system (GCP project `bq-demos-469816`, proj # 549403515075)

| Component | Where | URL / id |
|---|---|---|
| Web app + token | Cloud Run `aug24-web` | https://aug24-web-cuxcxfhcya-uc.a.run.app/ |
| MCP server | Cloud Run `aug24-mcp` (image v3) | https://aug24-mcp-549403515075.us-central1.run.app/mcp |
| Agent worker | GKE deploy `aug24-agent`, private cluster `aug24-cluster`, us-central1 | (in-cluster) |
| Data | Firestore db `aug24` | orders 44721–44725, customers C-1001/C-1002, tickets |
| Knowledge | Vertex RAG corpus `aug24-returns-kb`, **europe-west3** | ragCorpora id `2305843009213693952` |
| LiveKit | Cloud project `personal-mv5pzdc8.livekit.cloud` | agent name `anycompany-agent` |
| Phone | SIP number | +1 512 584 6942 |
| Egress | Cloud NAT `aug24-router` / `aug24-nat` on network `bqdemo1` | — |

**Inference (STT/LLM/TTS/turn) runs on LiveKit Cloud, NOT GCP.** Agent's real models:
`assemblyai/universal-3-5-pro` (STT) · `google/gemma-4-31b-it` (LLM) · `fishaudio/s2.1-pro` (TTS) · `inference.TurnDetector()` · Silero VAD · ai-coustics noise cancel.

## 2. Deploy / redeploy commands

```bash
# MCP server (Cloud Run)
cd deploy/aug24-mcp-server
gcloud run deploy aug24-mcp --source . --region us-central1 --project bq-demos-469816

# Web app (Cloud Run)
cd deploy/aug24-webapp
gcloud run deploy aug24-web --source . --region us-central1 --project bq-demos-469816

# Agent (GKE) — graceful drain baked into the yaml
kubectl apply -f deploy/aug24-agent-gke.yaml   # terminationGracePeriodSeconds:600 + --drain-timeout 600
```
The real agent source lives in `../anycompany-agent/src/agent.py` (persistent, not here).

## 3. Presentation artifacts (published, private on claude.ai)

- 🏗️ **The AnyCompany Build** (capstone, 14 sections) — https://claude.ai/code/artifact/c0d8cb95-17f0-40da-b0ce-c82ed69dfce4
- 🎙️ **The LiveKit Side** (cheatsheet) — https://claude.ai/code/artifact/a4a6e277-1c92-474a-868c-7bd3126f4645
- Study family (artifact id prefixes): playbook `280e533f` · The Model Decision `85318d63`→`85378d63` · What Runs Where `a5d683d5` · LiveKit From the Ground Up `5fda0bed` · What We Actually Built `6aab8963` · From Sound to Conversation `eca37b35` · Inside the Room `cf30cc8a` · What LiveKit Ships `c7cafc7b` · Wiring Up a Phone Number `fc53e690` · Talking While You Wait `ed2f4e3f` · Knocking on Your Own Door `8f26694e`
- HTML source for all of the above is in `presentation/` (endtoend.html = the Build, cheatsheet.html = the LiveKit Side).

## 4. Known bugs to fix (to make the agent work properly)

1. **`track_package` retry storm** — model retried on ToolError and filed 4 tickets. Added idempotency (`self._timeout_tickets`) + `max_tool_steps=3`, but max_tool_steps then silently disabled the filler. **Still open** — reconcile idempotency with the filler.
2. **Ticket-number readback** — agent misreads the ticket number back to the caller.
3. **Digit padding** — prompt "order numbers are five digits" made the model pad `4472` → `47210`. Loosen the prompt / validate in the tool.
4. **`turn_latency.py` prints 0 ms in cloud/production** — metrics regression at INFO level; works in console mode.
5. **`with_filler` vs `max_tool_steps`** — enabling max_tool_steps silenced the filler (no-op).

## 5. Verifying RAG works (the two-part proof)

- MCP logs show the tool fired: `TOOL search_knowledge(...) → RAG` + `RAG retrieved N passages`.
- Ask a **document-unique** question so a correct answer proves grounding, not model memory:
  - "How long to return a doorbell camera?" → **14 days** (unique to the PDF)
  - "How quickly must I report a damaged device?" → **48 hours**
```bash
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="aug24-mcp"' \
  --project=bq-demos-469816 --freshness=1h --format='value(timestamp,textPayload)' | grep -iE 'TOOL|RAG'
```

## 6. Reference

- `livekit-docs/` — 39 LiveKit doc pages (telephony/SIP, agent server, models, tokens, regions, egress) + `urls.txt`.
- `deploy/return-policy.pdf` — the RAG source doc (30-day return / 14-day cameras+locks / 48-hr damage report / 2-yr warranty).
