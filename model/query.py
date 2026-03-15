from pydantic import BaseModel

class Query(BaseModel):
    id: int
    query_content: str
