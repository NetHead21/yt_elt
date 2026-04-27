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
