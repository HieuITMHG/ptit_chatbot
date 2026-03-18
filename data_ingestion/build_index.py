from core.database import db, client
from data_ingestion.chunking.chunker_factory import build_chunker
from model.chunk import Chunk
from core.qdrant import client
from qdrant_client.models import VectorParams, Distance, Filter, FieldCondition, MatchValue
import hashlib

def make_point_id(url, chunk_index):
    raw = f"{url}_{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()

documents_collection = db["documents"]

BATCH_SIZE = 64

class IndexBuilder():
    def __int__(self, config, embedder):
        self.qdrant_collection_name = config.embedding["vector_col_name"]
        self.chunks_collection = db[config.chunking["chunk_col_name"]]
        self.embedder = embedder

    def save_chunks(self, chunks, doc):
        chunk_lst = []
        for idx, chunk in enumerate(chunks):
            ch = Chunk(id=make_point_id(url=doc["source_url"], 
                        chunk_index=idx),
                        document_url=doc["source_url"],
                        chunk_index=idx,
                        token_count=chunk["token_count"],
                        title=doc["title"],
                        chunk_content=chunk["text"],
                        author=doc["author"],
                        published_date=doc["published_date"])
            chunk_lst.append(ch.model_dump())
            
        try:
            self.chunks_collection.insert_many(chunk_lst)
            print(f"Đã lưu lưu của {doc["source_url"]}")
        except Exception as e:
            print(f"Lỗi khi insert các chunk của doc {doc["source_url"]}: {e}")

        return chunk_lst

    def chunking_pipeline(self, url_lst):
        chunker = build_chunker(config=self.config.chunking, embedder=self.embedder)

        if url_lst:
            for url in url_lst:
                exist_chunks = list(self.chunks_collection.find({"document_url": url}))

                if len(exist_chunks) != 0:
                    self.chunks_collection.delete_many({"document_url": url})
                        
                    client.delete(
                        collection_name=self.qdrant_collection_name,
                        points_selector=Filter(
                            must=[
                                FieldCondition(
                                    key="document_url",
                                    match=MatchValue(value=url)
                                )
                            ]
                        )
                    )

                doc = documents_collection.find_one({"source_url": url})
                new_chunks = chunker.split_text(text=doc["content"], title=doc["title"])
                return self.save_chunks(chunks=new_chunks, doc = doc)
        else:
            docs = documents_collection.find({})
            for doc in docs:
                exists = self.chunks_collection.find_one({"document_url": doc["source_url"]})

                if exists:
                    continue
                else:
                    new_chunks = chunker.split_text(text=doc["content"], title=doc["title"])
                    return self.save_chunks(chunks=new_chunks, doc = doc)
    

    def embed_chunks(self, chunks):
        batch = []
        for chunk in chunks:
            print(chunk["document_url"])
            batch.append(chunk)

            if len(batch) == BATCH_SIZE:
                texts = [c["chunk_content"] for c in batch]

                vectors = self.embedder.encode(texts)

                points = []

                for i, vec in enumerate(vectors):
                    points.append({
                        "id": batch[i]["id"],
                        "vector": vec,
                        "payload": batch[i]
                    })
                    
                client.upsert(
                    collection_name=self.qdrant_collection_name,
                    points=points
                )

                batch = []
        if batch:
            texts = [c["chunk_content"] for c in batch]
            vectors = self.embedder.encode(texts)

            points = []
            for i, vec in enumerate(vectors):
                points.append({
                    "id": batch[i]["id"],
                    "vector": vec,
                    "payload": batch[i]
                })

            client.upsert(
                collection_name=self.qdrant_collection_name,
                points=points
            )

    def embedding_pipeline(self, chunk_lst):
        if client.collection_exists(collection_name=self.qdrant_collection_name):
            print("Collection đã tồn tại")
        else:
            client.create_collection(collection_name=self.qdrant_collection_name,
                                    vectors_config=VectorParams(size=self.embedder.get_sentence_embedding_dimension(),
                                                                distance=Distance.COSINE))
            print(f"Đã tạo collection {self.qdrant_collection_name}")
        
        if chunk_lst:
            self.embed_chunks(chunks=chunk_lst)
        else:
            chunks = self.chunks_collection.find({}, {"_id": 0}).batch_size(512)
            self.embed_chunks(chunks=chunks)
        