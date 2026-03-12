from pydantic import BaseModel, Field

class Query(BaseModel):
    id: int
    query_content: str
