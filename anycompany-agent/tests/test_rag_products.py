"""Live retrieval checks against the product-manual corpus (Vertex AI RAG).

Fourteen Aria manuals share the same section skeleton, so the thing to verify
is not "did something come back" but "did the RIGHT manual come back": every
query below names a product-specific fact that exists in exactly one document.
A wrong-manual hit is how a voice agent tells a customer to hold the wrong
button for the wrong number of seconds.

Needs ADC (gcloud auth application-default) and network; skipped otherwise.
Run:  uv run python -m pytest tests/test_rag_products.py -v
"""

import json
import time
import urllib.request

import pytest

PROJECT = "bq-demos-469816"
REGION = "us-central1"
CORPUS = f"projects/{PROJECT}/locations/{REGION}/ragCorpora/718579227263238144"

try:
    import google.auth
    import google.auth.transport.requests

    _creds, _ = google.auth.default()
    _creds.refresh(google.auth.transport.requests.Request())
    TOKEN = _creds.token
except Exception:  # pragma: no cover - no ADC on this machine
    TOKEN = None

pytestmark = pytest.mark.skipif(TOKEN is None, reason="no Google ADC available")

LATENCIES: list[float] = []


def retrieve(question: str, top_k: int = 3) -> list[str]:
    body = json.dumps(
        {
            "vertex_rag_store": {"rag_resources": {"rag_corpus": CORPUS}},
            "query": {"text": question, "rag_retrieval_config": {"top_k": top_k}},
        }
    ).encode()
    req = urllib.request.Request(
        f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT}"
        f"/locations/{REGION}:retrieveContexts",
        data=body,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    t0 = time.monotonic()
    data = json.load(urllib.request.urlopen(req, timeout=30))
    LATENCIES.append((time.monotonic() - t0) * 1000)
    ctx = data.get("contexts", {}).get("contexts", [])
    return [c.get("text", "") for c in ctx]


# (question, must_appear_in_top_k, must_not_dominate)
# must_not_dominate: a look-alike product whose manual would be the *wrong*
# answer — it may appear, but the right fact must be there too.
CASES = [
    # thermostats: two models, different reset holds and error codes
    (
        "How do I factory reset my Aria Thermostat?",
        ["10 seconds", "ring turns red"],
        "Smart Thermostat V2",
    ),
    ("What does error E4 mean on my thermostat?", ["E4", "C-wire"], None),
    (
        "My Smart Thermostat V2 says the Power Bridge is not detected",
        ["V2-01", "furnace"],
        None,
    ),
    # locks: two models, different batteries and resets
    (
        "What batteries does the Aria Smart Lock take and how long do they last?",
        ["AA", "6 months"],
        "Door Lock Pro",
    ),
    (
        "My smart lock sticks when it's cold, what do I do?",
        ["strike plate", "graphite"],
        None,
    ),
    (
        "How many wrong codes before the Door Lock Pro keypad locks out?",
        ["5 wrong codes", "60 seconds"],
        None,
    ),
    # doorbell vs floodlight vs indoor cam
    (
        "How long does the Aria Doorbell Cam battery last on one charge?",
        ["3 to 6 months"],
        "Doorbell Pro",
    ),
    ("Does the Aria Doorbell Pro have a battery?", ["hardwired", "no battery"], None),
    ("How far does the floodlight cam detect motion?", ["30 feet"], None),
    # sensors — the demo device
    (
        "My motion sensor says not reporting, what's wrong?",
        ["CR123A", "2 years"],
        "Smart Sensor four pack",
    ),
    ("Will the motion sensor ignore my dog?", ["40 lb", "7 feet"], None),
    (
        "A sensor from my Smart Sensor four pack shows open when the door is closed",
        ["0.75 inch"],
        None,
    ),
    # plan + policy (the original document must still win policy questions)
    ("What do I get without a video subscription?", ["3 hours"], None),
    ("How many days do I have to return something?", ["30 days"], None),
    ("How long do I have to return a doorbell camera?", ["14-day", "security"], None),
    # hub range — the repeater answer
    (
        "My sensors at the far end of the house keep dropping offline",
        ["60 feet", "Smart Plug"],
        None,
    ),
]


@pytest.mark.parametrize(
    "question,needles,_lookalike", CASES, ids=[c[0][:48] for c in CASES]
)
def test_the_right_manual_comes_back(question, needles, _lookalike):
    passages = retrieve(question)
    assert passages, f"nothing retrieved for {question!r}"
    blob = "\n".join(passages).lower()
    missing = [n for n in needles if n.lower() not in blob]
    assert not missing, (
        f"top-3 passages lack {missing} for {question!r}.\nGot:\n"
        + "\n---\n".join(p[:200] for p in passages)
    )


def test_retrieval_latency_is_off_the_greeting_path_but_sane():
    """No Google-published figure exists; we publish our own. The tool runs
    mid-conversation (not at greeting), so the bar is 'well under a turn'."""
    retrieve("aria thermostat blinking red ring")
    med = sorted(LATENCIES)[len(LATENCIES) // 2]
    assert med < 3000, f"median retrieveContexts latency {med:.0f} ms"
    print(
        f"\nretrieveContexts: n={len(LATENCIES)} median={med:.0f} ms max={max(LATENCIES):.0f} ms"
    )
