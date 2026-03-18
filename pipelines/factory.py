from enums.rag_type import RagType
from pipelines.hybrid_rag import HybirdRag
from pipelines.naive_rag import NaiveRag
from pipelines.rerank_rag import RerankRag

def build_rag(type, config):
    if type == RagType.HYBRID.value:
        return HybirdRag(embedding_model=config.embedding["model"],
                         collection_name=config.embedding["col_name"])
    elif type == RagType.NAIVE.value:
        return NaiveRag(embedding_model=config.embedding["model"],
                        collection_name=config.embedding["col_name"])
    elif type == RagType.RERANK.value:
        return RerankRag(embedding_model=config.embedding["model"],
                        collection_name=config.embedding["col_name"])
