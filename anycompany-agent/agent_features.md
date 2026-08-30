# Ember — agent features, and where each one lives

A map from the LiveKit optimisation checklist to the code. "Where" is a file and
symbol you can open; "why" is the one-line reason it is there. Items are in the
order a call experiences them.

| # | Feature | Status | Where |
|---|---|---|---|
| 1 | Semantic turn detection | in place | `agent.py` `SESSION_OPTIONS` → `inference.TurnDetector()` |
| 2 | Provider failover (STT / LLM / TTS) | **added** | `agent.py` entrypoint (`inference.STT(..., fallback=)`, `inference.TTS(..., fallback=)`); `Assistant.__init__` (`llm.FallbackAdapter`) |
| 3 | Preemptive generation | in place | `SESSION_OPTIONS` → `preemptive_generation={"enabled": True}` |
| 4 | Latency + usage observability | in place, **usage added** | `turn_latency.py` (`TurnLatency.attach`, `metrics.UsageCollector`) |
| 5a | Non-blocking tools with spoken progress | in place | `Assistant.track_package`, `check_warranty` (`context.update`, `with_filler`) |
| 5b | `disallow_interruptions` on the transactional step | **added** | `Assistant._transfer` |
| 5c | Dynamic tool scope (progressive disclosure) | **added** | `Assistant.GATED_TOOLS`, `gate_tools`, `ungate_tools`, `_identified` |
| 6 | Sub-workflows: `AgentTask` | **added** | `tasks.py` — `IdentifyCallerTask`, `ReturnIntakeTask`, `TroubleshootDeviceTask`; launched from `Assistant.on_enter`, `start_return`, `troubleshoot_device` |
| 7 | Persona handoffs (Triage → Manager) | deliberately **not used** | see `build-archive/reviews/multi-agent-review.html` |
| — | Warm transfer to a human with a brief | in place | `Assistant._transfer` → desk (`_ring_desk`) → `WarmTransferTask` → in-room |
| — | Parallel preload before the first word | in place | entrypoint `asyncio.gather(session.start, _preload)` → `update_instructions` |
| — | Long-term memory (Vertex AI Memory Bank) | in place | `save_call_memory`, MCP `remember` / `recall`, `/api/preload` |
| — | Product-manual RAG corpus (14 manuals + policy) | **added** | `build-archive/deploy/rag-products/make_manuals.py` → GCS → Vertex RAG corpus; MCP `search_knowledge`; test `tests/test_rag_products.py` |
| — | PII masking before anything leaves the process | in place | `pii.py`, used in `_transfer` and `save_call_memory` |

## 1 · Semantic turn detection — in place

`SESSION_OPTIONS.turn_handling.turn_detection = inference.TurnDetector()`
(LiveKit-hosted end-of-turn model, the Inference equivalent of the
`MultilingualModel` plugin). Adaptive interruption plus
`resume_false_interruption` so a cough mid-answer does not derail her.

## 2 · Provider failover — added

Three legs, three fallbacks, all inside the same call:

```python
# entrypoint
stt=inference.STT(model="assemblyai/universal-3-5-pro", language="en",
                  fallback=["deepgram/nova-3"])
tts=inference.TTS(model="fishaudio/s2.1-pro", voice="fa4c…",
                  fallback=["cartesia/sonic-3"])
# Assistant.__init__
llm=llm.FallbackAdapter([inference.LLM("google/gemma-4-31b-it"),
                         inference.LLM("google/gemini-2.5-flash")],
                        attempt_timeout=6.0)
```

LiveKit Inference models take `fallback=` natively for STT/TTS; the LLM uses the
generic `FallbackAdapter`. The TTS fallback changes the voice mid-call — worse
than nothing? No: the alternative is dead air and a dropped call. The handoff
brief (`_handoff_brief`) runs through the same adapter, so a brief is produced
even if Gemma is the leg that failed.

## 3 · Preemptive generation — in place

`preemptive_generation={"enabled": True}` in `SESSION_OPTIONS`. The LLM starts
on the transcript before end-of-turn is confirmed.

## 4 · Observability — in place; usage summary added

`turn_latency.py` reads the per-turn `MetricsReport` (`end_of_turn_delay`,
`llm_node_ttft`, `tts_node_ttfb`, `e2e_latency`) and prints a colour-coded
table at shutdown. Added: a `metrics.UsageCollector` on `metrics_collected`
and a `usage summary` log line at hang-up — tokens in/out and audio seconds per
call, so cost per call is a grep away.

## 5a · Non-blocking tools — in place

`track_package` and `check_warranty` bridge slow upstreams with
`context.update(...)` (immediate spoken status) and `context.with_filler(...)`
(timed "still waiting" lines), with a hard `asyncio.timeout` and an idempotent
ticket on failure so a retry never files twice.

## 5b · `disallow_interruptions` — added

`Assistant._transfer` now says one line ("One moment — I'm bringing in a
specialist and passing along a summary…"), then calls
`context.disallow_interruptions()` before ringing the desk. A "hello?" while
the desk rings can no longer cancel the handoff mid-flight.

## 5c · Dynamic tool scope — added

Parloa's "eligibility layer", in LiveKit terms: code decides what the model may
call; the model only chooses among what is eligible.

- `Assistant.GATED_TOOLS` = `my_devices, find_my_device, my_recent_order,
  my_order, start_return, troubleshoot_device, check_warranty, track_package`.
- Guest call → `on_enter` → `gate_tools()` → only `end_call` and
  `transfer_to_human` are visible (2 of 10).
- Identification succeeds → `ungate_tools()` (also triggered as a backstop from
  `_identified`, the MCP result resolver that reads the verified DB row).
- Signed-in callers never gate: the account was on the token.

Test: `tests/test_tasks.py::test_scoped_tools_are_gated_for_an_unknown_caller`.

## 6 · Sub-workflows with `AgentTask` — added

`src/tasks.py`. One Ember, one voice; each task takes temporary control for one
user goal, sees only its own tools, and returns a typed dataclass that **code**
acts on. Same construct as LiveKit's `hotel_receptionist` / `healthcare`
examples and `WarmTransferTask`.

| Task | Launched from | Tools it owns | Returns |
|---|---|---|---|
| `IdentifyCallerTask` | `Assistant.on_enter` (guest path only) | `lookup_account_by_phone`, `lookup_account_by_number` (Toolbox MCP), `confirm_identity`, `cannot_identify` | `Identity(account, first_name)` or `None` |
| `ReturnIntakeTask` | tool `start_return` | `lookup_order`, `record_return`, `stop_return`, `search_knowledge` (RAG) | `ReturnIntake(order_id, item, status, condition, reason, within_window, next)` |
| `TroubleshootDeviceTask` | tool `troubleshoot_device` | `find_device`, `get_device_state`, `get_device_history`, `search_knowledge`, `conclude`, `stop_troubleshooting` | `Troubleshoot(device_id, name, finding, resolved, next)` |

What the caller notices: nothing. What changes underneath:

- **The refund decision is code.** `tasks.decide_return(order, condition, today)`
  mirrors policy v3: damaged / defective / wrong item → refunds desk (the
  specialist judges transit vs customer damage); unwanted inside the item's
  window → refunds desk; outside → declined with a ticket offer; not yet
  delivered → cancellation to the desk. The window is `return_window_days(item)`
  — 30 days standard, 14 for locks and doorbell cameras — constants tested at
  the boundary. The model never says an amount or a timeline.
- **`start_return` acts on `result.next`:** `refund_desk` → `_transfer(...)`
  with a summary built from the typed fields; `declined` → say why and offer a
  ticket; `person` → transfer; `abandoned` → carry on.
- **Every task has an exit tool** (`stop_return`, `stop_troubleshooting`,
  `cannot_identify`) so the model is never trapped inside a task.
- **Identity backstop:** `_identified()` completes the identify task from the
  verified MCP row even if the model forgets to call `confirm_identity`.
- **MCP tools per task:** `Assistant._mcp_tools("search_knowledge", …)` pulls
  named tools from the already-connected servers, so a task carries e.g. the
  policy search without seeing the other five MCP tools.
- Each task is given the Assistant's LLM (`model=self.llm`) — tasks otherwise
  inherit the *session's* model, which we don't set.
- The identify task runs only in a live job (`self._ctx is not None`); offline
  evals that drive `session.run()` keep the plain agent.

Retired: `request_refund` and `sync_device` (in-memory demo tools) — superseded
by the two tasks. `check_warranty` and `track_package` stay as the slow-upstream
examples.

Tests: `tests/test_tasks.py` (decision table, per-task tool sets, typed
completion, backstop, gating) plus the existing live beats.

## 7 · Persona handoffs — deliberately not used

The triage → billing-bot → tech-bot pattern is what tutorials show; LiveKit's
own richest examples and Parloa's production data use one agent plus bounded
tasks. Rationale and sources: `build-archive/reviews/multi-agent-review.html`.
One line for the panel: *"we add a task, not forty tools — and the caller is
never transferred between bots."*

## Product knowledge in the RAG corpus — added

The corpus (`aug24-returns-kb`, Vertex AI RAG Engine, europe-west3) now holds
**15 documents**: the returns policy plus an owner's manual for every product —
both thermostats, three cameras, two locks, both sensors, hub, plug, leak
sensor, and the video plan. Manuals are generated by
`build-archive/deploy/rag-products/make_manuals.py` (reportlab), uploaded to
`gs://bq-demos-469816-aug24-kb-eu/products/`, and imported with **512-token
chunks / 64 overlap** (tighter than the 1,024 default — the manuals are dense
symptom→fix lists, and small chunks keep one product's facts from blurring into
a look-alike's).

Every manual carries deliberately product-specific numbers (the Aria Thermostat
resets with a 10-second hold, the V2 with 15, the Doorbell Cam battery lasts
3–6 months, the Doorbell Pro has none), so `tests/test_rag_products.py` can
verify the **right** manual comes back, not just *a* manual: 17 live checks,
including two-model disambiguation and the policy's split return window
(30 days standard, 14 for locks and doorbells — which `tasks.decide_return`
mirrors in code). Measured `retrieveContexts` median: **~1.0 s** — fine
mid-conversation, which is why `search_knowledge` never runs on the greeting
path. If precision ever slips as the corpus grows: first re-chunk smaller with
higher overlap, then add the Vertex Ranking API reranker (<100 ms); the LLM
reranker (1–2 s) does not fit a voice turn.

## Not in the workshop list but on the call path

- **Warm transfer with an LLM brief** — `_handoff_brief` (summary, next steps,
  mood, urgency, PII-masked) → desk rings with it → `WarmTransferTask` when a
  trunk exists → in-room fallback. `_handed_off` blocks `end_call` afterwards.
- **Parallel preload** — profile, devices with live state, latest order, last
  call and Memory Bank facts fetched with `asyncio.gather` alongside
  `session.start`, injected via `update_instructions`. The greeting waits for
  nothing.
- **Memory** — Vertex AI Memory Bank, scoped by account; explicit `remember`,
  semantic `recall`, automatic `generate_memories` at hang-up.
- **PII masking** — `pii.py` on the brief and the stored transcript; opaque uid
  as LiveKit identity so logs carry no email or phone.

## How to see each one in a call

| Feature | What to do | What to look for |
|---|---|---|
| Gating | Call as guest, ask "what's my last order?" before giving a number | She asks for the account first; log line `tools gated until identified: 2 visible` |
| IdentifyCallerTask | Give "A H four eight two one" | `identity captured from verified lookup`, then `tools ungated: 10 visible` |
| ReturnIntakeTask | "I want to return order five eight one three zero, it arrived damaged" | She takes condition + reason, then "One moment — I'm bringing in a specialist…"; log `return intake: 58130 damaged within=True -> refund_desk`; desk rings |
| TroubleshootDeviceTask | "My hallway sensor isn't working" | She reads live state + history, offers one fix step; log `troubleshoot -> Troubleshoot(...)` |
| disallow_interruptions | Say "hello?" while the desk rings | The transfer continues |
| Failover | (not demoable without breaking a provider) | `FallbackAdapter` log lines if a leg fails |
| Usage summary | End the call | `usage summary: …` in the job log |
