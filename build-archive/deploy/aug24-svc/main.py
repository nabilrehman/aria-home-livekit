import os
from flask import Flask, jsonify

app = Flask(__name__)
ROLE = os.environ.get("ROLE", "unknown")

MEANING = {
    "agent": {"mirrors": "AWS EC2 · Voice Agent (Python, LiveKit Agents)",
              "does": "would register with LiveKit and run the STT-LLM-TTS loop; "
                      "on GCP this is where GKE vs Cloud Run is the real decision"},
    "web":   {"mirrors": "AWS EC2 · Next.js web app + specialist console",
              "does": "serves the customer UI and mints short-lived room tokens "
                      "so the browser never sees the LiveKit secret"},
    "mcp":   {"mirrors": "AWS EC2 · Ticketing MCP service (external-system boundary)",
              "does": "the dashed box — writes cross this boundary; reads stay direct"},
}

@app.get("/")
def root():
    m = MEANING.get(ROLE, {})
    return jsonify({
        "service": f"aug24-{ROLE}",
        "status": "placeholder — proves the shape, not the logic",
        "mirrors_aws": m.get("mirrors"),
        "what_it_would_do": m.get("does"),
        "note": "delete-me demo; label demo=aug24",
    })

@app.get("/health")
def health():
    return jsonify({"ok": True, "role": ROLE})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
