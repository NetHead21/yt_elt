from datetime import timedelta
import pytest

from dags.warehouse.data_transformation import parse_duration, transform_data

SAMPLE_ROW = {
    "video_id": "abc123",
    "title": "Test Video",
    "published_at": "2024-01-01T00:00:00Z",
    "duration": "PT10M30S",
    "view_count": "1000000",
    "like_count": "50000",
    "comment_count": "3000",
}

# ---------------------------------------------------------------------------
# parse_duration
# ---------------------------------------------------------------------------


class TestParseDuration:
    def test_minutes_and_seconds(self):
        assert parse_duration("PT10M30S") == timedelta(minutes=10, seconds=30)

    def test_hours_only(self):
        assert parse_duration("PT3H") == timedelta(hours=3)

    def test_minutes_only(self):
        assert parse_duration("PT20M") == timedelta(minutes=20)
