"""
Manifest utilities — tracks processing state for every document in the pipeline.

The manifest is a single JSON file at parsed/manifest.json. Every pipeline script
reads it before processing (to skip already-done work) and writes it after (to
record completion, stats, and any errors).

Writes are atomic: we write to a temp file then rename, so the manifest is never
left in a partial state.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ── Schema helpers ─────────────────────────────────────────────────────────────

def _empty_entry(doc_id: str, file_name: str, book_title: str) -> dict:
    return {
        "doc_id": doc_id,
        "file_name": file_name,
        "book_title": book_title,
        "status": {
            "extracted": False,
            "chunked": False,
            "cards_generated": False,
            "indexed": False,
            "study_notes_generated": False,
            "hypotheses_generated": False,
            "vault_exported": False,
        },
        "stats": {
            "total_pages": 0,
            "poor_quality_pages": 0,
            "extraction_quality": "unknown",
            "chunk_count_retrieval": 0,
            "chunk_count_summary": 0,
            "card_count": 0,
            "card_errors": 0,
        },
        "timestamps": {
            "extracted_at": None,
            "chunked_at": None,
            "cards_generated_at": None,
            "indexed_at": None,
            "study_notes_generated_at": None,
            "vault_exported_at": None,
        },
        "errors": [],
    }


# ── I/O ────────────────────────────────────────────────────────────────────────

def load(manifest_path: Path) -> dict[str, Any]:
    """Load manifest from disk. Returns empty dict if file does not exist."""
    if not manifest_path.exists():
        return {}
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(manifest_path: Path, manifest: dict[str, Any]) -> None:
    """Save manifest atomically (write temp → rename)."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=manifest_path.parent, prefix=".manifest_", suffix=".tmp"
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, default=str)
        os.replace(tmp_path, manifest_path)
    except Exception:
        os.unlink(tmp_path)
        raise


# ── Entry helpers ──────────────────────────────────────────────────────────────

def get_or_create(manifest: dict, doc_id: str, file_name: str, book_title: str) -> dict:
    """Return existing entry or create a fresh one."""
    if doc_id not in manifest:
        manifest[doc_id] = _empty_entry(doc_id, file_name, book_title)
    return manifest[doc_id]


def is_done(manifest: dict, doc_id: str, phase: str) -> bool:
    """Return True if the given phase has already been completed for this doc."""
    entry = manifest.get(doc_id, {})
    return entry.get("status", {}).get(phase, False)


def mark_done(manifest: dict, doc_id: str, phase: str) -> None:
    """Mark a phase as complete and record the timestamp."""
    entry = manifest.setdefault(doc_id, {})
    entry.setdefault("status", {})[phase] = True
    ts_key = f"{phase}_at"
    entry.setdefault("timestamps", {})[ts_key] = datetime.now(timezone.utc).isoformat()


def update_stats(manifest: dict, doc_id: str, stats: dict) -> None:
    """Merge stats dict into the entry's stats."""
    entry = manifest.setdefault(doc_id, {})
    entry.setdefault("stats", {}).update(stats)


def add_error(manifest: dict, doc_id: str, error: str) -> None:
    """Append an error message to the entry."""
    entry = manifest.setdefault(doc_id, {})
    entry.setdefault("errors", []).append(
        {"timestamp": datetime.now(timezone.utc).isoformat(), "message": error}
    )
