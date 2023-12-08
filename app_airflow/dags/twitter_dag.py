import sys
sys.path.append("app_airflow")

from airflow.models import DAG
from airflow.utils.dates import days_ago
from operators.twitter_operator import TwitterOperator
from datetime import datetime, timedelta
from os.path import join


with DAG(dag_id='TwitterDAG', start_date=days_ago(7), schedule_interval="@daily") as dag:
    query = 'data science'

    twitter_operator = TwitterOperator(
        file_path=join("datalake", "twitter_datascience", "extracted={{ ds }}", "twitter_{{ ds_nodash }}.json"), 
        search_query = query, 
        start_time = "{{ data_interval_start.strftime('%Y-%m-%dT%H:%M:%S.00Z') }}", 
        end_time = "{{ data_interval_end.strftime('%Y-%m-%dT%H:%M:%S.00Z') }}",
        task_id='twitter_operator')