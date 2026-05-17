from core.database import db
import json
from rag.model.qrel import Qrel

queries_collection = db["hybrid_queries"]
qrels_collection = db["hybrid_qrels"]

sample_url = "rag/evaluation/ds_gen/cleaned_dataset.json"

if __name__ == "__main__":

    with open(sample_url, "r", encoding="utf-8") as f:
        query_lst = json.load(f)

    qrel_lst = []

    batch_size = 50

    for query in query_lst:
        query_id = query["query_id"]

        for rel in query["relevant_chunks"]:
            for key, val in rel.items():

                new_qrel = Qrel(
                    chunk_id=key,
                    query_id=query_id
                )

                qrel_lst.append(new_qrel)

                if len(qrel_lst) >= batch_size:
                    qrels_collection.insert_many(
                        [qrel.model_dump() for qrel in qrel_lst]
                    )
                    qrel_lst = []

    if qrel_lst:
        qrels_collection.insert_many(
            [qrel.model_dump() for qrel in qrel_lst]
        )