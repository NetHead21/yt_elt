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


@dag(schedule="@daily", start_date=datetime(2026, 1, 1), catchup=False)
def warehouse_dag():
    wait_for_yt_elt = ExternalTaskSensor(
        task_id="wait_for_yt_elt",
        external_dag_id="yt_elt_dag",
        external_task_id="save",  # the last task in yt_elt_dag
        mode="reschedule",  # frees up a worker slot while waiting
        timeout=3600,  # fails after 1 hour if not done
    )

    @task
    def setup_database_tables():
        db = PostgresDB()

        db.create_schema(STAGING_TABLE["schema_name"])
        db.create_table(**STAGING_TABLE)

        db.create_schema(CORE_TABLE["schema_name"])
        db.create_table(**CORE_TABLE)
