"""
02_chunk.py — ParsedDocument → Chunks

Reads every ParsedDocument from parsed/ and splits each document into two
kinds of chunks stored in chunks/{doc_id}.json:

  summary chunks    — one per detected section/chapter (1000–3000 chars).
                      Used for study note and summary generation.

  retrieval chunks  — derived from summary chunks, split to ≤1000 chars with
                      150-char overlap. Used for semantic search/embedding.

Chunking strategy:
  1. Section-aware (primary): detect headings using heuristics, flush buffer
     at each break when buffer ≥ MIN_CHUNK_CHARS.
  2. Sliding window (fallback): used for the whole document if fewer than 3
     section breaks are found, or to re-split any oversized summary chunk.

Idempotent by default — skips documents already chunked unless --force.

Usage:
    python scripts/02_chunk.py
    python scripts/02_chunk.py --doc-id abc123def456
    python scripts/02_chunk.py --force
    python scripts/02_chunk.py --dry-run
"""
from __future__ import annotations

import json
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

import scripts.manifest as manifest_utils
from app.models.chunk import Chunk
from app.models.parsed_document import ParsedDocument

load_dotenv()

PARSED_DIR = Path(os.getenv("PARSED_DIR", "./parsed"))
CHUNKS_DIR = Path(os.getenv("CHUNKS_DIR", "./chunks"))
MANIFEST_PATH = PARSED_DIR / "manifest.json"

MIN_CHUNK_CHARS: int = int(os.getenv("CHUNK_MIN_CHARS", "400"))
MAX_SUMMARY_CHARS: int = int(os.getenv("CHUNK_MAX_SUMMARY_CHARS", "3000"))
MAX_RETRIEVAL_CHARS: int = int(os.getenv("CHUNK_MAX_RETRIEVAL_CHARS", "1000"))
WINDOW_SIZE: int = int(os.getenv("CHUNK_WINDOW_SIZE", "800"))
WINDOW_OVERLAP: int = int(os.getenv("CHUNK_WINDOW_OVERLAP", "150"))
MIN_SECTION_BREAKS_FOR_SECTION_STRATEGY: int = 3

console = Console()
app = typer.Typer(add_completion=False)


# ── Heading detection ──────────────────────────────────────────────────────────

_HEADING_PATTERNS = [
    # ALL CAPS line, 4–80 chars, starts with a capital letter
    re.compile(r"^[A-Z][A-Z\s\-:,0-9]{3,79}$"),
    # Chapter / Part / Section with number
    re.compile(
        r"^(Chapter|CHAPTER|Part|PART|Section|SECTION)\s*[0-9IVXLCDM]+",
        re.IGNORECASE,
    ),
    # Pure numeric heading: "1.", "1.1", "2.3.4 Title"
    re.compile(r"^\d+(\.\d+)*\.?\s+[A-Z]"),
]


def is_heading(line: str) -> bool:
    """Return True if this line looks like a section heading."""
    stripped = line.strip()
    if not stripped or len(stripped) < 4 or len(stripped) > 120:
        return False
    # Skip lines that are purely punctuation or numbers
    if re.fullmatch(r"[\W\d]+", stripped):
        return False
    for pattern in _HEADING_PATTERNS:
        if pattern.match(stripped):
            return True
    return False


# ── Summary chunk builder (section-aware) ─────────────────────────────────────

def _make_chunk(
    doc: ParsedDocument,
    buffer: list[tuple[int, str]],
    section_hint: Optional[str],
    strategy: str,
    chunk_type: str,
) -> Chunk:
    """Build a Chunk from a buffer of (page_num, line_text) tuples."""
    page_nums = [pn for pn, _ in buffer]
    text = "\n".join(line for _, line in buffer).strip()
    return Chunk(
        chunk_id=str(uuid.uuid4()),
        doc_id=doc.doc_id,
        book_title=doc.book_title,
        author=doc.author,
        file_path=doc.file_path,
        page_start=min(page_nums) if page_nums else 1,
        page_end=max(page_nums) if page_nums else 1,
        chunk_index=0,  # assigned later
        chunk_type=chunk_type,
        section_hint=section_hint,
        strategy=strategy,
        text=text,
        char_count=len(text),
    )


def build_section_chunks(doc: ParsedDocument) -> tuple[list[Chunk], int]:
    """
    Walk the document page-by-page and flush the buffer whenever a section
    heading is detected (and the buffer is large enough).

    Returns (chunks, number_of_section_breaks_detected).
    """
    chunks: list[Chunk] = []
    buffer: list[tuple[int, str]] = []
    buffer_chars = 0
    current_section: Optional[str] = None
    section_breaks = 0

    for page in doc.pages:
        for line in page.text.split("\n"):
            stripped = line.strip()

            if is_heading(stripped) and buffer_chars >= MIN_CHUNK_CHARS:
                # Flush current buffer as a summary chunk
                chunk = _make_chunk(doc, buffer, current_section, "section_break", "summary")
                chunks.append(chunk)
                section_breaks += 1
                buffer = []
                buffer_chars = 0
                current_section = stripped

            buffer.append((page.page_num, line))
            buffer_chars += len(line) + 1  # +1 for newline

            # Force-flush if buffer has grown too large
            if buffer_chars >= MAX_SUMMARY_CHARS:
                strategy = "section_break" if current_section else "sliding_window"
                chunk = _make_chunk(doc, buffer, current_section, strategy, "summary")
                chunks.append(chunk)
                buffer = []
                buffer_chars = 0

    # Flush remainder
    if buffer and buffer_chars >= 200:
        strategy = "section_break" if section_breaks > 0 else "sliding_window"
        chunk = _make_chunk(doc, buffer, current_section, strategy, "summary")
        chunks.append(chunk)

    return chunks, section_breaks


# ── Sliding window builder ─────────────────────────────────────────────────────

def _chars_to_page_range(
    char_start: int, char_end: int, page_map: list[tuple[int, int, int]]
) -> tuple[int, int]:
    """
    Given a character range in the full document text, return (page_start, page_end).
    page_map: list of (page_num, char_start_inclusive, char_end_exclusive)
    """
    pages_hit = [pn for pn, ps, pe in page_map if ps < char_end and pe > char_start]
    if not pages_hit:
        return page_map[0][0] if page_map else 1, page_map[-1][0] if page_map else 1
    return min(pages_hit), max(pages_hit)


def build_sliding_window_chunks(
    doc: ParsedDocument,
    window: int = WINDOW_SIZE,
    overlap: int = WINDOW_OVERLAP,
    chunk_type: str = "summary",
) -> list[Chunk]:
    """Build chunks using a sliding window over the full document text."""
    # Build full text and a page map
    full_text = ""
    page_map: list[tuple[int, int, int]] = []
    for page in doc.pages:
        start = len(full_text)
        full_text += page.text + "\n"
        page_map.append((page.page_num, start, len(full_text)))

    chunks: list[Chunk] = []
    pos = 0
    while pos < len(full_text):
        end = min(pos + window, len(full_text))
        chunk_text = full_text[pos:end].strip()
        if chunk_text and len(chunk_text) >= 200:
            page_start, page_end = _chars_to_page_range(pos, end, page_map)
            chunks.append(
                Chunk(
                    chunk_id=str(uuid.uuid4()),
                    doc_id=doc.doc_id,
                    book_title=doc.book_title,
                    author=doc.author,
                    file_path=doc.file_path,
                    page_start=page_start,
                    page_end=page_end,
                    chunk_index=0,
                    chunk_type=chunk_type,
                    section_hint=None,
                    strategy="sliding_window",
                    text=chunk_text,
                    char_count=len(chunk_text),
                )
            )
        if end >= len(full_text):
            break
        pos += window - overlap

    return chunks


# ── Retrieval chunk derivation ─────────────────────────────────────────────────

def derive_retrieval_chunks(summary_chunk: Chunk) -> list[Chunk]:
    """
    Derive one or more retrieval-size chunks from a summary chunk.

    If the summary chunk is already ≤ MAX_RETRIEVAL_CHARS, return it unchanged
    (with chunk_type set to "retrieval").  Otherwise split it using a sliding
    window, trying to break at paragraph boundaries.
    """
    if summary_chunk.char_count <= MAX_RETRIEVAL_CHARS:
        return [summary_chunk.model_copy(update={"chunk_id": str(uuid.uuid4()), "chunk_type": "retrieval"})]

    text = summary_chunk.text
    pieces: list[Chunk] = []
    pos = 0
    while pos < len(text):
        end = min(pos + MAX_RETRIEVAL_CHARS, len(text))
        # Try to break at a paragraph boundary within the last 100 chars
        if end < len(text):
            newline_pos = text.rfind("\n\n", max(0, end - 100), end)
            if newline_pos > pos:
                end = newline_pos
            else:
                newline_pos = text.rfind("\n", max(0, end - 80), end)
                if newline_pos > pos:
                    end = newline_pos

        chunk_text = text[pos:end].strip()
        if chunk_text:
            pieces.append(
                Chunk(
                    chunk_id=str(uuid.uuid4()),
                    doc_id=summary_chunk.doc_id,
                    book_title=summary_chunk.book_title,
                    author=summary_chunk.author,
                    file_path=summary_chunk.file_path,
                    page_start=summary_chunk.page_start,
                    page_end=summary_chunk.page_end,
                    chunk_index=0,
                    chunk_type="retrieval",
                    section_hint=summary_chunk.section_hint,
                    strategy=summary_chunk.strategy,
                    text=chunk_text,
                    char_count=len(chunk_text),
                )
            )

        if end >= len(text):
            break
        pos = max(pos + 1, end - WINDOW_OVERLAP)  # guard against infinite loop

    return pieces


# ── Main chunking orchestrator ─────────────────────────────────────────────────

def chunk_document(doc: ParsedDocument) -> list[Chunk]:
    """
    Produce the full list of chunks (summary + retrieval) for a document.

    Strategy selection:
    - Try section-aware chunking first.
    - If fewer than MIN_SECTION_BREAKS_FOR_SECTION_STRATEGY breaks are found,
      fall back to sliding window for summary chunks.
    - Always derive retrieval chunks from summary chunks.
    """
    # --- Summary chunks ---
    section_chunks, section_breaks = build_section_chunks(doc)

    if section_breaks < MIN_SECTION_BREAKS_FOR_SECTION_STRATEGY:
        console.print(
            f"  [dim]Only {section_breaks} section break(s) detected — "
            f"falling back to sliding window for summary chunks.[/dim]"
        )
        summary_chunks = build_sliding_window_chunks(
            doc,
            window=MAX_SUMMARY_CHARS,
            overlap=WINDOW_OVERLAP,
            chunk_type="summary",
        )
    else:
        summary_chunks = section_chunks

    # --- Retrieval chunks (derived from summary) ---
    retrieval_chunks: list[Chunk] = []
    for sc in summary_chunks:
        retrieval_chunks.extend(derive_retrieval_chunks(sc))

    # --- Assign sequential indices ---
    all_chunks = []
    for i, c in enumerate(summary_chunks):
        all_chunks.append(c.model_copy(update={"chunk_index": i}))
    offset = len(summary_chunks)
    for i, c in enumerate(retrieval_chunks):
        all_chunks.append(c.model_copy(update={"chunk_index": offset + i}))

    return all_chunks


# ── CLI ────────────────────────────────────────────────────────────────────────

@app.command()
def main(
    doc_id: Optional[str] = typer.Option(None, "--doc-id", help="Process only this doc_id"),
    force: bool = typer.Option(False, "--force", help="Re-chunk even if already done"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would run without doing it"),
    parsed_dir: Path = typer.Option(PARSED_DIR, "--parsed-dir"),
    chunks_dir: Path = typer.Option(CHUNKS_DIR, "--chunks-dir"),
) -> None:
    chunks_dir.mkdir(parents=True, exist_ok=True)
    manifest = manifest_utils.load(MANIFEST_PATH)

    parsed_files = sorted(parsed_dir.glob("*.json"))
    parsed_files = [f for f in parsed_files if f.name != "manifest.json"]

    if not parsed_files:
        console.print(f"[yellow]No parsed documents found in {parsed_dir}. Run 01_extract.py first.[/yellow]")
        raise typer.Exit()

    to_process: list[Path] = []
    for pf in parsed_files:
        did = pf.stem
        if doc_id and did != doc_id:
            continue
        if not force and manifest_utils.is_done(manifest, did, "chunked"):
            console.print(f"[dim]Skipping {pf.name} — already chunked[/dim]")
            continue
        to_process.append(pf)

    if not to_process:
        console.print("[green]Nothing to process.[/green]")
        return

    if dry_run:
        console.print(f"[cyan]Dry run — would chunk {len(to_process)} document(s):[/cyan]")
        for p in to_process:
            console.print(f"  {p.name}")
        return

    results = []
    for pf in to_process:
        console.print(f"\n[bold]Chunking:[/bold] {pf.name}")
        try:
            with open(pf, "r", encoding="utf-8") as f:
                raw = json.load(f)
            doc = ParsedDocument.model_validate(raw)
        except Exception as e:
            console.print(f"  [red]ERROR loading ParsedDocument:[/red] {e}")
            did = pf.stem
            manifest_utils.add_error(manifest, did, f"chunk load error: {e}")
            manifest_utils.save(MANIFEST_PATH, manifest)
            results.append({"doc_id": pf.stem, "status": "error", "error": str(e)})
            continue

        try:
            chunks = chunk_document(doc)
        except Exception as e:
            console.print(f"  [red]ERROR chunking:[/red] {e}")
            manifest_utils.add_error(manifest, doc.doc_id, f"chunking error: {e}")
            manifest_utils.save(MANIFEST_PATH, manifest)
            results.append({"doc_id": doc.doc_id, "status": "error", "error": str(e)})
            continue

        summary_count = sum(1 for c in chunks if c.chunk_type == "summary")
        retrieval_count = sum(1 for c in chunks if c.chunk_type == "retrieval")

        # Write chunks JSON
        out_path = chunks_dir / f"{doc.doc_id}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump([c.model_dump(mode="json") for c in chunks], f, indent=2, default=str)

        # Update manifest
        manifest_utils.update_stats(
            manifest,
            doc.doc_id,
            {
                "chunk_count_summary": summary_count,
                "chunk_count_retrieval": retrieval_count,
            },
        )
        manifest_utils.mark_done(manifest, doc.doc_id, "chunked")
        manifest_utils.save(MANIFEST_PATH, manifest)

        console.print(f"  doc_id:           {doc.doc_id}")
        console.print(f"  title:            {doc.book_title}")
        console.print(f"  summary chunks:   {summary_count}")
        console.print(f"  retrieval chunks: {retrieval_count}")
        console.print(f"  output:           {out_path}")

        results.append(
            {
                "doc_id": doc.doc_id,
                "title": doc.book_title,
                "status": "ok",
                "summary_chunks": summary_count,
                "retrieval_chunks": retrieval_count,
            }
        )

    # Summary table
    console.print()
    table = Table(title="Chunking Summary", show_lines=True)
    table.add_column("Title")
    table.add_column("Status")
    table.add_column("Summary", justify="right")
    table.add_column("Retrieval", justify="right")
    for r in results:
        status = "[green]ok[/green]" if r["status"] == "ok" else "[red]error[/red]"
        table.add_row(
            r.get("title", r["doc_id"]),
            status,
            str(r.get("summary_chunks", "—")),
            str(r.get("retrieval_chunks", "—")),
        )
    console.print(table)


if __name__ == "__main__":
    app()
