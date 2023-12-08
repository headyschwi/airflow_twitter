from datetime import datetime, timedelta
import requests
import json
import os

# Montando url

TIMESTAMP = '%Y-%m-%dT%H:%M:%S.00Z'
end_time = datetime.now().strftime(TIMESTAMP)
start_time = (datetime.now() - timedelta(days=1)).date().strftime(TIMESTAMP)

query = 'data science'
tweet_fields = 'tweet.fields=author_id,created_at,lang,public_metrics,source,text,withheld'
user_fields = 'expansions=author_id&user.fields=created_at,description,location,name,public_metrics,username,verified,withheld'

url_raw = f"https://labdados.com/2/tweets/search/recent?query={query}&{tweet_fields}&{user_fields}&start_time={start_time}&end_time={end_time}"

# Fazendo requisição
response = requests.get(url_raw, headers={'Authorization': f'Bearer {os.environ["BEARER_TOKEN"]}'})
response_json = response.json()

# Imprimindo resultados
print(json.dumps(response_json, indent=4, sort_keys=True))


# Paginando resultados
while 'next_token' in response_json.get('meta', {}):
    next_token = response_json['meta']['next_token']

    url_next = f"{url_raw}&next_token={next_token}"
    response = requests.get(url_next, headers={'Authorization': f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    print(json.dumps(response_json, indent=4, sort_keys=True))