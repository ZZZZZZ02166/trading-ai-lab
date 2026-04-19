"""GET /cards — browse cards from disk JSON."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/cards", tags=["cards"])
CARDS_DIR = Path(os.getenv("CARDS_DIR", "./cards"))


def _load_all_cards() -> list[dict]:
    cards = []
    for f in sorted(CARDS_DIR.glob("*.json")):
        if f.stem.startswith("raw_"):
            continue
        cards.extend(json.loads(f.read_text(encoding="utf-8")))
    return cards


@router.get("", response_model=list[dict[str, Any]])
def list_cards(
    book: Optional[str] = Query(None, description="Filter by book_title substring"),
    card_type: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    doc_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> list[dict]:
    cards = _load_all_cards()

    if book:
        cards = [c for c in cards if book.lower() in c.get("book_title", "").lower()]
    if card_type:
        cards = [c for c in cards if c.get("card_type") == card_type]
    if tag:
        cards = [c for c in cards if tag in c.get("tags", [])]
    if doc_id:
        cards = [c for c in cards if c.get("doc_id") == doc_id]

    start = (page - 1) * page_size
    return cards[start : start + page_size]


@router.get("/{card_id}", response_model=dict[str, Any])
def get_card(card_id: str) -> dict:
    for card in _load_all_cards():
        if card.get("card_id") == card_id:
            return card
    raise HTTPException(status_code=404, detail=f"Card {card_id!r} not found")
