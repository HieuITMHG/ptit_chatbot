from app.worker import celery_app 
from core.config_loader import PipelineConfig
from pipelines.rerank_rag import RerankRag, get_answer

config = PipelineConfig("configs/rerank_rag.yaml")
rag_engine = RerankRag(
    embedding_model=config.embedding["model"],
    collection_name=config.embedding["vector_col_name"]
)

@celery_app.task(name="chat_rag_task") 
def chat_rag_task(prompt: str):
    result = get_answer(
        rag_engine=rag_engine,
        prompt=prompt,
        top_k=5
    )
    return result