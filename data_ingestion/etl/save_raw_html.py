import requests
from .helpers import load_site_map, parse_datatime, normalize_dt
from pathlib import Path

from core.boto_client import s3
from core.config import settings

from model.page import Page
from model.sitemap import Sitemap

from repositories.page_repository import save_page, find_one_page, updata_page_last_mod
from repositories.sitemap_repository import save_sitemap, find_one_sitemap, updata_sitemap_last_mod

current_file = Path(__file__)

BASE_DIR = current_file.parent

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def save_html(url):
    try:
        response = requests.get(url=url, headers=headers, verify=False)
        object_name = url.replace("https://ptithcm.edu.vn", "")
        s3.put_object(
            Bucket=settings.bucket_name,
            Key=object_name,
            Body=response.content,
            ContentType='text/html'
        )
        print(f"Save {object_name} succcesfully!!")
    except Exception as e:
        print(f"Error while save html object to s3: {e}")

def initiate_data(sitemap_index_url):
    url_tags, last_mod_tags = load_site_map(url=sitemap_index_url)

    for url, last_mod in zip(url_tags, last_mod_tags):
        sitemap = Sitemap(url=url.text.replace("https://ptithcm.edu.vn", ""), last_mod=last_mod.text)
    
        page_url_tags, page_last_mod_tags = load_site_map(url=url.text)

        for page_url, page_last_mod in zip(page_url_tags, page_last_mod_tags):
            page = Page(url=page_url.text.replace("https://ptithcm.edu.vn", ""),
                        sitemap_url=sitemap.url,
                        last_mod=page_last_mod.text)
            # save_html(page_url)
            try:
                print(f"Đang lưu page {page_url.text} và db")
                save_page(page=page)
                print("Lưu thành công")
            except Exception as e:
                print(e)
        try:
            print(f"Đã lưu xong site map {url.text}")
            save_sitemap(sitemap=sitemap)
            print("Lưu thành công")
        except Exception as e:
            print(e)

def crawl_raw_html(sitemap_index_url):
    print("start cào html")
    need_parse = []
    url_tags, last_mod_tags = load_site_map(url=sitemap_index_url)

    for url, last_mod in zip(url_tags, last_mod_tags):
        save_url = url.text.replace("https://ptithcm.edu.vn", "")
        sitemap = find_one_sitemap(url=save_url)
        page_urls, page_last_mods = load_site_map(url=url.text)
        if sitemap:
            web_last_mod = normalize_dt(parse_datatime(last_mod))
            db_last_mod = normalize_dt(sitemap["last_mod"])

            if web_last_mod.timestamp() != db_last_mod.timestamp():
                for purl, plast_mod in zip(page_urls, page_last_mods):
                    save_purl = purl.text.replace("https://ptithcm.edu.vn", "")
                    page = find_one_page(save_purl)
                    web_plast_mod = normalize_dt(parse_datatime(plast_mod))

                    if page == None:
                        page = Page(url=save_purl,
                                    sitemap_url=save_url,
                                    last_mod=plast_mod.text)
                        save_html(purl.text)
                        save_page(page)
                        print(f"Page mới {save_purl}")
                        need_parse.append(page)
                    else:
                        db_page_last_mod = normalize_dt(page["last_mod"])
                        if web_plast_mod.timestamp() != db_page_last_mod.timestamp():
                            updata_page_last_mod(url=save_purl, new_last_mod=plast_mod.text)
                            save_html(page)
                            need_parse.append(page)
                            print(f"Modify page {save_purl}")
                updata_sitemap_last_mod(url=save_url, new_last_mod=last_mod.text)
            else:
                print("Éo có gì mới")
        else:
            sitemap = Sitemap(url=save_url, last_mod=last_mod.text)
            for url, last_mod in zip(page_urls, page_last_mods):
                save_url = url.text.replace("https://ptithcm.edu.vn", "")
                page = Page(url=save_url, sitemap_url=sitemap.url, last_mod=last_mod.text)
                save_html(url=url.text)
                save_page(page=page)
                need_parse.append(page)
            save_sitemap(sitemap=sitemap)
    return need_parse

# if __name__ == "__main__":
#     crawl_raw_html(sitemap_index_url=settings.sitemap_index_url, root_csv_path=settings.root_csv)
#     initiate_data(settings.sitemap_index_url)
#     crawl_raw_html(sitemap_index_url=settings.sitemap_index_url)