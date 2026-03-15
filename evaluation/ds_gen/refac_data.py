from core.database import db
import json
import hashlib

semantic_chunks_collection = db["semantic_chunks"]

json_lst = [
    "evaluation/eval_pipeline/cluster_0.json",
    "evaluation/eval_pipeline/cluster_1.json",
    "evaluation/eval_pipeline/cluster_2.json"
]

def make_point_id(url, chunk_index):
    raw = f"{url}_{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()

if __name__ == "__main__":
    for file in json_lst:
        with open(file, "r", encoding="utf-8") as f:
            chunks_lst = json.load(f)

        for chunk in chunks_lst:
            id = make_point_id(url=chunk["document_url"], chunk_index=chunk["chunk_index"])
            chunk["id"] = id 

            semantic_chunks_collection.update_one(
                {
                    "document_url": chunk["document_url"],
                    "chunk_index": chunk["chunk_index"]
                },
                {
                    "$set": {
                        "id": id
                    }
                }
            )
        
        with open(file, "w", encoding="utf-8") as f:
            json.dump(chunks_lst, f, ensure_ascii=False, indent=4)
            
        print(f" Đã cập nhật MongoDB và ghi đè thành công file: {file}")

    print("Hoàn tất xử lý tất cả các file!")