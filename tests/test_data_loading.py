import json
import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from dags.warehouse.data_loading import load_from_json

SAMPLE_DATA = [
    {
        "video_id": "abc123",
        "title": "MrBeast Video 1",
        "published_at": "2024-01-01T00:00:00Z",
        "duration": "PT10M30S",
        "view_count": 1000000,
        "like_count": 50000,
        "comment_count": 3000,
    },
    {
        "video_id": "def456",
        "title": "MrBeast Video 2",
        "published_at": "2024-02-15T00:00:00Z",
        "duration": "PT8M45S",
        "view_count": 500000,
        "like_count": 25000,
        "comment_count": 1500,
    },
]
