# Aria Home · Cloud SQL tools (MCP Toolbox for Databases)

Google's [MCP Toolbox](https://github.com/googleapis/mcp-toolbox) serving the
relational half of Aria Home as MCP tools. There is no application code here —
every tool is a parameterised SQL statement declared in `tools.yaml`.

## Why two MCP servers

| Server | Store | Answers |
|---|---|---|
| **this one** (Toolbox) | Cloud SQL / Postgres | Who is calling · what they own · what they bought · file a ticket |
| `aug24-mcp` (custom) | Firestore + Vertex RAG | What each device is reporting **right now** · policy questions |

The device **registry** is relational; the device **state** is a document. They
join on `device_id`: `find_device` returns it from Postgres, `get_device_state`
reads it from Firestore. "Is my thermostat active?" crosses both.

Toolbox handles the SQL half because it is genuinely just SQL — declaring it
beats writing and maintaining a data API. The custom server stays for telemetry
and retrieval, which are not SQL.

## Run locally

```bash
brew install mcp-toolbox          # or download the binary
export DB_USER=aria DB_PASS='...'
toolbox --tools-file tools.yaml   # MCP at http://127.0.0.1:5000/mcp
```

Point the agent at it:
```bash
export TOOLBOX_MCP_URL=http://127.0.0.1:5000/mcp
```

## Deploy to Cloud Run

The service account needs `roles/cloudsql.client`.

```bash
gcloud run deploy aria-toolbox --source . \
  --region us-central1 --project bq-demos-469816 \
  --set-secrets "DB_PASS=aria-db-pass:latest" \
  --set-env-vars "DB_USER=aria" \
  --no-allow-unauthenticated
```

Then set `TOOLBOX_MCP_URL=https://<service-url>/mcp` on the agent.

## Safety

Every statement is parameterised — the model supplies values, never SQL. The
`aria_support` toolset is read-only apart from `file_ticket`: nothing exposed
here can change a subscription, cancel an order, or unlock a door.
