from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MetaThemeStatus(str, Enum):
    PROVISIONAL = "provisional"
    ACTIVE = "active"
    CONFIRMED = "confirmed"


class MetaTheme(BaseModel):
    meta_theme_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    theme_type: str = "meta_theme"
    title: str = ""                         # filled by Claude naming step
    summary: str = ""                       # filled by Claude naming step
    merge_reason: str = ""                  # filled by Claude naming step

    parent_theme_ids: list[str]             # the two (or more) themes being merged
    source_card_ids: list[str]              # union of all parent source cards
    source_doc_ids: list[str]              # unique books represented
    source_edge_ids: list[str]              # edges within this meta-theme

    top_tags: list[str]
    card_count: int
    book_count: int
    confidence: float

    # Critic gate results (stored for auditability)
    critic_composite_score: float           # must be ≥ 0.55
    critic_cross_edge_count: int            # must be ≥ 3
    critic_centroid_cosine: float           # must be ≥ 0.65
    critic_passed: bool

    status: MetaThemeStatus = MetaThemeStatus.PROVISIONAL
    needs_review_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    derived_by: str = "claude-sonnet-4-6"
