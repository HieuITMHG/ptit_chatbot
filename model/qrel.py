from pydantic import BaseModel

class Qrel(BaseModel):
    chunk_id: str
    query_id: int
    relevance_score: float
    reasoning: str