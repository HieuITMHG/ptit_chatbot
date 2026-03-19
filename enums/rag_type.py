from enum import Enum

class RagType(Enum):
    NAIVE = "naive"
    HYBRID = "hybrid"
    HYBRIDV2 = "hybridv2"
    RERANK = "rerank"