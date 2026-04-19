"""GET /hypotheses — browse hypotheses from disk JSON."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/hypotheses", tags=["hypotheses"])
EXPERIMENTS_DIR = Path(os.getenv("EXPERIMENTS_DIR", "./experiments"))


def _load_all_hypotheses() -> list[dict]:
    hypotheses = []
    for f in sorted(EXPERIMENTS_DIR.glob("hypotheses_*.json")):
        hypotheses.extend(json.loads(f.read_text(encoding="utf-8")))
    return hypotheses


@router.get("", response_model=list[dict[str, Any]])
def list_hypotheses(
    tag: Optional[str] = Query(None),
    doc_id: Optional[str] = Query(None),
) -> list[dict]:
    items = _load_all_hypotheses()
    if tag:
        items = [h for h in items if tag in h.get("tags", [])]
    if doc_id:
        items = [h for h in items if doc_id in h.get("source_doc_ids", [])]
    return items


@router.get("/{hypothesis_id}", response_model=dict[str, Any])
def get_hypothesis(hypothesis_id: str) -> dict:
    for h in _load_all_hypotheses():
        if h.get("hypothesis_id") == hypothesis_id:
            return h
    raise HTTPException(status_code=404, detail=f"Hypothesis {hypothesis_id!r} not found")
