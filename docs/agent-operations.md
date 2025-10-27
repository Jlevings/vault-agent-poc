# Agent Operations Guide

This guide explains how to interact with the AI agent once it is deployed, run verification tests, and extend its toolset.

## Service Endpoints

- **HTTP API:** `POST /api/v1/chat` accepts JSON payloads `{ "message": "<user prompt>" }`.
- **Web UI:** Served at `/` (static optional). Defaults to a simple HTML chat page.
- **Health Check:** `GET /healthz`.

Expose the endpoints locally by port-forwarding the service (see `docs/local-deployment.md`).

## Sample Prompt Flow

```bash
curl -s http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Suggest an automation solution for supply chain tracking and who to contact."}'
```

Expected behavior:
1. Agent parses the message and determines a database lookup is needed.
2. Agent reads the Postgres credential from Vault KV (`VAULT_KV_PATH`).
3. Agent runs a SQL query:
   ```sql
   SELECT product_name, description, owner_name, owner_email
   FROM ibm_products
   WHERE lower(description) LIKE '%supply chain%';
   ```
4. Agent generates a recommendation with owner contact info and returns JSON response.

## Observability

- `kubectl logs -n vault-ai deployment/agent-service` shows agent decisions, Vault lookups, and SQL results.
- Vault audit logs record every KV read (enable file or syslog audit devices in the Vault admin UI).

## Testing

Run automated checks from the `agent/` directory:

```bash
pip install -r requirements-dev.txt
pytest
```

The test suite contains:
- Mocked Postgres tool tests (`tests/test_db_tool.py`).
- Contract test for the chat endpoint using FastAPI’s test client.

Integration testing:

```bash
./scripts/run_local_checks.sh
```

The script installs (or refreshes) dev dependencies for the active interpreter, runs the pytest suite with `PYTHONPATH=agent`, and emits a sample agent response. Run it from the repo root after activating your Python 3.12 virtualenv and setting any required environment variables in `.env`.

## Extending Tooling

- **Dynamic Credentials:** Swap `VaultClient.get_database_credentials()` to call the database secrets engine when you're ready for short-lived credentials.
- **Additional Datastores:** Add new tool classes in `agent/app/tools/` and register them in the orchestrator.
- **LLM Providers:** Update `agent/app/config.py` to toggle between OpenAI, IBM Granite, or local models.

## Incident Response

1. Rotate the Postgres password, update the KV secret, and recycle the agent Deployment.
2. Revoke or rotate the Vault token backing the agent.
3. Review Vault audit logs to trace recent reads of the credential path.
