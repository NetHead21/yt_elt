import json
import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from dags.warehouse.data_loading import load_from_json
