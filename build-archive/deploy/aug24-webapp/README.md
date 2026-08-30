# Aria Home web client — Firebase auth → LiveKit

Signed-in callers never identify themselves. Firebase proves who they are, this
service maps them to an Aria Home account, and the account number rides on the
LiveKit token as a participant attribute — so Ember opens with "Hi Sarah" instead
of "what's your phone number?".

## Flow

```
browser ──signInWithEmailAndPassword──► Firebase Auth
        ◄──────── ID token ────────────
        ──POST /token  Authorization: Bearer <ID token>──► this service (Cloud Run)
                                                            verify_id_token()
                                                            email → Aria Home account
                                                            mint LiveKit JWT
        ◄──── { token, url, room } ───────────────────────
        ──────── WebSocket + WebRTC ─────────────────────► LiveKit
                                                            reads roomConfig,
                                                            dispatches Ember
```

## What the LiveKit token carries

| Claim | Value | Why |
|---|---|---|
| `identity` | Firebase `uid` | Opaque. LiveKit writes identity and room name into infrastructure logs that are **not** PII-redacted, so never an email or phone. |
| `name` | Display name | UI only. |
| `attributes` | `aria_account`, `aria_name` | How Ember knows the caller. Account **number** only — the profile stays server-side, because a JWT is base64, not encrypted, and this one goes to the browser. |
| `roomConfig.agents` | `anycompany-agent` | Auto-dispatch on connect — no extra backend round-trip. |
| `roomConfig.empty_timeout` | 120s | A room nobody joins closes itself instead of billing. |
| `roomConfig.max_participants` | 3 | Caller + Ember + one specialist. |
| `exp` | 15 min | Bounds new connections, not the live call — an active WebSocket survives expiry. |

The LiveKit API key and secret never leave this service.

## Setup

1. **Enable Firebase Auth** on the project (Firebase console → Authentication → Get
   started), and turn on **Email/Password** and **Google** as sign-in providers.
2. **Create the demo user** — Authentication → Users → Add user:
   `sarah@example.com`, any password you'll remember. She maps to account
   **AH-4821** (Video Plus, thermostat + 2 cameras + lock).
   Other seeded logins: `marcus@example.com` (AH-3390), `priya@example.com`
   (AH-5567), `daniel@example.com` (AH-6012). Any other sign-in falls back to
   AH-4821 so a fresh Google login still lands in a populated account.
3. **Copy the web config** — Project settings → General → Your apps → Web app.
   You need `apiKey`, `authDomain`, `projectId`. These are **public by design**:
   they identify the project, they don't grant anything.
4. **Deploy:**

```bash
gcloud run deploy aug24-web --source . --region us-central1 --project bq-demos-469816 \
  --set-env-vars "LIVEKIT_URL=wss://personal-mv5pzdc8.livekit.cloud" \
  --set-env-vars "AGENT_NAME=anycompany-agent" \
  --set-env-vars "FIREBASE_API_KEY=...,FIREBASE_AUTH_DOMAIN=...,FIREBASE_PROJECT_ID=..." \
  --set-secrets  "LIVEKIT_API_KEY=livekit-api-key:latest,LIVEKIT_API_SECRET=livekit-api-secret:latest"
```

5. **Authorise the domain** — Firebase console → Authentication → Settings →
   Authorized domains → add the Cloud Run hostname, or Google sign-in popups fail.

`verify_id_token` fetches Google's public certs over the network and needs no IAM
role. Only the LiveKit secrets need Secret Manager access on the runtime service
account.

## Still open

- **Phone callers bypass all of this.** SIP has no browser and no ID token; those
  callers are identified by ANI via `lookup_account(phone)`, unchanged.
- **`DEMO_ACCOUNTS` is a dict.** In production it's a users table keyed by uid —
  see the Cloud SQL schema work.
