#!/usr/bin/env python3
"""
Phase 11: Critic-gated meta-theme synthesis from theme edges.

Fully deterministic — no Claude API calls, no hardcoded content.
Title, summary, and merge_reason are left blank; filled by scripts/11b_name_meta_themes.py.

Critic gate (ALL must pass):
  1. Theme-edge composite score ≥ 0.45  (adjusted for MiniLM score range)
  2. Cross-theme card edge count ≥ 3    (real conceptual links exist)
  3. At least 2 different books in BOTH parent themes
  4. Neither parent theme already merged or retired
  5. Centroid cosine similarity ≥ 0.62  (adjusted for MiniLM score range)

Usage:
    python scripts/11_synthesize_meta_themes.py
    python scripts/11_synthesize_meta_themes.py --dry-run
    python scripts/11_synthesize_meta_themes.py --force
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from dotenv import load_dotenv

load_dotenv()

THEMES_FILE = BASE / "themes" / "themes.json"
THEME_EDGES_FILE = BASE / "theme_edges" / "theme_edges.json"
EDGES_FILE = BASE / "edges" / "edges.json"
META_THEMES_DIR = BASE / "meta_themes"
META_THEMES_RAW_OUT = META_THEMES_DIR / "meta_themes_raw.json"

META_THEMES_DIR.mkdir(exist_ok=True)

# ── Critic thresholds (calibrated for all-MiniLM-L6-v2) ──────────────────────
CRITIC_MIN_COMPOSITE = 0.45
CRITIC_MIN_CROSS_EDGES = 3
CRITIC_MIN_BOOKS_EACH = 2
CRITIC_MIN_CENTROID_COSINE = 0.62

EMBED_BATCH = 32


# ── Helpers ────────────────────────────────────────────────────────────────────

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def top_tags_merged(cards: list[dict], n: int = 8) -> list[str]:
    counter: Counter = Counter()
    for c in cards:
        for tag in c.get("tags", []):
            counter[tag] += 1
    return [t for t, _ in counter.most_common(n)]


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Critic-gated meta-theme synthesis")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-synthesis", action="store_true", help="Skip automatic theme synthesis trigger after completion")
    args = parser.parse_args()

    if META_THEMES_RAW_OUT.exists() and not args.force:
        print(f"meta_themes_raw.json already exists. Use --force to regenerate.")
        return

    for path in (THEMES_FILE, THEME_EDGES_FILE, EDGES_FILE):
        if not path.exists():
            raise SystemExit(f"{path.name} not found. Run prior pipeline steps first.")

    themes = json.loads(THEMES_FILE.read_text())
    theme_edges = json.loads(THEME_EDGES_FILE.read_text())
    card_edges = json.loads(EDGES_FILE.read_text())

    theme_map = {t["theme_id"]: t for t in themes}

    # Build card_id → theme_id
    card_to_theme: dict[str, str] = {}
    for t in themes:
        for cid in t["source_card_ids"]:
            card_to_theme[cid] = t["theme_id"]

    # Cross-theme edge counts
    from collections import defaultdict
    cross_edge_counts: dict[tuple[str, str], int] = defaultdict(int)
    for e in card_edges:
        ta = card_to_theme.get(e["from_card_id"])
        tb = card_to_theme.get(e["to_card_id"])
        if ta and tb and ta != tb:
            key = (min(ta, tb), max(ta, tb))
            cross_edge_counts[key] += 1

    # Load card data for union construction
    card_json_map: dict[str, dict] = {}
    cards_dir = BASE / "cards"
    for f in sorted(cards_dir.glob("*.json")):
        if "_error" not in f.name:
            for c in json.loads(f.read_text()):
                card_json_map[c["card_id"]] = c

    # Compute centroids — embed all needed cards once
    needed_ids = set()
    for t in themes:
        needed_ids.update(t["source_card_ids"])
    needed_cards = [card_json_map[cid] for cid in needed_ids if cid in card_json_map]

    from app.services.embed_service import EmbedService
    embed_svc = EmbedService()
    texts = [f"{c['title']}\n\n{c['body']}" for c in needed_cards]
    print(f"Embedding {len(needed_cards)} cards for centroid computation...")
    vecs = embed_svc.embed(texts, batch_size=EMBED_BATCH)
    card_vec_map: dict[str, np.ndarray] = {
        c["card_id"]: np.array(v) for c, v in zip(needed_cards, vecs)
    }
    print("Done.")

    theme_centroid: dict[str, np.ndarray] = {}
    for t in themes:
        vs = [card_vec_map[cid] for cid in t["source_card_ids"] if cid in card_vec_map]
        if vs:
            theme_centroid[t["theme_id"]] = np.mean(vs, axis=0)

    # Evaluate each theme edge as a merge candidate
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    meta_themes = []
    already_merged: set[str] = set()

    critic_log = []

    for te in sorted(theme_edges, key=lambda e: -e["confidence"]):
        id_a = te["from_theme_id"]
        id_b = te["to_theme_id"]
        t_a = theme_map.get(id_a)
        t_b = theme_map.get(id_b)

        if not t_a or not t_b:
            continue

        gate_results = {}

        # Gate 1: composite score
        gate_results["composite_ok"] = te["confidence"] >= CRITIC_MIN_COMPOSITE

        # Gate 2: cross-theme edge count
        key = (min(id_a, id_b), max(id_a, id_b))
        cross_count = cross_edge_counts.get(key, 0)
        gate_results["cross_edges_ok"] = cross_count >= CRITIC_MIN_CROSS_EDGES
        gate_results["cross_edge_count"] = cross_count

        # Gate 3: book diversity in both parents
        gate_results["books_a_ok"] = t_a["book_count"] >= CRITIC_MIN_BOOKS_EACH
        gate_results["books_b_ok"] = t_b["book_count"] >= CRITIC_MIN_BOOKS_EACH

        # Gate 4: neither already merged/retired
        gate_results["not_merged_a"] = t_a["status"] not in ("merged", "retired")
        gate_results["not_merged_b"] = t_b["status"] not in ("merged", "retired")
        gate_results["not_in_meta_a"] = id_a not in already_merged
        gate_results["not_in_meta_b"] = id_b not in already_merged

        # Gate 5: centroid cosine
        cent_a = theme_centroid.get(id_a)
        cent_b = theme_centroid.get(id_b)
        centroid_cos = cosine_sim(cent_a, cent_b) if cent_a is not None and cent_b is not None else 0.0
        gate_results["centroid_ok"] = centroid_cos >= CRITIC_MIN_CENTROID_COSINE
        gate_results["centroid_cosine"] = round(centroid_cos, 4)

        all_pass = (
            gate_results["composite_ok"]
            and gate_results["cross_edges_ok"]
            and gate_results["books_a_ok"]
            and gate_results["books_b_ok"]
            and gate_results["not_merged_a"]
            and gate_results["not_merged_b"]
            and gate_results["not_in_meta_a"]
            and gate_results["not_in_meta_b"]
            and gate_results["centroid_ok"]
        )

        critic_log.append({
            "theme_a": t_a["title"],
            "theme_b": t_b["title"],
            "composite": te["confidence"],
            "passed": all_pass,
            **gate_results,
        })

        if not all_pass:
            continue

        # Build meta-theme
        union_card_ids = list(set(t_a["source_card_ids"]) | set(t_b["source_card_ids"]))
        union_doc_ids = list(set(t_a["source_doc_ids"]) | set(t_b["source_doc_ids"]))
        union_edge_ids = list(set(t_a["source_edge_ids"]) | set(t_b["source_edge_ids"]))
        union_cards = [card_json_map[cid] for cid in union_card_ids if cid in card_json_map]

        meta_theme = {
            "meta_theme_id": str(uuid.uuid4()),
            "theme_type": "meta_theme",
            "title": "",
            "summary": "",
            "merge_reason": "",
            "parent_theme_ids": [id_a, id_b],
            "parent_theme_titles": [t_a["title"], t_b["title"]],
            "source_card_ids": union_card_ids,
            "source_doc_ids": union_doc_ids,
            "source_edge_ids": union_edge_ids,
            "top_tags": top_tags_merged(union_cards),
            "card_count": len(union_card_ids),
            "book_count": len(union_doc_ids),
            "confidence": round((t_a["confidence"] + t_b["confidence"]) / 2, 4),
            "critic_composite_score": te["confidence"],
            "critic_cross_edge_count": cross_count,
            "critic_centroid_cosine": gate_results["centroid_cosine"],
            "critic_passed": True,
            "status": "provisional",
            "needs_review_reason": None,
            "created_at": now_iso,
            "derived_by": "claude-sonnet-4-6",
        }
        meta_themes.append(meta_theme)
        already_merged.add(id_a)
        already_merged.add(id_b)

    # Summary
    print(f"\n{'─'*60}")
    print(f"Theme edges evaluated: {len(theme_edges)}")
    print(f"Meta-themes created:   {len(meta_themes)}")
    print(f"\nCritic log (all pairs):")
    for entry in critic_log:
        status = "PASS" if entry["passed"] else "fail"
        gates = []
        if not entry["composite_ok"]:    gates.append(f"composite={entry['composite']:.3f}<{CRITIC_MIN_COMPOSITE}")
        if not entry["cross_edges_ok"]:  gates.append(f"cross_edges={entry['cross_edge_count']}<{CRITIC_MIN_CROSS_EDGES}")
        if not entry["books_a_ok"]:      gates.append(f"books_a={entry.get('books_a_ok')}")
        if not entry["books_b_ok"]:      gates.append(f"books_b={entry.get('books_b_ok')}")
        if not entry["centroid_ok"]:     gates.append(f"centroid={entry['centroid_cosine']:.3f}<{CRITIC_MIN_CENTROID_COSINE}")
        if not entry.get("not_in_meta_a") or not entry.get("not_in_meta_b"):
            gates.append("already_in_meta")
        reason = "; ".join(gates) if gates else "all gates passed"
        print(f"  [{status}] {entry['composite']:.3f} | {entry['theme_a'][:30]} ↔ {entry['theme_b'][:30]} | {reason}")

    if meta_themes:
        print(f"\nMeta-themes:")
        for m in meta_themes:
            print(f"  {m['card_count']}c {m['book_count']}b | {m['parent_theme_titles'][0][:35]} + {m['parent_theme_titles'][1][:35]}")
            print(f"    tags: {m['top_tags'][:4]}")

    if not args.dry_run:
        META_THEMES_RAW_OUT.write_text(json.dumps(meta_themes, indent=2))
        print(f"\nWrote {len(meta_themes)} meta-themes → {META_THEMES_RAW_OUT}")
        if meta_themes:
            print("Next step: run scripts/11b_name_meta_themes.py to add titles and summaries.")
        else:
            print("No meta-themes passed the critic gate. Review theme_edges and critic log.")
    else:
        print("\n[DRY RUN] — nothing written")

    if not args.dry_run and not args.no_synthesis:
        import importlib.util as _ilu, sys as _sys
        _spec = _ilu.spec_from_file_location("ts", Path(__file__).parent / "19_run_theme_synthesis.py")
        _ts = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_ts)
        _ts.auto_trigger_synthesis("11_synthesize_meta_themes: meta-themes updated")


if __name__ == "__main__":
    main()
