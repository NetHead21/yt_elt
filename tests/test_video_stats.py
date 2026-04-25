from unittest.mock import patch, MagicMock
import requests
import pytest

from dags.api.video_stats import YoutubeClient


API_KEY = "fake-api-key"


@pytest.fixture
def client():
    return YoutubeClient(api_key=API_KEY)
