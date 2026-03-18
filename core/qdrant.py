import time
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse
from .config import settings 

# Khởi tạo client (Thay bằng settings của bạn)
client = QdrantClient(url=settings.qdrant_endpoint, api_key=settings.qdrant_key)

def sync_qdrant_cloud_to_local(batch_size=100, max_retries=5):
    cloud_collections = client.get_collections().collections
    print(f"Bắt đầu đồng bộ {len(cloud_collections)} collections...\n")

    for coll in cloud_collections:
        collection_name = coll.name
        print(f"⏳ Đang xử lý collection: '{collection_name}'...")

        # 1. Lấy cấu hình và tạo collection nếu chưa có
        # Lưu ý: Nếu dùng recreate_collection, nó sẽ XÓA sạch local mỗi lần chạy.
        # Để giữ lại dữ liệu cũ và "pass qua", ta dùng logic kiểm tra sự tồn tại.
        collection_info = client.get_collection(collection_name)
        vectors_config = collection_info.config.params.vectors

        try:
            local_client.get_collection(collection_name)
            print(f"   Collection '{collection_name}' đã tồn tại ở local. Sẽ kiểm tra ID để bỏ qua trùng lặp.")
        except Exception:
            local_client.create_collection(
                collection_name=collection_name,
                vectors_config=vectors_config
            )
            print(f"   Đã tạo mới collection '{collection_name}' ở local.")

        # 2. Bắt đầu cuộn (scroll) dữ liệu
        offset = None
        total_migrated = 0
        total_skipped = 0

        while True:
            records = []
            # Thử lại 5 lần khi lấy dữ liệu (Scroll)
            for attempt in range(max_retries):
                try:
                    records, offset = client.scroll(
                        collection_name=collection_name,
                        limit=batch_size,
                        offset=offset,
                        with_payload=True,
                        with_vectors=True
                    )
                    break 
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"   ⚠️ Lỗi lấy dữ liệu (Lần {attempt+1}/{max_retries}). Thử lại sau 2s...")
                        time.sleep(2)
                    else:
                        print(f"   ❌ Thất bại sau 5 lần thử lấy dữ liệu: {e}")
                        return

            if not records:
                break

            # --- LOGIC BỎ QUA ID ĐÃ TỒN TẠI ---
            # Lấy danh sách ID trong batch hiện tại
            batch_ids = [r.id for r in records]
            
            # Kiểm tra xem ID nào đã có ở Local
            existing_points = local_client.retrieve(
                collection_name=collection_name,
                ids=batch_ids,
                with_payload=False,
                with_vectors=False
            )
            existing_ids = {p.id for p in existing_points}

            # Chỉ lọc ra những point CHƯA có ở local
            points_to_upsert = [
                PointStruct(id=r.id, vector=r.vector, payload=r.payload)
                for r in records if r.id not in existing_ids
            ]

            skipped_in_batch = len(records) - len(points_to_upsert)
            total_skipped += skipped_in_batch

            # 3. Đẩy dữ liệu vào Local với logic Retry
            if points_to_upsert:
                for attempt in range(max_retries):
                    try:
                        local_client.upsert(
                            collection_name=collection_name,
                            points=points_to_upsert
                        )
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"   ⚠️ Lỗi ghi dữ liệu (Lần {attempt+1}/{max_retries}). Đang thử lại...")
                            time.sleep(2)
                        else:
                            print(f"   ❌ Không thể ghi vào local sau 5 lần thử: {e}")

            total_migrated += len(points_to_upsert)
            print(f"   -> Đã thêm mới: {total_migrated} | Đã bỏ qua: {total_skipped}...")

            if offset is None:
                break

        print(f"✅ Xong '{collection_name}'! Thêm mới: {total_migrated}, Bỏ qua: {total_skipped}.\n")

    print("🎉 TẤT CẢ DỮ LIỆU ĐÃ ĐƯỢC ĐỒNG BỘ!")

if __name__ == "__main__":
    sync_qdrant_cloud_to_local()