from pydantic import BaseModel, Field

class Quote(BaseModel):
    id: int 
    quote_content: str
    doc_url: str
