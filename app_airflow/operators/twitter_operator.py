import sys
sys.path.append("app_airflow")

from airflow.models import BaseOperator, DAG, TaskInstance
from hooks.twitter_hook import TwitterHook
import json
from os.path import join
import pathlib

class TwitterOperator(BaseOperator):

    template_fields = ['file_path', 'search_query', 'start_time', 'end_time']

    def __init__(self, file_path, search_query, start_time, end_time, conn_id = 'twitter_default', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_query = search_query
        self.start_time = start_time
        self.end_time = end_time
        self.conn_id = conn_id
        self.file_path = file_path
    
    def execute(self, context):

        (pathlib.Path(self.file_path).parent).mkdir(parents=True, exist_ok=True)

        with open(self.file_path, "w") as f:
            hook = TwitterHook(self.search_query, self.start_time, self.end_time, self.conn_id)
            response = hook.run()
            for page in response:
                json.dump(page, f, ensure_ascii=False)
                f.write("\n")
            return response

if __name__ == "__main__":
    from datetime import datetime, timedelta
    from pprint import pprint

    TIMESTAMP = '%Y-%m-%dT%H:%M:%S.00Z'

    end_time = datetime.now().strftime(TIMESTAMP)
    start_time = (datetime.now() - timedelta(days=1)).date().strftime(TIMESTAMP)   
    query = 'data science'

    with DAG(dag_id='twitter_operator', start_date=datetime.now()) as dag:
        twitter_operator = TwitterOperator(file_path=join(
            "datalake", "twitter_datascience", f"extracted={datetime.now().date()}", f"twitter_{datetime.now().strftime('%Y%m%d')}.json"), 
            search_query = query, start_time = start_time, end_time = end_time, task_id='twitter_operator')
        
        task_instance = TaskInstance(task=twitter_operator)
        
        twitter_operator.execute(task_instance.task_id)        