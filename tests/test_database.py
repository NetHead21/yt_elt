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
