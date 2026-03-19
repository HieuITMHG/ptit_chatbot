import json
import numpy as np
from sklearn.cluster import KMeans
from core.qdrant import client

collection_name = "hybrid_collection"
num_clusters = 4

if __name__ == "__main__":
    print(f"Bắt đầu tải dữ liệu từ collection '{collection_name}'...")
    
    all_vectors = []
    all_payloads = []
    
    # Bước 1: Dùng lệnh scroll để lấy TẤT CẢ vectors và payloads theo từng batch
    offset = None
    while True:
        records, offset = client.scroll(
            collection_name=collection_name,
            limit=1000,          # Tải mỗi lần 1000 chunks để không bị quá tải mạng
            with_vectors=True,   # Bắt buộc lấy vector để chạy K-Means
            with_payload=True,   # Bắt buộc lấy payload để lưu ra file JSON
            offset=offset
        )
        
        for record in records:
            all_vectors.append(record.vector)
            all_payloads.append(record.payload)
            
        print(f"Đã tải {len(all_vectors)} chunks...")
            
        if offset is None:
            break # Hết dữ liệu thì thoát vòng lặp

    print(f"\n✅ Đã tải xong tổng cộng {len(all_vectors)} vectors và payloads.")

    if not all_vectors:
        print("Không tìm thấy dữ liệu nào trong collection!")
        exit()

    # Bước 2: Chuyển list vector thành mảng Numpy để đưa vào thuật toán
    X = np.array(all_vectors)

    # Bước 3: Chạy K-Means clustering để chia làm 3 phần
    print(f"\nĐang chạy K-Means clustering chia {num_clusters} cụm...")
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(X)
    
    # Bước 4: Nhóm các payload lại theo từng nhãn cụm (cluster label)
    # Tạo một dictionary với 3 key: 0, 1, 2 chứa list các rỗng
    clusters_data = {i: [] for i in range(num_clusters)}
    
    for label, payload in zip(labels, all_payloads):
        clusters_data[label].append(payload)

    # Bước 5: Ghi mỗi list payload vào một file JSON riêng biệt
    print("\nĐang lưu kết quả ra file JSON...")
    for cluster_id, payloads in clusters_data.items():
        filename = f"cluster_enrich_{cluster_id}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            # Lưu ý dùng ensure_ascii=False để không bị lỗi font tiếng Việt
            json.dump(payloads, f, ensure_ascii=False, indent=4)
            
        print(f"✅ Đã lưu {len(payloads)} chunks vào file: {filename}")

    print("\n🎉 Hoàn tất quá trình Clustering!")