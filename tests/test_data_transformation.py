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

    def test_seconds_only(self):
        assert parse_duration("PT45S") == timedelta(seconds=45)

    def test_hours_and_minutes(self):
        assert parse_duration("PT2H45M") == timedelta(hours=2, minutes=45)

    def test_hours_and_seconds(self):
        assert parse_duration("PT1H30S") == timedelta(hours=1, seconds=30)

    def test_days_hours_minutes_seconds(self):
        assert parse_duration("PT1D2H30M15S") == timedelta(
            days=1, hours=2, minutes=30, seconds=15
        )

    def test_returns_timedelta_zero_for_none(self):
        assert parse_duration(None) == timedelta(0)

    def test_exactly_60_seconds(self):
        assert parse_duration("PT60S") == timedelta(seconds=60)

    def test_exactly_60_minutes(self):
        assert parse_duration("PT60M") == timedelta(minutes=60)
