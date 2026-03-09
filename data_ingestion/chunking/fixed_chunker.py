from typing import List

from .base_chunker import BaseChunker
from core.database import db

class FixedSizeChunker(BaseChunker):
    def split_text(self, text: str) -> List[str]:
        chunks = []
        encoded, content_len = self.length_function(text=text)
        
        if content_len <= self.chunk_size:
            return [text]
        
        start = 0

        while start < content_len:
            end = start + self.chunk_size
            
            remain_len = content_len - end

            if 0 < remain_len < (self.chunk_size / 5 ):
                end = content_len

            chunk_ids = encoded[start:end]

            decoded_chunk = self.encoding.decode(chunk_ids)

            chunks.append(decoded_chunk)

            if end >= content_len:
                break

            start = start + self.chunk_size - self.chunk_overlap

        return chunks
