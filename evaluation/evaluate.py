from enums.rag_type import RagType
from pipelines.hybrid_rag import HybirdRag
from pipelines.naive_rag import NaiveRag
from pipelines.rerank_rag import RerankRag
from pipelines.bge_hybrid_rag import BGEHybirdRag
from core.config_loader import PipelineConfig
from evaluation.eval_pipeline.generation_metrics import GenerationMetric
from evaluation.eval_pipeline.retrieval_metrics import RetrievalMetric

def run(rag, generation, retrieval, topk):
    if rag == RagType.HYBRID.value:
        config = PipelineConfig("configs/hybrid_rag.yaml")
        rag_engine = HybirdRag(embedding_model=config.embedding["model"],
                         collection_name=config.embedding["vector_col_name"])
    elif rag == RagType.NAIVE.value:
        config = PipelineConfig("configs/naive_rag.yaml")
        rag_engine = NaiveRag(embedding_model=config.embedding["model"],
                        collection_name=config.embedding["vector_col_name"])
    elif rag == RagType.RERANK.value:
        config = PipelineConfig("configs/rerank_rag.yaml")
        rag_engine = RerankRag(embedding_model=config.embedding["model"],
                        collection_name=config.embedding["vector_col_name"])
    elif rag == RagType.HYBRIDV2.value:
        config = PipelineConfig("configs/rerank_rag.yaml")
        rag_engine = BGEHybirdRag(embedding_model=config.embedding["model"],
                        collection_name=config.embedding["vector_col_name"])
    
    if retrieval:
        metric = RetrievalMetric(rag_engine=rag_engine, data_config=config.evaluation, top_k=topk)
        metric.evaluate()

    if generation:
        metric = GenerationMetric(rag_engine=rag_engine, data_config=config.evaluation, top_k=topk)
        metric.evaluate()

    