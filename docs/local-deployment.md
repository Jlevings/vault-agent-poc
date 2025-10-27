# Local Deployment Guide

This guide walks through deploying the AI agent POC to a local Kubernetes cluster running on macOS or Linux using either Rancher Desktop or Minikube.

## Prerequisites

- Docker runtime (Rancher Desktop or Minikube with Docker driver).
- `kubectl`, `helm`, `jq`.
- Outbound HTTPS access to HCP Vault from your workstation.
- Vault namespace, policy, and KV secret prepared (see `docs/vault-configuration.md`).

Set the project working directory:

```bash
cd poc.vault.boundary.ai.agent
```

## 1. Start a Local Kubernetes Cluster

### Option A: Rancher Desktop

1. Launch Rancher Desktop, select the `containerd` runtime.
2. Allocate at least 4 CPU cores and 6 GB memory.
3. Ensure `kubectl config current-context` points to `rancher-desktop`.

### Option B: Minikube

```bash
minikube start --cpus=4 --memory=6144 --kubernetes-version=v1.29.0
kubectl config use-context minikube
```

## 2. Create Namespace and Secrets

```bash
kubectl create namespace vault-ai
```

Create the secret consumed by the agent Deployment (substitute your values):

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

## 3. Deploy Postgres

Apply the manifests and seed data:

```bash
kubectl apply -n vault-ai -f k8s/postgres/
kubectl rollout status -n vault-ai statefulset/postgres

kubectl -n vault-ai exec -it postgres-0 -- psql -U postgres -d postgres -f /docker-entrypoint-initdb.d/seed.sql
```

The `seed.sql` file is provisioned through a ConfigMap in `k8s/postgres/configmap.yaml`.

## 4. Deploy the AI Agent

Build the agent image (if you modify the code):

- **Rancher Desktop (containerd):** `nerdctl --namespace k8s.io build -t vault-ai-agent:latest agent/`
- **Docker Engine:** `docker build -t vault-ai-agent:latest agent/`

Verify the image is available (optional): `nerdctl --namespace k8s.io images | grep vault-ai-agent`

Deploy manifests:

```bash
kubectl apply -n vault-ai -f k8s/agent/
kubectl rollout status -n vault-ai deployment/agent-service
```

## 5. Access the Chat Interface

Port-forward the service:

```bash
kubectl port-forward -n vault-ai svc/agent-service 8080:80
```

Open <http://localhost:8080> to use the chat UI or call the API directly per `docs/agent-operations.md`.

## 6. Troubleshooting

- **Vault auth issues:** Verify the token/policy allows `read` on the KV path. Check agent logs with `kubectl logs deployment/agent-service -n vault-ai`.
- **Database connectivity:** Ensure the `postgres` StatefulSet is ready and reachable at `postgres-0.postgres.vault-ai.svc.cluster.local:5432`.

## Cleanup

```bash
kubectl delete namespace vault-ai
minikube delete  # if using Minikube
```

## Next Steps

See `docs/agent-operations.md` for running sample prompts, testing integrations, and extending the agent toolset.
