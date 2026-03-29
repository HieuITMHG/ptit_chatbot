from abc import ABC, abstractmethod
from typing import List
import tiktoken

class BaseChunker(ABC):
    def __init__(self, 
                 tokenizer: str,
                 chunk_size: int = 500,
                 chunk_overlap: int = 50,
                 ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.encoding_for_model(tokenizer)
        self.length_function = lambda text: len(self.tokenizer.encode(text))
        
    
    @abstractmethod
    def split_text(self, text: str) -> List[str]:
        pass

    def get_stats(self, chunks: List[str]):
        pass