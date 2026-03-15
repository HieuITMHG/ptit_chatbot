from core.database import db

qrels_collection = db["qrels"]

def precision_recall(query_id: int, results: list, top_k: int) -> float:
    rels = list(qrels_collection.find({"query_id": query_id}, {"_id": 0}))
    total_rel = len(list(rels))

    if total_rel == 0 or top_k == 0:
        return 0.0

    result_ids = [r["id"] for r in results[0: top_k]]
    rel_ids = [rel["chunk_id"] for rel in rels]

    intersection = len(set(result_ids) & set(rel_ids))

    return intersection / top_k , intersection / total_rel
