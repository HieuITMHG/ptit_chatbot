from pipelines.naive_rag_pipeline import NaiveRag
from core.config_loader import PipelineConfig
from core.database import db
from .retrieval_metrics import RetrievalMetric
from .generation_metrics import GenerationMetric

hybrid_queries_collection = db["hybrid_queries"]

if __name__ == "__main__":
  
    config = PipelineConfig("configs/base.yaml")
    rag_engine = NaiveRag(embedding_model=config.embedding["model"],
                          collection_name=config.embedding["col_name"])
    
    # metric = RetrievalMetric(rag_engine=rag_engine,
    #                          data_config=config.chunking,
    #                          top_k=5)
    # result = metric.evaluate()
    # print(result)

    gmetric = GenerationMetric(rag_engine=rag_engine,
                               data_config=config.chunking,
                               top_k=5)
    
    gmetric.evaluate()
    
