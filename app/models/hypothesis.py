from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class Hypothesis(BaseModel):
    hypothesis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_card_ids: list[str]       # Which KnowledgeCards contributed
    source_doc_ids: list[str]        # Derived from cards, for quick filtering
    title: str
    claim: str                       # The core testable claim (1–3 sentences)
    rationale: str                   # Why the cards support this (3–6 sentences)
    testability_notes: str           # How this could be tested or falsified
    tags: list[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_used: str
