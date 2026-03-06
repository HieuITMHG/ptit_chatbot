import yaml
from pipelines.factory import build_retriever, build_reranker


def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)


cfg = load_config("configs/naive_rag.yaml")

retriever = build_retriever(cfg["retriever"])
reranker = build_reranker(cfg["reranker"])

query = "Học phí PTIT bao nhiêu?"

docs = retriever.search(query)

docs = reranker.rerank(query, docs)

print(docs)