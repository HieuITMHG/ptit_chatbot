from rag.model.chunk import Chunk

from core.database import db

chunks_collection = db["chunks"]

def save_chunk(chunk: Chunk):
    try:
        chunks_collection.insert_one(chunk.model_dump())
        print("Lưu chunk thành công")
    except Exception as e:
        print(f"Lỗi khi lưu chunk: {e}")

def find_one_chunk(url):
    try: 
        chunk = chunks_collection.find_one({"url": url})
    except Exception as e:
        print(f"Lỗi khi truy suất chunk để kiểm tra tồn tại: {e}")

    return chunk

