from core.database import db
import json
from model.query import Query
from model.qrel import Qrel

hybrid_queries_collection = db["hybrid_queries"]
hybrid_qrels_collection = db["hybrid_qrels"]

sample_url = "evaluation/ds_gen/enrich_dataset.json"

if __name__ == "__main__":

    with open(sample_url, "r", encoding="utf-8") as f:
        query_lst = json.load(f)

    for query in query_lst:
        qrel_lst = []
        que = Query(id=query["query_id"],
                    query_content=query["query"])
        
        for rel in query["relevant_chunks"]:
            qrel = Qrel(chunk_id=rel["chunk_id"],
                        query_id=que.id,
                        relevance_score=rel["relevance_score"],
                        reasoning=rel["reasoning"])
            qrel_lst.append(qrel.model_dump())
            
        try:
            hybrid_queries_collection.insert_one(que.model_dump())
            hybrid_qrels_collection.insert_many(qrel_lst)
            print(f"Đã lưu thông tin query {que.id}")
        except Exception as e:
            print(f"Lỗi khi lưu query {que.id}: {e}")
