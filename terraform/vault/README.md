## Vault Module

This working directory provisions the minimal Vault resources required for the static-credential POC:

- Assumes the namespace already exists (set `vault_namespace`).
- KV secrets engine (v2) mount.
- Seeded Postgres credential stored at `kv/<secret_name>`.
- `agent` policy granting read access to that secret.
- Optional demonstration token bound to the policy.

### Inputs

Supply values via `terraform.tfvars`, `-var` flags, or by defining them in the `.env` file
(loaded by default from `../../agent/.env`). Terraform variable values always take precedence
over the `.env` entries. Example overrides:

```hcl
vault_addr          = "https://vault.example.com"
vault_admin_token   = "${env.VAULT_TOKEN}"
kv_mount_path       = "kv"
kv_secret_name      = "postgres/static-creds"
kv_username         = "agent_reader"
kv_password         = "ChangeMe123!"
```

### Outputs

- `vault_namespace` – namespace where resources were created.
- `kv_mount_path` / `kv_secret_name` – combine to form `VAULT_KV_PATH` (`kv/data/postgres/static-creds`).
- `agent_policy_name` – reference when configuring Vault auth methods in the future.
- `agent_token` – optional token to inject into the agent or Kubernetes Secret for the MVP.

Use these outputs to populate the `agent-config` Kubernetes secret and `.env` file.
