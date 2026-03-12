from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1] 

class Settings(BaseSettings):
    root_csv:str
    sitemap_index_url:str
    bucket_name:str
    mongodb_url:str
    database_name:str
    openai_key:str
    class Config:
        env_file = ".env"
    
    @property
    def root_csv_path(self) -> Path:
        path = Path(self.root_csv)
        if not path.is_absolute():
            path = BASE_DIR / path
        return path.resolve()

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()