from .etl.save_raw_html import crawl_raw_html
from .etl.parse_data import parse_from_html

from core.config import settings

if __name__ == "__main__":
    need_parse = crawl_raw_html(settings.sitemap_index_url)

    for page in need_parse:
        parse_from_html(page)