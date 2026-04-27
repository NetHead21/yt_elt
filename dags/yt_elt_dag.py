from airflow.decorators import dag, task
from airflow.models import Variable
from datetime import datetime

from api.video_stats import YoutubeClient
from api.data_staging import save_to_json
