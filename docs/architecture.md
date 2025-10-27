# HCP Vault AI Agent POC Architecture

## Overview

This proof of concept (POC) shows how a local AI agent can retrieve database credentials from HashiCorp Cloud Platform (HCP) Vault and query a Postgres knowledge base to produce natural-language recommendations. All compute (agent + Postgres) runs in a local Kubernetes cluster, while Vault stays hosted in HCP.

## High-Level Flow

1. **User Prompt** – A user submits a question through the chat endpoint.
2. **Vault Lookup** – The agent calls Vault's KV secrets engine to read a pre-created Postgres username/password pair.
3. **Database Query** – Using those credentials, the agent connects directly to Postgres and queries the `ibm_products` table for relevant entries.
4. **Response Generation** – The agent feeds the results to the LLM orchestration layer and returns a synthesized recommendation.

## Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| HCP Vault Dedicated | HCP | Stores the static Postgres credential inside a KV secret (`kv/data/postgres/static-creds`). Optionally issues scoped tokens for the agent via OIDC/Kubernetes auth. |
| Postgres Database | Local Kubernetes | Hosts the `ibm_products` table seeded with sample automation product data. |
| AI Agent Service | Local Kubernetes | FastAPI application that authenticates to Vault, retrieves credentials, executes SQL queries, and returns LLM-generated responses. |

## Secrets & Identity

- **Vault Authentication** – For the MVP the agent uses a Vault token supplied via Kubernetes Secret or environment variable. You can later switch to Vault's Kubernetes or OIDC auth methods without changing the app flow.
- **Credential Storage** – Postgres credentials live under a KV secret. Example payload:
  ```json
  {
    "data": {
      "username": "agent_reader",
      "password": "s3cr3tP@ssw0rd"
    }
  }
  ```
- **Rotation** – Rotate the Postgres password manually (or via automation), then update the KV entry. No additional session brokering is involved in this simplified POC.

## Kubernetes Workloads

- `postgres` StatefulSet – Provides the demo data store and seeds the `ibm_products` table via `seed.sql`.
- `agent-service` Deployment – Hosts the Python agent. Environment variables supply Vault connection info, KV path, and Postgres host/port.

## Security Considerations

- Restrict the Vault token scope to read-only access on the KV path (`kv/data/postgres/static-creds`).
- Use TLS between the agent and Vault (HCP Vault enforces this by default).
- For production hardening, migrate to dynamic credentials (Vault Database Secrets Engine) once the POC is stable.

## Next Steps

1. Automate Vault KV provisioning with Terraform or the Vault CLI (`vault kv put kv/postgres/static-creds username=... password=...`).
2. Add Kubernetes auth for the agent Deployment to remove static Vault tokens.
3. Replace static credentials with Vault's dynamic Postgres secrets when ready.
