from contextlib import contextmanager
from typing import Any

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
