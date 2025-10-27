output "vault_addr" {
  description = "Vault API address."
  value       = local.vault_addr_value
}

output "vault_namespace" {
  description = "Namespace containing POC secrets."
  value       = local.vault_namespace_value
}

output "kv_mount_path" {
  description = "KV mount path holding the Postgres credentials."
  value       = local.kv_mount_path_value
}

output "kv_secret_name" {
  description = "Secret name within the KV mount containing credentials."
  value       = local.kv_secret_name_value
}

output "agent_policy_name" {
  description = "Vault policy name granting access to the credential."
  value       = vault_policy.agent.name
}

output "agent_token" {
  description = "Demonstration Vault token for the AI agent (if created)."
  value       = try(vault_token.agent[0].client_token, null)
  sensitive   = true
}
