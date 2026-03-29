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
def wait_for_qdrant(url, api_key=None, retries=10):
    for i in range(retries):
        try:
            client = QdrantClient(url=url, api_key=api_key, check_compatibility=False)
            client.get_collections()
            print("✅ Qdrant is ready")
            return
        except Exception:
            print("⏳ Waiting for Qdrant...")
            time.sleep(3)
    raise Exception("❌ Qdrant not available")

# ======================
# QDRANT MIGRATION
# ======================
def migrate_qdrant():
    print("🚀 Bắt đầu Migrate Qdrant...")

    # Tăng timeout lên 60s để tránh lỗi WriteTimeout
    cloud = QdrantClient(url=QDRANT_CLOUD_URL, api_key=QDRANT_CLOUD_API_KEY, check_compatibility=False, timeout=60)
    local = QdrantClient(url=QDRANT_LOCAL_URL, api_key=QDRANT_LOCAL_KEY, check_compatibility=False, timeout=60)

    try:
        cloud_collections = cloud.get_collections().collections
    except Exception as e:
        print(f"❌ Lỗi kết nối Qdrant Cloud: {e}")
        return

    for col in cloud_collections:
        name = col.name
        print(f"\n➡️ Đang xử lý collection: {name}")

        # --- LOGIC KIỂM TRA TỒN TẠI ---
        try:
            if local.collection_exists(name):
                # Kiểm tra số lượng bản ghi ở local
                local_info = local.get_collection(name)
                if local_info.points_count > 0:
                    print(f"   ⏩ Bỏ qua '{name}': Đã tồn tại {local_info.points_count} bản ghi ở Local.")
                    continue
        except Exception:
            pass # Nếu lỗi khi check tồn tại thì cứ tiến hành tạo mới/recreate

        # --- LẤY CẤU HÌNH TỪ CLOUD ---
        info = cloud.get_collection(name)
        vectors_config = info.config.params.vectors
        sparse_config = info.config.params.sparse_vectors # Quan trọng: Sửa lỗi 400 sparse vector

        # Tạo lại collection ở local
        print(f"   🔨 Đang tạo collection '{name}' ở Local...")
        local.recreate_collection(
            collection_name=name,
            vectors_config=vectors_config,
            sparse_vectors_config=sparse_config
        )

        # --- LẤY DỮ LIỆU (SCROLL) ---
        print(f"   📥 Đang tải dữ liệu từ Cloud (kèm vectors)...")
        points, _ = cloud.scroll(collection_name=name, limit=10000, with_vectors=True)

        if points:
            # Chuyển đổi sang PointStruct
            points_to_upsert = [
                PointStruct(
                    id=point.id,
                    vector=point.vector,
                    payload=point.payload
                ) for point in points if point.vector is not None
            ]
            
            if points_to_upsert:
                # CHIA BATCH ĐỂ ĐẨY (TRÁNH TIMEOUT)
                batch_size = 200
                total = len(points_to_upsert)
                for i in range(0, total, batch_size):
                    batch = points_to_upsert[i : i + batch_size]
                    local.upsert(collection_name=name, points=batch)
                    print(f"   ✅ Đã đẩy {min(i + batch_size, total)} / {total} vectors...")
                
                print(f"   ✨ Hoàn thành migrate: {name}")
            else:
                print("   ⚠️ Không tìm thấy vector hợp lệ.")
        else:
            print("   ⚠️ Cloud Collection này đang trống.")

# ======================
# MAIN
# ======================
if __name__ == "__main__":
    print("⏳ Đang kiểm tra dịch vụ...")

    # Chỉ chạy Qdrant vì MongoDB bạn đã báo xong
    wait_for_qdrant(QDRANT_LOCAL_URL, api_key=QDRANT_LOCAL_KEY)

    # migrate_mongo() # Đã xử lý xong nên cmt lại

    migrate_qdrant()

    print("\n🎉 TẤT CẢ ĐÃ HOÀN TẤT!")