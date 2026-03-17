from pymongo import MongoClient
from .config import settings

client = MongoClient(settings.mongodb_url)
db = client[settings.database_name]

try:
    local_client = MongoClient(settings.local_mongodb_uri)
    local_db = local_client[settings.database_name]
except:
    print("Không thể kết nối mongodb local")
