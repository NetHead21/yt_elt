from airflow.decorators import dag, task
from airflow.models import Variable
from datetime import datetime

from api.video_stats import YoutubeClient
from api.data_staging import save_to_json


@dag(schedule="@daily", start_date=datetime(2026, 1, 1), catchup=False)
def yt_elt_dag():
    @task
    def get_playlist_id() -> str:
        client = YoutubeClient(api_key=Variable.get("API_KEY"))
        channel_handle = Variable.get("CHANNEL_HANDLE")
        channel_id = client.get_channel_id(channel_handle)
        return f"UU{channel_id[2:]}"

    @task
    def get_video_ids(playlist_id: str) -> list:
        client = YoutubeClient(api_key=Variable.get("API_KEY"))
        return client.get_video_ids(playlist_id)

    @task
    def get_video_stats(video_ids: list) -> list:
        client = YoutubeClient(api_key=Variable.get("API_KEY"))
        return client.get_video_stats(video_ids)

    @task
    def save(video_stats: list) -> None:
        save_to_json(video_stats)
