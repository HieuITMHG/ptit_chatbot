import requests
from helpers import load_site_map, csv_to_dict
from pathlib import Path
import boto3
from botocore.config import Config
import csv

current_file = Path(__file__)

BASE_DIR = current_file.parent
root_csv_path = BASE_DIR / "sitemap_index.csv"

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
            sitemap_csv_path = BASE_DIR / f"{file_name}.csv"

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
            print(root_lastmod.text)
            print(saved_index[root_id])

            if root_lastmod.text != saved_index[root_id]:
                url_tags, lastmod_tags = load_site_map(root_url.text)
                csv_path = BASE_DIR / f"{root_id.replace(".xml", "").replace("/", "")}.csv"
                child_index = csv_to_dict(csv_path)
                for url, lastmod in zip(url_tags, lastmod_tags):
                    id = url.text.replace("https://ptithcm.edu.vn", "")
                    if id in child_index:
                        if lastmod.text != child_index[id]:
                            need_process_lst.append(url.text)
    return need_process_lst

if __name__ == "__main__":
    # first_load(index_url=sitemap_index_url)
    check_index(index_url=sitemap_index_url, root_csv_path=root_csv_path)






