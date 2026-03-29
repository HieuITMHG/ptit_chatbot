from pydantic import BaseModel

class ChatRequest(BaseModel):
    request_content: str
