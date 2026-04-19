#!/usr/bin/env python3
"""
Phase 19: Theme Synthesis / Evolution

Two AI passes over the knowledge graph:
  1. Synthesis pass (Sonnet, temp=0.5) — proposes relationship actions between themes
  2. Critic pass   (Haiku, temp=0.0)  — challenges proposals; defaults to reject

Outputs: synthesis_candidates/, synthesis_reviews/, synthesis_runs/ (full audit snapshots)
May update: meta_themes/meta_themes.json, theme_edges/theme_edges.json, themes/themes.json

Usage:
    python scripts/19_run_theme_synthesis.py              # normal run (24h idempotency)
    python scripts/19_run_theme_synthesis.py --force      # always re-run
    python scripts/19_run_theme_synthesis.py --dry-run    # print compact repr, no API calls
    python scripts/19_run_theme_synthesis.py --synthesis-only  # no critic, no graph changes
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import anthropic

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
THEMES_FILE = ROOT / "themes" / "themes.json"
THEME_EDGES_FILE = ROOT / "theme_edges" / "theme_edges.json"
META_THEMES_FILE = ROOT / "meta_themes" / "meta_themes.json"
META_THEMES_RAW_FILE = ROOT / "meta_themes" / "meta_themes_raw.json"
HYPOTHESES_FILE = ROOT / "experiments" / "hypotheses.json"
BACKTEST_RESULTS_FILE = ROOT / "experiments" / "backtest_results.json"
CARDS_DIR = ROOT / "cards"

SYNTHESIS_CANDIDATES_DIR = ROOT / "synthesis_candidates"
SYNTHESIS_REVIEWS_DIR = ROOT / "synthesis_reviews"
SYNTHESIS_RUNS_DIR = ROOT / "synthesis_runs"
LOGS_DIR = ROOT / "logs"

CANDIDATES_FILE = SYNTHESIS_CANDIDATES_DIR / "synthesis_candidates.json"
REVIEWS_FILE = SYNTHESIS_REVIEWS_DIR / "synthesis_reviews.json"
API_USAGE_LOG = LOGS_DIR / "api_usage.jsonl"

# ── Models ────────────────────────────────────────────────────────────────
LLM_MODEL = os.environ.get("LLM_MODEL", "claude-sonnet-4-6")
HAIKU_MODEL = "claude-haiku-4-5-20251001"

# ── Idempotency guard (hours) ──────────────────────────────────────────────
IDEMPOTENCY_HOURS = 24


# ────────────────────────────────────────────────────────────────────────────
# auto_trigger_synthesis — imported by pipeline scripts
# ────────────────────────────────────────────────────────────────────────────

def auto_trigger_synthesis(reason: str, force: bool = False) -> None:
    """
    Called by other pipeline scripts after they successfully update the graph.
    Runs this script as a subprocess. Pass force=True to override 24h guard.
    """
    script = Path(__file__).resolve()
    cmd = [sys.executable, str(script)]
    if force:
        cmd.append("--force")
    print(f"\n[auto-synthesis] Triggered by: {reason}")
    subprocess.run(cmd, check=False)


# ────────────────────────────────────────────────────────────────────────────
# Phase 0 — load_graph
# ────────────────────────────────────────────────────────────────────────────

def load_graph() -> dict:
    themes = json.loads(THEMES_FILE.read_text()) if THEMES_FILE.exists() else []
    theme_edges = json.loads(THEME_EDGES_FILE.read_text()) if THEME_EDGES_FILE.exists() else []

    if META_THEMES_FILE.exists():
        meta_themes = json.loads(META_THEMES_FILE.read_text())
    elif META_THEMES_RAW_FILE.exists():
        meta_themes = json.loads(META_THEMES_RAW_FILE.read_text())
        print("[warn] meta_themes.json absent — falling back to meta_themes_raw.json")
    else:
        meta_themes = []

    hypotheses = json.loads(HYPOTHESES_FILE.read_text()) if HYPOTHESES_FILE.exists() else []
    backtest_results = json.loads(BACKTEST_RESULTS_FILE.read_text()) if BACKTEST_RESULTS_FILE.exists() else []

    # Load cards compact (title + body[:120] + tags only)
    cards_by_id: dict[str, dict] = {}
    for card_file in CARDS_DIR.glob("*.json"):
        try:
            doc_cards = json.loads(card_file.read_text())
            for c in doc_cards:
                cards_by_id[c["card_id"]] = {
                    "card_id": c["card_id"],
                    "title": c.get("title", ""),
                    "body": c.get("body", "")[:120],
                    "tags": c.get("tags", []),
                }
        except Exception:
            pass

    return {
        "themes": themes,
        "theme_edges": theme_edges,
        "meta_themes": meta_themes,
        "hypotheses": hypotheses,
        "backtest_results": backtest_results,
        "cards_by_id": cards_by_id,
    }


# ────────────────────────────────────────────────────────────────────────────
# Phase 1 — build_compact_representation
# ────────────────────────────────────────────────────────────────────────────

def _first_sentence(text: str, max_chars: int = 150) -> str:
    if not text:
        return ""
    m = re.search(r"[.!?]\s", text)
    if m:
        s = text[: m.start() + 1]
    else:
        s = text
    return s[:max_chars].strip()


def _select_evidence_cards(theme: dict, all_themes: list[dict], cards_by_id: dict) -> list[dict]:
    """Pick 2 cards from theme whose tags overlap most with other themes."""
    other_tag_sets = []
    for t in all_themes:
        if t["theme_id"] != theme["theme_id"]:
            other_tag_sets.extend(t.get("top_tags", []))
    other_tags = set(other_tag_sets)

    scored = []
    for cid in theme.get("source_card_ids", []):
        card = cards_by_id.get(cid)
        if not card:
            continue
        overlap = len(set(card.get("tags", [])) & other_tags)
        scored.append((overlap, card))

    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:2]]


def build_compact_representation(graph: dict) -> dict:
    themes = graph["themes"]
    theme_edges = graph["theme_edges"]
    meta_themes = graph["meta_themes"]
    hypotheses = graph["hypotheses"]
    backtest_results = graph["backtest_results"]
    cards_by_id = graph["cards_by_id"]

    # Build backtest lookup by hypothesis_id
    backtest_by_hyp: dict[str, str] = {}
    for br in backtest_results:
        backtest_by_hyp[br["hypothesis_id"]] = br.get("verdict", "unknown")

    # Compact themes
    compact_themes = []
    for t in themes:
        evidence_cards = _select_evidence_cards(t, themes, cards_by_id)
        compact_themes.append({
            "theme_id": t["theme_id"],
            "title": t["title"],
            "summary_first_sentence": _first_sentence(t.get("summary", ""), 150),
            "top_tags": t.get("top_tags", [])[:8],
            "card_count": t.get("card_count", len(t.get("source_card_ids", []))),
            "book_count": t.get("book_count", 0),
            "avg_edge_confidence": t.get("avg_edge_confidence", t.get("confidence", 0.0)),
            "status": t.get("status", "provisional"),
            "evidence_cards": [
                {"card_id": c["card_id"], "title": c["title"], "body": c["body"]}
                for c in evidence_cards
            ],
        })

    # Compact theme edges
    compact_edges = [
        {
            "theme_edge_id": e["theme_edge_id"],
            "from_title": e["from_theme_title"],
            "to_title": e["to_theme_title"],
            "relation_type": e["relation_type"],
            "confidence": round(e["confidence"], 3),
            "cross_edge_count": e.get("cross_edge_count", 0),
            "centroid_cosine": round(e.get("centroid_cosine", 0.0), 3),
        }
        for e in theme_edges
    ]

    # Compact meta-themes
    compact_meta = [
        {
            "title": m.get("title", "Unnamed"),
            "parent_theme_titles": m.get("parent_theme_titles", []),
            "merge_reason": _first_sentence(m.get("merge_reason", ""), 150),
        }
        for m in meta_themes
    ]

    # Hypothesis-theme map (only those with source_theme_ids)
    theme_id_to_title = {t["theme_id"]: t["title"] for t in themes}
    hyp_theme_map = []
    for h in hypotheses:
        sids = h.get("source_theme_ids") or []
        if not sids:
            continue
        verdict = backtest_by_hyp.get(h["hypothesis_id"], None)
        hyp_theme_map.append({
            "hypothesis_title": h["title"],
            "theme_titles": [theme_id_to_title.get(tid, tid) for tid in sids],
            "verdict": verdict,
        })

    # Backtest signals (weak signal label)
    backtest_signals = []
    for br in backtest_results:
        hyp_num = br.get("hypothesis_number", "H?")
        backtest_signals.append({
            "hypothesis": f"{hyp_num}: {br.get('hypothesis_title', '')[:60]}",
            "verdict": br.get("verdict", "unknown"),
        })

    return {
        "themes": compact_themes,
        "theme_edges": compact_edges,
        "meta_themes": compact_meta,
        "hypothesis_theme_map": hyp_theme_map,
        "backtest_signals_weak": backtest_signals,
    }


# ────────────────────────────────────────────────────────────────────────────
# Phase 2 — call_synthesis_pass
# ────────────────────────────────────────────────────────────────────────────

_SYNTHESIS_SYSTEM = """You are a knowledge graph analyst for a quantitative options research system.
Read the current graph and propose relationship actions between themes.
The framework is fixed; your reasoning must be generated fresh from the data you see.

Rules:
- Every proposal must cite specific evidence from the graph: cross_edge_count,
  centroid_cosine values, shared mechanisms in the evidence snippets, or explicit
  causal language in theme summaries
- Do NOT propose merges based solely on title similarity
- Prefer hierarchy: create_parent_meta_theme preserves both original themes
- Keep proposals conservative — propose at most 15 candidates total
- If no meaningful relationship is found, propose nothing for that pair
- Backtest results are labeled WEAK SIGNAL — do not use as structural evidence
- Return a valid JSON array of candidate objects only, nothing else"""


def _build_synthesis_user_prompt(compact: dict) -> str:
    lines = []

    lines.append(f"CURRENT THEMES ({len(compact['themes'])}):")
    for t in compact["themes"]:
        lines.append(f"\nID: {t['theme_id']}")
        lines.append(f"Title: {t['title']}")
        lines.append(f"Summary: {t['summary_first_sentence']}")
        lines.append(f"Tags: {', '.join(t['top_tags'])}")
        lines.append(f"Cards: {t['card_count']} | Books: {t['book_count']} | AvgConf: {t['avg_edge_confidence']:.3f} | Status: {t['status']}")
        if t["evidence_cards"]:
            lines.append("Evidence cards:")
            for c in t["evidence_cards"]:
                lines.append(f"  [{c['card_id'][:8]}] \"{c['title']}\": {c['body']}")

    lines.append(f"\nTHEME EDGES (current graph) ({len(compact['theme_edges'])}):")
    for e in compact["theme_edges"]:
        lines.append(f"[{e['theme_edge_id']}] {e['from_title']} → {e['to_title']}")
        lines.append(f"  relation={e['relation_type']} | conf={e['confidence']:.3f} | cross_edges={e['cross_edge_count']} | centroid={e['centroid_cosine']:.3f}")

    if compact["meta_themes"]:
        lines.append(f"\nEXISTING META-THEMES ({len(compact['meta_themes'])}):")
        for m in compact["meta_themes"]:
            lines.append(f"  \"{m['title']}\" ← parents: {m['parent_theme_titles']}")
            lines.append(f"  reason: {m['merge_reason']}")

    if compact["hypothesis_theme_map"]:
        lines.append("\nHYPOTHESIS-THEME ASSOCIATIONS:")
        for h in compact["hypothesis_theme_map"]:
            lines.append(f"  \"{h['hypothesis_title']}\" → {h['theme_titles']}")

    if compact["backtest_signals_weak"]:
        lines.append("\nBACKTEST SIGNALS (WEAK SIGNAL — do not use as structural evidence):")
        for s in compact["backtest_signals_weak"]:
            lines.append(f"  {s['hypothesis']}: {s['verdict']}")

    lines.append("""
Propose relationship actions for pairs or clusters you find noteworthy.
Return JSON array with fields:
  action, theme_ids, theme_titles, synthesis_reason, evidence,
  confidence (0.0-1.0), source_card_ids ([] if not citing specific cards),
  source_edge_ids (theme_edge_ids from THEME EDGES above),
  proposed_title (null unless create_parent_meta_theme),
  proposed_summary (null unless create_parent_meta_theme)

Valid actions: keep_separate | relate | strengthen_link | supports |
               merge_candidate | create_parent_meta_theme | split_theme_if_too_broad""")

    return "\n".join(lines)


def call_synthesis_pass(client: anthropic.Anthropic, compact: dict) -> tuple[list[dict], dict]:
    user_prompt = _build_synthesis_user_prompt(compact)
    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=6000,
        temperature=0.5,
        system=_SYNTHESIS_SYSTEM,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw_text = response.content[0].text.strip()
    # Strip markdown code fences if present
    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```[^\n]*\n?", "", raw_text)
        raw_text = re.sub(r"\n?```$", "", raw_text.strip())

    candidates = json.loads(raw_text)
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return candidates, usage


# ────────────────────────────────────────────────────────────────────────────
# Phase 3 — filter_for_critic
# ────────────────────────────────────────────────────────────────────────────

def filter_for_critic(candidates: list[dict]) -> tuple[list[dict], list[dict]]:
    to_review = [c for c in candidates if c.get("action") != "keep_separate"]
    keep_separate = [c for c in candidates if c.get("action") == "keep_separate"]
    return to_review, keep_separate


# ────────────────────────────────────────────────────────────────────────────
# Phase 4 — call_critic_pass
# ────────────────────────────────────────────────────────────────────────────

_CRITIC_SYSTEM = """You are a conservative critic reviewing proposed knowledge graph changes.
Your default is to reject. Only accept when the mechanistic overlap is strong,
explicitly supported by the evidence, and genuinely useful for future hypothesis generation.

Heuristics (not hard rules — use as strong defaults, not absolute gates):
- Fewer than 3 cross-theme card edges cited → lean toward reject
- Centroid cosine < 0.65 for create_parent_meta_theme → lean toward reject
- Title similarity without mechanistic connection → reject
- Action stronger than evidence justifies → downgrade to simpler action

Override rule: if the synthesis_reason or evidence field cites a clear, specific
mechanistic connection that makes the merge or parent useful for hypothesis generation,
you may accept even if a heuristic is not fully met — but you must explicitly explain
the override in critic_reasoning.

Downgrade rules (direction right but action too aggressive):
  merge_candidate → downgrade to strengthen_link or relate
  create_parent_meta_theme → downgrade to merge_candidate

Return valid JSON array of review objects only, nothing else."""


def call_critic_pass(client: anthropic.Anthropic, candidates_for_review: list[dict]) -> tuple[list[dict], dict]:
    if not candidates_for_review:
        return [], {"input_tokens": 0, "output_tokens": 0}

    user_prompt = (
        "Review each synthesis candidate. For each return:\n"
        "  review_id (generate a new UUID4), candidate_id, original_action,\n"
        "  critic_verdict (accepted|rejected|downgraded),\n"
        "  action_taken, downgraded_to (null or simpler action string), critic_reasoning\n\n"
        "Candidates to review:\n"
        + json.dumps(candidates_for_review, indent=2)
    )

    response = client.messages.create(
        model=HAIKU_MODEL,
        max_tokens=3000,
        temperature=0.0,
        system=_CRITIC_SYSTEM,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw_text = response.content[0].text.strip()
    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```[^\n]*\n?", "", raw_text)
        raw_text = re.sub(r"\n?```$", "", raw_text.strip())

    reviews = json.loads(raw_text)
    # Ensure reviewed_at is set
    now = datetime.now(timezone.utc).isoformat()
    for r in reviews:
        r.setdefault("reviewed_at", now)
        r.setdefault("review_id", str(uuid.uuid4()))

    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return reviews, usage


# ────────────────────────────────────────────────────────────────────────────
# Phase 5 — apply_accepted_candidates
# ────────────────────────────────────────────────────────────────────────────

def apply_accepted_candidates(
    graph: dict,
    candidates: list[dict],
    reviews: list[dict],
    run_id: str,
) -> tuple[dict, dict, dict, list[str]]:
    """Returns (updated_meta_themes, updated_edges, updated_themes, change_log)."""
    themes = {t["theme_id"]: t for t in graph["themes"]}
    theme_edges = list(graph["theme_edges"])
    meta_themes = list(graph["meta_themes"])
    change_log = []

    # Build review lookup by candidate_id
    review_by_cid: dict[str, dict] = {}
    for r in reviews:
        review_by_cid[r.get("candidate_id", "")] = r

    # Build set of existing meta-theme parent-id sets (for dedup)
    existing_parent_sets = [
        frozenset(m.get("parent_theme_ids", []))
        for m in meta_themes
    ]

    # Build edge lookup by (from_id, to_id)
    edge_lookup: dict[tuple, dict] = {}
    for e in theme_edges:
        key = (e["from_theme_id"], e["to_theme_id"])
        edge_lookup[key] = e

    title_to_id = {t["title"]: t["theme_id"] for t in graph["themes"]}
    now = datetime.now(timezone.utc).isoformat()

    for cand in candidates:
        cid = cand.get("candidate_id", "")
        action = cand.get("action", "")
        review = review_by_cid.get(cid)

        if review is None:
            # keep_separate or no review — no graph changes
            continue
        if review.get("critic_verdict") != "accepted":
            continue

        theme_ids = cand.get("theme_ids", [])

        # ── create_parent_meta_theme ────────────────────────────────────────
        if action == "create_parent_meta_theme":
            parent_set = frozenset(theme_ids)
            if parent_set in existing_parent_sets:
                change_log.append(f"SKIP create_parent_meta_theme (already exists): {cand.get('proposed_title')}")
                continue
            new_entry = {
                "meta_theme_id": str(uuid.uuid4()),
                "theme_type": "higher_order_synthesis",
                "title": cand.get("proposed_title", "Unnamed Synthesis"),
                "summary": cand.get("proposed_summary", ""),
                "merge_reason": cand.get("synthesis_reason", ""),
                "parent_theme_ids": list(theme_ids),
                "parent_theme_titles": cand.get("theme_titles", []),
                "source_card_ids": cand.get("source_card_ids", []),
                "source_doc_ids": [],
                "source_edge_ids": cand.get("source_edge_ids", []),
                "top_tags": [],
                "card_count": 0,
                "book_count": 0,
                "confidence": cand.get("confidence", 0.5),
                "status": "provisional",
                "needs_review_reason": None,
                "created_at": now,
                "derived_by": f"{LLM_MODEL}/ai_synthesis",
                "synthesis_candidate_id": cid,
                "critic_review_id": review.get("review_id", ""),
            }
            meta_themes.append(new_entry)
            existing_parent_sets.append(parent_set)
            change_log.append(f"CREATED meta-theme: \"{new_entry['title']}\" ← {cand.get('theme_titles')}")

        # ── strengthen_link ─────────────────────────────────────────────────
        elif action == "strengthen_link" and len(theme_ids) >= 2:
            t1, t2 = theme_ids[0], theme_ids[1]
            key = (t1, t2)
            rev_key = (t2, t1)
            target_key = key if key in edge_lookup else (rev_key if rev_key in edge_lookup else None)
            if target_key:
                old_conf = edge_lookup[target_key]["confidence"]
                new_conf = cand.get("confidence", old_conf)
                if new_conf > old_conf:
                    edge_lookup[target_key]["confidence"] = new_conf
                    change_log.append(f"STRENGTHENED edge: {cand.get('theme_titles')} {old_conf:.3f} → {new_conf:.3f}")
                else:
                    change_log.append(f"SKIP strengthen (proposed conf {new_conf:.3f} ≤ existing {old_conf:.3f})")
            else:
                change_log.append(f"SKIP strengthen_link (no existing edge): {cand.get('theme_titles')}")

        # ── relate / supports — add new edge if absent ─────────────────────
        elif action in ("relate", "supports") and len(theme_ids) >= 2:
            t1, t2 = theme_ids[0], theme_ids[1]
            key = (t1, t2)
            rev_key = (t2, t1)
            if key not in edge_lookup and rev_key not in edge_lookup:
                relation = "causal" if action == "supports" else "overlaps_with"
                new_edge = {
                    "theme_edge_id": str(uuid.uuid4()),
                    "from_theme_id": t1,
                    "to_theme_id": t2,
                    "from_theme_title": cand["theme_titles"][0] if cand.get("theme_titles") else "",
                    "to_theme_title": cand["theme_titles"][1] if len(cand.get("theme_titles", [])) > 1 else "",
                    "relation_type": relation,
                    "confidence": cand.get("confidence", 0.5),
                    "shared_tag_score": 0.0,
                    "cross_edge_count": 0,
                    "centroid_cosine": 0.0,
                    "card_overlap_jaccard": 0.0,
                    "reason": f"ai_synthesis: {cand.get('synthesis_reason', '')[:200]}",
                    "created_at": now,
                    "derived_by": f"{LLM_MODEL}/ai_synthesis",
                }
                theme_edges.append(new_edge)
                edge_lookup[key] = new_edge
                change_log.append(f"ADDED edge ({relation}): {cand.get('theme_titles')}")
            else:
                change_log.append(f"SKIP relate (edge already exists): {cand.get('theme_titles')}")

        # ── split_theme_if_too_broad — flag only, no structural change ──────
        elif action == "split_theme_if_too_broad" and theme_ids:
            for tid in theme_ids:
                if tid in themes:
                    themes[tid]["status"] = "needs_review"
                    themes[tid]["needs_review_reason"] = cand.get("synthesis_reason", "Flagged by AI synthesis for potential split.")
                    change_log.append(f"FLAGGED for split: \"{themes[tid]['title']}\"")

        # ── merge_candidate — record only, no structural change ─────────────
        elif action == "merge_candidate":
            change_log.append(f"RECORDED merge_candidate (no graph change): {cand.get('theme_titles')}")

    return (
        meta_themes,
        list(edge_lookup.values()),
        list(themes.values()),
        change_log,
    )


# ────────────────────────────────────────────────────────────────────────────
# Phase 6 — persist_outputs
# ────────────────────────────────────────────────────────────────────────────

def _log_api_usage(script: str, model: str, input_tokens: int, output_tokens: int) -> None:
    LOGS_DIR.mkdir(exist_ok=True)
    cost = input_tokens * 0.000003 + output_tokens * 0.000015
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "script": script,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(cost, 6),
    }
    with API_USAGE_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def persist_outputs(
    run_id: str,
    compact: dict,
    candidates: list[dict],
    reviews: list[dict],
    keep_separate: list[dict],
    new_meta_themes: list,
    new_edges: list,
    new_themes: list,
    graph: dict,
    change_log: list[str],
    synthesis_usage: dict,
    critic_usage: dict,
    synthesis_prompt_system: str,
    synthesis_prompt_user: str,
    graph_changed: bool,
    dry_run: bool = False,
) -> None:
    for d in [SYNTHESIS_CANDIDATES_DIR, SYNTHESIS_REVIEWS_DIR, SYNTHESIS_RUNS_DIR, LOGS_DIR]:
        d.mkdir(exist_ok=True)

    # Stamp candidates with run_id
    now = datetime.now(timezone.utc).isoformat()
    for c in candidates:
        c.setdefault("candidate_id", str(uuid.uuid4()))
        c["run_id"] = run_id
        c.setdefault("created_from_run", now)
        if "status" not in c:
            c["status"] = "pending"

    # Merge review verdicts into candidate status
    review_by_cid = {r.get("candidate_id", ""): r for r in reviews}
    for c in candidates:
        r = review_by_cid.get(c["candidate_id"])
        if r:
            verdict = r.get("critic_verdict", "pending")
            c["status"] = verdict

    if not dry_run:
        # Always write candidates and reviews
        CANDIDATES_FILE.write_text(json.dumps(candidates, indent=2))
        REVIEWS_FILE.write_text(json.dumps(reviews, indent=2))

        # Conditionally write graph files
        if graph_changed:
            (ROOT / "meta_themes" / "meta_themes.json").write_text(json.dumps(new_meta_themes, indent=2))
            (ROOT / "theme_edges" / "theme_edges.json").write_text(json.dumps(new_edges, indent=2))
            (ROOT / "themes" / "themes.json").write_text(json.dumps(new_themes, indent=2))

    # Build run snapshot
    syn_cost = synthesis_usage["input_tokens"] * 0.000003 + synthesis_usage["output_tokens"] * 0.000015
    crit_cost = critic_usage["input_tokens"] * 0.000003 + critic_usage["output_tokens"] * 0.000015
    total_cost = round(syn_cost + crit_cost, 6)

    n_accepted = sum(1 for r in reviews if r.get("critic_verdict") == "accepted")
    n_rejected = sum(1 for r in reviews if r.get("critic_verdict") == "rejected")
    n_downgraded = sum(1 for r in reviews if r.get("critic_verdict") == "downgraded")

    run_snapshot = {
        "run_id": run_id,
        "run_timestamp": now,
        "model": LLM_MODEL,
        "critic_model": HAIKU_MODEL,
        "synthesis_temperature": 0.5,
        "critic_temperature": 0.0,
        "compact_representation": compact,
        "synthesis_prompt_system": synthesis_prompt_system,
        "synthesis_prompt_user": synthesis_prompt_user,
        "critic_prompt_system": _CRITIC_SYSTEM,
        "critic_prompt_user": "(see synthesis_reviews.json)",
        "n_candidates_proposed": len(candidates),
        "n_keep_separate": len(keep_separate),
        "n_accepted": n_accepted,
        "n_rejected": n_rejected,
        "n_downgraded": n_downgraded,
        "synthesis_input_tokens": synthesis_usage["input_tokens"],
        "synthesis_output_tokens": synthesis_usage["output_tokens"],
        "critic_input_tokens": critic_usage["input_tokens"],
        "critic_output_tokens": critic_usage["output_tokens"],
        "estimated_cost_usd": total_cost,
        "graph_changed": graph_changed,
        "change_log": change_log,
    }

    if not dry_run:
        run_file = SYNTHESIS_RUNS_DIR / f"synthesis_run_{run_id}.json"
        run_file.write_text(json.dumps(run_snapshot, indent=2))
        latest = SYNTHESIS_RUNS_DIR / "synthesis_run_latest.json"
        latest.write_text(json.dumps(run_snapshot, indent=2))

        # Log API usage
        _log_api_usage("19_run_theme_synthesis/synthesis", LLM_MODEL,
                       synthesis_usage["input_tokens"], synthesis_usage["output_tokens"])
        if critic_usage["input_tokens"] > 0:
            _log_api_usage("19_run_theme_synthesis/critic", HAIKU_MODEL,
                           critic_usage["input_tokens"], critic_usage["output_tokens"])

    return run_snapshot


# ────────────────────────────────────────────────────────────────────────────
# Phase 7 — print_audit_summary
# ────────────────────────────────────────────────────────────────────────────

def print_audit_summary(
    run_id: str,
    candidates: list[dict],
    reviews: list[dict],
    keep_separate: list[dict],
    change_log: list[str],
    total_cost: float,
    graph_changed: bool,
) -> None:
    review_by_cid = {r.get("candidate_id", ""): r for r in reviews}
    n_accepted = sum(1 for r in reviews if r.get("critic_verdict") == "accepted")
    n_rejected = sum(1 for r in reviews if r.get("critic_verdict") == "rejected")
    n_downgraded = sum(1 for r in reviews if r.get("critic_verdict") == "downgraded")

    print(f"\n{'━'*60}")
    print(f"Theme Synthesis Run — {run_id}")
    print(f"Model: {LLM_MODEL} / critic: {HAIKU_MODEL}")
    print(f"Cost: ${total_cost:.4f}")
    print(f"\nCandidates proposed:  {len(candidates)}")
    print(f"  → Accepted:         {n_accepted}")
    print(f"  → Rejected:         {n_rejected}")
    print(f"  → Downgraded:       {n_downgraded}")
    print(f"  → keep_separate:    {len(keep_separate)} (not reviewed by critic)")

    # New parent meta-themes
    new_parents = [c for c in candidates if c.get("action") == "create_parent_meta_theme"
                   and c.get("status") == "accepted"]
    if new_parents:
        print(f"\nNew parent meta-themes created ({len(new_parents)}):")
        for c in new_parents:
            print(f"  ✓ \"{c.get('proposed_title')}\" ← {c.get('theme_titles')}")

    # Strengthened edges
    strengthened = [c for c in candidates if c.get("action") == "strengthen_link"
                    and c.get("status") == "accepted"]
    if strengthened:
        print(f"\nTheme edges strengthened ({len(strengthened)}):")
        for c in strengthened:
            print(f"  ↑ {c.get('theme_titles')}: conf → {c.get('confidence', '?'):.3f}")

    # Flagged for split
    flagged = [c for c in candidates if c.get("action") == "split_theme_if_too_broad"
               and c.get("status") == "accepted"]
    if flagged:
        print(f"\nThemes flagged for future splitting ({len(flagged)}) (NOT yet split):")
        for c in flagged:
            print(f"  ⚠ {c.get('theme_titles')}: {str(c.get('synthesis_reason', ''))[:100]}")

    # Rejected merge/parent proposals
    rejected = [c for c in candidates if c.get("status") == "rejected"
                and c.get("action") in ("merge_candidate", "create_parent_meta_theme")]
    if rejected:
        print(f"\nRejected merge/parent proposals ({len(rejected)}):")
        for c in rejected:
            r = review_by_cid.get(c.get("candidate_id", ""))
            reasoning = r.get("critic_reasoning", "")[:100] if r else ""
            print(f"  ✗ {c.get('theme_titles')}: {reasoning}")

    # Change log
    if change_log:
        print(f"\nGraph changes ({len(change_log)}):")
        for line in change_log:
            print(f"  {line}")

    print(f"\nGraph unchanged: {not graph_changed}")
    if not graph_changed:
        print("  → No meaningful synthesis changes justified on this run.")
    print(f"{'━'*60}\n")


# ────────────────────────────────────────────────────────────────────────────
# Idempotency check
# ────────────────────────────────────────────────────────────────────────────

def _recently_run(hours: int = IDEMPOTENCY_HOURS) -> bool:
    if not CANDIDATES_FILE.exists():
        return False
    age_seconds = (datetime.now(timezone.utc) - datetime.fromtimestamp(
        CANDIDATES_FILE.stat().st_mtime, tz=timezone.utc
    )).total_seconds()
    return age_seconds < hours * 3600


# ────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Theme Synthesis / Evolution Stage")
    parser.add_argument("--force", action="store_true", help="Run even if within 24h idempotency window")
    parser.add_argument("--dry-run", action="store_true", help="Print compact representation, no API calls")
    parser.add_argument("--synthesis-only", action="store_true", help="Skip critic pass and graph changes")
    args = parser.parse_args()

    if not args.force and not args.dry_run and _recently_run():
        print(f"[skip] synthesis_candidates.json was written within {IDEMPOTENCY_HOURS}h. Use --force to re-run.")
        return

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    print(f"[19_run_theme_synthesis] run_id={run_id}  model={LLM_MODEL} / critic={HAIKU_MODEL}")

    # Phase 0
    print("Phase 0: Loading graph…")
    graph = load_graph()
    print(f"  themes={len(graph['themes'])}  edges={len(graph['theme_edges'])}  meta_themes={len(graph['meta_themes'])}")
    print(f"  hypotheses={len(graph['hypotheses'])}  backtest_results={len(graph['backtest_results'])}  cards={len(graph['cards_by_id'])}")

    # Phase 1
    print("Phase 1: Building compact representation…")
    compact = build_compact_representation(graph)

    if args.dry_run:
        import json as _json
        text = _json.dumps(compact, indent=2)
        print(f"\nCompact representation ({len(text)} chars, ~{len(text)//4} tokens estimated):")
        print(text[:3000])
        if len(text) > 3000:
            print(f"\n… [truncated, full={len(text)} chars]")
        return

    # Phase 2
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    synthesis_prompt_user = _build_synthesis_user_prompt(compact)

    print("Phase 2: Calling synthesis pass (Sonnet)…")
    candidates_raw, synthesis_usage = call_synthesis_pass(client, compact)
    print(f"  {len(candidates_raw)} candidates proposed  |  tokens: {synthesis_usage['input_tokens']}in / {synthesis_usage['output_tokens']}out")

    # Assign candidate_ids
    now = datetime.now(timezone.utc).isoformat()
    for c in candidates_raw:
        c.setdefault("candidate_id", str(uuid.uuid4()))
        c.setdefault("status", "pending")
        c.setdefault("created_from_run", now)

    # Phase 3
    candidates_for_review, keep_separate = filter_for_critic(candidates_raw)
    print(f"Phase 3: {len(candidates_for_review)} candidates for critic review, {len(keep_separate)} keep_separate")

    # Phase 4
    reviews: list[dict] = []
    critic_usage: dict = {"input_tokens": 0, "output_tokens": 0}

    if not args.synthesis_only and candidates_for_review:
        print("Phase 4: Calling critic pass (Haiku)…")
        reviews, critic_usage = call_critic_pass(client, candidates_for_review)
        print(f"  {len(reviews)} reviews returned  |  tokens: {critic_usage['input_tokens']}in / {critic_usage['output_tokens']}out")
    elif args.synthesis_only:
        print("Phase 4: Skipped (--synthesis-only)")

    # Phase 5
    if not args.synthesis_only:
        print("Phase 5: Applying accepted candidates…")
        new_meta_themes, new_edges, new_themes, change_log = apply_accepted_candidates(
            graph, candidates_raw, reviews, run_id
        )
        graph_changed = bool(change_log and any(
            line.startswith(("CREATED", "STRENGTHENED", "ADDED", "FLAGGED"))
            for line in change_log
        ))
    else:
        new_meta_themes = graph["meta_themes"]
        new_edges = graph["theme_edges"]
        new_themes = graph["themes"]
        change_log = []
        graph_changed = False

    # Phase 6
    print("Phase 6: Persisting outputs…")
    run_snapshot = persist_outputs(
        run_id=run_id,
        compact=compact,
        candidates=candidates_raw,
        reviews=reviews,
        keep_separate=keep_separate,
        new_meta_themes=new_meta_themes,
        new_edges=new_edges,
        new_themes=new_themes,
        graph=graph,
        change_log=change_log,
        synthesis_usage=synthesis_usage,
        critic_usage=critic_usage,
        synthesis_prompt_system=_SYNTHESIS_SYSTEM,
        synthesis_prompt_user=synthesis_prompt_user,
        graph_changed=graph_changed,
    )

    # Phase 7
    print_audit_summary(
        run_id=run_id,
        candidates=candidates_raw,
        reviews=reviews,
        keep_separate=keep_separate,
        change_log=change_log,
        total_cost=run_snapshot["estimated_cost_usd"],
        graph_changed=graph_changed,
    )


if __name__ == "__main__":
    main()
