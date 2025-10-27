variable "vault_addr" {
  description = "HCP Vault cluster address (e.g., https://vault.example.com). Overrides any value discovered in the .env file."
  type        = string
  default     = ""
}

variable "vault_admin_token" {
  description = "Administrative token with rights to manage namespaces and policies. Overrides any value discovered in the .env file."
  type        = string
  sensitive   = true
  default     = ""
}

variable "vault_root_namespace" {
  description = "Root namespace used for administrative operations (HCP defaults to 'admin')."
  type        = string
  default     = "admin"
}

variable "vault_namespace" {
  description = "Namespace that will host POC resources. Created if it does not exist."
  type        = string
  default     = "admin/poc-ai-agent"
}

variable "kv_mount_path" {
  description = "Path where the KV (v2) secrets engine is/should be mounted."
  type        = string
  default     = "kv"
}

variable "create_kv_mount" {
  description = "Enable the KV mount if it does not already exist."
  type        = bool
  default     = true
}

variable "kv_secret_name" {
  description = "Secret path (relative to the KV mount) where Postgres creds are stored."
  type        = string
  default     = "postgres/static-creds"
}

variable "kv_username" {
  description = "Username to seed in the KV secret when create_kv_secret is true."
  type        = string
  default     = "agent_reader"
}

variable "kv_password" {
  description = "Password to seed in the KV secret when create_kv_secret is true."
  type        = string
  default     = "ChangeMe123!"
  sensitive   = true
}

variable "create_kv_secret" {
  description = "Whether to write the static credential into the KV path."
  type        = bool
  default     = true
}

variable "agent_policy_name" {
  description = "Name of the Vault policy that grants read access to the KV secret."
  type        = string
  default     = "agent"
}

variable "create_agent_token" {
  description = "Whether to mint a demonstration token attached to the agent policy."
  type        = bool
  default     = true
}

variable "agent_token_ttl" {
  description = "TTL for the demonstration token (if created)."
  type        = string
  default     = "24h"
}

variable "load_env" {
  description = "Whether to attempt loading Vault connection values from a .env file."
  type        = bool
  default     = true
}

variable "env_file_path" {
  description = "Optional path to a .env file containing Vault variables. Defaults to ../../agent/.env if not provided."
  type        = string
  default     = ""
}
