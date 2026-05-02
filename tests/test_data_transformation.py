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
