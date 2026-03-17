from qdrant_client import QdrantClient
from .config import settings
from qdrant_client.http.models import PointStruct #

client = QdrantClient(url=settings.qdrant_endpoint,
                      api_key=settings.qdrant_key)

local_client = QdrantClient() 

def sync_qdrant_cloud_to_local(batch_size=100):
    # 1. Lấy danh sách tất cả collections trên Cloud
    cloud_collections = client.get_collections().collections
    
    print(f"Bắt đầu đồng bộ {len(cloud_collections)} collections của Qdrant...\n")

    for coll in cloud_collections:
        collection_name = coll.name
        print(f"⏳ Đang xử lý collection: '{collection_name}'...")

        # 2. Lấy cấu hình của collection trên cloud (kích thước vector, thuật toán tính khoảng cách...)
        collection_info = client.get_collection(collection_name)
        vectors_config = collection_info.config.params.vectors

        # 3. Tạo collection mới ở local với cấu hình y hệt
        # Dùng recreate_collection sẽ tự động xóa collection cũ ở local (nếu có) để làm mới
        local_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=vectors_config
        )
        print(f"   Đã tạo xong schema cho '{collection_name}' ở local.")

        # 4. Bắt đầu cuộn (scroll) dữ liệu từ Cloud về
        offset = None
        total_migrated = 0

        while True:
            # Lấy 1 batch dữ liệu bao gồm cả payload (thông tin đi kèm) và vector
            records, offset = client.scroll(
                collection_name=collection_name,
                limit=batch_size,
                offset=offset,
                with_payload=True,
                with_vectors=True
            )

            if not records:
                break # Đã hết dữ liệu

            # --- PHẦN CODE MỚI THÊM ---
            # Chuyển đổi từ Record sang PointStruct
            points_to_upsert = [
                PointStruct(
                    id=record.id,
                    vector=record.vector,
                    payload=record.payload
                )
                for record in records
            ]

            # 5. Đẩy batch dữ liệu này vào local
            local_client.upsert(
                collection_name=collection_name,
                points=points_to_upsert # <--- Dùng biến đã được chuyển đổi
            )
            
            total_migrated += len(records)
            print(f"   -> Đã copy {total_migrated} vectors...")

            # Nếu offset trả về là None nghĩa là đã cuộn đến bản ghi cuối cùng
            if offset is None:
                break

        print(f"✅ Hoàn tất '{collection_name}'! Tổng cộng: {total_migrated} vectors.\n")

    print("🎉 TẤT CẢ DỮ LIỆU QDRANT ĐÃ ĐƯỢC ĐỒNG BỘ VỀ LOCAL THÀNH CÔNG!")

# if __name__ == "__main__":
#     sync_qdrant_cloud_to_local()


