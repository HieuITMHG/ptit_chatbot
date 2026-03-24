# from app.worker import celery_app 
# from core.config_loader import PipelineConfig
# from pipelines.rerank_rag import RerankRag, get_answer
# from FlagEmbedding import BGEM3FlagModel

# config = PipelineConfig("configs/rerank_rag.yaml")
# embedder = BGEM3FlagModel(config.embedding["model"])
# rag_engine = RerankRag(
#     embedding_model=embedder,
#     collection_name=config.embedding["vector_col_name"]
# )

# @celery_app.task(name="chat_rag_task") 
# def chat_rag_task(prompt: str):
#     try:
#         print("start")
#         result = get_answer(
#             rag_engine=rag_engine,
#             prompt=prompt,
#             top_k=5
#         )
#         print("end")
#     except Exception as e:
#         print(e)
#     return result