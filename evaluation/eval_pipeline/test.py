from core.qdrant import client
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("BAAI/bge-m3")

query = "Những ai đủ điều kiện để nộp hồ sơ đăng ký dự thi cao học đợt 2 năm 2016 và thời hạn nộp hồ sơ đến khi nào?"

response = client.query_points(collection_name="main_collection",
                               query=embedder.encode(query),
                               with_payload=True)
for point in response.points:
    print(point.id)

