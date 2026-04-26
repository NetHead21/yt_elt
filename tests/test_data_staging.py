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


class TestSaveToJson:
    def test_creates_output_file(self, tmp_path):
        save_to_json(SAMPLE_DATA, output_dir=tmp_path)

        output_file = tmp_path / f"yt_data_{date.today()}.json"
        assert output_file.exists()
