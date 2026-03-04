from model.sitemap import Sitemap

from core.database import db

sitemaps_collection = db["sitemaps"]

def save_sitemap(sitemap: Sitemap):
    try:
        sitemaps_collection.insert_one(sitemap.model_dump())
        print("Lưu sitemap thành công")
    except Exception as e:
        print(f"Lỗi khi lưu sitemap: {e}")

def find_one_sitemap(url):
    try: 
        sitemap = sitemaps_collection.find_one({"url": url})
    except Exception as e:
        print(f"Lỗi khi truy suất sitemap để kiểm tra tồn tại: {e}")

    return sitemap

def updata_sitemap_last_mod(url, new_last_mod):
    try:
        sitemaps_collection.update_one(
            {"url": url},
            {"$set": {"last_mod": new_last_mod}}
        )
        print("Đã update sitemap last mod")
    except Exception as e:
        print(f"Lỗi khi khi update sitemap last mod: {e}")