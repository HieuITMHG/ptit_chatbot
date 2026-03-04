from pymongo import MongoClient
from .config import get_settings

settings = get_settings()

client = MongoClient(settings.mongodb_url)

db = client[settings.database_name]

try:
    client.admin.command('ping')
    print("Kết nối MongoDB thành công!")
except Exception as e:
    print(f"Lỗi kết nối: {e}")