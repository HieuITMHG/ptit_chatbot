from qdrant_client import QdrantClient
from .config import settings

client = QdrantClient(url=settings.qdrant_endpoint,
                      api_key=settings.qdrant_key)


