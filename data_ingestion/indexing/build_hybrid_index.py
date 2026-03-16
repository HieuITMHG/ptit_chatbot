from core.config_loader import PipelineConfig
from core.database import db
from core.qdrant import client
from qdrant_client.models import VectorParams, Distance
from data_ingestion.chunking.helpers import embedder
import hashlib
from pipelines.bm25 import preprocess

def make_point_id(url, chunk_index):
    raw = f"{url}_{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()

documents_collection = db["documents"]
enrich_hybrids_collection = db["enrich_hybrids"]

BATCH_SIZE = 64

def embedding_pipeline(config):
    if client.collection_exists(collection_name=config["col_name"]):
        print("Collection đã tồn tại")
    else:
        client.create_collection(collection_name=config["col_name"],
                                 vectors_config=VectorParams(size=embedder.get_sentence_embedding_dimension(),
                                                             distance=Distance.COSINE))
        print(f"Đã tạo collection {config["col_name"]}")

    chunks = enrich_hybrids_collection.find({}, {"_id": 0}).batch_size(512)
    batch = []
    for chunk in chunks:
        print(chunk["document_url"])
        batch.append(chunk)

        if len(batch) == BATCH_SIZE:
            texts = [preprocess(c["chunk_content"]) for c in batch]

            vectors = embedder.encode(texts)

            points = []

            for i, vec in enumerate(vectors):
                points.append({
                    "id": batch[i]["id"],
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
                "id": batch[i]["id"],
                "vector": vec,
                "payload": batch[i]
            })

        client.upsert(
            collection_name=config["col_name"],
            points=points
        )

if __name__ == "__main__":
    config = PipelineConfig("configs/hybrid_rag.yaml")
    embedding_pipeline(config.embedding)

