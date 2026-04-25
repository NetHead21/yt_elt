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

    def test_next_page_url_contains_page_token(self, client):
        page1 = {
            "items": [{"contentDetails": {"videoId": "vid1"}}],
            "nextPageToken": "abc123",
        }
        page2 = {"items": [{"contentDetails": {"videoId": "vid2"}}]}

        with patch.object(client, "_get_json", side_effect=[page1, page2]) as mock_get:
            client.get_video_ids("PL123")
            second_call_url = mock_get.call_args_list[1][0][0]

        assert "abc123" in second_call_url


# ---------------------------------------------------------------------------
# batch_list
# ---------------------------------------------------------------------------


class TestBatchList:
    def test_single_batch_when_under_limit(self, client):
        ids = [f"vid{i}" for i in range(10)]
        batches = list(client.batch_list(ids))

        assert len(batches) == 1
        assert batches[0] == ids

    def test_splits_into_correct_batches(self, client):
        ids = [f"vid{i}" for i in range(120)]
        batches = list(client.batch_list(ids))

        assert len(batches) == 3
        assert len(batches[0]) == 50
        assert len(batches[1]) == 50
        assert len(batches[2]) == 20

    def test_empty_list_yields_no_batches(self, client):
        batches = list(client.batch_list([]))
        assert batches == []

    def test_custom_batch_size(self, client):
        ids = [f"vid{i}" for i in range(10)]
        batches = list(client.batch_list(ids, batch_size=3))

        assert len(batches) == 4
        assert len(batches[-1]) == 1

    def test_exact_batch_size_yields_one_batch(self, client):
        ids = [f"vid{i}" for i in range(50)]
        batches = list(client.batch_list(ids))

        assert len(batches) == 1


# ---------------------------------------------------------------------------
# _extract_video_stats
# ---------------------------------------------------------------------------


class TestExtractVideoStats:
    def test_extracts_all_fields(self, client):
        data = {
            "items": [
                {
                    "id": "vid1",
                    "snippet": {"title": "My Video", "publishedAt": "2024-01-01"},
                    "contentDetails": {"duration": "PT10M"},
                    "statistics": {
                        "viewCount": "1000",
                        "likeCount": "50",
                        "commentCount": "10",
                    },
                }
            ]
        }

        result = client._extract_video_stats(data)

        assert len(result) == 1
        assert result[0] == {
            "video_id": "vid1",
            "title": "My Video",
            "published_at": "2024-01-01",
            "duration": "PT10M",
            "view_count": "1000",
            "like_count": "50",
            "comment_count": "10",
        }

    def test_defaults_counts_to_zero_when_missing(self, client):
        data = {
            "items": [
                {
                    "id": "vid1",
                    "snippet": {"title": "My Video", "publishedAt": "2024-01-01"},
                    "contentDetails": {"duration": "PT5M"},
                    "statistics": {},
                }
            ]
        }

        result = client._extract_video_stats(data)

        assert result[0]["view_count"] == 0
        assert result[0]["like_count"] == 0
        assert result[0]["comment_count"] == 0

    def test_returns_empty_list_when_no_items(self, client):
        result = client._extract_video_stats({"items": []})
        assert result == []

    def test_extracts_multiple_items(self, client):
        data = {
            "items": [
                {
                    "id": f"vid{i}",
                    "snippet": {"title": f"Video {i}", "publishedAt": "2024-01-01"},
                    "contentDetails": {"duration": "PT1M"},
                    "statistics": {},
                }
                for i in range(3)
            ]
        }

        result = client._extract_video_stats(data)
        assert len(result) == 3
