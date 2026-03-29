from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Chunk(BaseModel):
    id: str
    document_url: str
    chunk_index: int
    token_count: int
    title: Optional[str] = "N/A"
    chunk_content: str
    author: Optional[str] = "Unknown"
    published_date: Optional[datetime] = None
        