from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ThemeRelationType(str, Enum):
    RELATED_TO = "related_to"
    SUPPORTS = "supports"
    OVERLAPS_WITH = "overlaps_with"
    DEPENDS_ON = "depends_on"
    CONTRADICTS = "contradicts"
    MERGE_CANDIDATE_FOR = "merge_candidate_for"
    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"


class ThemeEdge(BaseModel):
    theme_edge_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_theme_id: str
    to_theme_id: str
    relation_type: ThemeRelationType
    confidence: float                   # composite score 0.0–1.0

    # Component scores (stored for debugging / re-weighting)
    shared_tag_score: float             # Jaccard on top_tags
    cross_edge_count: int               # edges linking cards across the two themes
    centroid_cosine: float              # cosine between embedding centroids
    card_overlap_jaccard: float         # Jaccard on source_card_ids (secondary)

    reason: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    derived_by: str = "claude-sonnet-4-6"
