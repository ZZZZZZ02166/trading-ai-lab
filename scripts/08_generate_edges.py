#!/usr/bin/env python3
"""
Phase 8: Generate card-to-card edges using Qdrant cosine similarity + tag overlap.

Fully deterministic — no Claude API calls, no hardcoded content.

Algorithm:
  1. Load all knowledge cards from cards/*.json
  2. Embed each card (title + body) using the local EmbedService
  3. For each card, query Qdrant cards collection for top-10 nearest neighbours by vector
  4. Filter: cosine_similarity ≥ 0.72 AND (tag_overlap ≥ 2 OR same card_type cross-book)
  5. Deduplicate: canonical direction = lexicographically smaller card_id first
  6. Assign relation_type via confidence/tag/type rules
  7. Compute confidence = 0.5×cosine + 0.3×tag_score + 0.2×cross_book_bonus
  8. Discard edges with confidence < 0.70
  9. Write to edges/edges.json

Expected output: 400–900 strong edges.

Usage:
    python scripts/08_generate_edges.py
    python scripts/08_generate_edges.py --dry-run
    python scripts/08_generate_edges.py --force
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from dotenv import load_dotenv

load_dotenv()

CARDS_DIR = BASE / "cards"
EDGES_DIR = BASE / "edges"
QDRANT_PATH = str(BASE / "qdrant_storage")
EDGES_OUT = EDGES_DIR / "edges.json"

EDGES_DIR.mkdir(exist_ok=True)

# ── Thresholds ────────────────────────────────────────────────────────────────
# all-MiniLM-L6-v2 produces cosine scores in the 0.45–0.85 range.
# Threshold calibrated empirically from 5-card sample.
COSINE_MIN = 0.55           # minimum cosine similarity to consider a pair
COSINE_STRONG = 0.75        # threshold for "supports" (very similar)
CONFIDENCE_MIN = 0.50       # discard edges below this

# ── Confidence formula weights ────────────────────────────────────────────────
W_COSINE = 0.50
W_TAG = 0.30
W_CROSS = 0.20

TAG_NORM_CAP = 5            # cap tag overlap score at 5 shared tags → 1.0

COLLECTION = "cards"
TOP_K = 15                  # top-K neighbours (+1 to skip self)
EMBED_BATCH = 32


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_all_cards() -> list[dict]:
    cards = []
    for f in sorted(CARDS_DIR.glob("*.json")):
        if "_error" in f.name:
            continue
        data = json.loads(f.read_text())
        cards.extend(data)
    return cards


def tag_overlap_count(a: list[str], b: list[str]) -> int:
    return len(set(a) & set(b))


def assign_relation_type(
    cosine: float,
    overlap: int,
    card_type_a: str,
    card_type_b: str,
    cross_book: bool,
) -> str:
    if cosine >= COSINE_STRONG:
        return "supports"
    caution = {"caution"}
    content = {"mechanism", "concept", "definition", "principle"}
    if card_type_a in caution and card_type_b in content:
        return "extends"
    if card_type_b in caution and card_type_a in content:
        return "extends"
    if overlap >= 2 and cross_book:
        return "related_to"
    if overlap >= 2:
        return "same_theme"
    if card_type_a != card_type_b:
        return "related_to"
    return "same_theme"


def compute_confidence(cosine: float, overlap: int, cross_book: bool) -> float:
    tag_score = min(overlap / TAG_NORM_CAP, 1.0)
    cross_bonus = 1.0 if cross_book else 0.0
    return W_COSINE * cosine + W_TAG * tag_score + W_CROSS * cross_bonus


def canonical_pair(id_a: str, id_b: str) -> tuple[str, str]:
    return (id_a, id_b) if id_a < id_b else (id_b, id_a)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate card-to-card edges")
    parser.add_argument("--dry-run", action="store_true", help="Show stats, don't write")
    parser.add_argument("--force", action="store_true", help="Overwrite existing edges.json")
    args = parser.parse_args()

    if EDGES_OUT.exists() and not args.force:
        print(f"edges.json already exists ({EDGES_OUT}). Use --force to regenerate.")
        return

    from app.services.embed_service import EmbedService
    from qdrant_client import QdrantClient

    cards = load_all_cards()
    print(f"Loaded {len(cards)} cards from {len({c['doc_id'] for c in cards})} books")

    # card_id → card lookup
    card_map: dict[str, dict] = {c["card_id"]: c for c in cards}

    # Embed all cards
    print(f"Loading embedding model...")
    embed_svc = EmbedService()
    texts = [f"{c['title']}\n\n{c['body']}" for c in cards]
    print(f"Embedding {len(cards)} cards in batches of {EMBED_BATCH}...")
    vectors = embed_svc.embed(texts, batch_size=EMBED_BATCH)
    print("Embedding done.")

    # card_id → vector lookup
    card_vectors = {c["card_id"]: vectors[i] for i, c in enumerate(cards)}

    client = QdrantClient(path=QDRANT_PATH)

    seen_pairs: set[tuple[str, str]] = set()
    edges: list[dict] = []

    skipped_low_conf = 0
    skipped_self = 0
    skipped_dup = 0
    skipped_no_vec = 0

    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    for i, card in enumerate(cards):
        if i % 50 == 0:
            print(f"  Processing card {i+1}/{len(cards)} — {len(edges)} edges so far")

        card_id = card["card_id"]
        card_tags = card.get("tags", [])
        card_type = card.get("card_type", "")
        doc_id = card["doc_id"]

        vec = card_vectors.get(card_id)
        if vec is None:
            skipped_no_vec += 1
            continue

        # Search for nearest neighbours by vector
        try:
            response = client.query_points(
                collection_name=COLLECTION,
                query=vec,
                limit=TOP_K,
                with_payload=True,
            )
            results = response.points
        except Exception as e:
            print(f"    WARNING: Qdrant search failed for {card_id}: {e}")
            continue

        for hit in results:
            cosine = hit.score
            payload = hit.payload or {}
            neighbour_id = payload.get("card_id")

            if not neighbour_id:
                continue

            # Skip self
            if neighbour_id == card_id:
                skipped_self += 1
                continue

            if cosine < COSINE_MIN:
                continue

            if neighbour_id not in card_map:
                continue

            neighbour = card_map[neighbour_id]
            neighbour_tags = neighbour.get("tags", [])
            neighbour_type = neighbour.get("card_type", "")
            neighbour_doc = neighbour["doc_id"]

            overlap = tag_overlap_count(card_tags, neighbour_tags)
            cross_book = doc_id != neighbour_doc

            # Deduplicate
            pair = canonical_pair(card_id, neighbour_id)
            if pair in seen_pairs:
                skipped_dup += 1
                continue
            seen_pairs.add(pair)

            confidence = compute_confidence(cosine, overlap, cross_book)
            if confidence < CONFIDENCE_MIN:
                skipped_low_conf += 1
                continue

            from_id, to_id = pair
            relation = assign_relation_type(cosine, overlap, card_type, neighbour_type, cross_book)
            source_basis = "combined" if overlap > 0 else "semantic_similarity"

            edge = {
                "edge_id": str(uuid.uuid4()),
                "from_card_id": from_id,
                "to_card_id": to_id,
                "relation_type": relation,
                "confidence": round(confidence, 4),
                "cosine_similarity": round(cosine, 4),
                "tag_overlap_count": overlap,
                "cross_book": cross_book,
                "reason": (
                    f"cosine={cosine:.3f}, tag_overlap={overlap}, "
                    f"cross_book={cross_book}, types=({card_type}↔{neighbour_type})"
                ),
                "source_basis": source_basis,
                "created_at": now_iso,
                "derived_by": "claude-sonnet-4-6",
            }
            edges.append(edge)

    # Sort by confidence descending
    edges.sort(key=lambda e: e["confidence"], reverse=True)

    print(f"\n{'─'*50}")
    print(f"Edges generated:       {len(edges)}")
    print(f"Skipped (low conf):    {skipped_low_conf}")
    print(f"Skipped (dup):         {skipped_dup}")
    print(f"Skipped (self):        {skipped_self}")
    if skipped_no_vec:
        print(f"Skipped (no vector):   {skipped_no_vec}")

    rel_counts: dict[str, int] = defaultdict(int)
    cross_count = 0
    for e in edges:
        rel_counts[e["relation_type"]] += 1
        if e["cross_book"]:
            cross_count += 1

    print(f"\nRelation type breakdown:")
    for rel, cnt in sorted(rel_counts.items(), key=lambda x: -x[1]):
        print(f"  {rel}: {cnt}")
    print(f"\nCross-book edges: {cross_count} / {len(edges)}")

    if not args.dry_run:
        EDGES_OUT.write_text(json.dumps(edges, indent=2))
        print(f"\nWrote {len(edges)} edges → {EDGES_OUT}")
    else:
        print("\n[DRY RUN] — nothing written")


if __name__ == "__main__":
    main()
