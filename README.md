# Options Research Brain

A local-first, private knowledge system that ingests options/trading PDF books and produces:

- **Knowledge cards** — structured, typed extractions (concepts, definitions, principles, cautions, mechanisms, strategy ideas, volatility insights)
- **Semantic search** — ask questions across all books via Qdrant vector search
- **Human study notes** — detailed Obsidian vault notes written for deep personal learning
- **Research hypotheses** — testable claims synthesized from cross-book patterns

Everything runs locally. No cloud storage. Raw PDFs stay intact.

---

## Setup

### 1. Install dependencies

```bash
# Recommended: create a virtual environment first
python -m venv .venv && source .venv/bin/activate

pip install -e .
```

### 2. Configure environment

```bash
cp .env.example .env
# Open .env and add your ANTHROPIC_API_KEY
```

Minimum required:
```
ANTHROPIC_API_KEY=sk-ant-...
```

All other values have sensible defaults (see `.env.example`).

### 3. Add books

Drop your PDF books into the `books/` folder:

```
books/
  Options Volatility and Pricing.pdf
  The Bible of Options Strategies.pdf
  ...
```

---

## Running the Pipeline

Run phases in order. Each phase is idempotent — re-running skips already-processed documents.

```bash
# Phase 1 — Extract text from PDFs
python scripts/01_extract.py

# Phase 2 — Chunk documents into sections
python scripts/02_chunk.py

# Phase 3 — Generate knowledge cards (uses Claude API)
python scripts/03_generate_cards.py

# Phase 4 — Index chunks and cards into Qdrant
python scripts/04_index.py

# Phase 5 — Generate research hypotheses (uses Claude API)
python scripts/05_generate_hypotheses.py

# Phase 6 — Export knowledge cards and hypotheses to Obsidian vault
python scripts/06_export_vault.py

# Phase 7 — Generate human study notes in Obsidian vault (uses Claude API)
python scripts/07_generate_study_notes.py
```

### Per-book runs

```bash
python scripts/03_generate_cards.py --doc-id abc123def456
```

### Force reprocess

```bash
python scripts/01_extract.py --force
```

### Dry run (see what would be processed)

```bash
python scripts/02_chunk.py --dry-run
```

---

## Search API

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Then search:

```bash
# Semantic search across knowledge cards
curl "http://localhost:8000/search?q=gamma+risk+near+expiration&collection=cards&top_k=10"

# Filter by book
curl "http://localhost:8000/search?q=implied+volatility+edge&book_title=Options+Volatility"

# Filter by card type
curl "http://localhost:8000/search?q=dealer+hedging&card_type=mechanism"

# Health check
curl http://localhost:8000/health
```

---

## Custom Slash Commands (Claude Code)

If you use Claude Code, these project commands are available:

| Command | What it does |
|---|---|
| `/project:status` | Show processing state for all books |
| `/project:ingest` | Run extract + chunk (no AI, safe) |
| `/project:generate-cards` | Run card generation with cost estimate |
| `/project:index` | Embed and upsert into Qdrant |
| `/project:study-notes` | Generate Obsidian study notes |
| `/project:search <query>` | Search the knowledge base |
| `/project:costs` | Show API usage and estimated costs |

---

## Folder Structure

```
books/               Raw PDFs — never modified
parsed/              Extracted text JSON + manifest.json
chunks/              Chunk arrays per document
cards/               Knowledge card arrays per document
experiments/         Hypothesis files
logs/                api_usage.jsonl (token/cost tracking)
vault/
  Books/<title>/     Study notes (Overview, Summary, Chapters, Concepts, Cheat Sheet)
  Synthesis/         Cross-book synthesis
  cards/             Per-card Obsidian notes
  hypotheses/        Per-hypothesis Obsidian notes
app/                 FastAPI backend
scripts/             Numbered pipeline scripts (01–07)
qdrant_storage/      Local Qdrant vector index
data/                Future ORATS/options data
```

---

## Processing Manifest

`parsed/manifest.json` tracks every document through the pipeline:

```bash
cat parsed/manifest.json | python -m json.tool
```

---

## API Cost Tracking

All Claude API calls are logged to `logs/api_usage.jsonl`. Check costs:

```bash
cat logs/api_usage.jsonl | python -m json.tool
```

Or use `/project:costs` in Claude Code.

---

## Future

- ORATS integration for hypothesis backtesting
- Experiment result storage
- Cross-book synthesis search
