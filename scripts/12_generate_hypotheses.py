#!/usr/bin/env python3
"""
Phase 12: Hypothesis generation from themes and meta-themes.

Claude reasoning step — reads themes.json, meta_themes.json, and selected cards,
then writes hypotheses to experiments/hypotheses.json.

This script reads and validates hypotheses from experiments/hypotheses_input.json
(the hand-curated or Claude-generated input file), applies the quality gate,
and writes passing hypotheses to experiments/hypotheses.json.

To add hypotheses: edit experiments/hypotheses_input.json, then run this script.

Quality gate (a hypothesis is rejected if):
  - claim contains no measurable variable (IV, delta, vol, price, return, spread, gamma, vega, theta)
  - claim contains no conditional/causal language (when/if/under/causes/predicts/correlates/increases/decreases)
  - testability_notes < 50 chars or no data source reference
  - title is empty

Usage:
    python scripts/12_generate_hypotheses.py
    python scripts/12_generate_hypotheses.py --force
"""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
EXPERIMENTS_DIR = BASE / "experiments"
INPUT_FILE = EXPERIMENTS_DIR / "hypotheses_input.json"
OUTPUT_FILE = EXPERIMENTS_DIR / "hypotheses.json"
REJECTED_FILE = EXPERIMENTS_DIR / "rejected_hypotheses.jsonl"

EXPERIMENTS_DIR.mkdir(exist_ok=True)

# ── Quality gate ──────────────────────────────────────────────────────────────
MEASURABLE = ["iv", "implied volatility", "delta", "gamma", "vega", "theta",
              "price", "spread", "return", "vol", "volatility", "sharpe",
              "premium", "skew", "term structure", "realized", "garch",
              "variance", "confidence", "edge", "drawdown", "kelly"]
CONDITIONAL = ["when", "if", "under", "causes", "predicts", "correlates",
               "increases", "decreases", "higher", "lower", "above", "below",
               "exceeds", "falls", "rises", "narrows", "widens"]
DATA_KEYWORDS = ["orats", "cboe", "data", "backtest", "historical", "sample",
                 "returns", "daily", "weekly", "monthly", "years", "period",
                 "dataset", "series", "prices", "options"]
MIN_TESTABILITY_CHARS = 50


def validate(h: dict) -> tuple[bool, str]:
    claim = h.get("claim", "").lower()
    testability = h.get("testability_notes", "")
    title = h.get("title", "").strip()

    if not title:
        return False, "Empty title"
    if not any(v in claim for v in MEASURABLE):
        return False, f"Claim has no measurable variable. Claim: {claim[:100]}"
    if not any(w in claim for w in CONDITIONAL):
        return False, f"Claim has no conditional language. Claim: {claim[:100]}"
    if len(testability) < MIN_TESTABILITY_CHARS:
        return False, f"testability_notes too short ({len(testability)} chars)"
    if not any(k in testability.lower() for k in DATA_KEYWORDS):
        return False, "testability_notes has no data source reference"
    return True, ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Overwrite existing hypotheses.json")
    parser.add_argument("--no-synthesis", action="store_true", help="Skip automatic theme synthesis trigger after completion")
    args = parser.parse_args()

    if OUTPUT_FILE.exists() and not args.force:
        existing = json.loads(OUTPUT_FILE.read_text())
        print(f"hypotheses.json exists with {len(existing)} hypotheses. Use --force to regenerate.")
        return

    if not INPUT_FILE.exists():
        raise SystemExit(
            f"hypotheses_input.json not found at {INPUT_FILE}.\n"
            "Create it with raw hypothesis dicts, then run this script to validate and write."
        )

    raw = json.loads(INPUT_FILE.read_text())
    print(f"Loaded {len(raw)} raw hypotheses from input file")

    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    valid, rejected = [], []

    for h in raw:
        record = {
            "hypothesis_id": h.get("hypothesis_id") or str(uuid.uuid4()),
            "title": h.get("title", ""),
            "claim": h.get("claim", ""),
            "rationale": h.get("rationale", ""),
            "testability_notes": h.get("testability_notes", ""),
            "variables_needed": h.get("variables_needed", []),
            "data_required": h.get("data_required", ""),
            "what_would_support": h.get("what_would_support", ""),
            "what_would_reject": h.get("what_would_reject", ""),
            "source_card_ids": h.get("source_card_ids", []),
            "source_theme_ids": h.get("source_theme_ids", []),
            "source_meta_theme_ids": h.get("source_meta_theme_ids", []),
            "source_doc_ids": h.get("source_doc_ids", []),
            "tags": h.get("tags", []),
            "confidence": h.get("confidence", 0.0),
            "status": h.get("status", "candidate"),
            "created_at": now_iso,
            "model_used": "claude-sonnet-4-6",
        }

        ok, reason = validate(record)
        if ok:
            valid.append(record)
            print(f"  ✓ {record['title']}")
        else:
            record["rejection_reason"] = reason
            rejected.append(record)
            print(f"  ✗ REJECTED: {reason[:80]}")

    OUTPUT_FILE.write_text(json.dumps(valid, indent=2))
    print(f"\nWrote {len(valid)} hypotheses → {OUTPUT_FILE}")

    if rejected:
        with open(REJECTED_FILE, "a") as f:
            for h in rejected:
                f.write(json.dumps(h) + "\n")
        print(f"Wrote {len(rejected)} rejected → {REJECTED_FILE}")

    if not args.no_synthesis:
        import importlib.util as _ilu, sys as _sys
        _spec = _ilu.spec_from_file_location("ts", Path(__file__).parent / "19_run_theme_synthesis.py")
        _ts = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_ts)
        _ts.auto_trigger_synthesis("12_generate_hypotheses: hypotheses validated")


if __name__ == "__main__":
    main()
