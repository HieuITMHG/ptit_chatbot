from pydantic import BaseModel
from typing import List

class ChatResponse(BaseModel):
    response_content: str
    sources: List[str]
    metadata: dict