import requests
import json
import os

headers = {
    'Accept': '*/*',
    'Sec-Fetch-Site': 'same-origin',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Sec-Fetch-Mode': 'cors',
    'Host': 'theanalyst.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15',
    'Referer': 'https://theanalyst.com/competition/premier-league/stats',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'x-sdapi-token': os.environ.get('OPTA_TOKEN', 'LRkJ2MjwlC8RxUfVkne4'),
    'tracestate': '66686@nr=0-1-3422235-1588640526-f0d32cdcf58d4a5c----1773673882501',
    'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjM0MjIyMzUiLCJhcCI6IjE1ODg2NDA1MjYiLCJpZCI6ImYwZDMyY2RjZjU4ZDRhNWMiLCJ0ciI6ImIzOTc5MjQ5NDliOTYxNDU5MWNjZWVkMmFmOGZhMzM4IiwidGkiOjE3NzM2NzM4ODI1MDEsInRrIjoiNjY2ODYifX0=',
    'traceparent': '00-b397924949b9614591cceed2af8fa338-f0d32cdcf58d4a5c-01',
}

session = requests.Session()
session.headers.update(headers)

print("Fetching Premier League data...")
try:
    response_pl = session.get(
        'https://theanalyst.com/wp-json/sdapi/v1/soccerdata/tournamentstats',
        params={'tmcl': '51r6ph2woavlbbpk8f29nynf8'},
        timeout=30
    )
    response_pl.raise_for_status()
    with open("data/raw/opta_pl_stats.json", "w") as f:
        json.dump(response_pl.json(), f, indent=2)
    print("✅ PL data saved to data/raw/opta_pl_stats.json")
except requests.exceptions.HTTPError as e:
    print(f"❌ Request failed: {e}")
except requests.exceptions.Timeout:
    print("❌ Request timed out after 30 seconds")
except requests.exceptions.ConnectionError:
    print("❌ Connection error — check your network or the API endpoint")




