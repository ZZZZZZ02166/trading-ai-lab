from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    doc_id: str
    book_title: str
    author: Optional[str] = None
    file_path: str
    page_start: int                  # First page this chunk covers (1-indexed)
    page_end: int                    # Last page this chunk covers (inclusive)
    chunk_index: int                 # 0-based position within the full chunk list
    chunk_type: str                  # "retrieval" | "summary"
    section_hint: Optional[str] = None  # Detected heading text, if any
    strategy: str                    # "section_break" | "sliding_window"
    text: str
    char_count: int
