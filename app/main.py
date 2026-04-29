from fastapi import FastAPI
from fastapi.routing import APIRoute
from core.config import settings
from starlette.middleware.cors import CORSMiddleware
from app.repositories.user_repo import create_user_if_not_exists
from app.services.auth_service import password_hash
from contextlib import asynccontextmanager

from .api.main import api_router

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    username = settings.test_username
    password = settings.test_password

    hashed = password_hash.hash(password)
    create_user_if_not_exists(username, hashed)

    print(f"Test user ready: {username}")

    yield

app = FastAPI(
    title=settings.compose_project_name,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan
)

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.all_cors_origins], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)
