resource "vault_mount" "kv" {
  count = var.create_kv_mount ? 1 : 0

  provider = vault.poc

  path        = local.kv_mount_path_value
  type        = "kv-v2"
  description = "KV store for AI agent static credentials"
}

resource "vault_kv_secret_v2" "postgres_creds" {
  count = var.create_kv_secret ? 1 : 0

  provider = vault.poc

  mount = local.kv_mount_path_value
  name  = local.kv_secret_name_value
  data_json = jsonencode({
    username = local.kv_username_value
    password = local.kv_password_value
  })

  depends_on = [vault_mount.kv]
}

resource "vault_policy" "agent" {
  provider = vault.poc

  name   = var.agent_policy_name
  policy = <<-EOT
    path "${local.kv_full_path}" {
      capabilities = ["read"]
    }
  EOT
}

resource "vault_token" "agent" {
  count = var.create_agent_token ? 1 : 0

  provider = vault.poc

  policies     = [vault_policy.agent.name]
  display_name = "vault-ai-agent"
  ttl          = var.agent_token_ttl
  renewable    = true
}
