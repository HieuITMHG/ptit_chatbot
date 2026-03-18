from enum import Enum

class RagType(Enum):
    NAIVE = "naive"
    HYBRID = "hybrid"
    RERANK = "rerank"