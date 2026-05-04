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

    def test_returns_timedelta_type(self):
        result = parse_duration("PT5M")
        assert isinstance(result, timedelta)


# ---------------------------------------------------------------------------
# transform_data
# ---------------------------------------------------------------------------


class TestTransformData:
    def test_does_not_mutate_original_row(self):
        original = SAMPLE_ROW.copy()
        transform_data(SAMPLE_ROW)
        assert SAMPLE_ROW == original

    def test_converts_duration_to_timedelta(self):
        result = transform_data(SAMPLE_ROW)
        assert isinstance(result["duration"], timedelta)
        assert result["duration"] == timedelta(minutes=10, seconds=30)

    def test_classifies_short_video(self):
        row = {**SAMPLE_ROW, "duration": "PT30S"}
        result = transform_data(row)
        assert result["video_type"] == "Short"

    def test_classifies_exactly_60s_as_short(self):
        row = {**SAMPLE_ROW, "duration": "PT60S"}
        result = transform_data(row)
        assert result["video_type"] == "Short"

    def test_classifies_normal_video(self):
        row = {**SAMPLE_ROW, "duration": "PT10M30S"}
        result = transform_data(row)
        assert result["video_type"] == "Normal"

    def test_classifies_long_video_as_normal(self):
        row = {**SAMPLE_ROW, "duration": "PT2H"}
        result = transform_data(row)
        assert result["video_type"] == "Normal"

    def test_does_not_override_existing_video_type(self):
        row = {**SAMPLE_ROW, "video_type": "Custom"}
        result = transform_data(row)
        assert result["video_type"] == "Custom"

    def test_casts_view_count_to_int(self):
        result = transform_data(SAMPLE_ROW)
        assert result["view_count"] == 1000000
        assert isinstance(result["view_count"], int)
