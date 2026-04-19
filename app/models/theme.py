from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ThemeStatus(str, Enum):
    PROVISIONAL = "provisional"
    ACTIVE = "active"
    CONFIRMED = "confirmed"
    NEEDS_REVIEW = "needs_review"   # cluster too large or too weak
    MERGED = "merged"               # absorbed into a meta-theme (kept for traceability)
    RETIRED = "retired"


class Theme(BaseModel):
    theme_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""                        # filled by Claude naming step
    summary: str = ""                      # filled by Claude naming step
    source_card_ids: list[str]
    source_doc_ids: list[str]              # unique books represented
    source_edge_ids: list[str]
    top_tags: list[str]                    # most frequent tags across member cards
    avg_edge_confidence: float             # mean confidence of internal edges
    card_count: int
    book_count: int
    confidence: float                      # overall theme confidence
    status: ThemeStatus = ThemeStatus.PROVISIONAL
    needs_review_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    derived_by: str = "claude-sonnet-4-6"
