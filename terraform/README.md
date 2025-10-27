# Terraform Stacks

The Terraform configuration is intentionally lightweight for the KV-based POC:

1. `postgres/` – documentation for deploying the local Postgres instance (currently via Kubernetes manifests, no Terraform yet).
2. `vault/` – provisions the Vault namespace, KV mount, policy, and demo token so the agent can read static credentials.

Run them sequentially when you need automation:

```bash
# Postgres is applied with kubectl per the README

cd terraform/vault
terraform init
terraform apply   # capture outputs (namespace, token, etc.)
```

Use the outputs from the `vault` stack to populate the agent environment variables and Kubernetes secrets. When you're ready to introduce dynamic credentials or Kubernetes auth, expand the `vault/` stack accordingly.
