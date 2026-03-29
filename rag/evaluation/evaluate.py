from rag.enums.rag_type import RagType
from rag.pipelines.hybrid_rag import HybirdRag
from rag.pipelines.naive_rag import NaiveRag
from rag.pipelines.rerank_rag import RerankRag
from rag.pipelines.bge_hybrid_rag import BGEHybirdRag
from core.config_loader import PipelineConfig
from .eval_pipeline.generation_metrics import GenerationMetric
from .eval_pipeline.retrieval_metrics import RetrievalMetric
from FlagEmbedding import BGEM3FlagModel

def run(rag, generation, retrieval, topk):
    if rag == RagType.HYBRID.value:
        config = PipelineConfig("rag/configs/hybrid_rag.yaml")
        embedder = BGEM3FlagModel(config.embedding["model"])
        rag_engine = HybirdRag(embedding_model=config.embedding["model"],
                         collection_name=config.embedding["vector_col_name"])
    elif rag == RagType.NAIVE.value:
        config = PipelineConfig("rag/configs/naive_rag.yaml")
        rag_engine = NaiveRag(embedding_model=config.embedding["model"],
                        collection_name=config.embedding["vector_col_name"])
    elif rag == RagType.RERANK.value:
        embedder = BGEM3FlagModel(config.embedding["model"])
        config = PipelineConfig("rag/configs/rerank_rag.yaml")
        rag_engine = RerankRag(embedding_model=embedder,
                        collection_name=config.embedding["vector_col_name"])
    elif rag == RagType.HYBRIDV2.value:
        config = PipelineConfig("rag/configs/rerank_rag.yaml")
        rag_engine = BGEHybirdRag(embedding_model=config.embedding["model"],
                        collection_name=config.embedding["vector_col_name"])
    
    if retrieval:
        metric = RetrievalMetric(rag_engine=rag_engine, data_config=config.evaluation, top_k=topk, rag_type=rag)
        metric.evaluate()

    if generation:
        metric = GenerationMetric(rag_engine=rag_engine, data_config=config.evaluation, top_k=topk)
        metric.evaluate()

    