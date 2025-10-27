"""Application configuration utilities."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables."""

    vault_addr: str = Field(default=None, alias="VAULT_ADDR")
    vault_namespace: str = Field(default="admin/poc-ai-agent", alias="VAULT_NAMESPACE")
    vault_token: Optional[str] = Field(default=None, alias="VAULT_TOKEN")
    vault_kv_path: str = Field(default="kv/data/postgres/static-creds", alias="VAULT_KV_PATH")
    vault_kv_username_key: str = Field(default="username", alias="VAULT_KV_USERNAME_KEY")
    vault_kv_password_key: str = Field(default="password", alias="VAULT_KV_PASSWORD_KEY")

    postgres_host: str = Field(default="postgres-0.postgres.vault-ai.svc.cluster.local", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="postgres", alias="POSTGRES_DB")

    llm_provider: str = Field(default="stub", alias="LLM_PROVIDER")
    llm_api_key: Optional[str] = Field(default=None, alias="LLM_API_KEY")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
