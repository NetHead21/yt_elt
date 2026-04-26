import json
import logging
from pathlib import Path
from datetime import date
from unittest.mock import patch

from dags.api.data_staging import save_to_json

SAMPLE_DATA = [
    {
        "video_id": "vid1",
        "title": "Test Video",
        "published_at": "2024-01-01",
        "duration": "PT10M",
        "view_count": "1000",
        "like_count": "50",
        "comment_count": "10",
    }
]
