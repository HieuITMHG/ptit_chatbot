import pickle
import numpy as np
from .bm25 import BM25, preprocess
import __main__

BM25_INDEX_PATH = "rag/pipelines/bm25_index.pkl"

__main__.BM25 = BM25

with open(BM25_INDEX_PATH, "rb") as f:
        data = pickle.load(f)

bm25 = data["bm25"]
raw_docs = data["raw_docs"]

def search(query, bm25, raw_docs, limit: int = 20):

    query_tokens = preprocess(query).split()

    scores = bm25.search(query_tokens)

    top_indices = np.argsort(scores)[::-1][:limit]

    results = []

    for idx in top_indices:

        doc = raw_docs[idx]

        results.append({
            "id": str(doc["id"]),
            "doc_url": doc.get("document_url"),
            "chunk_index": doc.get("chunk_index"),
            "token_count": doc.get("token_count"),
            "title": doc.get("title"),
            "chunk_content": doc.get("chunk_content"),
            "author": doc.get("author"),
            "published_date": doc.get("publised_date"),
            "score": scores[idx],   
        })

    return results

results = search("Lễ kỷ niệm 38 năm Ngày Nhà giáo Việt Nam tại cơ sở TPHCM diễn ra vào thời điểm nào?", bm25=bm25, raw_docs=raw_docs, limit=20)

for result in results:
    print(result["id"])

