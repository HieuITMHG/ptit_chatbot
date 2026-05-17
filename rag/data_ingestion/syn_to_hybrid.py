from core.database import db
from rag.pipelines.bm25 import preprocess

semantic_chunks_collection = db["semantic_chunks"]
hybrid_chunks_collection = db["hybrid_chunks"]

def refac_hybrid_chunks():
    """
    Lấy chunk_content từ semantic_chunks
    preprocess lại KHÔNG remove stopword
    rồi update vào hybrid_chunks theo field `id`
    """

    semantic_docs = semantic_chunks_collection.find(
        {},
        {
            "_id": 0,
            "id": 1,
            "chunk_content": 1
        }
    )

    updated_count = 0
    missing_count = 0

    for semantic_doc in semantic_docs:

        doc_id = semantic_doc.get("id")
        chunk_content = semantic_doc.get("chunk_content", "")

        if not doc_id or not chunk_content:
            continue

        new_content = preprocess(chunk_content)

        result = hybrid_chunks_collection.update_one(
            {"id": doc_id},
            {
                "$set": {
                    "chunk_content": new_content
                }
            }
        )

        if result.matched_count > 0:
            updated_count += 1
            print(updated_count)
        else:
            missing_count += 1
            print(missing_count)
            print(f"Không tìm thấy hybrid chunk với id: {doc_id}")

    print(f"Updated: {updated_count}")
    print(f"Missing: {missing_count}")


if __name__ == "__main__":
    refac_hybrid_chunks()
