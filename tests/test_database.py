from unittest.mock import MagicMock, patch, call
import pytest

from dags.warehouse.database import PostgresDB


SAMPLE_DATA = [
    {
        "video_id": "abc123",
        "title": "MrBeast Video 1",
        "published_at": "2024-01-01 00:00:00",
        "duration": "PT10M30S",
        "view_count": 1000000,
        "like_count": 50000,
        "comment_count": 3000,
    },
    {
        "video_id": "def456",
        "title": "MrBeast Video 2",
        "published_at": "2024-02-15 00:00:00",
        "duration": "PT8M45S",
        "view_count": 500000,
        "like_count": 25000,
        "comment_count": 1500,
    },
]

COLUMNS = {
    "video_id": "VARCHAR(11) PRIMARY KEY NOT NULL",
    "title": "TEXT NOT NULL",
    "published_at": "TIMESTAMP NOT NULL",
    "duration": "VARCHAR(20) NOT NULL",
    "view_count": "INT",
    "like_count": "INT",
    "comment_count": "INT",
}


@pytest.fixture
def mock_cursor():
    return MagicMock()


@pytest.fixture
def mock_conn(mock_cursor):
    conn = MagicMock()
    conn.cursor.return_value = mock_cursor
    return conn


@pytest.fixture
def db(mock_conn):
    with patch("dags.warehouse.database.PostgresHook") as mock_hook_cls:
        mock_hook = MagicMock()
        mock_hook.get_conn.return_value = mock_conn
        mock_hook_cls.return_value = mock_hook
        yield PostgresDB()


# ---------------------------------------------------------------------------
# __init__ / hook
# ---------------------------------------------------------------------------


class TestInit:
    def test_default_connection_id(self):
        with patch("dags.warehouse.database.PostgresHook"):
            db = PostgresDB()
        assert db.postgres_conn_id == "postgres_db_yt_elt"

    def test_default_database(self):
        with patch("dags.warehouse.database.PostgresHook"):
            db = PostgresDB()
        assert db.database == "elt_db"

    def test_custom_connection_id(self):
        with patch("dags.warehouse.database.PostgresHook"):
            db = PostgresDB(postgres_conn_id="custom_conn")
        assert db.postgres_conn_id == "custom_conn"

    def test_hook_is_lazy(self):
        with patch("dags.warehouse.database.PostgresHook") as mock_hook_cls:
            db = PostgresDB()
            mock_hook_cls.assert_not_called()
            _ = db.hook
            mock_hook_cls.assert_called_once()

    def test_hook_is_cached(self):
        with patch("dags.warehouse.database.PostgresHook") as mock_hook_cls:
            db = PostgresDB()
            _ = db.hook
            _ = db.hook
            mock_hook_cls.assert_called_once()


# ---------------------------------------------------------------------------
# get_cursor
# ---------------------------------------------------------------------------


class TestGetCursor:
    def test_commits_on_success(self, db, mock_conn):
        with db.get_cursor():
            pass
        mock_conn.commit.assert_called_once()

    def test_rollback_on_exception(self, db, mock_conn):
        with pytest.raises(ValueError):
            with db.get_cursor():
                raise ValueError("something went wrong")
        mock_conn.rollback.assert_called_once()

    def test_closes_cursor_and_connection(self, db, mock_conn, mock_cursor):
        with db.get_cursor():
            pass
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_closes_on_exception(self, db, mock_conn, mock_cursor):
        with pytest.raises(RuntimeError):
            with db.get_cursor():
                raise RuntimeError("error")
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


# ---------------------------------------------------------------------------
# create_schema
# ---------------------------------------------------------------------------


class TestCreateSchema:
    def test_executes_create_schema(self, db, mock_cursor):
        db.create_schema("staging")
        mock_cursor.execute.assert_called_once()

    def test_sql_contains_schema_name(self, db, mock_cursor):
        db.create_schema("staging")
        executed_sql = str(mock_cursor.execute.call_args[0][0])
        assert "staging" in executed_sql

    def test_sql_contains_create_schema(self, db, mock_cursor):
        db.create_schema("staging")
        executed_sql = str(mock_cursor.execute.call_args[0][0])
        assert "CREATE SCHEMA" in executed_sql


# ---------------------------------------------------------------------------
# create_table
# ---------------------------------------------------------------------------


class TestCreateTable:
    def test_executes_create_table(self, db, mock_cursor):
        db.create_table("yt_api", "staging", COLUMNS)
        mock_cursor.execute.assert_called_once()

    def test_sql_contains_table_and_schema(self, db, mock_cursor):
        db.create_table("yt_api", "staging", COLUMNS)
        executed_sql = str(mock_cursor.execute.call_args[0][0])
        assert "staging" in executed_sql
        assert "yt_api" in executed_sql

    def test_sql_contains_all_columns(self, db, mock_cursor):
        db.create_table("yt_api", "staging", COLUMNS)
        executed_sql = str(mock_cursor.execute.call_args[0][0])
        for col in COLUMNS:
            assert col in executed_sql

    def test_sql_contains_create_table(self, db, mock_cursor):
        db.create_table("yt_api", "staging", COLUMNS)
        executed_sql = str(mock_cursor.execute.call_args[0][0])
        assert "CREATE TABLE" in executed_sql


# ---------------------------------------------------------------------------
# insert_data
# ---------------------------------------------------------------------------


class TestInsertData:
    def test_executes_insert(self, db, mock_cursor):
        db.insert_data("staging", "yt_api", SAMPLE_DATA)
        mock_cursor.executemany.assert_called_once()

    def test_skips_on_empty_data(self, db, mock_cursor):
        db.insert_data("staging", "yt_api", [])
        mock_cursor.executemany.assert_not_called()

    def test_passes_data_to_executemany(self, db, mock_cursor):
        db.insert_data("staging", "yt_api", SAMPLE_DATA)
        _, called_data = mock_cursor.executemany.call_args[0]
        assert called_data == SAMPLE_DATA

    def test_sql_contains_schema_and_table(self, db, mock_cursor):
        db.insert_data("staging", "yt_api", SAMPLE_DATA)
        executed_sql = str(mock_cursor.executemany.call_args[0][0])
        assert "staging" in executed_sql
        assert "yt_api" in executed_sql

    def test_sql_contains_all_columns(self, db, mock_cursor):
        db.insert_data("staging", "yt_api", SAMPLE_DATA)
        executed_sql = str(mock_cursor.executemany.call_args[0][0])
        for col in SAMPLE_DATA[0].keys():
            assert col in executed_sql


# ---------------------------------------------------------------------------
# upsert_data
# ---------------------------------------------------------------------------


class TestUpsertData:
    def test_executes_upsert(self, db, mock_cursor):
        db.upsert_data("staging", "yt_api", SAMPLE_DATA)
        mock_cursor.executemany.assert_called_once()

    def test_skips_on_empty_data(self, db, mock_cursor):
        db.upsert_data("staging", "yt_api", [])
        mock_cursor.executemany.assert_not_called()

    def test_passes_data_to_executemany(self, db, mock_cursor):
        db.upsert_data("staging", "yt_api", SAMPLE_DATA)
        _, called_data = mock_cursor.executemany.call_args[0]
        assert called_data == SAMPLE_DATA

    def test_sql_contains_schema_and_table(self, db, mock_cursor):
        db.upsert_data("staging", "yt_api", SAMPLE_DATA)
        executed_sql = str(mock_cursor.executemany.call_args[0][0])
        assert "staging" in executed_sql
        assert "yt_api" in executed_sql

    def test_sql_contains_on_conflict(self, db, mock_cursor):
        db.upsert_data("staging", "yt_api", SAMPLE_DATA)
        executed_sql = str(mock_cursor.executemany.call_args[0][0])
        assert "ON CONFLICT" in executed_sql

    def test_sql_contains_do_update(self, db, mock_cursor):
        db.upsert_data("staging", "yt_api", SAMPLE_DATA)
        executed_sql = str(mock_cursor.executemany.call_args[0][0])
        assert "DO UPDATE SET" in executed_sql

    def test_sql_contains_excluded(self, db, mock_cursor):
        db.upsert_data("staging", "yt_api", SAMPLE_DATA)
        executed_sql = str(mock_cursor.executemany.call_args[0][0])
        assert "EXCLUDED" in executed_sql

    def test_sql_contains_all_columns(self, db, mock_cursor):
        db.upsert_data("staging", "yt_api", SAMPLE_DATA)
        executed_sql = str(mock_cursor.executemany.call_args[0][0])
        for col in SAMPLE_DATA[0].keys():
            assert col in executed_sql

    def test_sql_excludes_video_id_from_update_set(self, db, mock_cursor):
        db.upsert_data("staging", "yt_api", SAMPLE_DATA)
        executed_sql = str(mock_cursor.executemany.call_args[0][0])
        do_update_part = executed_sql.split("DO UPDATE SET")[1]
        assert '"video_id" = EXCLUDED."video_id"' not in do_update_part

    def test_sql_contains_non_pk_columns_in_update_set(self, db, mock_cursor):
        db.upsert_data("staging", "yt_api", SAMPLE_DATA)
        executed_sql = str(mock_cursor.executemany.call_args[0][0])
        do_update_part = executed_sql.split("DO UPDATE SET")[1]
        for col in ("title", "view_count", "like_count", "comment_count"):
            assert col in do_update_part

    def test_single_row_data(self, db, mock_cursor):
        single = [SAMPLE_DATA[0]]
        db.upsert_data("staging", "yt_api", single)
        _, called_data = mock_cursor.executemany.call_args[0]
        assert called_data == single


# ---------------------------------------------------------------------------
# delete_removed_videos
# ---------------------------------------------------------------------------


class TestDeleteRemovedVideos:
    def test_executes_delete(self, db, mock_cursor):
        db.delete_removed_videos("staging", "yt_api", ["abc123", "def456"])
        mock_cursor.execute.assert_called_once()

    def test_skips_on_empty_list(self, db, mock_cursor):
        db.delete_removed_videos("staging", "yt_api", [])
        mock_cursor.execute.assert_not_called()

    def test_sql_contains_schema_and_table(self, db, mock_cursor):
        db.delete_removed_videos("staging", "yt_api", ["abc123"])
        executed_sql = str(mock_cursor.execute.call_args[0][0])
        assert "staging" in executed_sql
        assert "yt_api" in executed_sql
