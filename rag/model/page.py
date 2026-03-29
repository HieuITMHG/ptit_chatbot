from pydantic import BaseModel
from datetime import datetime

class Page(BaseModel):
    url: str
    sitemap_url: str
    last_mod: datetime
    is_parse: bool = False
