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
    "X-Requested-With": "XMLHttpRequest"
})

session.get("https://kog.tw/")

url = "https://kog.tw/get.php?p=index"
response = session.get(url)

if response.status_code == 200:
    if not response.text.strip():
        print("Failed: Server returned an empty response.")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', class_='table-striped')

    if not table:
        print("Could not find the finishes table in the HTML.")
        sys.exit(1)

    tbody = table.find('tbody')
    rows = tbody.find_all('tr')

    recent_finishes = []

    for row in rows:
        tds = row.find_all('td')
        if len(tds) == 4:
            date_str = tds[0].text.strip()
            player_name = tds[1].text.strip()
            map_name = tds[2].text.strip()
            time_str = tds[3].text.strip()

            recent_finishes.append({
                "date": date_str,
                "player": player_name,
                "map": map_name,
                "time": time_str
            })

    print(json.dumps(recent_finishes, ensure_ascii=False))

else:
    print(f"Failed to fetch index. Status code: {response.status_code}")
