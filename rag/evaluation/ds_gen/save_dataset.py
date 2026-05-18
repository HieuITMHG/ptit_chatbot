from core.database import db
import json
from rag.model.qrel import Qrel

qrels_collection = db["qrels_v2"]

sample_url = "rag/evaluation/ds_gen/manual_dataset_v2.json"

if __name__ == "__main__":

    with open(sample_url, "r", encoding="utf-8") as f:
        query_lst = json.load(f)

    qrel_lst = []

    batch_size = 50

    for query in query_lst:
        query_id = int(query["query_id"])

        for rel in query["relevant_chunks"]:
            new_qrel = Qrel(
                chunk_id=rel,
                query_id=query_id
            )

            qrel_lst.append(new_qrel)

            if len(qrel_lst) >= batch_size:
                qrels_collection.insert_many(
                    [qrel.model_dump() for qrel in qrel_lst]
                )
                qrel_lst = []
            
            print(f"Đã lưu query {query}")

    if qrel_lst:
        qrels_collection.insert_many(
            [qrel.model_dump() for qrel in qrel_lst]
        )