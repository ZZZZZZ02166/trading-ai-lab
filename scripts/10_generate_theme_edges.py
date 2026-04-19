#!/usr/bin/env python3
"""
Phase 10: Generate theme-to-theme edges using multi-signal composite scoring.

Fully deterministic — no Claude API calls, no hardcoded content.

Composite score weights:
  0.35  shared_top_tags       Jaccard on top_tags lists
  0.30  cross_theme_edge_count  edges linking cards across the two themes (normalised)
  0.25  centroid_cosine       cosine between embedding centroids of member cards
  0.10  card_overlap_jaccard  Jaccard on source_card_ids (secondary)

Relation type assignment:
  composite ≥ 0.55  →  merge_candidate_for
  0.35–0.55         →  overlaps_with
  one theme's top_tags ⊂ other's → parent_of / child_of
  < 0.20            →  skip (no edge)

Usage:
    python scripts/10_generate_theme_edges.py
    python scripts/10_generate_theme_edges.py --dry-run
    python scripts/10_generate_theme_edges.py --force
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from dotenv import load_dotenv

load_dotenv()

THEMES_FILE = BASE / "themes" / "themes.json"
EDGES_FILE = BASE / "edges" / "edges.json"
THEME_EDGES_DIR = BASE / "theme_edges"
THEME_EDGES_OUT = THEME_EDGES_DIR / "theme_edges.json"
QDRANT_PATH = str(BASE / "qdrant_storage")

THEME_EDGES_DIR.mkdir(exist_ok=True)

# ── Thresholds ────────────────────────────────────────────────────────────────
SKIP_BELOW = 0.20
OVERLAPS_MIN = 0.35
MERGE_MIN = 0.55

# Weights
W_TAG = 0.35
W_EDGE = 0.30
W_CENTROID = 0.25
W_CARD = 0.10

# Max cross-theme edge count for normalisation (edges beyond this give full score)
EDGE_NORM_CAP = 10

COLLECTION = "cards"
EMBED_BATCH = 32


# ── Helpers ───────────────────────────────────────────────────────────────────

def jaccard(a: list, b: list) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def assign_relation_type(
    composite: float,
    tags_a: list[str],
    tags_b: list[str],
) -> str:
    set_a, set_b = set(tags_a), set(tags_b)
    if set_a and set_b:
        if set_a < set_b:           # a's tags are strict subset of b's
            return "child_of"
        if set_b < set_a:           # b's tags are strict subset of a's
            return "parent_of"
    if composite >= MERGE_MIN:
        return "merge_candidate_for"
    return "overlaps_with"


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate theme-to-theme edges")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if THEME_EDGES_OUT.exists() and not args.force:
        print(f"theme_edges.json already exists. Use --force to regenerate.")
        return

    if not THEMES_FILE.exists():
        raise SystemExit(f"themes.json not found. Run 09_extract_themes.py + naming step first.")
    if not EDGES_FILE.exists():
        raise SystemExit(f"edges.json not found. Run 08_generate_edges.py first.")

    themes = json.loads(THEMES_FILE.read_text())
    all_edges = json.loads(EDGES_FILE.read_text())
    print(f"Loaded {len(themes)} themes, {len(all_edges)} card edges")

    # Build cross-theme edge lookup: (theme_id_a, theme_id_b) → count
    # Build card_id → theme_id map
    card_to_theme: dict[str, str] = {}
    for t in themes:
        for cid in t["source_card_ids"]:
            card_to_theme[cid] = t["theme_id"]

    # Count cross-theme edges
    from collections import defaultdict
    cross_edge_counts: dict[tuple[str, str], int] = defaultdict(int)
    for e in all_edges:
        ta = card_to_theme.get(e["from_card_id"])
        tb = card_to_theme.get(e["to_card_id"])
        if ta and tb and ta != tb:
            key = (min(ta, tb), max(ta, tb))
            cross_edge_counts[key] += 1

    # Retrieve card embeddings from Qdrant → compute theme centroids
    print("Loading embedding model and retrieving card vectors from Qdrant...")
    from app.services.embed_service import EmbedService
    from qdrant_client import QdrantClient

    embed_svc = EmbedService()
    client = QdrantClient(path=QDRANT_PATH)

    # Collect all card texts for all themes, embed in one batch
    all_theme_cards: list[dict] = []
    card_json_map: dict[str, dict] = {}
    import glob
    cards_dir = BASE / "cards"
    for f in sorted(cards_dir.glob("*.json")):
        if "_error" not in f.name:
            for c in json.loads(f.read_text()):
                card_json_map[c["card_id"]] = c

    # Get the unique card_ids needed across all themes
    needed_card_ids = set()
    for t in themes:
        needed_card_ids.update(t["source_card_ids"])

    needed_cards = [card_json_map[cid] for cid in needed_card_ids if cid in card_json_map]
    texts = [f"{c['title']}\n\n{c['body']}" for c in needed_cards]
    print(f"Embedding {len(needed_cards)} cards for centroid computation...")
    vecs = embed_svc.embed(texts, batch_size=EMBED_BATCH)
    card_vec_map: dict[str, np.ndarray] = {
        c["card_id"]: np.array(v) for c, v in zip(needed_cards, vecs)
    }
    print("Done.")

    # Compute centroids per theme
    theme_centroid: dict[str, np.ndarray] = {}
    for t in themes:
        vecs_for_theme = [card_vec_map[cid] for cid in t["source_card_ids"] if cid in card_vec_map]
        if vecs_for_theme:
            theme_centroid[t["theme_id"]] = np.mean(vecs_for_theme, axis=0)

    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    theme_edges = []
    skipped = 0

    for t_a, t_b in combinations(themes, 2):
        id_a, id_b = t_a["theme_id"], t_b["theme_id"]

        # Signal 1: shared top tags (Jaccard)
        tag_score = jaccard(t_a["top_tags"], t_b["top_tags"])

        # Signal 2: cross-theme edge count (normalised)
        key = (min(id_a, id_b), max(id_a, id_b))
        cross_count = cross_edge_counts.get(key, 0)
        edge_score = min(cross_count / EDGE_NORM_CAP, 1.0)

        # Signal 3: centroid cosine similarity
        cent_a = theme_centroid.get(id_a)
        cent_b = theme_centroid.get(id_b)
        centroid_score = cosine_sim(cent_a, cent_b) if cent_a is not None and cent_b is not None else 0.0

        # Signal 4: card overlap Jaccard (secondary)
        card_jaccard = jaccard(t_a["source_card_ids"], t_b["source_card_ids"])

        composite = (
            W_TAG * tag_score
            + W_EDGE * edge_score
            + W_CENTROID * centroid_score
            + W_CARD * card_jaccard
        )

        if composite < SKIP_BELOW:
            skipped += 1
            continue

        relation = assign_relation_type(composite, t_a["top_tags"], t_b["top_tags"])
        confidence = round(composite, 4)

        reason = (
            f"tag_jaccard={tag_score:.3f}, cross_edges={cross_count}, "
            f"centroid_cosine={centroid_score:.3f}, card_jaccard={card_jaccard:.3f}"
        )

        edge = {
            "theme_edge_id": str(uuid.uuid4()),
            "from_theme_id": id_a,
            "to_theme_id": id_b,
            "from_theme_title": t_a["title"],
            "to_theme_title": t_b["title"],
            "relation_type": relation,
            "confidence": confidence,
            "shared_tag_score": round(tag_score, 4),
            "cross_edge_count": cross_count,
            "centroid_cosine": round(centroid_score, 4),
            "card_overlap_jaccard": round(card_jaccard, 4),
            "reason": reason,
            "created_at": now_iso,
            "derived_by": "claude-sonnet-4-6",
        }
        theme_edges.append(edge)

    # Sort by confidence descending
    theme_edges.sort(key=lambda e: e["confidence"], reverse=True)

    print(f"\n{'─'*50}")
    print(f"Theme pairs evaluated: {len(list(combinations(themes, 2)))}")
    print(f"Theme edges kept:      {len(theme_edges)}")
    print(f"Theme pairs skipped:   {skipped}")

    from collections import Counter
    rel_counts = Counter(e["relation_type"] for e in theme_edges)
    print(f"\nRelation type breakdown:")
    for rel, cnt in rel_counts.most_common():
        print(f"  {rel}: {cnt}")

    print(f"\nTop theme connections by confidence:")
    for e in theme_edges[:10]:
        print(f"  [{e['confidence']:.3f}] {e['from_theme_title'][:35]} ↔ {e['to_theme_title'][:35]}")
        print(f"         → {e['relation_type']} | {e['reason']}")

    merge_candidates = [e for e in theme_edges if e["relation_type"] == "merge_candidate_for"]
    if merge_candidates:
        print(f"\nMerge candidates ({len(merge_candidates)}):")
        for e in merge_candidates:
            print(f"  [{e['confidence']:.3f}] {e['from_theme_title'][:40]} ↔ {e['to_theme_title'][:40]}")

    if not args.dry_run:
        THEME_EDGES_OUT.write_text(json.dumps(theme_edges, indent=2))
        print(f"\nWrote {len(theme_edges)} theme edges → {THEME_EDGES_OUT}")
    else:
        print("\n[DRY RUN] — nothing written")


if __name__ == "__main__":
    main()
