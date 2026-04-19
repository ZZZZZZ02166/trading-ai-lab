#!/usr/bin/env python3
"""
Phase 5: Generate testable hypotheses from knowledge cards.

Groups cards by theme, prioritises cross-book card clusters, calls the
Claude API to synthesise hypotheses, validates each against the quality
gate defined in CLAUDE.md, and writes results to disk.

Usage:
    python scripts/05_generate_hypotheses.py
    python scripts/05_generate_hypotheses.py --doc-id <id>   # one book only
    python scripts/05_generate_hypotheses.py --dry-run
    python scripts/05_generate_hypotheses.py --force
"""

from __future__ import annotations

import argparse
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
CARDS_DIR = BASE / "cards"
EXPERIMENTS_DIR = BASE / "experiments"
LOGS_DIR = BASE / "logs"
MANIFEST_PATH = BASE / "parsed/manifest.json"

EXPERIMENTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")

# ── Quality gate (from CLAUDE.md) ─────────────────────────────────────────────
MEASURABLE_VARS = ["iv", "implied volatility", "delta", "gamma", "vega", "theta",
                   "price", "spread", "return", "vol", "volatility", "sharpe",
                   "premium", "skew", "term structure", "realized", "garch"]
CONDITIONAL_WORDS = ["when", "if", "under", "causes", "predicts", "correlates",
                     "increases", "decreases", "higher", "lower", "above", "below"]
MIN_TESTABILITY_CHARS = 50

# ── Theme clusters: each cluster drives one API batch ─────────────────────────
# tag sets — cards matching ANY of these tags are candidates for the cluster
THEME_CLUSTERS = [
    {
        "name": "variance_premium_and_vol_selling_edge",
        "description": "When and why selling implied volatility has positive expected value",
        "tags": ["variance-premium", "implied-volatility", "realized-volatility",
                 "vol-selling", "straddle", "short-gamma"],
    },
    {
        "name": "gamma_theta_tradeoff_and_hedging",
        "description": "The structural gamma-theta tradeoff and how to manage it",
        "tags": ["gamma", "theta", "gamma-theta", "delta-hedging", "rebalancing",
                 "short-gamma", "long-gamma"],
    },
    {
        "name": "volatility_forecasting_and_trade_entry",
        "description": "Using GARCH, vol cones, and estimators to time vol trades",
        "tags": ["garch", "volatility-forecasting", "volatility-cone",
                 "historical-volatility", "estimators", "yang-zhang"],
    },
    {
        "name": "iv_skew_and_term_structure",
        "description": "Trading the shape and dynamics of the IV surface",
        "tags": ["skew", "term-structure", "iv-surface", "calendar-spread",
                 "sticky-strike", "sticky-delta", "forward-vol"],
    },
    {
        "name": "earnings_and_event_volatility",
        "description": "IV behaviour around earnings and discrete events",
        "tags": ["earnings", "event-vol", "iv-crush", "straddle", "vega"],
    },
    {
        "name": "position_sizing_and_kelly",
        "description": "Optimal position sizing for volatility strategies",
        "tags": ["kelly-criterion", "position-sizing", "fractional-kelly",
                 "money-management", "bankroll", "drawdown"],
    },
    {
        "name": "transaction_costs_and_hedging_efficiency",
        "description": "How transaction costs constrain hedging frequency and profitability",
        "tags": ["transaction-costs", "hedging-bands", "bid-ask",
                 "market-impact", "zakamouline", "whalley-wilmott"],
    },
    {
        "name": "vix_and_index_vol_structure",
        "description": "VIX dynamics, contango, and index vol vs individual stocks",
        "tags": ["vix", "vix-futures", "contango", "vxx", "roll-decay",
                 "equity-index", "variance-premium"],
    },
    {
        "name": "fat_tails_and_tail_risk",
        "description": "Fat-tail distributions and their consequences for option selling",
        "tags": ["fat-tails", "kurtosis", "tail-risk", "black-swan",
                 "jump-risk", "leverage-effect"],
    },
    {
        "name": "vol_measurement_and_regime",
        "description": "How measured volatility varies across regimes and what that implies",
        "tags": ["volatility-clustering", "mean-reversion", "regime",
                 "bull-bear-regime", "stylized-facts", "log-normal"],
    },
    {
        "name": "market_making_and_edge",
        "description": "How market makers extract edge and what that means for takers",
        "tags": ["market-making", "bid-ask", "edge", "spread", "inventory-risk",
                 "adverse-selection"],
    },
    {
        "name": "pnl_distribution_and_path_dependency",
        "description": "The statistical properties of hedged vol positions over time",
        "tags": ["pnl", "path-dependency", "dispersion", "sampling-risk",
                 "discrete-hedging", "realized-vol"],
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_all_cards(doc_id_filter: str | None = None) -> list[dict]:
    cards = []
    for f in sorted(CARDS_DIR.glob("*.json")):
        if "_error" in f.name:
            continue
        data = json.loads(f.read_text())
        if doc_id_filter:
            data = [c for c in data if c["doc_id"] == doc_id_filter]
        cards.extend(data)
    return cards


def cards_for_cluster(all_cards: list[dict], cluster: dict, max_per_book: int = 3) -> list[dict]:
    """Return up to max_per_book cards per book that match any cluster tag."""
    tag_set = {t.lower() for t in cluster["tags"]}
    matched: dict[str, list[dict]] = {}  # doc_id → cards
    for c in all_cards:
        card_tags = {t.lower() for t in c.get("tags", [])}
        if card_tags & tag_set:
            matched.setdefault(c["doc_id"], []).append(c)
    # Cap per book, prefer variety across books
    result = []
    for doc_id, doc_cards in matched.items():
        result.extend(doc_cards[:max_per_book])
    # Prefer cross-book clusters (skip if only 1 book)
    unique_books = {c["doc_id"] for c in result}
    return result, unique_books


def format_cards_for_prompt(cards: list[dict]) -> str:
    lines = []
    for i, c in enumerate(cards, 1):
        lines.append(
            f"[{i}] card_id={c['card_id']}\n"
            f"    book: {c['book_title']}\n"
            f"    type: {c['card_type']}\n"
            f"    title: {c['title']}\n"
            f"    body: {c['body']}\n"
            f"    tags: {c['tags']}\n"
        )
    return "\n".join(lines)


def call_claude(client: anthropic.Anthropic, cluster: dict, cards: list[dict]) -> tuple[list[dict], int, int]:
    """Call Claude and return (raw_hypotheses, input_tokens, output_tokens)."""
    card_text = format_cards_for_prompt(cards)
    card_ids = [c["card_id"] for c in cards]
    doc_ids = list({c["doc_id"] for c in cards})

    system = (
        "You are a quantitative options research analyst. "
        "Your task is to synthesise testable trading hypotheses from a set of knowledge cards. "
        "Each hypothesis must be grounded in the card content — no invented claims. "
        "Return a JSON array only. No prose before or after the JSON."
    )

    user = f"""Cluster theme: {cluster['description']}

Knowledge cards:
{card_text}

Generate 3–5 testable hypotheses. Each hypothesis must:
1. Have a measurable variable (IV, delta, vol, spread, return, Sharpe, gamma, vega, premium, skew)
2. Use conditional or causal language (when / if / under / causes / predicts / correlates / increases / decreases)
3. Be falsifiable — testability_notes must name a data source and a falsification condition
4. Synthesise insights from at least 2 different books where possible

Return a JSON array with this exact schema per element:
{{
  "title": "Short descriptive title (≤12 words)",
  "claim": "The core testable claim in 1–3 sentences. Must contain a measurable variable and conditional language.",
  "rationale": "Why the source cards support this claim (3–6 sentences). Name the books and concepts.",
  "testability_notes": "How to test or falsify this claim. Name the data source (e.g. ORATS, CBOE, daily returns), the backtest window, and what outcome would falsify the claim.",
  "tags": ["tag1", "tag2"],
  "source_card_ids": {json.dumps(card_ids)},
  "source_doc_ids": {json.dumps(doc_ids)}
}}

Return only the JSON array. No other text."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        temperature=0,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    hypotheses = json.loads(raw)
    return hypotheses, response.usage.input_tokens, response.usage.output_tokens


def validate_hypothesis(h: dict) -> tuple[bool, str]:
    """Return (is_valid, rejection_reason)."""
    claim = h.get("claim", "").lower()
    testability = h.get("testability_notes", "")
    title = h.get("title", "").strip()

    if not title:
        return False, "Empty title"

    has_measurable = any(v in claim for v in MEASURABLE_VARS)
    if not has_measurable:
        return False, f"Claim contains no measurable variable. Claim: {claim[:100]}"

    has_conditional = any(w in claim for w in CONDITIONAL_WORDS)
    if not has_conditional:
        return False, f"Claim contains no conditional/causal language. Claim: {claim[:100]}"

    if len(testability) < MIN_TESTABILITY_CHARS:
        return False, f"testability_notes too short ({len(testability)} chars)"

    data_keywords = ["orats", "cboe", "data", "backtest", "historical", "sample",
                     "returns", "daily", "weekly", "monthly", "years", "period"]
    has_data_ref = any(k in testability.lower() for k in data_keywords)
    if not has_data_ref:
        return False, f"testability_notes does not reference a data source"

    return True, ""


def log_usage(doc_id: str, cluster_name: str, input_tokens: int, output_tokens: int):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "doc_id": doc_id or "all",
        "script": "05_generate_hypotheses",
        "cluster": cluster_name,
        "model": MODEL,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(input_tokens * 0.000003 + output_tokens * 0.000015, 6),
    }
    with open(LOGS_DIR / "api_usage.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")


def update_manifest(processed_doc_ids: list[str]):
    manifest = json.loads(MANIFEST_PATH.read_text())
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    for doc_id in processed_doc_ids:
        if doc_id in manifest:
            manifest[doc_id].setdefault("status", {})["hypotheses_generated"] = True
            manifest[doc_id].setdefault("timestamps", {})["hypotheses_generated"] = now
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate hypotheses from knowledge cards")
    parser.add_argument("--doc-id", help="Process cards for a single document only")
    parser.add_argument("--dry-run", action="store_true", help="Show what would run, no API calls")
    parser.add_argument("--force", action="store_true", help="Re-run even if already done")
    parser.add_argument("--no-synthesis", action="store_true", help="Skip automatic theme synthesis trigger after completion")
    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY not set in environment")

    client = anthropic.Anthropic(api_key=api_key)

    # Load cards
    all_cards = load_all_cards(doc_id_filter=args.doc_id)
    print(f"Loaded {len(all_cards)} cards from {len({c['doc_id'] for c in all_cards})} books")

    if not all_cards:
        print("No cards found — nothing to process.")
        return

    valid_hypotheses: list[dict] = []
    rejected_hypotheses: list[dict] = []

    total_input_tokens = 0
    total_output_tokens = 0

    for cluster in THEME_CLUSTERS:
        cards, unique_books = cards_for_cluster(all_cards, cluster)

        if not cards:
            print(f"  [{cluster['name']}] No matching cards — skipping")
            continue

        if len(unique_books) < 2 and not args.doc_id:
            print(f"  [{cluster['name']}] Only 1 book matched ({len(cards)} cards) — skipping (prefer cross-book)")
            continue

        print(f"  [{cluster['name']}] {len(cards)} cards from {len(unique_books)} books", end="")

        if args.dry_run:
            print(" [DRY RUN]")
            continue

        print(" — calling API...")

        try:
            raw_hyps, in_tok, out_tok = call_claude(client, cluster, cards)
        except Exception as e:
            print(f"    ERROR calling API: {e}")
            continue

        total_input_tokens += in_tok
        total_output_tokens += out_tok
        log_usage(args.doc_id, cluster["name"], in_tok, out_tok)

        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        for h in raw_hyps:
            is_valid, reason = validate_hypothesis(h)

            hypothesis_record = {
                "hypothesis_id": str(uuid.uuid4()),
                "source_card_ids": h.get("source_card_ids", [c["card_id"] for c in cards]),
                "source_doc_ids": h.get("source_doc_ids", list({c["doc_id"] for c in cards})),
                "title": h.get("title", ""),
                "claim": h.get("claim", ""),
                "rationale": h.get("rationale", ""),
                "testability_notes": h.get("testability_notes", ""),
                "tags": h.get("tags", []),
                "created_at": now_iso,
                "model_used": MODEL,
            }

            if is_valid:
                valid_hypotheses.append(hypothesis_record)
                print(f"    ✓ {hypothesis_record['title']}")
            else:
                hypothesis_record["rejection_reason"] = reason
                rejected_hypotheses.append(hypothesis_record)
                print(f"    ✗ REJECTED: {reason[:80]}")

    # Write valid hypotheses
    if valid_hypotheses:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_path = EXPERIMENTS_DIR / f"hypotheses_{ts}.json"
        out_path.write_text(json.dumps(valid_hypotheses, indent=2, default=str))
        print(f"\nWrote {len(valid_hypotheses)} hypotheses → {out_path}")

    # Write rejected hypotheses (append)
    if rejected_hypotheses:
        reject_path = EXPERIMENTS_DIR / "rejected_hypotheses.jsonl"
        with open(reject_path, "a") as f:
            for h in rejected_hypotheses:
                f.write(json.dumps(h, default=str) + "\n")
        print(f"Wrote {len(rejected_hypotheses)} rejected → {reject_path}")

    # Update manifest
    processed_doc_ids = list({c["doc_id"] for c in all_cards})
    if not args.dry_run:
        update_manifest(processed_doc_ids)

    # Summary
    est_cost = total_input_tokens * 0.000003 + total_output_tokens * 0.000015
    print(f"\n{'─'*50}")
    print(f"Total: {len(valid_hypotheses)} valid, {len(rejected_hypotheses)} rejected")
    print(f"Tokens: {total_input_tokens:,} in / {total_output_tokens:,} out")
    print(f"Estimated cost: ${est_cost:.4f}")

    if not args.dry_run and not args.no_synthesis:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location("ts", Path(__file__).parent / "19_run_theme_synthesis.py")
        _ts = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_ts)
        _ts.auto_trigger_synthesis("05_generate_hypotheses: new hypotheses generated")


if __name__ == "__main__":
    main()
