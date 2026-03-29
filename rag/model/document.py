from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Document(BaseModel):
    source_url: str
    title: Optional[str] = "N/A"
    content: str
    parent_id: str
    author: Optional[str] = "Unknown"
    published_date: Optional[datetime] = None
        
