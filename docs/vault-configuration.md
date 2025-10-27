# HCP Vault Configuration Guide

This guide walks through configuring an HCP Vault Dedicated cluster to store Postgres credentials in the KV secrets engine for the AI agent POC.

## Prerequisites

- Admin access to an HCP Vault Dedicated cluster.
- `vault` CLI authenticated with sufficient privileges.
- A dedicated namespace (e.g., `admin/poc-ai-agent`) to isolate policies and secrets.

Set convenience environment variables:

```bash
export VAULT_ADDR="https://<your-hcp-vault-url>"
export VAULT_NAMESPACE="admin"
vault login -method=oidc  # or use any admin token
```

## 1. Namespace (optional)

```bash
vault namespace create admin/poc-ai-agent
```

Use `-namespace=admin/poc-ai-agent` for the remaining commands if you created a dedicated namespace.

## 2. Enable KV Secrets Engine

Either reuse an existing KV mount or enable a new one (example: `kv/` using KV v2):

```bash
vault secrets enable -namespace=admin/poc-ai-agent -path=kv kv-v2
```

## 3. Store Static Postgres Credentials

Create a read-only Postgres user manually, then store its credentials in KV:

```bash
vault kv put -namespace=admin/poc-ai-agent kv/postgres/static-creds \
  username="agent_reader" \
  password="S3cur3P@ss!"
```

The agent expects the secret to follow the structure:

```json
{
  "username": "agent_reader",
  "password": "S3cur3P@ss!"
}
```

## 4. Define Agent Policy

Create a policy that restricts the agent to read-only access on that path:

```hcl
# file: policies/agent.hcl
path "kv/data/postgres/static-creds" {
  capabilities = ["read"]
}
```

Apply the policy:

```bash
vault policy write -namespace=admin/poc-ai-agent agent policies/agent.hcl
```

## 5. Issue a Token (MVP)

For the initial POC you can generate a long-lived token for the application:

```bash
vault token create -namespace=admin/poc-ai-agent \
  -policy=agent \
  -display-name=vault-ai-agent \
  -orphan \
  -no-default-policy \
  -ttl=8760h \
  -explicit-max-ttl=0
```

This yields a one-year token that can be renewed if desired. For production, migrate to Kubernetes or OIDC auth methods instead of long-lived static tokens.

## 6. Verification

Run a quick read to confirm access:

```bash
vault kv get -namespace=admin/poc-ai-agent kv/postgres/static-creds
```

The output should display the username/password pair you stored. The application will read the same secret path at runtime.

## Next Steps

- Optionally configure Vault's Kubernetes auth method to avoid long-lived tokens.
- When ready to move beyond static credentials, enable the database secrets engine and update the application to request dynamic credentials instead of KV secrets.
