from airflow.hooks.http_hook import HttpHook
import requests
import json
from datetime import datetime, timedelta

class TwitterHook(HttpHook):
    def __init__(self, search_query, start_time, end_time, conn_id = 'twitter_default'):
        super().__init__(http_conn_id = conn_id)
        self.search_query = search_query
        self.start_time = start_time
        self.end_time = end_time
        self.conn_id = conn_id

    def create_url(self):
        TIMESTAMP = '%Y-%m-%dT%H:%M:%S.00Z'
        
        tweet_fields = 'tweet.fields=author_id,created_at,lang,public_metrics,source,text,withheld'
        user_fields = 'expansions=author_id&user.fields=created_at,description,location,name,public_metrics,username,verified,withheld'

        url_raw = f"{self.base_url}/tweets/search/recent?query={self.search_query}&{tweet_fields}&{user_fields}&start_time={self.start_time}&end_time={self.end_time}"

        return url_raw

    def connect_to_endpoint(self, url, session):
        request = requests.Request('GET', url)
        prep = session.prepare_request(request)
        self.log.info(f"URL: {url}")

        return self.run_and_check(session, prep, {})  


    def paginate(self, url, session):

        responses = []
        response = self.connect_to_endpoint(url, session)
        json_response = response.json()

        responses.append(json_response)

        while 'next_token' in json_response.get('meta', {}):
            next_token = json_response['meta']['next_token']

            url_next = f"{url}&next_token={next_token}"
            json_response = self.connect_to_endpoint(url_next, session).json()

            responses.append(json_response)
        
        return responses
    
    def run(self):
        session = self.get_conn()
        url = self.create_url()

        return self.paginate(url, session)
    
if __name__ == "__main__":
    TIMESTAMP = '%Y-%m-%dT%H:%M:%S.00Z'

    end_time = datetime.now().strftime(TIMESTAMP)
    start_time = (datetime.now() - timedelta(days=1)).date().strftime(TIMESTAMP)

    query = 'data science'

    twitter_hook = TwitterHook(search_query = query, start_time = start_time, end_time = end_time)
    responses = twitter_hook.run()

    print(json.dumps(responses, indent=4, sort_keys=True))
