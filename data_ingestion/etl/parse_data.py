from core.boto_client import s3
from bs4 import BeautifulSoup
import trafilatura
import time
import re
import unicodedata

from core.config import settings
from core.database import db

from model.document import Document
from model.lowcontent import LowContent

from repositories.page_repository import update_page_is_parse

pages_collection = db["pages"]
sitemaps_collection = db["sitemaps"]
documents_collection = db["documents"]
lowcontents_collection = db["lowcontents"]

def extract_title(soup):
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og["content"].strip()

    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    if soup.title and soup.title.string:
        return soup.title.string.split(" - ")[0].strip()

    return None

def convert_from_html(page):
    is_exist = documents_collection.count_documents({"source_url":page["url"]}, limit=1) > 0

    try:
        response = s3.get_object(
            Bucket=settings.bucket_name,
            Key=page["url"]
        )
    except Exception as e:
        print(f"Lỗi không tìm thấy html trên s3: {e}")
        time.sleep(5)
        return False

    html = response["Body"].read().decode("utf-8-sig")
    soup = BeautifulSoup(html, "lxml")

    source_url = page["url"]
    title = extract_title(soup=soup)
    author = soup.find("meta", attrs={"name": "author"})
    author_content = author["content"] if author else None
    published_date = soup.find("meta", property="article:published_time")
    raw_date = None
    if published_date:
        raw_date = published_date.get("content")

    markdown_content = trafilatura.extract(
            html, 
            output_format='markdown',
            include_tables=True,
            include_images=True,
            include_links=True
    )
    markdown_content = re.sub(r"\n+", " ", markdown_content).strip()
    markdown_content = unicodedata.normalize("NFC", markdown_content)

    if (len(markdown_content) < 500):
        print("Nội dung không đủ dài")
        lowcontent = LowContent(url=page["url"])
        lowcontents_collection.insert_one(lowcontent.model_dump())
        return False
    else:
        if is_exist:
            query = {"source_url": source_url}
            new_values = {"$set": 
                                {
                                    "title": title, 
                                    "content": markdown_content,
                                    "author": author_content
                                }
                            }
            result = documents_collection.update_one(
                query,
                new_values
            )

            print(f"Số lượng bản ghi khớp: {result.matched_count}")
            print(f"Số lượng bản ghi đã sửa: {result.modified_count}")
        else:
            doc = Document(source_url=source_url,
                        title=title,
                        content=markdown_content,
                        parent_id=page["sitemap_url"],
                        author=author_content,
                        published_date=raw_date)
            
            documents_collection.insert_one(doc.model_dump())

            print(f"Đã lưu thành công {title}")

    update_page_is_parse(url=page["url"], is_parse=True)
    
    print(f"Đã xử lý {title} với độ dài là {len(markdown_content)}")

def parse_data(need_parse_lst: list=None):
    url_lst = []
    if need_parse_lst:
        for page in need_parse_lst:
            if convert_from_html(page):
                url_lst.append(page["url"])
    else:
        pages = pages_collection.find({"is_parse": False})

        for page in pages:
            if convert_from_html(page):
                url_lst.append(page["url"])

    return url_lst

            
