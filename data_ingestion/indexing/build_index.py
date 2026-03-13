from core.config_loader import PipelineConfig
from core.database import db
from data_ingestion.chunking.chunker_factory import build_chunker
from model.chunk import Chunk

documents_collection = db["documents"]
semantic_chunks_collection = db["semantic_chunks"]


def chunking_pipeline(config):
    chunker = build_chunker(config=config)

    docs = documents_collection.find({})

    for doc in docs:
        chunks = chunker.split_text(doc["content"])
        chunk_lst = []
        for idx, chunk in enumerate(chunks):
            ch = Chunk(document_url=doc["source_url"],
                       chunk_index=idx,
                       token_count=chunk["token_count"],
                       title=doc["title"],
                       chunk_content=chunk["text"],
                       author=doc["author"],
                       published_date=doc["published_date"])
            chunk_lst.append(ch.model_dump())
            
        try:
            semantic_chunks_collection.insert_many(chunk_lst)
            print(f"Đã lưu lưu của {doc["source_url"]}")
        except Exception as e:
            print(f"Lỗi khi insert các chunk của doc {doc["source_url"]}: {e}")

if __name__ == "__main__":
    config = PipelineConfig("configs/base.yaml")
    chunking_pipeline(config.chunking)

