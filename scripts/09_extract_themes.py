#!/usr/bin/env python3
"""
Phase 9: Extract themes from card-to-card edges via graph community detection.

Fully deterministic — no Claude API calls, no hardcoded content.
Title and summary fields are left blank; filled by scripts/09b_name_themes.py.

Algorithm:
  1. Load edges.json; keep edges with confidence ≥ 0.75
  2. Build undirected weighted graph (cards = nodes, edge weight = confidence)
  3. Run greedy modularity community detection (networkx)
  4. Quality-filter each community:
       - min 4 cards
       - min avg edge confidence ≥ 0.77
       - max 30 cards (larger → status=needs_review)
       - min 2 books represented
  5. Collect top tags per community (frequency-ranked)
  6. Write provisional Theme skeletons to themes/themes_raw.json

Usage:
    python scripts/09_extract_themes.py
    python scripts/09_extract_themes.py --dry-run
    python scripts/09_extract_themes.py --force
    python scripts/09_extract_themes.py --edge-conf 0.75 --min-cards 4
"""

from __future__ import annotations

import argparse
import json
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE = Path(__file__).resolve().parent.parent
CARDS_DIR = BASE / "cards"
EDGES_FILE = BASE / "edges" / "edges.json"
THEMES_DIR = BASE / "themes"
THEMES_RAW_OUT = THEMES_DIR / "themes_raw.json"

THEMES_DIR.mkdir(exist_ok=True)

# ── Thresholds ─────────────────────────────────────────────────────────────────
# Calibrated for all-MiniLM-L6-v2 which produces confidence scores in 0.50–0.80 range.
DEFAULT_EDGE_CONF = 0.60        # only use edges above this for clustering
DEFAULT_MIN_CARDS = 3
DEFAULT_MIN_AVG_CONF = 0.62
DEFAULT_MAX_CARDS = 30
DEFAULT_MIN_BOOKS = 2
TOP_TAGS_N = 8                  # number of top tags to store per theme


# ── Helpers ────────────────────────────────────────────────────────────────────

def load_all_cards() -> dict[str, dict]:
    """Return card_id → card dict."""
    cards = {}
    for f in sorted(CARDS_DIR.glob("*.json")):
        if "_error" in f.name:
            continue
        for c in json.loads(f.read_text()):
            cards[c["card_id"]] = c
    return cards


def top_tags(cards: list[dict], n: int) -> list[str]:
    counter: Counter = Counter()
    for c in cards:
        for tag in c.get("tags", []):
            counter[tag] += 1
    return [tag for tag, _ in counter.most_common(n)]


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Extract themes via graph clustering")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--edge-conf", type=float, default=DEFAULT_EDGE_CONF,
                        help=f"Min edge confidence to include (default {DEFAULT_EDGE_CONF})")
    parser.add_argument("--min-cards", type=int, default=DEFAULT_MIN_CARDS)
    parser.add_argument("--min-avg-conf", type=float, default=DEFAULT_MIN_AVG_CONF)
    parser.add_argument("--max-cards", type=int, default=DEFAULT_MAX_CARDS)
    parser.add_argument("--min-books", type=int, default=DEFAULT_MIN_BOOKS)
    args = parser.parse_args()

    if THEMES_RAW_OUT.exists() and not args.force:
        print(f"themes_raw.json already exists. Use --force to regenerate.")
        return

    if not EDGES_FILE.exists():
        raise SystemExit(f"edges.json not found at {EDGES_FILE}. Run 08_generate_edges.py first.")

    try:
        import networkx as nx
        from networkx.algorithms.community import greedy_modularity_communities
    except ImportError:
        raise SystemExit("networkx not installed. Run: pip install networkx")

    # Load
    all_edges = json.loads(EDGES_FILE.read_text())
    card_map = load_all_cards()
    print(f"Loaded {len(all_edges)} total edges, {len(card_map)} cards")

    # Filter edges
    strong_edges = [e for e in all_edges if e["confidence"] >= args.edge_conf]
    print(f"Using {len(strong_edges)} edges with confidence ≥ {args.edge_conf}")

    # Build graph
    G = nx.Graph()
    for e in strong_edges:
        G.add_edge(
            e["from_card_id"],
            e["to_card_id"],
            weight=e["confidence"],
            edge_id=e["edge_id"],
        )

    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Community detection
    communities = list(greedy_modularity_communities(G, weight="weight"))
    print(f"Found {len(communities)} raw communities")

    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    themes = []
    skipped_too_small = 0
    skipped_one_book = 0
    needs_review_count = 0

    for community in sorted(communities, key=len, reverse=True):
        card_ids = list(community)
        n = len(card_ids)

        if n < args.min_cards:
            skipped_too_small += 1
            continue

        # Cards in this community
        community_cards = [card_map[cid] for cid in card_ids if cid in card_map]
        if not community_cards:
            continue

        # Book diversity
        doc_ids = list({c["doc_id"] for c in community_cards})
        if len(doc_ids) < args.min_books:
            skipped_one_book += 1
            continue

        # Edges within this community
        card_set = set(card_ids)
        internal_edges = [
            e for e in strong_edges
            if e["from_card_id"] in card_set and e["to_card_id"] in card_set
        ]
        edge_ids = [e["edge_id"] for e in internal_edges]
        avg_conf = (
            sum(e["confidence"] for e in internal_edges) / len(internal_edges)
            if internal_edges else 0.0
        )

        if avg_conf < args.min_avg_conf:
            # Still include but flag
            status = "needs_review"
            needs_review_reason = f"avg_edge_confidence={avg_conf:.3f} below threshold {args.min_avg_conf}"
            needs_review_count += 1
        elif n > args.max_cards:
            status = "needs_review"
            needs_review_reason = f"cluster too large: {n} cards > max {args.max_cards}"
            needs_review_count += 1
        else:
            status = "provisional"
            needs_review_reason = None

        cluster_top_tags = top_tags(community_cards, TOP_TAGS_N)
        overall_confidence = round(avg_conf, 4)

        theme = {
            "theme_id": str(uuid.uuid4()),
            "title": "",
            "summary": "",
            "source_card_ids": card_ids,
            "source_doc_ids": doc_ids,
            "source_edge_ids": edge_ids,
            "top_tags": cluster_top_tags,
            "avg_edge_confidence": round(avg_conf, 4),
            "card_count": n,
            "book_count": len(doc_ids),
            "confidence": overall_confidence,
            "status": status,
            "needs_review_reason": needs_review_reason,
            "created_at": now_iso,
            "derived_by": "claude-sonnet-4-6",
        }
        themes.append(theme)

    # Sort: provisional first, then needs_review; within each group by card_count desc
    themes.sort(key=lambda t: (t["status"] != "provisional", -t["card_count"]))

    print(f"\n{'─'*50}")
    print(f"Communities processed:  {len(communities)}")
    print(f"Themes kept:            {len(themes)}")
    print(f"  provisional:          {sum(1 for t in themes if t['status'] == 'provisional')}")
    print(f"  needs_review:         {needs_review_count}")
    print(f"Skipped (< {args.min_cards} cards):   {skipped_too_small}")
    print(f"Skipped (< {args.min_books} books):   {skipped_one_book}")
    print(f"\nTheme sizes:")
    for t in themes:
        flag = " [NEEDS_REVIEW]" if t["status"] == "needs_review" else ""
        print(
            f"  {t['card_count']:>3} cards, {t['book_count']} books, "
            f"conf={t['avg_edge_confidence']:.3f} | "
            f"tags: {', '.join(t['top_tags'][:4])}{flag}"
        )

    if not args.dry_run:
        THEMES_RAW_OUT.write_text(json.dumps(themes, indent=2))
        print(f"\nWrote {len(themes)} raw themes → {THEMES_RAW_OUT}")
        print("Next step: run scripts/09b_name_themes.py to add titles and summaries.")
    else:
        print("\n[DRY RUN] — nothing written")


if __name__ == "__main__":
    main()
