"""POST /search — semantic search over chunks or cards."""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.dependencies import get_embed_service, get_qdrant_service
from app.services.embed_service import EmbedService
from app.services.qdrant_service import QdrantService

router = APIRouter(prefix="/search", tags=["search"])


class SearchResult(BaseModel):
    score: float
    id: int
    payload: dict[str, Any]


@router.post("", response_model=list[SearchResult])
def search(
    q: str = Query(..., description="Search query"),
    collection: str = Query("cards", description="'cards' or 'chunks'"),
    top_k: int = Query(10, ge=1, le=50),
    book_title: Optional[str] = Query(None),
    card_type: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    doc_id: Optional[str] = Query(None),
    embed_svc: EmbedService = Depends(get_embed_service),
    qdrant_svc: QdrantService = Depends(get_qdrant_service),
) -> list[SearchResult]:
    vector = embed_svc.embed_one(q)

    filters: dict[str, Any] = {}
    if book_title:
        filters["book_title"] = book_title
    if card_type:
        filters["card_type"] = card_type
    if tag:
        filters["tags"] = [tag]
    if doc_id:
        filters["doc_id"] = doc_id

    hits = qdrant_svc.search(
        collection=collection,
        query_vector=vector,
        top_k=top_k,
        filters=filters or None,
    )
    return [
        SearchResult(score=h.score, id=h.id, payload=h.payload or {})
        for h in hits
    ]
