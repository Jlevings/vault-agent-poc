"""LLM client abstraction."""

from __future__ import annotations

import logging
from typing import List

from jinja2 import Environment, PackageLoader, select_autoescape

from ..config import Settings
from .database import ProductRecord

logger = logging.getLogger(__name__)


class LLMClient:
    """Simplified LLM client with a deterministic stub fallback."""

    SYSTEM_PROMPT = (
        "You are an IBM automation advisor. Summarize the findings, make a clear recommendation, "
        "and propose actionable next steps based on the database results."
    )

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._env = Environment(
            loader=PackageLoader("app", "prompt_templates"),
            autoescape=select_autoescape(),
        )

    def generate_recommendation(self, user_prompt: str, products: List[ProductRecord]) -> str:
        provider = self._settings.llm_provider.lower()
        if provider == "stub":
            return self._stub_response(user_prompt, products)

        raise NotImplementedError(
            f"LLM provider '{self._settings.llm_provider}' is not implemented in this reference build."
        )

    def _stub_response(self, user_prompt: str, products: List[ProductRecord]) -> str:
        template = self._env.get_template("recommendation.txt.jinja2")
        logger.debug("Rendering stub LLM response for prompt: %s", user_prompt)
        return template.render(prompt=user_prompt, products=products)
