from pydantic import BaseModel

class RetrievalResult(BaseModel):
    top_k: int
    precision: float
    recall: float
    hit: float
    ndcg: float
    mrr: float
