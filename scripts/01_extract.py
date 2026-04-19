"""
01_extract.py — PDF → ParsedDocument (text extraction + PNG rendering for visual pages)

Extraction mode per page:
  text               — text extraction only (default for most pages)
  vision_primary     — page has sparse/no text + visuals; PNG saved for /project:process-vision
  vision_supplement  — page has good text + visuals; PNG saved for /project:process-vision
  blank              — genuinely empty, skipped

Visual pages are identified by two signals:
  1. Raster images embedded in the PDF ≥ MIN_IMAGE_WIDTH_PT × MIN_IMAGE_HEIGHT_PT
  2. Vector drawing commands + text coverage < 40% (drawn charts, payoff diagrams)

PNGs are saved to rendered_pages/{doc_id}/page_{n}.png for later processing
by /project:process-vision.

Idempotent: already-extracted documents are skipped unless --force.

Usage:
    python scripts/01_extract.py
    python scripts/01_extract.py --doc-id abc123def456
    python scripts/01_extract.py --force
    python scripts/01_extract.py --dry-run
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

import fitz  # PyMuPDF
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

import scripts.manifest as manifest_utils
from app.models.parsed_document import PageContent, ParsedDocument

load_dotenv()

# ── Settings ───────────────────────────────────────────────────────────────────

BOOKS_DIR = Path(os.getenv("BOOKS_DIR", "./books"))
PARSED_DIR = Path(os.getenv("PARSED_DIR", "./parsed"))
RENDERED_DIR = Path(os.getenv("RENDERED_DIR", "./rendered_pages"))
MANIFEST_PATH = PARSED_DIR / "manifest.json"

# Minimum image dimensions (in PDF points) to qualify for vision extraction.
# At 72 dpi: 1 point = 1/72 inch. 90×70 pt ≈ 3.2cm × 2.5cm — catches any
# real diagram or formula image while skipping icons and logos.
MIN_IMAGE_WIDTH_PT = 90
MIN_IMAGE_HEIGHT_PT = 70

# Pages where text covers less than this fraction of the page area AND that
# have drawing commands are classified as vector diagram pages.
TEXT_COVERAGE_DIAGRAM_THRESHOLD = 0.40

# PNG render resolution for visual pages saved to rendered_pages/
# 100 dpi is sufficient for Claude vision to read formulas and diagrams;
# ~45% smaller files vs 150 dpi — reduces image token cost proportionally.
RENDER_DPI = 100

# ── Smart classification patterns ──────────────────────────────────────────────

# Keywords in extracted text that signal an embedded figure/diagram on the page
VISUAL_KEYWORDS = re.compile(
    r'\b(figure|fig\.|chart|diagram|exhibit|graph|plot|panel|illustration)\b',
    re.IGNORECASE,
)

# Dense math/stat symbols signal formula-heavy pages worth rendering
MATH_SYMBOLS = re.compile(
    r'[∑∫αβγδεζηθλμνξπρστυφχψωΔΓΛΣΦΨΩ∂√∞≈≠≤≥±×÷]'
)

# Short pages starting with these patterns are boilerplate — never render
BOILERPLATE_PATTERNS = re.compile(
    r'^\s*(references|bibliography|index|about\s+the\s+author|'
    r'acknowledgements?|contents|table\s+of\s+contents|'
    r'copyright|all\s+rights\s+reserved|printed\s+in|'
    r'appendix\s+[a-z0-9]|appendices)',
    re.IGNORECASE | re.MULTILINE,
)

console = Console()
app = typer.Typer(add_completion=False)


# ── Page classification ────────────────────────────────────────────────────────

def has_meaningful_raster(fitz_page) -> bool:
    """
    Return True if the page has at least one embedded raster image large enough
    to contain a diagram, chart, or formula (not a tiny icon or logo).
    """
    for img_info in fitz_page.get_images(full=True):
        xref = img_info[0]
        try:
            for rect in fitz_page.get_image_rects(xref):
                if rect.width >= MIN_IMAGE_WIDTH_PT and rect.height >= MIN_IMAGE_HEIGHT_PT:
                    return True
        except Exception:
            continue
    return False


def get_text_coverage(fitz_page) -> float:
    """
    Return the fraction of page area covered by text bounding boxes (0–1).

    Chart/diagram pages score low (0.20–0.35) because the visual takes up most
    of the space.  Text-only pages and tables score high (0.40–0.80).
    """
    page_area = fitz_page.rect.width * fitz_page.rect.height
    if page_area == 0:
        return 0.0
    blocks = fitz_page.get_text("blocks")
    text_area = sum(
        (b[2] - b[0]) * (b[3] - b[1])
        for b in blocks
        if len(b) > 4 and b[4].strip()
    )
    return min(text_area / page_area, 1.0)


def has_vector_diagram(fitz_page) -> bool:
    """
    Return True if the page likely contains a vector-drawn diagram (payoff
    chart, Greeks graph, volatility surface, etc.).

    Signal: drawing commands exist AND text covers < 40% of the page area.
    This separates real charts from decorative borders (borders sit on
    text-heavy pages → high text coverage) and from tables (tables are text).
    """
    if not fitz_page.get_drawings():
        return False
    return get_text_coverage(fitz_page) < TEXT_COVERAGE_DIAGRAM_THRESHOLD


def has_figure_reference(text: str) -> bool:
    """
    Return True if the page text mentions a figure/chart keyword.
    Used ONLY for neighbour flagging (the actual figure is often the NEXT page).
    NOT used to render the current page — figure mentions in prose are too noisy.
    """
    return bool(VISUAL_KEYWORDS.search(text))


def has_dense_math(text: str) -> bool:
    """
    Return True only if the page is genuinely formula-heavy (≥8 math/stat symbols).
    Threshold is intentionally high — a page with 2-3 symbols in prose text can be
    read from the extracted text alone. Only render when the page is so symbol-dense
    that the text layer alone would be misleading or incomplete.
    """
    return len(MATH_SYMBOLS.findall(text)) >= 8


def is_boilerplate_page(text: str) -> bool:
    """
    Return True if the page is clearly boilerplate that should never be rendered:
    references, bibliography, TOC, copyright, author bio, or appendix section
    openers (short title pages).

    Appendix CONTENT pages with real formulas or diagrams will still be caught
    by has_visuals or has_figure_reference — this only skips short opener pages.
    """
    stripped = text.strip()
    return len(stripped) < 300 and bool(BOILERPLATE_PATTERNS.search(stripped))


def classify_page(fitz_page, text: str) -> str:
    """
    Decide how to extract a page:

      text               — sufficient text, no qualifying visuals
      vision_primary     — sparse/no text + has visuals (diagram fills the page)
      vision_supplement  — good text + has visuals (diagram + surrounding prose)
      blank              — nothing to extract

    Three visual signals checked in order:
      1. Boilerplate guard — references, TOC, copyright, appendix openers → always "text"
      2. Raster images     — embedded PNG/JPEG ≥ MIN dimensions
      3. Vector diagram    — PDF drawing commands + text coverage < 40%
      4. Figure reference  — text mentions Figure/Chart/Diagram or has dense math symbols
    """
    text_len = len(text.strip())

    # Boilerplate pages are never worth rendering regardless of other signals
    if is_boilerplate_page(text):
        return "text"

    has_visuals = has_meaningful_raster(fitz_page) or has_vector_diagram(fitz_page)
    has_math = has_dense_math(text)

    if has_visuals or has_math:
        return "vision_primary" if text_len < 100 else "vision_supplement"
    if text_len >= 80:
        return "text"
    return "blank"


# ── Text utilities ─────────────────────────────────────────────────────────────

def clean_page_text(raw: str) -> str:
    text = raw.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    cleaned: list[str] = []
    blank_run = 0
    for line in lines:
        if not line.strip():
            blank_run += 1
            if blank_run <= 2:
                cleaned.append("")
        else:
            blank_run = 0
            cleaned.append(line)
    return "\n".join(cleaned).strip()


def assess_page_quality(text: str) -> dict:
    char_count = len(text.strip())
    if char_count < 50:
        return {"status": "empty", "needs_ocr": True}
    alpha_ratio = sum(c.isalpha() for c in text) / char_count
    if alpha_ratio < 0.40:
        return {"status": "low_quality", "needs_ocr": True}
    return {"status": "ok", "needs_ocr": False}


# ── PNG rendering ──────────────────────────────────────────────────────────────

def save_rendered_png(fitz_page, doc_id: str, page_num: int, dpi: int = RENDER_DPI) -> Path:
    """
    Render a PDF page to PNG and save to rendered_pages/{doc_id}/page_{page_num}.png.
    Returns the path to the saved PNG.
    """
    out_dir = RENDERED_DIR / doc_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"page_{page_num:04d}.png"

    if not out_path.exists():
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = fitz_page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
        pix.save(str(out_path))

    return out_path


# ── doc_id / metadata helpers ──────────────────────────────────────────────────

def compute_doc_id(pdf_path: Path) -> str:
    h = hashlib.sha256()
    with open(pdf_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def derive_title(raw_title: str, pdf_path: Path) -> str:
    title = raw_title.strip()
    if title and len(title) > 2:
        return title
    stem = pdf_path.stem
    cleaned = re.sub(r"[_\-]+", " ", stem).strip()
    return cleaned.title()


def derive_author(raw_author: str) -> Optional[str]:
    author = raw_author.strip()
    if not author or author.lower() in {"", "unknown", "none", "author"}:
        return None
    if re.fullmatch(r"[\d\W]+", author):
        return None
    ascii_ratio = sum(c.isascii() for c in author) / max(len(author), 1)
    if ascii_ratio < 0.6:
        return None
    return author


# ── Core extraction ────────────────────────────────────────────────────────────

def extract_pdf(pdf_path: Path, project_root: Path) -> ParsedDocument:
    doc_id = compute_doc_id(pdf_path)

    with fitz.open(str(pdf_path)) as doc:
        meta = doc.metadata or {}
        book_title = derive_title(meta.get("title", ""), pdf_path)
        author = derive_author(meta.get("author", ""))

        pages: list[PageContent] = []
        vision_page_count = 0
        rendered_pngs: list[str] = []

        # ── Pass 1: classify every page (no rendering yet) ─────────────────────
        page_texts: list[str] = []
        page_modes: list[str] = []
        for i in range(len(doc)):
            fitz_page = doc[i]
            raw_text = fitz_page.get_text("text")
            text = clean_page_text(raw_text)
            mode = classify_page(fitz_page, text)
            page_texts.append(text)
            page_modes.append(mode)

        # ── Pass 2: render PNGs for visual pages and build PageContent objects ──
        for i in range(len(doc)):
            fitz_page = doc[i]
            text = page_texts[i]
            mode = page_modes[i]

            if mode in ("vision_primary", "vision_supplement"):
                png_path = save_rendered_png(fitz_page, doc_id, i + 1)
                rendered_pngs.append(str(png_path))
                vision_page_count += 1

            quality = assess_page_quality(text)

            pages.append(
                PageContent(
                    page_num=i + 1,
                    text=text,
                    char_count=len(text),
                    quality_status=quality["status"],
                    needs_ocr=quality["needs_ocr"],
                    extraction_mode=mode,
                )
            )

    if vision_page_count > 0:
        console.print(
            f"  visual pages: {vision_page_count} — PNGs saved to "
            f"rendered_pages/{doc_id}/\n"
            f"  Run [cyan]/project:process-vision[/cyan] to describe these pages."
        )

    poor_count = sum(1 for p in pages if p.needs_ocr)
    ocr_ratio = poor_count / max(len(pages), 1)
    extraction_quality = "poor" if ocr_ratio > 0.20 else "ok"

    try:
        rel_path = str(pdf_path.relative_to(project_root))
    except ValueError:
        rel_path = str(pdf_path)

    return ParsedDocument(
        doc_id=doc_id,
        book_title=book_title,
        author=author,
        file_path=rel_path,
        file_name=pdf_path.name,
        total_pages=len(pages),
        pages=pages,
        extraction_quality=extraction_quality,
        poor_quality_pages=poor_count,
        vision_pages=vision_page_count,
    )


# ── CLI ────────────────────────────────────────────────────────────────────────

@app.command()
def main(
    doc_id: Optional[str] = typer.Option(None, "--doc-id", help="Process only this doc_id"),
    force: bool = typer.Option(False, "--force", help="Re-extract even if already done"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would run without doing it"),
    books_dir: Path = typer.Option(BOOKS_DIR, "--books-dir"),
    output_dir: Path = typer.Option(PARSED_DIR, "--output-dir"),
) -> None:
    project_root = Path(__file__).parent.parent.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(books_dir.glob("*.pdf"))
    if not pdf_files:
        console.print(f"[yellow]No PDFs found in {books_dir}.[/yellow]")
        raise typer.Exit()

    manifest = manifest_utils.load(MANIFEST_PATH)

    to_process: list[Path] = []
    for pdf in pdf_files:
        did = compute_doc_id(pdf)
        if doc_id and did != doc_id:
            continue
        if not force and manifest_utils.is_done(manifest, did, "extracted"):
            console.print(f"[dim]Skipping {pdf.name} ({did}) — already extracted[/dim]")
            continue
        to_process.append(pdf)

    if not to_process:
        console.print("[green]Nothing to process.[/green]")
        return

    if dry_run:
        console.print(f"[cyan]Dry run — would extract {len(to_process)} file(s):[/cyan]")
        for p in to_process:
            console.print(f"  {p.name}")
        return

    results: list[dict] = []

    for pdf_path in to_process:
        console.print(f"\n[bold]Extracting:[/bold] {pdf_path.name}")
        try:
            parsed = extract_pdf(pdf_path, project_root)
        except Exception as e:
            console.print(f"  [red]ERROR:[/red] {e}")
            did = compute_doc_id(pdf_path)
            manifest_utils.get_or_create(manifest, did, pdf_path.name, pdf_path.stem)
            manifest_utils.add_error(manifest, did, str(e))
            manifest_utils.save(MANIFEST_PATH, manifest)
            results.append({"file": pdf_path.name, "status": "error", "error": str(e)})
            continue

        # Write parsed JSON
        out_path = output_dir / f"{parsed.doc_id}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(parsed.model_dump(mode="json"), f, indent=2, default=str)

        # Update manifest
        manifest_utils.get_or_create(manifest, parsed.doc_id, parsed.file_name, parsed.book_title)
        manifest_utils.update_stats(
            manifest,
            parsed.doc_id,
            {
                "total_pages": parsed.total_pages,
                "poor_quality_pages": parsed.poor_quality_pages,
                "extraction_quality": parsed.extraction_quality,
                "vision_pages": parsed.vision_pages,
            },
        )
        manifest_utils.mark_done(manifest, parsed.doc_id, "extracted")
        manifest_utils.save(MANIFEST_PATH, manifest)

        quality_label = (
            "[red]POOR — may need OCR[/red]"
            if parsed.extraction_quality == "poor"
            else "[green]ok[/green]"
        )
        mode_counts: dict[str, int] = {}
        for p in parsed.pages:
            mode_counts[p.extraction_mode] = mode_counts.get(p.extraction_mode, 0) + 1

        console.print(f"  doc_id:  {parsed.doc_id}")
        console.print(f"  title:   {parsed.book_title}")
        console.print(f"  author:  {parsed.author or 'unknown'}")
        console.print(f"  pages:   {parsed.total_pages}  (poor: {parsed.poor_quality_pages})")
        console.print(f"  quality: {quality_label}")
        console.print(f"  modes:   {mode_counts}")
        console.print(f"  output:  {out_path}")

        if parsed.extraction_quality == "poor":
            console.print(
                f"  [yellow]WARNING: {parsed.poor_quality_pages}/{parsed.total_pages} pages "
                f"flagged as low-quality. Run /project:process-vision to describe visual pages.[/yellow]"
            )

        results.append(
            {
                "file": pdf_path.name,
                "doc_id": parsed.doc_id,
                "title": parsed.book_title,
                "status": "ok",
                "pages": parsed.total_pages,
                "quality": parsed.extraction_quality,
                "vision_pages": parsed.vision_pages,
            }
        )

    # Summary table
    console.print()
    table = Table(title="Extraction Summary", show_lines=True)
    table.add_column("File")
    table.add_column("Status")
    table.add_column("Pages", justify="right")
    table.add_column("Quality")
    table.add_column("Visual", justify="right")
    for r in results:
        status = "[green]ok[/green]" if r["status"] == "ok" else "[red]error[/red]"
        q = r.get("quality", "—")
        q_label = "[red]poor[/red]" if q == "poor" else q
        table.add_row(
            r["file"][:50],
            status,
            str(r.get("pages", "—")),
            q_label,
            str(r.get("vision_pages", 0)),
        )
    console.print(table)

    total_visual = sum(r.get("vision_pages", 0) for r in results if r["status"] == "ok")
    if total_visual > 0:
        console.print(
            f"\n[dim]{total_visual} visual page(s) queued. "
            f"Run [cyan]/project:process-vision[/cyan] to describe them.[/dim]"
        )


if __name__ == "__main__":
    app()
