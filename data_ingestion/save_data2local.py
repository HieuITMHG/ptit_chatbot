from pymongo import MongoClient
from core.config import settings 
from core.database import db, local_db

documents_collection = local_db["documents"]

def sync_cloud_to_local(batch_size=1000):
    docs = documents_collection.find({}).limit(100)

    for doc in docs:
        print(doc["content"])

if __name__ == "__main__":
    sync_cloud_to_local()