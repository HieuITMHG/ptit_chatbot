from sentence_transformers import SentenceTransformer

# from core.database import db
# from core.config_loader import PipelineConfig
from core.qdrant import client

# quote_query_collection = db["quote_query"]

# def count_all_relevance_quote(query_id):
#     quote_query_collection.find({"query_id": query_id})



# def cal_recall_at_k(k: int, query_id) -> float:
#     quote_query_lst = quote_query_collection.find({"query_id": query_id})
#     total_relevance = len(quote_query_lst)


if __name__ == "__main__":
    encoder = SentenceTransformer("intfloat/multilingual-e5-base")
    res = client.query_points(collection_name="m-e5-base",
                        query=encoder.encode("cách đăng ký ký túc xá"),
                        limit=10)
    for point in res.points:
        print(point.payload)

