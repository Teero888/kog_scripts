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

session.get("https://kog.tw/")

url = "https://kog.tw/get.php?p=maps"
response = session.get(url)

if response.status_code == 200:
    if not response.text.strip():
        print("Failed: The server returned an empty response. We are being blocked.")
        sys.exit(1)
    soup = BeautifulSoup(response.text, 'html.parser')
    map_cards = soup.find_all('div', class_='card')
    if len(map_cards) == 0:
        print("\nFound 0 maps! The HTML structure might be different than expected.")
        print("Here is what the server actually sent us (first 1000 chars):")
        print(response.text[:1000])
        sys.exit(1)
    all_maps = []
    for card in map_cards:
        name_tag = card.find('h4')
        map_name = name_tag.text.strip() if name_tag else "Unknown"
        list_items = card.find_all('li', class_='list-group-item')
        stars = 0
        map_type = "Unknown"
        points = "0 points"
        mapper = "Unknown"
        if len(list_items) >= 4:
            stars = len(list_items[0].find_all('i', class_='bi-star-fill'))
            map_type = list_items[1].text.strip()
            points = list_items[2].text.strip()
            mapper = list_items[3].text.strip()

        footer = card.find('div', class_='card-footer')
        release_date = ""
        if footer:
            release_date = footer.text.strip().replace("Released at ", "")

        map_data = {
            "name": map_name,
            "stars": stars,
            "type": map_type,
            "points": points,
            "mapper": mapper,
            "release_date": release_date
        }

        all_maps.append(map_data)

    print(json.dumps(all_maps, ensure_ascii=False))

else:
    print(f"Failed to fetch maps. Status code: {response.status_code}")
