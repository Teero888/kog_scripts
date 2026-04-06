import sys
import json
import time
import sys
from urllib.parse import urlparse, parse_qs
from curl_cffi import requests
from bs4 import BeautifulSoup

def time_to_seconds(t_str):
    """Converts HH:MM:SS to total seconds."""
    try:
        parts = list(map(int, t_str.split(':')))
        if len(parts) == 3: # HH:MM:SS
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        return 0
    except:
        return 0

def parse_kog_to_spec(html_content):
    soup = BeautifulSoup(html_content, "lxml")

    result = {
        "status": 200,
        "data": {
            "points": {},
            "finishedMaps": [],
            "unfinishedMaps": [],
            "warnings": [],
            "last_tee": {}
        }
    }
    
    d = result["data"]

    stats_list = soup.find_all("li", class_="list-group-item")
    player_name = soup.find("h2").text.strip() if soup.find("h2") else ""

    rank, t_points, points, s_points = 0, 0, 0, 0
    for li in stats_list:
        txt = li.get_text(strip=True)
        if "Rank" in txt:
            rank = int(li.find("b").text.replace(".", "").strip())
            # Extract total points from "Rank X. with Y points"
            t_points = int(''.join(filter(str.isdigit, txt.split("with")[-1])))
        elif "Fixed points" in txt:
            points = int(li.find("b").text.strip())
        elif "Season points" in txt:
            s_points = int(li.find("b").text.strip())

    d["points"] = {
        "Rank": rank,
        "Name": player_name,
        "TPoints": t_points,
        "PvPpoints": 0, # Not explicitly in this HTML snippet
        "Points": points,
        "Seasonpoints": s_points,
        "RewardIndex": 0,
        "Powers": ""
    }

    fin_table = soup.select_one("#pills-finished table tbody")
    if fin_table:
        for row in fin_table.find_all("tr"):
            cols = row.find_all("td")
            map_name = row.find("th").text.strip()
            if len(cols) >= 3:
                d["finishedMaps"].append({
                    "Map": map_name,
                    "Time": time_to_seconds(cols[0].text.strip()),
                    "Timestamp": cols[2].text.strip()
                })

    unfin_table = soup.select_one("#pills-unfinished table tbody")
    if unfin_table:
        for row in unfin_table.find_all("tr"):
            map_name = row.find("th").text.strip()
            d["unfinishedMaps"].append({"Map": map_name})

    summary_table = soup.select_one("#nav-maps table tbody tr")
    if summary_table:
        # Categories in order: Solo, Easy, Main, Hard, Insane, Extreme, Mod
        keys = ["sol", "easy", "mn", "hrd", "ins", "ext", "mod"]
        cells = summary_table.find_all("td")
        for i, cell in enumerate(cells):
            if i < len(keys):
                parts = cell.text.split("/")
                finished = int(parts[0].strip())
                total = int(parts[1].strip())
                d[f"fin_{keys[i]}"] = [{"myoutput": finished}]
                map_key = "main_maps" if keys[i] == "mn" else f"{keys[i]}_maps"
                d[map_key] = [{"myoutput": total}]

    # Last Tee (Skin Data)
    skin_img = soup.find("img", id="playerSkin")
    if skin_img and 'src' in skin_img.attrs:
        params = parse_qs(urlparse(skin_img['src']).query)
        d["last_tee"] = [{
            "SkinName": params.get("skin", [""])[0],
            "SkinColorBody": int(params.get("body_color", [0])[0]),
            "SkinColorFeet": int(params.get("feet_color", [0])[0])
        }]

    return result

def main():
    player_name = sys.argv[1] if len(sys.argv) > 1 else "Teero"

    with requests.Session() as s:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0"}
        # Front door for session
        s.get("https://kog.tw/", headers=headers, impersonate="chrome124")

        # Request data
        url = f"https://kog.tw/get.php?p=players&p=players&player={player_name}"
        headers.update({"Referer": "https://kog.tw/"})
        resp = s.get(url, headers=headers, impersonate="chrome124", timeout=60)

        if 'div class="container"' in resp.text:
            output = parse_kog_to_spec(resp.text)
            print(json.dumps(output))
        else:
            print(json.dumps({"status": 403, "error": "Blocked or empty response"}, indent=4))
            sys.exit(1)

if __name__ == "__main__":
    main()