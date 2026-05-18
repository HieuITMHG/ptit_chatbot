from pymongo import UpdateOne
from core.database import db
from rag.pipelines.bm25 import preprocess

semantic_chunks_collection = db["semantic_chunks_v2"]
hybrid_chunks_collection = db["hybrid_chunks_v2"]

BATCH_SIZE = 1000

last_object_id = None
total = 0

while True:
    query = {}

    if last_object_id:
        query["_id"] = {"$gt": last_object_id}

    docs = list(
        semantic_chunks_collection
        .find(query)
        .sort("_id", 1)
        .limit(BATCH_SIZE)
    )

    if not docs:
        break

    operations = []

    for doc in docs:
        content = doc.get("chunk_content", "")

        hybrid_doc = {
            "id": doc.get("id"), 
            "document_url": doc.get("document_url"),
            "chunk_index": doc.get("chunk_index"),
            "token_count": doc.get("token_count"),
            "title": doc.get("title"),
            "chunk_content": content,
            "processed_content": preprocess(content),
            "author": doc.get("author"),
            "published_date": doc.get("published_date"),
        }

        operations.append(
            UpdateOne(
                {"id": hybrid_doc["id"]},
                {"$set": hybrid_doc},
                upsert=True
            )
        )

    if operations:
        hybrid_chunks_collection.bulk_write(
            operations,
            ordered=False
        )

    total += len(docs)
    last_object_id = docs[-1]["_id"]

    print(f"Processed: {total}")

print("Done")