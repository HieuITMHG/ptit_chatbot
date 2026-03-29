from rag.pipelines.rerank_rag import get_answer as get_rag_answer
from rag.pipelines.rerank_rag import RerankRag
from core.config_loader import PipelineConfig
from FlagEmbedding import BGEM3FlagModel
import time

config = PipelineConfig("rag/configs/rerank_rag.yaml")
embedder = BGEM3FlagModel(config.embedding["model"])

rag_engine = RerankRag(
    embedding_model=embedder,
    collection_name=config.embedding["vector_col_name"]
)

if __name__ == "__main__":
    start_time = time.perf_counter()
    res = get_rag_answer(rag_engine=rag_engine, prompt="chào ptit", top_k=5)
    end_time = time.perf_counter()

    print(f"Thời gian hoàn thành là: {end_time - start_time}")

