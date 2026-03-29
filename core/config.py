from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any
from pydantic import BeforeValidator, computed_field, AnyUrl

BASE_DIR = Path(__file__).resolve().parents[1] 

def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)

class Settings(BaseSettings):

    env: str
    compose_project_name: str
    API_V1_STR: str = "/api/v1"

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    
    sitemap_index_url:str
    openai_key:str

    bucket_name:str
    s3_enpoint: str
    aws_access_key_id :str
    aws_secret_access_key:str

    mongodb_uri:str
    database_name:str
    mongo_initdb_root_username: str
    mongo_initdb_root_password: str
    
    qdrant_key:str
    qdrant_endpoint:str

    redis_url:str
    celery_result_backend:str

    cookie_secure: bool
    cookie_samesite: str

    FRONTEND_HOST: str = "http://localhost:5173"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    class Config:
        env_file = ".env.dev"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
