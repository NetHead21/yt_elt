from contextlib import contextmanager
from typing import Any

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


class PostgresDB:
    """Client for interacting with a PostgreSQL database via Airflow's PostgresHook."""

    def __init__(
        self, postgres_conn_id: str = "postgres_db_yt_elt", database: str = "elt_db"
    ):
        """
        Args:
            postgres_conn_id: Airflow connection ID for the PostgreSQL database.
            database: Target database name.
        """
        self.postgres_conn_id = postgres_conn_id
        self._hook: PostgresHook | None = None
        self.database = database

    @property
    def hook(self) -> PostgresHook:
        """Returns a cached PostgresHook instance, creating it on first access."""
        if self._hook is None:
            self._hook = PostgresHook(
                postgres_conn_id=self.postgres_conn_id, database=self.database
            )
        return self._hook

    def get_connection(self):
        """Returns a raw psycopg2 connection from the hook."""
        return self.hook.get_conn()

    @contextmanager
    def get_cursor(self):
        """Context manager that yields a RealDictCursor, commits on success, rolls back on error."""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
