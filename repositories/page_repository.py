from model.page import Page

from core.database import db

pages_collection = db["pages"]

def save_page(page: Page):
    try:
        pages_collection.insert_one(page.model_dump())
        print("Lưu page thành công")
    except Exception as e:
        print(f"Lỗi khi lưu page: {e}")

def find_one_page(url):
    try: 
        page = pages_collection.find_one({"url": url})
    except Exception as e:
        print(f"Lỗi khi truy suất page để kiểm tra tồn tại: {e}")

    return page

def updata_page_last_mod(url, new_last_mod):
    try:
        pages_collection.update_one(
            {"url": url},
            {"$set": {"last_mod": new_last_mod}}
        )
        print("Đã update page last mod")
    except Exception as e:
        print(f"Lỗi khi khi update page last mod: {e}")