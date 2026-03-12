from pydantic import BaseModel

class QuoteQuery(BaseModel):
    quote_id: int 
    query_id: int