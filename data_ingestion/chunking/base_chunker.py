from abc import ABC, abstractmethod
from typing import List, Any

class BaseChunker(ABC):
    def __init__(self, 
                 encoding: Any,
                 chunk_size: int = 500,
                 chunk_overlap: int = 50,
                 length_function: Any = len,
                 ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function
        self.encoding = encoding
    
    @abstractmethod
    def split_text(self, text: str) -> List[str]:
        pass

    def get_stats(self, chunks: List[str]):
        pass