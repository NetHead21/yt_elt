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
    if not input_file.exists():
        logging.error(f"Input file {input_file} does not exists.")
        return []

    try:
        with input_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        logging.info(f"Data successfully loaded from {input_file}")
        return data
    except IOError as e:
        logging.error(f"Error loading data from {input_file}: {e}")
        return []
