from pipelines.naive_rag_pipeline import NaiveRag
from pipelines.rerank_rag_pipeline import RerankRag
from pipelines.hybrid_rag import HybirdRag
from core.config_loader import PipelineConfig
from core.database import db
from .retrieval_metrics import RetrievalMetric
from .generation_metrics import GenerationMetric

hybrid_queries_collection = db["hybrid_queries"]

if __name__ == "__main__":
  
    base_config = PipelineConfig("configs/base.yaml")
    hybrid_config = PipelineConfig("configs/hybrid_rag.yaml")
    rerank_engine = RerankRag(embedding_model=base_config.embedding["model"],
                          collection_name=base_config.embedding["col_name"])
    
    hybrid_engine = HybirdRag(embedding_model=hybrid_config.embedding["model"],
                              collection_name=hybrid_config.embedding["col_name"])
    
    metric = RetrievalMetric(rag_engine=hybrid_engine,
                             data_config=base_config.chunking,
                             top_k=5)
    result = metric.evaluate()
    print(result)

    # gmetric = GenerationMetric(rag_engine=rag_engine,
    #                            data_config=config.chunking,
    #                            top_k=5)
    
    # gmetric.evaluate()
    
