from contextlib import contextmanager

import psycopg

from app.config import Settings
from app.tools.database import PostgresTool
from app.tools.vault import DatabaseCredentials


@contextmanager
def cursor_factory(rows):
    class Cursor:
        def __init__(self, rows):
            self._rows = rows

        def execute(self, sql, params):
            self.sql = sql
            self.params = params

        def fetchall(self):
            return self._rows

    cursor = Cursor(rows)
    yield cursor


class DummyConnection:
    def __init__(self, rows):
        self._rows = rows

    def cursor(self, row_factory=None):
        return cursor_factory(self._rows)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_fetch_products_maps_rows(monkeypatch):
    settings = Settings(POSTGRES_DB="postgres", POSTGRES_HOST="localhost", POSTGRES_PORT=5432)
    tool = PostgresTool(settings)
    credentials = DatabaseCredentials(username="postgres", password="pw")

    rows = [
        {
            "product_name": "Test Product",
            "description": "Automation description",
            "owner_name": "Owner",
            "owner_email": "owner@example.com",
            "recommended_use_cases": ["use-case"],
        }
    ]

    monkeypatch.setattr(psycopg, "connect", lambda **kwargs: DummyConnection(rows))

    result = tool.fetch_products(credentials, ["automation"])
    assert len(result) == 1
    assert result[0].product_name == "Test Product"
