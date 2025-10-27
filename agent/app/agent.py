"""Agent orchestration logic."""

from __future__ import annotations

import logging
import re
from dataclasses import asdict
from typing import Dict, List, Optional

from .config import Settings, get_settings
from .tools.database import PostgresTool, ProductRecord
from .tools.llm import LLMClient
from .tools.vault import VaultClient

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Coordinates Vault, Postgres, and LLM interactions to answer prompts."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._vault_client = VaultClient(self._settings)
        self._db_tool = PostgresTool(self._settings)
        self._llm_client = LLMClient(self._settings)

    @staticmethod
    def _extract_keywords(prompt: str) -> List[str]:
        words = re.findall(r"[A-Za-z0-9\-]+", prompt.lower())
        return [w for w in words if len(w) > 3]

    def handle_prompt(self, prompt: str) -> Dict[str, object]:
        logger.info("Handling user prompt")

        keywords = self._extract_keywords(prompt)
        logger.debug("Extracted keywords: %s", keywords)

        credentials = self._vault_client.get_database_credentials()
        products = self._db_tool.fetch_products(credentials, keywords)

        answer = self._llm_client.generate_recommendation(prompt, products)
        product_payload = [self._serialize_product(product) for product in products]

        return {
            "answer": answer,
            "products": product_payload,
            "keywords": keywords,
        }

    def shutdown(self) -> None:
        """Cleanup any reusable resources."""
        self._vault_client.close()

    @staticmethod
    def _serialize_product(product: ProductRecord) -> Dict[str, object]:
        payload = asdict(product)
        payload["recommended_use_cases"] = product.recommended_use_cases
        return payload
