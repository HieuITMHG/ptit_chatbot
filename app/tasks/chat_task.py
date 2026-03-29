from app.worker import celery
from core.redis_client import sync_redis_client
from rag.pipelines.rerank_rag import get_answer as get_rag_answer
from rag.pipelines.rerank_rag import RerankRag
from core.config_loader import PipelineConfig
from FlagEmbedding import BGEM3FlagModel
from celery.signals import worker_process_init
import json

rag_engine = None 

@worker_process_init.connect
def init_worker_models(**kwargs):
    global rag_engine 
    print("Worker đang khởi tạo mô hình AI...")
    config = PipelineConfig("rag/configs/rerank_rag.yaml")
    embedder = BGEM3FlagModel(config.embedding["model"])
    
    rag_engine = RerankRag(
        embedding_model=embedder,
        collection_name=config.embedding["vector_col_name"]
    )
    print("Khởi tạo mô hình thành công cho worker!")

@celery.task(name="get_answer")
def get_answer(task_id: str, prompt: str, username: str): 
    global rag_engine 
    
    print("Lấy câu trả lời")
    answer = get_rag_answer(rag_engine=rag_engine, prompt=prompt, top_k=5) 
    print("Có câu trả lời rồi")
    answer_json = json.dumps(answer, ensure_ascii=False)
    print("đã public")
    sync_redis_client.publish(task_id, answer_json)
    return answer