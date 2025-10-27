"""Utilities for querying the Postgres knowledge base."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, List

import psycopg
from psycopg.rows import dict_row

from ..config import Settings
from .vault import DatabaseCredentials

logger = logging.getLogger(__name__)


@dataclass
class ProductRecord:
    product_name: str
    description: str
    owner_name: str
    owner_email: str
    recommended_use_cases: List[str]


class PostgresTool:
    """Runs read-only queries against the Postgres target."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _connect(self, credentials: DatabaseCredentials) -> psycopg.Connection:
        logger.debug(
            "Connecting to Postgres at %s:%s",
            self._settings.postgres_host,
            self._settings.postgres_port,
        )
        return psycopg.connect(
            host=self._settings.postgres_host,
            port=self._settings.postgres_port,
            user=credentials.username,
            password=credentials.password,
            dbname=self._settings.postgres_db,
        )

    def fetch_products(
        self, credentials: DatabaseCredentials, keywords: Iterable[str]
    ) -> List[ProductRecord]:
        """Return products whose description matches any keyword (case-insensitive)."""
        keyword_patterns = [f"%{kw.lower()}%" for kw in keywords if kw]

        sql = """
        SELECT product_name, description, owner_name, owner_email, recommended_use_cases
        FROM ibm_products
        WHERE
            cardinality(%(patterns)s::text[]) = 0
            OR EXISTS (
                SELECT 1
                FROM unnest(%(patterns)s::text[]) AS pattern
                WHERE lower(description) LIKE pattern
                   OR lower(product_name) LIKE pattern
            )
        ORDER BY product_name;
        """

        with self._connect(credentials) as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, {"patterns": keyword_patterns})
            rows = cur.fetchall()

        products = [
            ProductRecord(
                product_name=row["product_name"],
                description=row["description"],
                owner_name=row["owner_name"],
                owner_email=row["owner_email"],
                recommended_use_cases=row.get("recommended_use_cases") or [],
            )
            for row in rows
        ]

        logger.info("Fetched %s product rows from Postgres", len(products))
        return products
