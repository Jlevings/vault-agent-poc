# End-to-End Deployment Runbook

Use this guide to build and run the Vault-backed AI agent POC from scratch.

---

## 1. Account & Access Prerequisites

- Admin (or delegated) access to **HCP Vault Dedicated**.
- A workstation running macOS or Linux with:
  - Docker Desktop, Rancher Desktop, or Minikube (Docker driver recommended).
  - `kubectl`, `helm`, `vault`, `jq`, `psql`, and `pip` installed.
- Network egress to `*.vault.hashicorp.cloud`.

> Tip: Create a dedicated Vault namespace (e.g., `admin/poc-ai-agent`) so all resources can be torn down cleanly.

---

## 2. Repository Checkout & Local Tooling

```bash
git clone <this-repo-url>
cd poc.vault.boundary.ai.agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r agent/requirements-dev.txt
```

Copy `agent/.env.example` to `agent/.env` and populate placeholders—you'll replace them with Kubernetes secrets later. Review the repo layout in `README.md`.

---

## 3. Configure HCP Vault

Follow `docs/vault-configuration.md` to:
1. (Optional) create the `admin/poc-ai-agent` namespace.
2. Enable the KV secrets engine (`kv/`).
3. Store the Postgres credential at `kv/postgres/static-creds`.
4. Create the `agent` policy granting `read` on that path.
5. Issue a token for the agent (or configure Kubernetes/OIDC auth if desired).

Record the following values for later substitution:
- Vault address (`VAULT_ADDR`).
- Namespace (`VAULT_NAMESPACE`).
- KV path (`VAULT_KV_PATH`).
- Token with the `agent` policy (`VAULT_TOKEN`).

---

## 4. Prepare the Local Kubernetes Cluster

Choose one of:

- **Rancher Desktop** – enable Kubernetes, select `containerd`, allocate ≥4 CPU & 6 GB RAM.
- **Minikube** – `minikube start --cpus=4 --memory=6144 --kubernetes-version=v1.29.0`

Validate context:
```bash
kubectl config current-context
```

Create the namespace:
```bash
kubectl apply -f k8s/namespace.yaml
```

---

## 5. Create Kubernetes Secrets

Populate the secret consumed by the agent Deployment (replace placeholders):

```bash
kubectl -n vault-ai create secret generic agent-config \
  --from-literal=vault_addr="https://<VAULT_ADDR>" \
  --from-literal=vault_namespace="admin/poc-ai-agent" \
  --from-literal=vault_token="<VAULT_TOKEN_WITH_POLICY>" \
  --from-literal=vault_kv_path="kv/data/postgres/static-creds" \
  --from-literal=vault_kv_username_key="username" \
  --from-literal=vault_kv_password_key="password" \
  --from-literal=llm_api_key="<OPTIONAL_LLM_API_KEY>"
```

If you are using Vault Agent Injector or Secrets Store CSI Driver, replace this static secret with dynamic injection.

---

## 6. Deploy Supporting Services

### 6.1 Postgres
```bash
kubectl apply -n vault-ai -f k8s/postgres/
kubectl rollout status -n vault-ai statefulset/postgres
kubectl -n vault-ai exec -it postgres-0 -- psql -U postgres -d postgres -f /docker-entrypoint-initdb.d/seed.sql
```

### 6.2 AI Agent

Build the image if you have code changes:
```bash
nerdctl --namespace k8s.io build -t vault-ai-agent:latest agent/  # or docker build if you are using Docker Engine
# Minikube users:
minikube image load vault-ai-agent:latest
```

Apply the manifests:
```bash
kubectl apply -n vault-ai -f k8s/agent/
kubectl rollout status -n vault-ai deployment/agent-service
```

---

## 7. Smoke Test the Agent

Forward the service locally:
```bash
kubectl port-forward -n vault-ai svc/agent-service 8080:80
```

Send a prompt:
```bash
curl -s http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Recommend automation for supply chain tracking"}' | jq
```

Check logs:
```bash
kubectl logs -n vault-ai deployment/agent-service
```
You should see successful Vault KV reads and SQL query execution. Vault audit logs will show the KV access if enabled.

---

## 8. Optional Enhancements

- Replace the static Vault token with Kubernetes or OIDC auth.
- Move the Postgres credential to the database secrets engine for dynamic passwords.
- Swap the stub LLM with a live provider (`LLM_PROVIDER`).

---

## 9. Teardown

```bash
kubectl delete namespace vault-ai
minikube delete  # if using Minikube
```

Revoke the Vault token you issued for the agent:
```bash
vault token revoke <token>
```

---

## Quick Reference Index

| Task | Source Document |
|------|-----------------|
| Architecture overview | `docs/architecture.md` |
| Vault setup details   | `docs/vault-configuration.md` |
| Kubernetes manifests  | `k8s/*` |
| Ops & troubleshooting | `docs/agent-operations.md` |

Keep this runbook handy as you progress through setup. Once the static KV workflow is stable, you can iterate toward dynamic credentials with minimal changes to the application.
