"""Database connection utilities."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import psycopg
from psycopg import sql
from dotenv import load_dotenv


SCHEMA_PATH = Path(__file__).with_name("schema.sql")
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# Load environment variables from the package-local .env if present; allows
# running via CLI without exporting DATABASE_URL manually.
load_dotenv(ENV_PATH)


class Database:
    """Thin wrapper to manage connections and schema creation."""

    def __init__(self, dsn: str | None = None) -> None:
        resolved_dsn = dsn or os.getenv("DATABASE_URL")
        if not resolved_dsn:
            raise ValueError(
                "DATABASE_URL environment variable is required for database access."
            )
        self.dsn: str = resolved_dsn

    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection]:
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            yield conn

    def apply_schema(self) -> None:
        schema_sql = SCHEMA_PATH.read_text()
        with self.connection() as conn:
            with conn.cursor() as cur:
                # schema_sql is trusted file content; ignore literal string restriction for type checker.
                cur.execute(sql.SQL(schema_sql))  # type: ignore[arg-type]
