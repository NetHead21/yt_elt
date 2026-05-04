from datetime import date, datetime
from pathlib import Path

from airflow.decorators import dag, task
from airflow.sensors.external_task import ExternalTaskSensor

from warehouse.database import PostgresDB
from warehouse.data_transformation import transform_data
from warehouse.data_loading import load_from_json

STAGING_TABLE = {
    "schema_name": "staging",
    "table_name": "yt_api",
    "columns": {
        "video_id": "VARCHAR(11) PRIMARY KEY NOT NULL",
        "title": "TEXT NOT NULL",
        "published_at": "TIMESTAMP NOT NULL",
        "duration": "VARCHAR(20) NOT NULL",
        "view_count": "INT",
        "like_count": "INT",
        "comment_count": "INT",
    },
}

CORE_TABLE = {
    "schema_name": "core",
    "table_name": "yt_api",
    "columns": {
        "video_id": "VARCHAR(11) PRIMARY KEY NOT NULL",
        "title": "TEXT NOT NULL",
        "published_at": "TIMESTAMP NOT NULL",
        "duration": "TIME NOT NULL",
        "video_type": "VARCHAR(10) NOT NULL",
        "view_count": "INT",
        "like_count": "INT",
        "comment_count": "INT",
    },
}
