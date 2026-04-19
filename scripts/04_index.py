"""
04_index.py — Embed chunks and cards → upsert into Qdrant (local, no Docker).

Collections:
  chunks  — embed chunk.text; payload includes all Chunk fields + text
  cards   — embed title + "\n\n" + body; payload includes all KnowledgeCard fields

Idempotent: upsert uses chunk_id/card_id as stable point IDs.
Already-indexed documents are skipped unless --force.

Usage:
    python scripts/04_index.py
    python scripts/04_index.py --doc-id abc123def456
    python scripts/04_index.py --force
    python scripts/04_index.py --dry-run
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from dotenv import load_dotenv
from qdrant_client.models import PointStruct
from rich.console import Console
from rich.table import Table

import scripts.manifest as manifest_utils
from app.services.embed_service import EmbedService
from app.services.qdrant_service import QdrantService

load_dotenv()

CHUNKS_DIR = Path(os.getenv("CHUNKS_DIR", "./chunks"))
CARDS_DIR = Path(os.getenv("CARDS_DIR", "./cards"))
PARSED_DIR = Path(os.getenv("PARSED_DIR", "./parsed"))
MANIFEST_PATH = PARSED_DIR / "manifest.json"
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "32"))

console = Console()
app = typer.Typer(add_completion=False)


def _stable_point_id(uid: str) -> str:
    """Convert a UUID string to a deterministic integer point ID for Qdrant."""
    return int(hashlib.md5(uid.encode()).hexdigest(), 16) % (2**63)


def index_doc(
    doc_id: str,
    embed_svc: EmbedService,
    qdrant_svc: QdrantService,
) -> dict:
    chunks_path = CHUNKS_DIR / f"{doc_id}.json"
    cards_path = CARDS_DIR / f"{doc_id}.json"

    if not chunks_path.exists():
        return {"status": "error", "error": f"chunks file not found: {chunks_path}"}

    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    cards = json.loads(cards_path.read_text(encoding="utf-8")) if cards_path.exists() else []

    # ── Index chunks ──────────────────────────────────────────────────
    chunk_texts = [c["text"] for c in chunks]
    console.print(f"  Embedding {len(chunks)} chunks...", end="")
    chunk_vectors = embed_svc.embed(chunk_texts, batch_size=EMBED_BATCH_SIZE)
    console.print(" done")

    qdrant_svc.ensure_collection("chunks", embed_svc.vector_size)
    chunk_points = []
    for c, vec in zip(chunks, chunk_vectors):
        payload = {k: v for k, v in c.items() if k != "text"}
        payload["text"] = c["text"]
        chunk_points.append(
            PointStruct(id=_stable_point_id(c["chunk_id"]), vector=vec, payload=payload)
        )
    console.print(f"  Upserting {len(chunk_points)} chunk points...", end="")
    qdrant_svc.upsert("chunks", chunk_points)
    console.print(" done")

    # ── Index cards ───────────────────────────────────────────────────
    card_count = 0
    if cards:
        card_texts = [f"{c['title']}\n\n{c['body']}" for c in cards]
        console.print(f"  Embedding {len(cards)} cards...", end="")
        card_vectors = embed_svc.embed(card_texts, batch_size=EMBED_BATCH_SIZE)
        console.print(" done")

        qdrant_svc.ensure_collection("cards", embed_svc.vector_size)
        card_points = []
        for c, vec in zip(cards, card_vectors):
            card_points.append(
                PointStruct(id=_stable_point_id(c["card_id"]), vector=vec, payload=c)
            )
        console.print(f"  Upserting {len(card_points)} card points...", end="")
        qdrant_svc.upsert("cards", card_points)
        console.print(" done")
        card_count = len(cards)

    return {
        "status": "ok",
        "chunks_indexed": len(chunks),
        "cards_indexed": card_count,
    }


@app.command()
def main(
    doc_id: Optional[str] = typer.Option(None, "--doc-id", help="Process only this doc_id"),
    force: bool = typer.Option(False, "--force", help="Re-index even if already done"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would run"),
) -> None:
    manifest = manifest_utils.load(MANIFEST_PATH)

    doc_ids = [doc_id] if doc_id else list(manifest.keys())

    to_process = []
    for did in doc_ids:
        if did not in manifest:
            console.print(f"[yellow]Warning: {did} not in manifest, skipping[/yellow]")
            continue
        entry = manifest[did]
        if not entry["status"].get("chunked"):
            console.print(f"[dim]Skipping {did} — not yet chunked[/dim]")
            continue
        if not force and entry["status"].get("indexed"):
            console.print(f"[dim]Skipping {did} — already indexed[/dim]")
            continue
        to_process.append(did)

    if not to_process:
        console.print("[green]Nothing to index.[/green]")
        return

    if dry_run:
        console.print(f"[cyan]Dry run — would index {len(to_process)} doc(s):[/cyan]")
        for did in to_process:
            console.print(f"  {did} ({manifest[did].get('book_title', '?')})")
        return

    console.print(f"\nLoading embedding model: [cyan]{os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')}[/cyan]")
    embed_svc = EmbedService()
    qdrant_svc = QdrantService()

    results = []
    for did in to_process:
        title = manifest[did].get("book_title", did)
        console.print(f"\n[bold]Indexing:[/bold] {title} ({did})")
        try:
            result = index_doc(did, embed_svc, qdrant_svc)
            result["doc_id"] = did
            result["title"] = title
        except Exception as e:
            console.print(f"  [red]ERROR:[/red] {e}")
            result = {"doc_id": did, "title": title, "status": "error", "error": str(e)}
            manifest_utils.add_error(manifest, did, str(e))
            manifest_utils.save(MANIFEST_PATH, manifest)
            results.append(result)
            continue

        manifest_utils.mark_done(manifest, did, "indexed")
        manifest_utils.save(MANIFEST_PATH, manifest)
        results.append(result)

    # Summary
    console.print()
    table = Table(title="Indexing Summary", show_lines=True)
    table.add_column("Title")
    table.add_column("Status")
    table.add_column("Chunks", justify="right")
    table.add_column("Cards", justify="right")
    for r in results:
        status = "[green]ok[/green]" if r["status"] == "ok" else "[red]error[/red]"
        table.add_row(
            r["title"][:50],
            status,
            str(r.get("chunks_indexed", "—")),
            str(r.get("cards_indexed", "—")),
        )
    console.print(table)

    total_chunks = qdrant_svc.collection_count("chunks")
    total_cards = qdrant_svc.collection_count("cards")
    console.print(f"\nQdrant totals — chunks: {total_chunks}, cards: {total_cards}")


if __name__ == "__main__":
    app()
