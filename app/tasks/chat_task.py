from app.worker import celery
from core.redis_client import sync_redis_client
import time
from rag.pipelines.rerank_rag import get_answer as get_rag_answer
from rag.pipelines.rerank_rag import RerankRag
from core.config_loader import PipelineConfig
from FlagEmbedding import BGEM3FlagModel

config = PipelineConfig("rag/configs/rerank_rag.yaml")
embedder = BGEM3FlagModel(config.embedding["model"])

rag_engine = RerankRag(
    embedding_model=embedder,
    collection_name=config.embedding["vector_col_name"]
)

@celery.task(name="get_answer")
def get_answer(task_id: str, prompt: str, username: str): 
    print("Lấy câu trả lời")
    answer = get_rag_answer(rag_engine=rag_engine, prompt=prompt, top_k=5)
    print("Có câu trả lời rồi")
    sync_redis_client.publish(task_id, answer) 
    print("đã public")
    
    return answer