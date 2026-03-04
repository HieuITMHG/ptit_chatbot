import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timezone

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def load_site_map(url):
    response = requests.get(url=url, headers=headers, verify=False)

    if response.status_code != 200:
        return [], []

    soup = BeautifulSoup(response.content, "xml")

    url_tags = []
    last_mod_tags = []

    # nếu là sitemap index
    sitemap_tags = soup.find_all("sitemap")
    if sitemap_tags:
        for sm in sitemap_tags:
            loc = sm.find("loc")
            lastmod = sm.find("lastmod")
            if loc and lastmod:
                url_tags.append(loc)
                last_mod_tags.append(lastmod)
        return url_tags, last_mod_tags

    # nếu là sitemap thường
    url_elements = soup.find_all("url")
    if url_elements:
        for u in url_elements:
            loc = u.find("loc")
            lastmod = u.find("lastmod")
            if loc and lastmod:
                url_tags.append(loc)
                last_mod_tags.append(lastmod)
        return url_tags, last_mod_tags

    return [], []

def csv_to_dict(file_path):
    data = {}

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            data[row["url_path"]] = row["last_mod"]

    return data

def parse_datatime(last_mod):
    return datetime.fromisoformat(last_mod.text)

def normalize_dt(dt):
    # Nếu là string → parse
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)

    # Nếu naive → gắn UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt