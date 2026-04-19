"""
Embedding service — wraps sentence-transformers (local, no API key required).
Optionally supports OpenAI or Voyage backends via environment variables.
"""
from __future__ import annotations

import os
from typing import Optional

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBED_BACKEND = os.getenv("EMBED_BACKEND", "local")  # local | openai | voyage


class EmbedService:
    def __init__(self, model_name: str = EMBEDDING_MODEL, backend: str = EMBED_BACKEND):
        self.model_name = model_name
        self.backend = backend
        self._model = None

    def _load(self) -> None:
        if self._model is not None:
            return
        if self.backend == "local":
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        elif self.backend == "openai":
            import openai
            self._client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        elif self.backend == "voyage":
            import voyageai
            self._client = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])
        else:
            raise ValueError(f"Unknown embedding backend: {self.backend}")

    @property
    def vector_size(self) -> int:
        self._load()
        if self.backend == "local":
            return self._model.get_sentence_embedding_dimension()
        elif self.backend == "openai":
            # text-embedding-3-small: 1536, text-embedding-ada-002: 1536
            return 1536
        elif self.backend == "voyage":
            return 1024
        return 384

    def embed(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        self._load()
        if self.backend == "local":
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            return embeddings.tolist()
        elif self.backend == "openai":
            results = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                response = self._client.embeddings.create(
                    model=self.model_name, input=batch
                )
                results.extend([e.embedding for e in response.data])
            return results
        elif self.backend == "voyage":
            results = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                response = self._client.embed(batch, model=self.model_name)
                results.extend(response.embeddings)
            return results
        raise ValueError(f"Unknown backend: {self.backend}")

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


# Module-level singleton
_service: Optional[EmbedService] = None


def get_embed_service() -> EmbedService:
    global _service
    if _service is None:
        _service = EmbedService()
    return _service
