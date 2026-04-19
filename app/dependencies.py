"""Shared FastAPI dependencies — singleton services."""
from functools import lru_cache
from app.services.embed_service import EmbedService
from app.services.qdrant_service import QdrantService


@lru_cache(maxsize=1)
def get_embed_service() -> EmbedService:
    return EmbedService()


@lru_cache(maxsize=1)
def get_qdrant_service() -> QdrantService:
    return QdrantService()
