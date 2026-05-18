from core.database import db
from FlagEmbedding import BGEM3FlagModel
from rag.pipelines.naive_rag import NaiveRag
from rag.pipelines.rerank_rag import RerankRag
from core.config_loader import PipelineConfig
from pathlib import Path

OUTPUT_PATH = Path(r"rag\evaluation\ds_gen\output_v2.txt")

queries_collection = db["hybrid_queries"]

rag_config = PipelineConfig("rag/configs/naive_rag.yaml")

embedding_model = BGEM3FlagModel(rag_config.embedding["model"])

rag_engine = NaiveRag(embedding_model=embedding_model, collection_name=rag_config.embedding["vector_col_name"])
# rerank_engine = RerankRag(embedding_model=embedding_model, collection_name=rag_config.embedding["vector_col_name"])

sample_query = "Thành phần tổ giáo viên của trường thông tin vô tuyến điện Lý Tự Trọng ban đầu gồm có những ai?"

results = rag_engine.retrieve(query=sample_query, top_k=5)

for result in results:
    print(result["id"])
    print("==========================")

# query_lst = list(queries_collection.find({}))

# with open(OUTPUT_PATH, "a", encoding="utf-8") as f:

#     for idx, query in enumerate(query_lst, start=1):
        

#         query_text = query["query_content"]

#         results = rag_engine.retrieve(query_text, top_k=20)

#         # Header query
#         f.write("\n")
#         f.write("=" * 100 + "\n")
#         f.write(f"QUERY với id là {query["id"]}\n")
#         f.write("=" * 100 + "\n")
#         f.write(f"{query_text}\n\n")

#         # Retrieved chunks
#         for rank, chunk in enumerate(results, start=1):

#             f.write("-" * 80 + "\n")
#             f.write(f"TOP {rank}\n")
#             f.write("-" * 80 + "\n")

#             f.write(f"ID: {chunk['id']}\n")
#             f.write(f"Title: {chunk['title']}\n")
#             f.write(f"Token Count: {chunk['token_count']}\n")

#             f.write("CONTENT:\n")
#             f.write(chunk["chunk_content"])
#             f.write("\n\n")

#         f.write("\n\n")

#         print(idx)

