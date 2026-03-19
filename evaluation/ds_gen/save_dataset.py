from core.database import db
import json
from model.query import Query
from model.qrel import Qrel

queries_collection = db["hybrid_queries"]
qrels_collection = db["hybrid_qrels"]

sample_url = "evaluation/ds_gen/hybrid_dataset.json"

if __name__ == "__main__":

    with open(sample_url, "r", encoding="utf-8") as f:
        query_lst = json.load(f)

    for query in query_lst:
        qrel_lst = []
        que = Query(id=query["query_id"],
                    query_content=query["query"])
        
        for rel in query["relevant_chunks"]:
            qrel = Qrel(chunk_id=rel,
                        query_id=que.id)
            qrel_lst.append(qrel.model_dump())
            
        try:
            queries_collection.insert_one(que.model_dump())
            qrels_collection.insert_many(qrel_lst)
            print(f"Đã lưu thông tin query {que.id}")
        except Exception as e:
            print(f"Lỗi khi lưu query {que.id}: {e}")
