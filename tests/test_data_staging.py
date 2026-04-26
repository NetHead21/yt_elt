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

    def test_creates_output_directory_if_not_exists(self, tmp_path):
        output_dir = tmp_path / "new_dir"
        save_to_json(SAMPLE_DATA, output_dir=output_dir)

        assert output_dir.is_dir()

    def test_file_contains_correct_data(self, tmp_path):
        save_to_json(SAMPLE_DATA, output_dir=tmp_path)

        output_file = tmp_path / f"yt_data_{date.today()}.json"
        with output_file.open(encoding="utf-8") as f:
            result = json.load(f)

        assert result == SAMPLE_DATA

    def test_saves_empty_list(self, tmp_path):
        save_to_json([], output_dir=tmp_path)

        output_file = tmp_path / f"yt_data_{date.today()}.json"
        with output_file.open(encoding="utf-8") as f:
            result = json.load(f)

        assert result == []
