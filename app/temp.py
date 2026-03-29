from fastapi import FastAPI
from fastapi.routing import APIRoute
from core.config import settings

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

