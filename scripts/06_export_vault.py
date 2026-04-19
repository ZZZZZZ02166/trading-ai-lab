"""
06_export_vault.py — Export knowledge cards and hypotheses as Obsidian markdown.

For each document with cards_generated=True (and vault_exported=False unless --force):
  - Write vault/cards/<doc_slug>/<card_slug>.md for every card
  - Write vault/hypotheses/<hypothesis_id>.md for every hypothesis

For hypotheses, reads all experiments/hypotheses_*.json files.

Usage:
    python scripts/06_export_vault.py
    python scripts/06_export_vault.py --doc-id abc123def456
    python scripts/06_export_vault.py --force
    python scripts/06_export_vault.py --dry-run
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()

console = Console()

CARDS_DIR = Path(os.getenv("CARDS_DIR", "cards"))
EXPERIMENTS_DIR = Path(os.getenv("EXPERIMENTS_DIR", "experiments"))
VAULT_DIR = Path(os.getenv("VAULT_DIR", "vault"))
MANIFEST_PATH = Path(os.getenv("PARSED_DIR", "parsed")) / "manifest.json"

VAULT_CARDS_DIR = VAULT_DIR / "cards"
VAULT_HYPOTHESES_DIR = VAULT_DIR / "hypotheses"


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:80]


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    return {}


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, default=str))


def card_to_markdown(card: dict, doc_slug: str) -> str:
    tags_yaml = "\n".join(f"  - {t}" for t in card.get("tags", []))
    created = card.get("created_at", "")[:10] if card.get("created_at") else ""
    return f"""---
card_id: {card['card_id']}
doc_id: {card['doc_id']}
book_title: "{card['book_title']}"
author: "{card.get('author') or ''}"
card_type: {card['card_type']}
page_ref: "{card.get('page_ref', '')}"
page_start: {card.get('page_start', '')}
page_end: {card.get('page_end', '')}
tags:
{tags_yaml}
created_at: {created}
model_used: {card.get('model_used', '')}
---

# {card['title']}

**Type:** {card['card_type']}
**Source:** {card['book_title']} — {card.get('page_ref', '')}

## Summary

{card['body']}

## Tags

{' '.join(f'#{t}' for t in card.get('tags', []))}

## Notes

<!-- Personal notes here -->
"""


def hypothesis_to_markdown(hyp: dict) -> str:
    tags_yaml = "\n".join(f"  - {t}" for t in hyp.get("tags", []))
    src_docs = "\n".join(f"  - {d}" for d in hyp.get("source_doc_ids", []))
    created = hyp.get("created_at", "")[:10] if hyp.get("created_at") else ""
    return f"""---
hypothesis_id: {hyp['hypothesis_id']}
source_doc_ids:
{src_docs}
tags:
{tags_yaml}
created_at: {created}
model_used: {hyp.get('model_used', '')}
---

# {hyp['title']}

## Claim

{hyp['claim']}

## Rationale

{hyp['rationale']}

## Testability Notes

{hyp['testability_notes']}

## Tags

{' '.join(f'#{t}' for t in hyp.get('tags', []))}

## Experiment Notes

<!-- Record test results here -->
"""


def export_cards_for_doc(doc_id: str, dry_run: bool) -> int:
    cards_file = CARDS_DIR / f"{doc_id}.json"
    if not cards_file.exists():
        console.print(f"[yellow]  No cards file for {doc_id}, skipping[/yellow]")
        return 0

    cards = json.loads(cards_file.read_text())
    manifest = load_manifest()
    entry = manifest.get(doc_id, {})
    book_title = entry.get("book_title", doc_id)
    doc_slug = slugify(book_title) or doc_id

    out_dir = VAULT_CARDS_DIR / doc_slug
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for card in cards:
        card_slug = slugify(card.get("title", card["card_id"]))
        out_path = out_dir / f"{card_slug}.md"
        if not dry_run:
            out_path.write_text(card_to_markdown(card, doc_slug))
        written += 1

    console.print(f"  [green]Cards:[/green] {written} written to vault/cards/{doc_slug}/")
    return written


def export_hypotheses(dry_run: bool) -> int:
    hyp_files = sorted(EXPERIMENTS_DIR.glob("hypotheses_*.json"))
    if not hyp_files:
        console.print("[yellow]  No hypothesis files found[/yellow]")
        return 0

    if not dry_run:
        VAULT_HYPOTHESES_DIR.mkdir(parents=True, exist_ok=True)

    written = 0
    for hyp_file in hyp_files:
        hypotheses = json.loads(hyp_file.read_text())
        for hyp in hypotheses:
            hyp_slug = slugify(hyp.get("title", hyp["hypothesis_id"]))
            out_path = VAULT_HYPOTHESES_DIR / f"{hyp_slug}.md"
            if not dry_run:
                out_path.write_text(hypothesis_to_markdown(hyp))
            written += 1

    console.print(f"  [green]Hypotheses:[/green] {written} written to vault/hypotheses/")
    return written


def main(
    doc_id: Optional[str] = typer.Option(None, "--doc-id", help="Process only this doc_id"),
    force: bool = typer.Option(False, "--force", help="Re-export even if already done"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would run without writing"),
) -> None:
    manifest = load_manifest()

    if dry_run:
        console.print("[bold yellow]DRY RUN — no files will be written[/bold yellow]")

    # Determine which docs to process
    if doc_id:
        if doc_id not in manifest:
            console.print(f"[red]doc_id {doc_id} not found in manifest[/red]")
            raise typer.Exit(1)
        doc_ids = [doc_id]
    else:
        doc_ids = list(manifest.keys())

    total_cards = 0
    exported_docs = []

    for did in doc_ids:
        entry = manifest[did]
        status = entry.get("status", {})
        stats = entry.get("stats", {})
        book_title = entry.get("book_title", did)

        if not status.get("cards_generated"):
            console.print(f"[dim]Skipping {did} — cards not generated yet[/dim]")
            continue

        if status.get("vault_exported") and not force:
            console.print(f"[dim]Skipping {did} — vault already exported (use --force)[/dim]")
            continue

        console.print(f"\n[bold]Exporting vault for:[/bold] {book_title} ({did})")

        n = export_cards_for_doc(did, dry_run)
        total_cards += n

        if not dry_run:
            manifest[did]["status"]["vault_exported"] = True
            manifest[did]["timestamps"]["vault_exported_at"] = datetime.now(timezone.utc).isoformat()
            save_manifest(manifest)

        exported_docs.append(did)

    # Export hypotheses (always, not per-doc)
    console.print("\n[bold]Exporting hypotheses...[/bold]")
    total_hyp = export_hypotheses(dry_run)

    console.print(f"\n[bold green]Done.[/bold green] {len(exported_docs)} docs, {total_cards} cards, {total_hyp} hypotheses exported.")


if __name__ == "__main__":
    typer.run(main)
