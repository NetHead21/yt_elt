import requests
from dotenv import load_dotenv
import os

from .data_staging import save_to_json

MAX_RESULTS = 50