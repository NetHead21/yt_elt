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

    # ----------------------------------------------------------------------------------------------
    # DLL methods
    # ----------------------------------------------------------------------------------------------
    def create_schema(self, schema_name: str) -> None:
        """Creates a schema if it does not already exist.

        Args:
            schema_name: Name of the schema to create.
        """
        with self.get_cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {schema};").format(
                    schema=sql.Identifier(schema_name)
                )
            )

    def create_table(
        self, table_name: str, schema_name: str, columns: dict[str, str]
    ) -> None:
        """Creates a table if it does not already exist.

        Args:
            table_name: Name of the table to create.
            schema_name: Schema where the table will be created.
            columns: Dict mapping column names to their SQL type definitions
                     (e.g. {"video_id": "VARCHAR(11) PRIMARY KEY NOT NULL"}).
        """

        columns_def = sql.SQL(", ").join(
            sql.SQL("{col} {dtype}").format(
                col=sql.Identifier(col), dtype=sql.SQL(dtype)
            )
            for col, dtype in columns.items()
        )
        with self.get_cursor() as cursor:
            cursor.execute(
                sql.SQL(
                    "CREATE TABLE IF NOT EXISTS {schema}.{table} ({columns});"
                ).format(
                    schema=sql.Identifier(schema_name),
                    table=sql.Identifier(table_name),
                    columns=columns_def,
                )
            )

    # ----------------------------------------------------------------------------------------------
    # CREATE
    # ----------------------------------------------------------------------------------------------
    def insert_data(
        self, schema_name: str, table_name: str, data: list[dict[str, Any]]
    ) -> None:
        """Inserts a list of records into a table.

        Args:
            schema_name: Target schema name.
            table_name: Target table name.
            data: List of dicts where keys are column names and values are row values.
                  Does nothing if data is empty.
        """

        if not data:
            return

        columns = data[0].keys()
        query = sql.SQL(
            "INSERT INTO {schema}.{table} ({columns}) VALUES ({values});"
        ).format(
            schema=sql.Identifier(schema_name),
            table=sql.Identifier(table_name),
            columns=sql.SQL(", ").join(map(sql.Identifier, columns)),
            values=sql.SQL(", ").join(sql.Placeholder(col) for col in columns),
        )

        with self.get_cursor() as cursor:
            cursor.executemany(query, data)

    def upsert_data(
        self, schema_name: str, table_name: str, data: list[dict[str, Any]]
    ) -> None:
        """Inserts rows, updating existing ones on primary key conflict.

        Args:
            schema_name: Target schema name.
            table_name: Target table name.
            data: List of dicts where each dict is one row. All dicts must
                have the same keys.
        """

        if not data:
            return

        columns = list(data[0].keys())

        insert_sql = sql.SQL(
            "INSERT INTO {schema}.{table} ({cols}) VALUES ({vals}) ON CONFLICT (video_id) DO UPDATE SET {updates}"
        ).format(
            schema=sql.Identifier(schema_name),
            table=sql.Identifier(table_name),
            cols=sql.SQL(", ").join(map(sql.Identifier, columns)),
            vals=sql.SQL(", ").join(sql.Placeholder(col) for col in columns),
            pk=sql.Identifier("video_id"),
            updates=sql.SQL(", ").join(
                sql.SQL("{col} = EXCLUDED.{col}").format(col=sql.Identifier(col))
                for col in columns
                if col != "video_id"
            ),
        )

        with self.get_cursor() as cursor:
            cursor.executemany(insert_sql, data)
