from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class RelationType(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    EXTENDS = "extends"
    RELATED_TO = "related_to"
    SAME_THEME = "same_theme"
    PREREQUISITE_FOR = "prerequisite_for"
    USEFUL_FOR_HYPOTHESIS = "useful_for_hypothesis"


class SourceBasis(str, Enum):
    SEMANTIC_SIMILARITY = "semantic_similarity"
    TAG_OVERLAP = "tag_overlap"
    RULE_BASED = "rule_based"
    COMBINED = "combined"


class Edge(BaseModel):
    edge_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_card_id: str
    to_card_id: str
    relation_type: RelationType
    confidence: float                  # 0.0–1.0; only edges ≥ 0.70 kept
    cosine_similarity: float           # raw Qdrant score
    tag_overlap_count: int             # number of shared tags
    cross_book: bool                   # True if cards from different books
    reason: str                        # human-readable explanation
    source_basis: SourceBasis
    created_at: datetime = Field(default_factory=datetime.utcnow)
    derived_by: str = "claude-sonnet-4-6"
