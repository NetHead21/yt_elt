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
