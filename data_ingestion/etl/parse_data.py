from core.boto_client import s3
from bs4 import BeautifulSoup
import trafilatura
import time

from core.config import settings
from core.database import db

from model.document import Document
from model.lowcontent import LowContent

pages_collection = db["pages"]
sitemaps_collection = db["sitemaps"]
documents_collection = db["documents"]
lowcontents_collection = db["lowcontents"]

def parse_from_html(page: str):
    print(f"Processing {page["url"]}")

    is_exist =  documents_collection.count_documents({"source_url":page["url"]}, limit=1) > 0

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
    title = soup.title.string if soup.title else None
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
            result = documents_collection.update_one({
                query,
                new_values
            })

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

    
    print(f"Đã xử lý {title} với độ dài là {len(markdown_content)}")


# if __name__ == "__main__":
#     page_lst = pages_collection.find({})

#     for page in page_lst:
#         exist_doc = documents_collection.find_one({'source_url': page['url']})
#         if exist_doc:
#             print("Doc đã tồn tại")
#             continue
#         parse_from_html(page=page)
            
