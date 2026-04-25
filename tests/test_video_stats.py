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


# ---------------------------------------------------------------------------
# get_channel_id
# ---------------------------------------------------------------------------


class TestGetChannelId:
    def test_returns_channel_id(self, client):
        mock_data = {"items": [{"id": "UC123456"}]}

        with patch.object(client, "_get_json", return_value=mock_data):
            result = client.get_channel_id("MrBeast")

        assert result == "UC123456"

    def test_returns_none_when_empty_response(self, client):
        with patch.object(client, "_get_json", return_value={}):
            result = client.get_channel_id("UnknownChannel")

        assert result is None

    def test_returns_none_when_items_empty(self, client):
        with patch.object(client, "_get_json", return_value={"items": []}):
            result = client.get_channel_id("MrBeast")

        assert result is None

    def test_url_contains_channel_name_and_api_key(self, client):
        mock_data = {"items": [{"id": "UC123456"}]}

        with patch.object(client, "_get_json", return_value=mock_data) as mock_get:
            client.get_channel_id("MrBeast")
            url = mock_get.call_args[0][0]

        assert "MrBeast" in url
        assert API_KEY in url


# ---------------------------------------------------------------------------
# get_video_ids
# ---------------------------------------------------------------------------


class TestGetVideoIds:
    def test_returns_video_ids_single_page(self, client):
        mock_data = {
            "items": [
                {"contentDetails": {"videoId": "vid1"}},
                {"contentDetails": {"videoId": "vid2"}},
            ]
        }

        with patch.object(client, "_get_json", return_value=mock_data):
            result = client.get_video_ids("PL123")

        assert result == ["vid1", "vid2"]

    def test_paginates_through_multiple_pages(self, client):
        page1 = {
            "items": [{"contentDetails": {"videoId": "vid1"}}],
            "nextPageToken": "token123",
        }
        page2 = {
            "items": [{"contentDetails": {"videoId": "vid2"}}],
        }

        with patch.object(client, "_get_json", side_effect=[page1, page2]):
            result = client.get_video_ids("PL123")

        assert result == ["vid1", "vid2"]

    def test_returns_empty_list_on_failed_request(self, client):
        with patch.object(client, "_get_json", return_value={}):
            result = client.get_video_ids("PL123")

        assert result == []

    def test_returns_empty_list_when_no_items(self, client):
        with patch.object(client, "_get_json", return_value={"items": []}):
            result = client.get_video_ids("PL123")

        assert result == []
