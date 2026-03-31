import requests
from bs4 import BeautifulSoup
import sys
import json

if len(sys.argv) < 2:
    print("Usage: python get_map_top100.py <map_id>")
    print("Example: python get_map_top100.py 001")
    sys.exit(1)

map_id = sys.argv[1]

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://kog.tw/",
    "X-Requested-With": "XMLHttpRequest", 
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
})

print("Establishing session...")
session.get("https://kog.tw/")

url = f"https://kog.tw/get.php?p=maps&p=maps&map={map_id}"
print(f"Fetching Top 100 for Map: {map_id}...")

response = session.get(url)

if response.status_code == 200:
    if not response.text.strip():
        print("Failed: The server returned an empty response. We might be blocked.")
        sys.exit(1)

    print("Parsing leaderboard...")
    soup = BeautifulSoup(response.text, 'html.parser')

    rows = soup.find_all('tr')

    leaderboard = []

    for row in rows:

        th = row.find('th')
        tds = row.find_all('td')

        if th and len(tds) >= 2:
            rank = th.text.strip()
            score = tds[0].text.strip()
            player_tag = tds[1].find('a')
            if player_tag:
                player_name = player_tag.text.strip()
                leaderboard.append({
                    "rank": rank,
                    "score": score,
                    "player": player_name
                })
    print(f"\nSuccessfully scraped {len(leaderboard)} players from map {map_id}!")
    # print("\nPreview of Top 5:")
    # print(json.dumps(leaderboard[:5], indent=4))

    # If you want to save it to a file, uncomment these lines:
    # with open(f"map_{map_id}_top100.json", "w") as f:
    #     json.dump(leaderboard, f, indent=4)

else:
    print(f"Failed to fetch map {map_id}. Status code: {response.status_code}")
