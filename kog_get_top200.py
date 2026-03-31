import requests
from bs4 import BeautifulSoup
import json
import sys

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

url = "https://kog.tw/get.php?p=ranks&p=ranks"
print("Fetching Top 200 global ranks...")
response = session.get(url)

if response.status_code == 200:
    if not response.text.strip():
        print("Failed: The server returned an empty response.")
        sys.exit(1)

    print("Parsing global leaderboard...")
    soup = BeautifulSoup(response.text, 'html.parser')

    top_players = []

    first_place_card = soup.find('div', class_='card-body text-center')
    if first_place_card:
        name_tag = first_place_card.find('a')
        points_tag = first_place_card.find('h2')

        if name_tag and points_tag:
            top_players.append({
                "rank": 1,
                "name": name_tag.text.strip(),
                "points": int(points_tag.text.strip())
            })

    tables = soup.find_all('table', class_='table-striped')

    for table in tables:
        tbody = table.find('tbody')
        if not tbody:
            continue

        rows = tbody.find_all('tr')

        for row in rows:
            th = row.find('th')
            tds = row.find_all('td')

            if th and len(tds) == 2:
                rank = int(th.text.strip())
                player_name = tds[0].text.strip()
                points = int(tds[1].text.strip())

                top_players.append({
                    "rank": rank,
                    "name": player_name,
                    "points": points
                })
    top_players = sorted(top_players, key=lambda x: x['rank'])

    print(f"\nSuccessfully scraped {len(top_players)} players!")

    # Print the top 10 as a preview
    # print("\nPreview of Top 10:")
    # print(json.dumps(top_players[:10], indent=4))

    # Save the full list to a file if you want
    # with open("global_top_200.json", "w", encoding="utf-8") as f:
    #     json.dump(top_players, f, indent=4, ensure_ascii=False)
    #     print("\nSaved all 200 players to 'global_top_200.json'!")

else:
    print(f"Failed to fetch global ranks. Status code: {response.status_code}")
