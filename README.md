# HashiCorp Vault AI Agent POC

This repository contains an internal proof of concept that demonstrates how an AI agent can authenticate against HashiCorp Cloud Platform (HCP) Vault, retrieve database credentials from a KV secret, connect directly to Postgres, and respond to users in natural language.

The POC runs on a local Kubernetes cluster (Rancher Desktop or Minikube) while depending on HCP-hosted Vault for secret management. It includes:
- Documentation for configuring Vault KV entries and local Kubernetes workloads.
- Kubernetes manifests for deploying the AI agent microservice and local Postgres instance.
- Reference Python agent code that exposes a chat API and uses tool abstractions to call Vault and query Postgres.

## Getting Started

1. **Review the architecture** in `docs/architecture.md`.
2. **Prepare Vault** using `docs/vault-configuration.md`.
3. **Prepare the local environment** using `docs/local-deployment.md` (cluster setup, manifests, seeding Postgres).
4. **Operate the agent** via the instructions in `docs/agent-operations.md`.

Each document contains Terraform and CLI snippets, required environment variables, and verification steps.

## Repository Layout

```
.
├── agent/                 # Python reference implementation of the AI agent
├── docs/                  # Architecture, setup guides, operational runbooks
├── k8s/                   # Kubernetes manifests (agent, Postgres)
├── scripts/               # Helper scripts for local automation/testing
└── README.md
```

## Status

This POC is intentionally modular and uses placeholders for sensitive values (Vault addresses, KV paths, database connection info). Replace placeholders with your environment-specific values before deploying. Review the TODO notes in each manifest or script to finalize configuration.


## Testing

Run automated checks from the repository root once your Python 3.12 virtual environment is active:

```bash
./scripts/run_local_checks.sh
```

The script refreshes dev dependencies, runs pytest with the correct `PYTHONPATH`, and prints a sample agent response.
