import os
import time
from pymongo import MongoClient
from qdrant_client import QdrantClient

# ======================
# ENV VARIABLES
# ======================
ATLAS_URI = os.getenv("MONGODB_URL")
LOCAL_MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DATABASE_NAME", "PTITBOT")

QDRANT_CLOUD_URL = os.getenv("QDRANT_CLOUD_ENDPOINT")
QDRANT_CLOUD_API_KEY = os.getenv("QDRANT_CLOUD_KEY")

QDRANT_LOCAL_URL = "http://qdrant:6333"
QDRANT_LOCAL_KEY = os.getenv("QDRANT_KEY")
# ======================
# WAIT FOR SERVICES
# ======================
def wait_for_mongo(uri, retries=10):
    for i in range(retries):
        try:
            client = MongoClient(uri)
            client.admin.command("ping")
            print("✅ MongoDB is ready")
            return
        except Exception:
            print("⏳ Waiting for MongoDB...")
            time.sleep(3)
    raise Exception("❌ MongoDB not available")


def wait_for_qdrant(url, api_key=None, retries=10):
    for i in range(retries):
        try:
            client = QdrantClient(url=url, api_key=api_key)
            client.get_collections()
            print("✅ Qdrant is ready")
            return
        except Exception:
            print("⏳ Waiting for Qdrant...")
            time.sleep(3)
    raise Exception("❌ Qdrant not available")

# ======================
# MONGO MIGRATION
# ======================
def migrate_mongo():
    print("🚀 Migrating MongoDB...")

    atlas_client = MongoClient(ATLAS_URI)
    local_client = MongoClient(LOCAL_MONGO_URI)

    atlas_db = atlas_client[DB_NAME]
    local_db = local_client[DB_NAME]

    collections = atlas_db.list_collection_names()

    for col in collections:
        print(f"➡️ Migrating collection: {col}")
        atlas_col = atlas_db[col]
        local_col = local_db[col]

        docs = list(atlas_col.find())
        if docs:
            local_col.delete_many({})
            local_col.insert_many(docs)
            print(f"   ✅ {len(docs)} documents migrated")
        else:
            print("   ⚠️ Empty collection")

# ======================
# QDRANT MIGRATION
# ======================
def migrate_qdrant():
    print("🚀 Migrating Qdrant...")

    cloud = QdrantClient(url=QDRANT_CLOUD_URL, api_key=QDRANT_CLOUD_API_KEY)
    local = QdrantClient(url=QDRANT_LOCAL_URL, api_key=QDRANT_LOCAL_KEY)

    collections = cloud.get_collections().collections

    for col in collections:
        name = col.name
        print(f"➡️ Migrating collection: {name}")

        info = cloud.get_collection(name)
        vectors_config = info.config.params.vectors

        # recreate collection locally
        local.recreate_collection(
            collection_name=name,
            vectors_config=vectors_config,
        )

        points, _ = cloud.scroll(collection_name=name, limit=10000)

        if points:
            local.upsert(collection_name=name, points=points)
            print(f"   ✅ {len(points)} vectors migrated")
        else:
            print("   ⚠️ Empty collection")

# ======================
# MAIN
# ======================
if __name__ == "__main__":
    print("⏳ Waiting for services...")

    wait_for_mongo(LOCAL_MONGO_URI)
    wait_for_qdrant(QDRANT_LOCAL_URL)

    migrate_mongo()
    migrate_qdrant()

    print("🎉 Migration completed!")
