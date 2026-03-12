# from core.database import db
# from core.config_loader import PipelineConfig
# from data_ingestion.chunking.chunker_factory import build_chunker

# from model.chunk import Chunk
# from data_ingestion.chunking.helpers import length_function
# from repositories.chunk_repository import save_chunk

# documents_collection = db["documents"]
# chunks_collection = db["chunks"]

# def chunking_pipeline(config):
#     chunker = build_chunker(config.chunking)
#     docs = documents_collection.find({})

#     for doc in docs:
#         chunks = chunker.split_text(doc["content"])

#         for idx, c in enumerate(chunks):
#             print(idx)
#             print(doc["source_url"])
#             _,  count = length_function(c)
#             chunk = Chunk(document_url=doc["source_url"],
#                           chunk_index=idx,
#                           token_count=count,
#                           title=doc["title"],
#                           chunk_content=c,
#                           author=doc["author"],
#                           published_date=doc["published_date"])
            
#             save_chunk(chunk=chunk)

# def embedding_pipeline(config):
#     pass


# if __name__ == "__main__":
#     config = PipelineConfig("configs/naive_rag.yaml")
#     base_config = PipelineConfig("configs/base.yaml")
#     chunking_pipeline(config=config)