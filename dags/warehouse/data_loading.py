import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)


def load_from_json(input_file: Path) -> list:
    """Loads data from a JSON file and returns it as a list.

    Logs an error and returns an empty list if the file does not exist
    or if an IO error occurs during reading.

    Args:
        input_file: Path to the JSON file to load.

    Returns:
        A list of records loaded from the file, or an empty list on failure.
    """
