import os
from flask import Flask, jsonify
from google.cloud import firestore

app = Flask(__name__)
# the named database we seeded
db = firestore.Client(project=os.environ["GOOGLE_CLOUD_PROJECT"], database="aug24")

@app.get("/health")
def health():
    return jsonify({"ok": True, "backend": "firestore", "database": "aug24"})

@app.get("/order/<order_id>")
def order(order_id):
    """Real order lookup — reads Firestore, the GCP backend."""
    doc = db.collection("orders").document(order_id).get()
    if not doc.exists:
        return jsonify({"found": False, "order_id": order_id,
                        "say": "No order with that number. Ask them to check it."}), 404
    d = doc.to_dict()
    return jsonify({"found": True, "order_id": order_id,
                    "item": d.get("item"), "status": d.get("status"),
                    "source": "GCP Firestore (aug24 db)"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
