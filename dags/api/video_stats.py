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
