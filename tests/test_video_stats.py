from unittest.mock import patch, MagicMock
import requests
import pytest

from dags.api.video_stats import YoutubeClient


API_KEY = "fake-api-key"


@pytest.fixture
def client():
    return YoutubeClient(api_key=API_KEY)


# ---------------------------------------------------------------------------
# _get_json
# ---------------------------------------------------------------------------


class TestGetJson:
    def test_returns_json_on_success(self, client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}

        with patch("dags.api.video_stats.requests.get", return_value=mock_response):
            result = client._get_json("https://example.com")

        assert result == {"key": "value"}

    def test_returns_empty_dict_on_http_error(self, client):
        with patch("dags.api.video_stats.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.HTTPError("404")
            result = client._get_json("https://example.com")

        assert result == {}

    def test_returns_empty_dict_on_connection_error(self, client):
        with patch("dags.api.video_stats.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()
            result = client._get_json("https://example.com")

        assert result == {}

    def test_calls_raise_for_status(self, client):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch("dags.api.video_stats.requests.get", return_value=mock_response):
            result = client._get_json("https://example.com")

        assert result == {}
