locals {
  env_file_default = var.env_file_path != "" ? var.env_file_path : "${path.module}/../../agent/.env"
  env_contents     = var.load_env && fileexists(local.env_file_default) ? file(local.env_file_default) : ""
  env_lines = [
    for raw in split("\n", local.env_contents) : trimspace(raw)
    if trimspace(raw) != "" && !startswith(trimspace(raw), "#")
  ]
  env_pairs = {
    for line in local.env_lines :
    trimspace(split(line, "=")[0]) => trimspace(join("=", slice(split(line, "="), 1, length(split(line, "=")))))
    if length(split(line, "=")) >= 2
  }

  vault_addr_value = trimspace(var.vault_addr) != "" ? trimspace(var.vault_addr) : lookup(local.env_pairs, "VAULT_ADDR", "")

  vault_admin_token_value = trimspace(var.vault_admin_token) != "" ? trimspace(var.vault_admin_token) : lookup(local.env_pairs, "VAULT_ADMIN_TOKEN", "")

  vault_namespace_value = trimspace(var.vault_namespace) != "" ? trimspace(var.vault_namespace) : (trimspace(lookup(local.env_pairs, "VAULT_NAMESPACE", "")) != "" ? trimspace(lookup(local.env_pairs, "VAULT_NAMESPACE", "")) : "admin/poc-ai-agent")

  kv_mount_path_value  = trimspace(var.kv_mount_path) != "" ? trimspace(var.kv_mount_path) : "kv"
  kv_secret_name_value = trimspace(var.kv_secret_name) != "" ? trimspace(var.kv_secret_name) : "postgres/static-creds"
  kv_username_value    = trimspace(var.kv_username) != "" ? trimspace(var.kv_username) : "agent_reader"
  kv_password_value    = trimspace(var.kv_password) != "" ? trimspace(var.kv_password) : "ChangeMe123!"


  poc_vault_namespace = trim(join("/", compact([var.vault_root_namespace, local.vault_namespace_value])), "/")
  kv_full_path        = "${local.kv_mount_path_value}/data/${local.kv_secret_name_value}"

}
