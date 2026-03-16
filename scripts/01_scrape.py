import requests
import json

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
    'x-sdapi-token': 'LRkJ2MjwlC8RxUfVkne4',
    'tracestate': '66686@nr=0-1-3422235-1588640526-f0d32cdcf58d4a5c----1773673882501',
    'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjM0MjIyMzUiLCJhcCI6IjE1ODg2NDA1MjYiLCJpZCI6ImYwZDMyY2RjZjU4ZDRhNWMiLCJ0ciI6ImIzOTc5MjQ5NDliOTYxNDU5MWNjZWVkMmFmOGZhMzM4IiwidGkiOjE3NzM2NzM4ODI1MDEsInRrIjoiNjY2ODYifX0=',
    'traceparent': '00-b397924949b9614591cceed2af8fa338-f0d32cdcf58d4a5c-01',
}

# --- Premier League ---
print("Fetching Premier League data...")
response_pl = requests.get(
    'https://theanalyst.com/wp-json/sdapi/v1/soccerdata/tournamentstats',
    params={'tmcl': '51r6ph2woavlbbpk8f29nynf8'},
    headers=headers
)
print("PL Status:", response_pl.status_code)
if response_pl.status_code == 200:
    with open("data/raw/opta_pl_stats.json", "w") as f:
        json.dump(response_pl.json(), f, indent=2)
    print("✅ PL data saved to data/raw/opta_pl_stats.json")
else:
    print("❌ PL request failed")

# --- Champions League ---
print("\nFetching Champions League data...")
response_ucl = requests.get(
    'https://theanalyst.com/wp-json/sdapi/v1/soccerdata/tournamentstats',
    params={'tmcl': '2mr0u0l78k2gdsm79q56tb2fo'},
    headers=headers
)
print("UCL Status:", response_ucl.status_code)
if response_ucl.status_code == 200:
    with open("data/raw/opta_ucl_stats.json", "w") as f:
        json.dump(response_ucl.json(), f, indent=2)
    print("✅ UCL data saved to data/raw/opta_ucl_stats.json")
else:
    print("❌ UCL request failed")


