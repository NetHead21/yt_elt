import requests
from dotenv import load_dotenv
import os

from .data_staging import save_to_json

MAX_RESULTS = 50


class YoutubeClient:
    """Client for interacting with the YouTube Data API v3."""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: YouTube Data API v3 key.
        """
        self.api_key = api_key

    def _get_json(self, url: str) -> dict:
        """Makes a GET request and returns the JSON response. Returns {} on error.

        Args:
            url: The full request URL.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return {}

    def get_channel_id(self, channel_name: str) -> str:
        """Returns the channel ID for a given channel handle, or None if not found.

        Args:
            channel_name: YouTube channel handle (e.g. 'MrBeast').
        """
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel_name}&key={self.api_key}"
        data = self._get_json(url)
        if not data or not data.get("items"):
            return None
        channel_id = data["items"][0]["id"]
        return channel_id
