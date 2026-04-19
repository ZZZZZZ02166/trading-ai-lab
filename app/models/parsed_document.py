from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PageContent(BaseModel):
    page_num: int                       # 1-indexed
    text: str                           # Cleaned text (may include [VISUAL CONTENT: ...] blocks)
    char_count: int
    quality_status: str = "ok"          # "ok" | "empty" | "low_quality"
    needs_ocr: bool = False
    extraction_mode: str = "text"       # "text" | "vision_primary" | "vision_supplement" | "blank"


class ParsedDocument(BaseModel):
    doc_id: str                         # sha256[:12] of raw file bytes
    book_title: str                     # From PDF metadata or derived from filename
    author: Optional[str] = None        # From PDF metadata if available
    file_path: str                      # Relative to project root, e.g. "books/foo.pdf"
    file_name: str                      # "foo.pdf"
    total_pages: int
    pages: list[PageContent]
    extraction_quality: str = "ok"      # "ok" | "poor" (>20% pages need OCR)
    poor_quality_pages: int = 0
    vision_pages: int = 0               # Pages where vision extraction was used
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    extractor_version: str = "1.1"
