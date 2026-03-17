from pymongo import MongoClient
from .config import settings

client = MongoClient(settings.mongodb_url)
local_client = MongoClient(settings.local_mongodb_uri)

db = client[settings.database_name]
local_db = local_client[settings.database_name]

