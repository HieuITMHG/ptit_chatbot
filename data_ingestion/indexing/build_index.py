from core.config_loader import PipelineConfig
from core.database import db
from data_ingestion.chunking.chunker_factory import build_chunker
from model.chunk import Chunk
from core.qdrant import client
from qdrant_client.models import VectorParams, Distance
from data_ingestion.chunking.helpers import embedder
import hashlib

def make_point_id(url, chunk_index):
    raw = f"{url}_{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()

documents_collection = db["documents"]
semantic_chunks_collection = db["semantic_chunks"]

BATCH_SIZE = 64

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

def embedding_pipeline(config):
    if client.collection_exists(collection_name=config["col_name"]):
        print("Collection đã tồn tại")
    else:
        client.create_collection(collection_name=config["col_name"],
                                 vectors_config=VectorParams(size=embedder.get_sentence_embedding_dimension(),
                                                             distance=Distance.COSINE))
        print(f"Đã tạo collection {config["col_name"]}")

    chunks = semantic_chunks_collection.find({}, {"_id": 0}).batch_size(512)
    batch = []
    for chunk in chunks:
        print(chunk["document_url"])
        batch.append(chunk)

        if len(batch) == BATCH_SIZE:
            texts = [c["chunk_content"] for c in batch]

            vectors = embedder.encode(texts)

            points = []

            for i, vec in enumerate(vectors):
                points.append({
                    "id": make_point_id(batch[i]["document_url"], batch[i]["chunk_index"]),
                    "vector": vec,
                    "payload": batch[i]
                })
                
            client.upsert(
                collection_name=config["col_name"],
                points=points
            )

            batch = []
    if batch:
        texts = [c["chunk_content"] for c in batch]
        vectors = embedder.encode(texts)

        points = []
        for i, vec in enumerate(vectors):
            points.append({
                "id": make_point_id(batch[i]["document_url"], batch[i]["chunk_index"]),
                "vector": vec,
                "payload": batch[i]
            })

        client.upsert(
            collection_name=config["col_name"],
            points=points
        )

if __name__ == "__main__":
    config = PipelineConfig("configs/base.yaml")
    # chunking_pipeline(config.chunking)
    embedding_pipeline(config.embedding)

