"""Vault client wrapper for retrieving dynamic credentials."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

from ..config import Settings

logger = logging.getLogger(__name__)


@dataclass
class DatabaseCredentials:
    username: str
    password: str
    lease_id: Optional[str] = None
    ttl: Optional[int] = None


class VaultClient:
    """Lightweight Vault API client used by the agent."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._session = httpx.Client(timeout=10.0) if self.enabled else None

    @property
    def enabled(self) -> bool:
        return bool(self._settings.vault_token and self._settings.vault_addr)

    def _headers(self) -> Dict[str, str]:
        headers = {
            "X-Vault-Token": self._settings.vault_token or "",
        }
        if self._settings.vault_namespace:
            headers["X-Vault-Namespace"] = self._settings.vault_namespace
        return headers

    def get_database_credentials(self) -> DatabaseCredentials:
        """Fetch Postgres credentials from Vault KV or fall back to environment variables."""
        if not self.enabled or self._session is None:
            logger.info("Vault not fully configured; falling back to local credentials")
            username = os.getenv("POSTGRES_USER", "postgres")
            password = os.getenv("POSTGRES_PASSWORD", "postgres")
            return DatabaseCredentials(username=username, password=password)

        path = self._settings.vault_kv_path.lstrip("/")
        url = f"{self._settings.vault_addr}/v1/{path}"
        response = self._session.get(url, headers=self._headers())
        response.raise_for_status()

        data: Dict[str, Any] = response.json()  # type: ignore[assignment]
        # KV v2 nests credentials under data.data; KV v1 uses data directly
        credentials = data.get("data", {})
        if isinstance(credentials, dict) and "data" in credentials:
            credentials = credentials["data"]

        return DatabaseCredentials(
            username=credentials.get(self._settings.vault_kv_username_key, "postgres"),
            password=credentials.get(self._settings.vault_kv_password_key, ""),
        )

    def close(self) -> None:
        if self._session:
            self._session.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            logger.debug("Failed to close Vault session", exc_info=True)
