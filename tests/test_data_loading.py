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


class TestLoadFromJson:
    def test_returns_data_from_valid_file(self, tmp_path):
        input_file = tmp_path / "data.json"
        input_file.write_text(json.dumps(SAMPLE_DATA), encoding="utf-8")

        result = load_from_json(input_file)

        assert result == SAMPLE_DATA

    def test_returns_empty_list_when_file_not_found(self, tmp_path):
        input_file = tmp_path / "nonexistent.json"

        result = load_from_json(input_file)

        assert result == []

    def test_returns_empty_list_on_io_error(self, tmp_path):
        input_file = tmp_path / "data.json"
        input_file.write_text(json.dumps(SAMPLE_DATA), encoding="utf-8")

        with patch.object(Path, "open", side_effect=IOError("disk error")):
            result = load_from_json(input_file)

        assert result == []

    def test_returns_empty_list_for_empty_json_array(self, tmp_path):
        input_file = tmp_path / "empty.json"
        input_file.write_text("[]", encoding="utf-8")

        result = load_from_json(input_file)

        assert result == []

    def test_returns_correct_number_of_records(self, tmp_path):
        input_file = tmp_path / "data.json"
        input_file.write_text(json.dumps(SAMPLE_DATA), encoding="utf-8")

        result = load_from_json(input_file)

        assert len(result) == 2

    def test_handles_unicode_characters(self, tmp_path):
        data = [{"title": "日本語タイトル", "video_id": "abc123"}]
        input_file = tmp_path / "unicode.json"
        input_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        result = load_from_json(input_file)

        assert result[0]["title"] == "日本語タイトル"

    def test_logs_success_on_valid_file(self, tmp_path, caplog):
        input_file = tmp_path / "data.json"
        input_file.write_text(json.dumps(SAMPLE_DATA), encoding="utf-8")

        with caplog.at_level(logging.INFO):
            load_from_json(input_file)

        assert any("successfully loaded" in msg for msg in caplog.messages)

    def test_logs_error_when_file_not_found(self, tmp_path, caplog):
        input_file = tmp_path / "nonexistent.json"

        with caplog.at_level(logging.ERROR):
            load_from_json(input_file)

        assert any("does not exists" in msg for msg in caplog.messages)

    def test_logs_error_on_io_error(self, tmp_path, caplog):
        input_file = tmp_path / "data.json"
        input_file.write_text(json.dumps(SAMPLE_DATA), encoding="utf-8")

        with patch.object(Path, "open", side_effect=IOError("disk error")):
            with caplog.at_level(logging.ERROR):
                load_from_json(input_file)

        assert any("Error loading" in msg for msg in caplog.messages)
