import requests
import json
import sys

if len(sys.argv) < 2:
    print("Usage: python kog_player.py <player_name>")
    sys.exit(1)

player_name = sys.argv[1]

session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://kog.tw/",
    "X-Requested-With": "XMLHttpRequest",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
})

session.get("https://kog.tw/", headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})

token_url = "https://kog.tw/api.php?type=csrf-token"
token_res = session.get(token_url)

if not token_res.text.strip():
    print("Failed: The server still returned an empty response. It might be blocking python-requests entirely via Cloudflare TLS fingerprinting.")
    sys.exit(1)

try:
    nonce = token_res.json().get("nonce")
except requests.exceptions.JSONDecodeError:
    print("Failed to decode JSON. Raw response:")
    print(token_res.text[:500])
    sys.exit(1)

api_url = "https://kog.tw/api.php"
payload = {
    "nonce": nonce,
    "type": "players",
    "player": player_name,
    "tz": "America/New_York"
}

data_res = session.post(api_url, json=payload)
if data_res.status_code == 200:
    try:
        response_dict = data_res.json()
        if "data" in response_dict and isinstance(response_dict["data"], str):
            response_dict["data"] = json.loads(response_dict["data"])
        print(json.dumps(response_dict))
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode POST response. Raw text:")
        print(data_res.text[:500])
else:
    print(f"Failed to fetch data. Status Code: {data_res.status_code}")
    print(data_res.text[:500])
