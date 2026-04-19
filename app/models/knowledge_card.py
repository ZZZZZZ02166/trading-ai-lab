from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CardType(str, Enum):
    CONCEPT = "concept"
    DEFINITION = "definition"
    PRINCIPLE = "principle"
    CAUTION = "caution"
    MECHANISM = "mechanism"
    STRATEGY_IDEA = "strategy_idea"
    VOLATILITY_INSIGHT = "volatility_insight"
    MARKET_STRUCTURE_INSIGHT = "market_structure_insight"


class KnowledgeCard(BaseModel):
    card_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chunk_id: str
    doc_id: str
    book_title: str
    author: Optional[str] = None
    file_path: str
    page_ref: str                    # Human-readable, e.g. "pp. 42–44"
    page_start: int
    page_end: int
    card_type: CardType
    title: str                       # ≤10 words, specific enough to search for
    body: str                        # 2–5 sentences, self-contained
    tags: list[str]                  # lowercase snake_case
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_used: str
