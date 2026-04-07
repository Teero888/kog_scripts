import sys
import json
import time
import sys
from urllib.parse import urlparse, parse_qs
from curl_cffi import requests

def time_to_seconds(t_str):
    """Converts HH:MM:SS to total seconds."""
    try:
        parts = list(map(int, t_str.split(':')))
        if len(parts) == 3: # HH:MM:SS
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        return 0
    except:
        return 0

def main():
    if len(sys.argv) <= 1:
        print("invalid usage, first argument must be the player name")
        sys.exit(1);

    player_name = sys.argv[1]

    with requests.Session() as s:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0"}
        s.get("https://kog.tw/", headers=headers, impersonate="chrome124")
        url = f"https://kog.tw/get.php?p=players&p=players&player={player_name}"
        headers.update({"Referer": "https://kog.tw/"})
        resp = s.get(url, headers=headers, impersonate="chrome124", timeout=120)

        if not 'div class="container"' in resp.text:
            print(json.dumps({"status": 403, "error": "Blocked or empty response"}, indent=4))
            sys.exit(1)

if __name__ == "__main__":
    main()
