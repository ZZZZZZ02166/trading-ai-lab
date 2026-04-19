# Options Research Brain — CLAUDE.md

## What This Project Is

A local-first, private knowledge system that ingests options/trading PDF books and produces:
1. **Machine-usable knowledge**: structured chunks, knowledge cards, Qdrant semantic index
2. **Human-usable study notes**: detailed Obsidian vault notes written for deep personal learning
3. **Research hypotheses**: testable claims synthesized across books, prepared for backtest

Everything is local. No cloud storage. No external databases. PDFs stay intact.

---

## Core Architecture: Layered Pipeline

```
books/*.pdf
  ↓ scripts/01_extract.py      [deterministic — PyMuPDF]
parsed/{doc_id}.json           ← ParsedDocument + quality assessment
  ↓ scripts/02_chunk.py        [deterministic — section heuristics + sliding window]
chunks/{doc_id}.json           ← list[Chunk] (retrieval + summary types)
  ↓ scripts/03_generate_cards.py  [AI — Claude API]
cards/{doc_id}.json            ← list[KnowledgeCard]
  ↓ scripts/04_index.py        [deterministic — embed + Qdrant upsert]
qdrant_storage/                ← local vector index (no Docker)
  ↓ scripts/05_generate_hypotheses.py  [AI — Claude API]
experiments/hypotheses_*.json  ← validated Hypothesis list
  ↓ scripts/06_export_vault.py  [deterministic templates]
vault/cards/ + vault/hypotheses/
  ↓ scripts/07_generate_study_notes.py  [AI — Claude API]
vault/Books/<slug>/            ← human study notes
vault/Synthesis/               ← cross-book synthesis
```

State is tracked in `parsed/manifest.json`. The FastAPI app (`app/`) serves search and retrieval.

---

## Absolute Design Rules

**Never violate these:**

1. **Raw PDFs are sacred.** Never modify, move, or overwrite anything in `books/`. They are the source of truth.

2. **Every artifact must trace back to its source.** Every Chunk, KnowledgeCard, Hypothesis, and vault note must carry `doc_id`, `book_title`, `file_path`, `page_start`, `page_end`. No orphaned data.

3. **Deterministic code for data movement. AI only for interpretation.**
   - Extraction, chunking, embedding, indexing, vault templating = deterministic Python
   - Summarization, card generation, hypothesis synthesis, study notes = Claude API

4. **Idempotent by default. `--force` to override.**
   - Every script checks the manifest before processing. If already done, skip.
   - Never re-process without an explicit `--force` flag.

5. **Disk JSON is the source of truth. Qdrant is a search index.**
   - Cards and hypotheses are served from disk JSON, not Qdrant.
   - If Qdrant is deleted, re-run `04_index.py` and everything is back.
   - Never make Qdrant the only place a record exists.

6. **Don't silence bad data.** If a PDF extracts poorly (>20% low-quality pages), mark it `extraction_quality: "poor"` in the manifest and print a clear warning. Don't proceed silently with garbage text.

7. **One phase at a time.** Do not implement Phase 3 before Phase 1 is verified working. Each phase leaves the system in a runnable, inspectable state.

8. **Temperature 0 for card generation** (deterministic fact extraction). Temperature 0.3 for study notes (educational writing). Never use high temperature for structured JSON outputs.

---

## Folder Layout

```
trading-ai-lab/
├── books/               # Raw PDFs — NEVER MODIFY
├── parsed/              # ParsedDocument JSON + manifest.json
├── chunks/              # Chunk JSON arrays (per-doc)
├── cards/               # KnowledgeCard JSON arrays (per-doc) + error logs
├── experiments/         # Hypothesis JSON files + rejected_hypotheses.jsonl
├── logs/                # api_usage.jsonl (token/cost tracking)
├── vault/
│   ├── Books/<slug>/    # Per-book study notes (Overview, Summary, Chapters, Concepts, Cheat Sheet)
│   ├── Synthesis/       # Cross-book synthesis notes
│   ├── cards/           # Per-card Obsidian notes
│   └── hypotheses/      # Per-hypothesis Obsidian notes
├── app/
│   ├── main.py
│   ├── dependencies.py
│   ├── models/          # Pydantic schemas (ParsedDocument, Chunk, KnowledgeCard, Hypothesis)
│   ├── routers/         # search.py, cards.py, hypotheses.py
│   └── services/        # embed_service.py, qdrant_service.py
├── scripts/             # 01_ through 07_ numbered pipeline scripts
├── data/                # Future ORATS/options data
├── qdrant_storage/      # Local Qdrant persistence
├── .env                 # Real secrets — never commit
├── .env.example         # Template — always keep updated
├── pyproject.toml
└── README.md
```

---

## Data Models (Quick Reference)

All Pydantic models live in `app/models/`. Scripts import from there.

### ParsedDocument (`app/models/parsed_document.py`)
Key fields: `doc_id` (sha256[:12] of file bytes), `book_title`, `author`, `file_path`, `total_pages`, `pages: list[PageContent]`, `extraction_quality: "ok"|"poor"`, `poor_quality_pages: int`

### Chunk (`app/models/chunk.py`)
Key fields: `chunk_id` (uuid4), `doc_id`, `book_title`, `author`, `file_path`, `page_start`, `page_end`, `chunk_index`, `chunk_type: "retrieval"|"summary"`, `section_hint`, `strategy: "section_break"|"sliding_window"`, `text`, `char_count`

### KnowledgeCard (`app/models/knowledge_card.py`)
Key fields: `card_id` (uuid4), `chunk_id`, `doc_id`, `book_title`, `author`, `file_path`, `page_ref` (human-readable), `page_start`, `page_end`, `card_type` (enum), `title`, `body`, `tags: list[str]`, `created_at`, `model_used`

Card types: `concept | definition | principle | caution | mechanism | strategy_idea | volatility_insight | market_structure_insight`

### Hypothesis (`app/models/hypothesis.py`)
Key fields: `hypothesis_id` (uuid4), `source_card_ids`, `source_doc_ids`, `title`, `claim`, `rationale`, `testability_notes`, `tags`, `created_at`, `model_used`

---

## Processing Manifest

`parsed/manifest.json` tracks every document through the pipeline.

Per-document entry includes:
- `status`: dict of booleans — `extracted`, `chunked`, `cards_generated`, `indexed`, `study_notes_generated`, `hypotheses_generated`, `vault_exported`
- `stats`: page counts, quality flags, chunk counts, card counts, error counts
- `timestamps`: ISO timestamps per phase completion
- `errors`: list of error strings

All scripts update this file atomically. Read it to understand what has been processed.

---

## Chunking Strategy

Two chunk types per document:
- **`retrieval` chunks**: 400–1000 chars, optimized for embedding + precise recall
- **`summary` chunks**: 1000–3000 chars, one per section, used for study note generation

**Primary**: section-aware detection (ALL CAPS headings, numbered headings, title-case short lines)
**Fallback**: sliding window (800 chars, 150 overlap) — only when < 3 section breaks detected in whole document

Retrieval chunks are derived from summary chunks by splitting at ≤ 1000 chars with 150 char overlap.

---

## Qdrant Collections

Two collections: `chunks` (embed `chunk.text`) and `cards` (embed `title + "\n\n" + body`)

Vector size is auto-detected from `embed_service.vector_size`. Default model: `sentence-transformers/all-MiniLM-L6-v2` (local, 384-dim, no API key needed).

Payload indexes on: `book_title`, `card_type`, `tags`, `doc_id`, `chunk_type`

Upsert is idempotent. Qdrant is a search layer only — disk JSON is authoritative.

---

## API Usage Logging

Every Claude API call is logged to `logs/api_usage.jsonl`:
```json
{"timestamp": "...", "doc_id": "...", "script": "03_generate_cards", "model": "claude-sonnet-4-6", "input_tokens": 1200, "output_tokens": 400, "estimated_cost_usd": 0.0096}
```

Cost estimate: input * $0.000003 + output * $0.000015 (Sonnet pricing, approximate).
Each script prints a run summary: total tokens + estimated cost.

---

## Script CLI Flags (All Scripts)

- `--doc-id <id>` — process only one document
- `--force` — reprocess even if manifest says already done
- `--dry-run` — show what would run without executing
- `--books-dir` / `--parsed-dir` etc. — override .env paths

---

## Hypothesis Quality Gate

Hypotheses are validated before being written. A hypothesis is rejected if:
- `claim` contains no measurable variable (IV, delta, price, spread, return, vol)
- `claim` contains no conditional or causal language (when/if/under/causes/predicts/correlates)
- `testability_notes` is < 50 chars or doesn't reference a data source or falsification method

Rejected hypotheses go to `experiments/rejected_hypotheses.jsonl` with rejection reason.

---

## Study Notes Vault Structure

```
vault/Books/<book-slug>/
  00 Overview.md            # What book is about, themes, key takeaways
  01 Detailed Summary.md    # Deep, educational summary — not shallow
  Chapters/<chapter>.md     # Summary, concepts, lessons, warnings, connections
  Concepts/<concept>.md     # Definition, why it matters, common mistakes, page refs
  Cheat Sheet.md            # Quick-review: most important concepts + warnings

vault/Synthesis/
  Cross-Book Synthesis.md   # Agreement, contradictions, best explanations per topic
```

Study notes are written in clear, educational English. Difficulty is explained simply without losing accuracy. Source page references are included wherever possible. No invented content.

---

## Environment Variables

See `.env.example` for full list. Key vars:

```
ANTHROPIC_API_KEY       Required for card generation, hypotheses, study notes
EMBEDDING_MODEL         Default: sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL               Default: claude-sonnet-4-6
QDRANT_PATH             Default: ./qdrant_storage
```

---

## Running the Pipeline

```bash
# Setup
cp .env.example .env && vim .env   # add ANTHROPIC_API_KEY
pip install -e .

# Drop PDFs in books/

# Run pipeline phases in order
python scripts/01_extract.py       # PDF → parsed JSON + manifest
python scripts/02_chunk.py         # parsed → chunks
python scripts/03_generate_cards.py  # chunks → knowledge cards (uses Claude API)
python scripts/04_index.py         # chunks + cards → Qdrant
python scripts/05_generate_hypotheses.py  # cards → hypotheses (uses Claude API)
python scripts/06_export_vault.py  # cards + hypotheses → vault markdown
python scripts/07_generate_study_notes.py  # books → human study notes (uses Claude API)

# Start search API
uvicorn app.main:app --reload

# Per-book run
python scripts/03_generate_cards.py --doc-id abc123def456

# Check status
cat parsed/manifest.json | python -m json.tool
```

---

## What NOT to Do

- Do not add features not asked for. Bug fix = bug fix. Feature = feature.
- Do not refactor code in files you are not already editing.
- Do not add docstrings or comments to unchanged code.
- Do not make Qdrant the source of truth — it is a search index only.
- Do not use high temperature for structured JSON outputs (card generation).
- Do not silently continue with poor-quality PDF extractions.
- Do not implement Phase N+1 before Phase N is verified working.
- Do not create helpers or abstractions for one-time operations.
- Do not invent content not present in source PDFs. AI prompts must be grounded in source text.

---

## Future Phases (Not Yet Built)

- `scripts/08_backtest_prep.py` — translate hypotheses to ORATS query format
- ORATS client integration
- Experiment result storage + vault notes
- Optional graph visualization
