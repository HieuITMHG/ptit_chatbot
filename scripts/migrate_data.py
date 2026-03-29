import os
import time
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

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
            # check_compatibility=False giúp bỏ qua lỗi lệch version giữa client và server
            client = QdrantClient(url=url, api_key=api_key, check_compatibility=False)
            client.get_collections()
            print("✅ Qdrant is ready")
            return
        except Exception:
            print("⏳ Waiting for Qdrant...")
            time.sleep(3)
    raise Exception("❌ Qdrant not available")

# ======================
# MONGO MIGRATION (ĐÃ XỬ LÝ - ĐƯỢC CMT LẠI)
# ======================
# def migrate_mongo():
#     print("🚀 Migrating MongoDB...")
#     atlas_client = MongoClient(ATLAS_URI)
#     local_client = MongoClient(LOCAL_MONGO_URI)
#     atlas_db = atlas_client[DB_NAME]
#     local_db = local_client[DB_NAME]
#     collections = atlas_db.list_collection_names()
#     for col in collections:
#         print(f"➡️ Migrating collection: {col}")
#         atlas_col = atlas_db[col]
#         local_col = local_db[col]
#         docs = list(atlas_col.find())
#         if docs:
#             local_col.delete_many({})
#             local_col.insert_many(docs)
#             print(f"   ✅ {len(docs)} documents migrated")
#         else:
#             print("   ⚠️ Empty collection")

# ======================
# QDRANT MIGRATION
# ======================
def migrate_qdrant():
    print("🚀 Migrating Qdrant...")

    # Tăng timeout lên 60 giây để thoải mái truyền dữ liệu lớn
    cloud = QdrantClient(url=QDRANT_CLOUD_URL, api_key=QDRANT_CLOUD_API_KEY, check_compatibility=False, timeout=60)
    local = QdrantClient(url=QDRANT_LOCAL_URL, api_key=QDRANT_LOCAL_KEY, check_compatibility=False, timeout=60)

    try:
        collections = cloud.get_collections().collections
    except Exception as e:
        print(f"❌ Không thể lấy danh sách collection từ Cloud: {e}")
        return

    for col in collections:
        name = col.name
        print(f"➡️ Migrating collection: {name}")

        info = cloud.get_collection(name)
        vectors_config = info.config.params.vectors

        local.recreate_collection(
            collection_name=name,
            vectors_config=vectors_config,
        )

        # Lấy dữ liệu (có thể tăng limit nếu cần, nhưng 10k là khá ổn)
        points, _ = cloud.scroll(collection_name=name, limit=10000, with_vectors=True)

        if points:
            points_to_upsert = []
            for point in points:
                if point.vector is not None:
                    points_to_upsert.append(
                        PointStruct(
                            id=point.id,
                            vector=point.vector,
                            payload=point.payload
                        )
                    )
            
            if points_to_upsert:
                # CHIA BATCH: Mỗi lần đẩy 200 điểm để tránh Timeout
                batch_size = 200
                for i in range(0, len(points_to_upsert), batch_size):
                    batch = points_to_upsert[i : i + batch_size]
                    local.upsert(collection_name=name, points=batch)
                    print(f"   ✅ Đã đẩy {i + len(batch)} / {len(points_to_upsert)} vectors...")
                
                print(f"   ✨ Hoàn thành migrate collection: {name}")
            else:
                print("   ⚠️ No valid vectors found to migrate")
        else:
            print("   ⚠️ Empty collection")
# ======================
# MAIN
# ======================
if __name__ == "__main__":
    print("⏳ Waiting for services...")

    # Chờ Qdrant sẵn sàng
    wait_for_qdrant(QDRANT_LOCAL_URL, api_key=QDRANT_LOCAL_KEY)

    # Đã tắt MongoDB migration vì bạn đã xử lý rồi
    # migrate_mongo() 

    # Bắt đầu migrate dữ liệu vector
    migrate_qdrant()

    print("🎉 Migration completed!")