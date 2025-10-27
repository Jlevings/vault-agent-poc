"""Logging utilities for the AI agent."""

import logging
from typing import Optional

from .config import get_settings


def configure_logging(level: Optional[str] = None) -> None:
    """Configure root logging level and format."""
    settings = get_settings()
    log_level = level or settings.log_level.upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
