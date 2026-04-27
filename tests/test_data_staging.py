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

    def test_saves_multiple_records(self, tmp_path):
        data = SAMPLE_DATA * 5
        save_to_json(data, output_dir=tmp_path)

        output_file = tmp_path / f"yt_data_{date.today()}.json"
        with output_file.open(encoding="utf-8") as f:
            result = json.load(f)

        assert len(result) == 5

    def test_file_is_valid_json(self, tmp_path):
        save_to_json(SAMPLE_DATA, output_dir=tmp_path)

        output_file = tmp_path / f"yt_data_{date.today()}.json"
        content = output_file.read_text(encoding="utf-8")
        parsed = json.loads(content)

        assert isinstance(parsed, list)

    def test_handles_unicode_characters(self, tmp_path):
        data = [{"title": "日本語タイトル", "video_id": "vid1"}]
        save_to_json(data, output_dir=tmp_path)

        output_file = tmp_path / f"yt_data_{date.today()}.json"
        with output_file.open(encoding="utf-8") as f:
            result = json.load(f)

        assert result[0]["title"] == "日本語タイトル"

    def test_filename_contains_today_date(self, tmp_path):
        save_to_json(SAMPLE_DATA, output_dir=tmp_path)

        expected_file = tmp_path / f"yt_data_{date.today()}.json"
        assert expected_file.exists()

    def test_logs_success(self, tmp_path, caplog):
        with caplog.at_level(logging.INFO):
            save_to_json(SAMPLE_DATA, output_dir=tmp_path)

        assert any("successfully saved" in msg for msg in caplog.messages)

    def test_logs_error_on_io_failure(self, tmp_path, caplog):
        with patch.object(Path, "open", side_effect=IOError("disk full")):
            with caplog.at_level(logging.ERROR):
                save_to_json(SAMPLE_DATA, output_dir=tmp_path)

        assert any("Error saving" in msg for msg in caplog.messages)
