"""
Qdrant service — local persistence, no Docker required.
Collections: 'chunks' and 'cards'
"""
from __future__ import annotations

import os
from typing import Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    ScoredPoint,
    VectorParams,
)

QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_storage")
UPSERT_BATCH_SIZE = int(os.getenv("QDRANT_UPSERT_BATCH_SIZE", "100"))

COLLECTIONS = {
    "chunks": ["book_title", "doc_id", "chunk_type"],
    "cards": ["book_title", "doc_id", "card_type", "tags"],
}


class QdrantService:
    def __init__(self, path: str = QDRANT_PATH):
        self._path = path
        self._client: Optional[QdrantClient] = None

    @property
    def client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(path=self._path)
        return self._client

    def ensure_collection(self, collection: str, vector_size: int) -> None:
        existing = {c.name for c in self.client.get_collections().collections}
        if collection not in existing:
            self.client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            # Create payload indexes for filtered search
            for field in COLLECTIONS.get(collection, []):
                self.client.create_payload_index(
                    collection_name=collection,
                    field_name=field,
                    field_schema=PayloadSchemaType.KEYWORD,
                )

    def upsert(self, collection: str, points: list[PointStruct]) -> None:
        for i in range(0, len(points), UPSERT_BATCH_SIZE):
            batch = points[i : i + UPSERT_BATCH_SIZE]
            self.client.upsert(collection_name=collection, points=batch, wait=True)

    def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 10,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[ScoredPoint]:
        query_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                if isinstance(value, list):
                    conditions.append(
                        FieldCondition(key=key, match=MatchAny(any=value))
                    )
                else:
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
            query_filter = Filter(must=conditions)

        return self.client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )

    def collection_count(self, collection: str) -> int:
        try:
            return self.client.count(collection_name=collection).count
        except Exception:
            return 0


# Module-level singleton
_service: Optional[QdrantService] = None


def get_qdrant_service() -> QdrantService:
    global _service
    if _service is None:
        _service = QdrantService()
    return _service
