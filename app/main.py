"""FastAPI application — options research knowledge brain."""
from fastapi import FastAPI

from app.routers import cards, hypotheses, search

app = FastAPI(
    title="Options Research Brain",
    description="Local-first semantic search over options/trading knowledge cards and hypotheses.",
    version="0.1.0",
)

app.include_router(search.router)
app.include_router(cards.router)
app.include_router(hypotheses.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
