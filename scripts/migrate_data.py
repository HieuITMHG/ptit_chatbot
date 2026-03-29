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

    # Khởi tạo client Cloud và Local
    cloud = QdrantClient(url=QDRANT_CLOUD_URL, api_key=QDRANT_CLOUD_API_KEY, check_compatibility=False)
    local = QdrantClient(url=QDRANT_LOCAL_URL, api_key=QDRANT_LOCAL_KEY, check_compatibility=False)

    try:
        collections = cloud.get_collections().collections
    except Exception as e:
        print(f"❌ Không thể lấy danh sách collection từ Cloud: {e}")
        return

    for col in collections:
        name = col.name
        print(f"➡️ Migrating collection: {name}")

        # Lấy cấu hình vector từ Cloud để tạo collection tương ứng ở Local
        info = cloud.get_collection(name)
        vectors_config = info.config.params.vectors

        # Xóa và tạo lại collection ở Local (Tránh lặp dữ liệu)
        local.recreate_collection(
            collection_name=name,
            vectors_config=vectors_config,
        )

        # QUAN TRỌNG: with_vectors=True để lấy cả dữ liệu vector về máy
        points, _ = cloud.scroll(collection_name=name, limit=10000, with_vectors=True)

        if points:
            points_to_upsert = []
            for point in points:
                # Kiểm tra nếu point có vector thì mới thêm vào danh sách migrate
                if point.vector is not None:
                    points_to_upsert.append(
                        PointStruct(
                            id=point.id,
                            vector=point.vector,
                            payload=point.payload
                        )
                    )
            
            if points_to_upsert:
                # Đẩy dữ liệu vào Qdrant Local
                local.upsert(collection_name=name, points=points_to_upsert)
                print(f"   ✅ {len(points_to_upsert)} vectors migrated")
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