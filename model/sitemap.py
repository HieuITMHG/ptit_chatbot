from pydantic import BaseModel
from datetime import datetime

class Sitemap(BaseModel):
    url: str
    last_mod: datetime
