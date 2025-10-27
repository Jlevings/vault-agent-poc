provider "vault" {
  address   = local.vault_addr_value
  token     = local.vault_admin_token_value
  namespace = var.vault_root_namespace
}

provider "vault" {
  alias     = "poc"
  address   = local.vault_addr_value
  token     = local.vault_admin_token_value
  namespace = local.poc_vault_namespace
}
