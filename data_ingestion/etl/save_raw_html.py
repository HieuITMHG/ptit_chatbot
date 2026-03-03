import requests
from helpers import load_site_map, csv_to_dict
from pathlib import Path
import boto3
from botocore.config import Config
import csv
import pandas as pd

current_file = Path(__file__)

BASE_DIR = current_file.parent
root_csv_path = BASE_DIR / "index/sitemap_index.csv"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

sitemap_index_url = "https://ptithcm.edu.vn/sitemap_index.xml"

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='admin',         
    aws_secret_access_key='admin123',  
    region_name='us-east-1',
    config=Config(s3={'addressing_style': 'path'})
)

BUCKET_NAME = "raw-html"

def save_html(url):
    try:
        response = requests.get(url=url, headers=headers, verify=False)
        object_name = url.replace("https://ptithcm.edu.vn", "")
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=object_name,
            Body=response.content,
            ContentType='text/html'
        )
        print(f"Save {object_name} succcesfully!!")
    except Exception as e:
        print(f"Error while save html object to s3: {e}")


def first_load(index_url):
    root_url_tags, root_lastmod_tags = load_site_map(url=index_url)

    with open(root_csv_path, "w", newline="", encoding="utf-8") as root_file:
        writer = csv.writer(root_file)
        writer.writerow(["url_path", "last_mod"])

        for root_url, root_lastmod in zip(root_url_tags, root_lastmod_tags):

            sitemap_full_url = root_url.text
            sitemap_id = sitemap_full_url.replace("https://ptithcm.edu.vn", "")
            last_mod = root_lastmod.text

            writer.writerow([sitemap_id, last_mod])

            file_name = sitemap_id.replace(".xml", "").replace("/", "")
            sitemap_csv_path = BASE_DIR / f"index/{file_name}.csv"

            lst_url, lst_last_mod = load_site_map(url=sitemap_full_url)

            with open(sitemap_csv_path, "w", newline="", encoding="utf-8") as sitemap_file:
                sitemap_writer = csv.writer(sitemap_file)
                sitemap_writer.writerow(["url_path", "last_mod"])

                for url, lastmod in zip(lst_url, lst_last_mod):
                    page_path = url.text.replace("https://ptithcm.edu.vn", "")
                    sitemap_writer.writerow([page_path, lastmod.text])

                    save_html(url=url.text)

            print(f"Created {sitemap_csv_path.name}")

    print("First load completed!")

def check_index(index_url, root_csv_path):
    need_process_lst = []
    root_url_tags, root_lastmod_tags = load_site_map(url=index_url)
    saved_index = csv_to_dict(root_csv_path)


    for root_url, root_lastmod in zip(root_url_tags, root_lastmod_tags):

        root_id = root_url.text.replace("https://ptithcm.edu.vn", "")

        if root_id in saved_index:
            old_sitemap = {}
            old_sitemap[root_url.text] = root_lastmod.text #Bố
            if root_lastmod.text != saved_index[root_id]:
                url_tags, lastmod_tags = load_site_map(root_url.text)
                csv_path = BASE_DIR / f"index/{root_id.replace(".xml", "").replace("/", "")}.csv"
                child_index = csv_to_dict(csv_path)
                for url, lastmod in zip(url_tags, lastmod_tags):
                    id = url.text.replace("https://ptithcm.edu.vn", "")
                    if id in child_index:
                        if lastmod.text != child_index[id]:
                            old_sitemap[url.text] = lastmod.text
                    else:
                        old_sitemap[url.text] = lastmod.text

                need_process_lst.append(old_sitemap)
        else:
                new_sitemap = {}
                new_sitemap[root_url.text] = root_lastmod.text
                need_process_lst.append(new_sitemap)
    return need_process_lst

def crawl_raw_html(sitemap_index_url, root_csv_path):
    link_lst = check_index(index_url=sitemap_index_url, root_csv_path=root_csv_path)
    count = 0
    for item in link_lst:

        dad_url, dad_last_mod = next(
            (k, v) for k, v in item.items() if k.endswith(".xml")
        )

        dad_id = dad_url.replace("https://ptithcm.edu.vn", "")
        dad_name = dad_id.replace(".xml", "").replace("/", "")
        dad_csv_path = BASE_DIR / f"index/{dad_name}.csv"

        if len(item) == 1:

            print(f"Sitemap mới: {dad_id}")

            # Update root index bằng pandas
            df_root = pd.read_csv(root_csv_path)

            if dad_id not in df_root["url_path"].values:
                df_root = pd.concat([
                    df_root,
                    pd.DataFrame([{
                        "url_path": dad_id,
                        "last_mod": dad_last_mod
                    }])
                ], ignore_index=True)

                df_root.to_csv(root_csv_path, index=False)

            # Crawl toàn bộ sitemap con
            url_tags, last_mod_tags = load_site_map(dad_url)

            rows = []

            for url, last_mod in zip(url_tags, last_mod_tags):
                page_id = url.text.replace("https://ptithcm.edu.vn", "")
                rows.append({
                    "url_path": page_id,
                    "last_mod": last_mod.text
                })
                save_html(url.text)
                count +=1

            pd.DataFrame(rows).to_csv(dad_csv_path, index=False)

        else:

            print(f"Cập nhật sitemap: {dad_id}")

            # Update sitemap cha
            df_root = pd.read_csv(root_csv_path)
            df_root.loc[df_root["url_path"] == dad_id, "last_mod"] = dad_last_mod
            df_root.to_csv(root_csv_path, index=False)

            # Load sitemap con 1 lần duy nhất
            df_child = pd.read_csv(dad_csv_path)

            for key, value in item.items():

                if key.endswith(".xml"):
                    continue

                page_id = key.replace("https://ptithcm.edu.vn", "")

                if page_id in df_child["url_path"].values:
                    df_child.loc[
                        df_child["url_path"] == page_id,
                        "last_mod"
                    ] = value
                else:
                    df_child = pd.concat([
                        df_child,
                        pd.DataFrame([{
                            "url_path": page_id,
                            "last_mod": value
                        }])
                    ], ignore_index=True)

                save_html(key)
                count += 1

            df_child.to_csv(dad_csv_path, index=False)
    print(f"Đã crawl lại {count} bài post")

if __name__ == "__main__":
    # first_load(index_url=sitemap_index_url)
    crawl_raw_html(sitemap_index_url=sitemap_index_url, root_csv_path=root_csv_path)