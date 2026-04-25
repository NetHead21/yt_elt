import logging

logging.basicConfig(level=logging.INFO)

from pathlib import Path
from datetime import date
import json


def save_to_json(extracted_data: list, output_dir: Path = Path("data")) -> None:
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"yt_data_{date.today()}.json"

    try:
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=4)
        logging.info(f"Data successfully saved to {output_file}")
    except IOError as e:
        logging.error(f"Error saving data to {output_file}: {e}")
