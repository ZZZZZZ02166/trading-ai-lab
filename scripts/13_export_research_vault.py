#!/usr/bin/env python3
"""
Phase 13: Export research graph to Obsidian vault markdown.

Deterministic templating — reads JSON files, writes markdown.
No Claude API calls, no hardcoded content.

Writes:
  vault/Themes/<theme-slug>.md          — one per theme
  vault/MetaThemes/<meta-slug>.md       — one per meta-theme
  vault/Hypotheses/<hyp-slug>.md        — one per hypothesis
  vault/Synthesis/Research Map.md       — full graph summary

Usage:
    python scripts/13_export_research_vault.py
    python scripts/13_export_research_vault.py --force
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
THEMES_FILE = BASE / "themes" / "themes.json"
META_THEMES_FILE = BASE / "meta_themes" / "meta_themes.json"
HYPOTHESES_FILE = BASE / "experiments" / "hypotheses.json"
THEME_EDGES_FILE = BASE / "theme_edges" / "theme_edges.json"

VAULT_THEMES = BASE / "vault" / "Themes"
VAULT_META = BASE / "vault" / "MetaThemes"
VAULT_HYP = BASE / "vault" / "Hypotheses"
VAULT_SYNTH = BASE / "vault" / "Synthesis"

for d in (VAULT_THEMES, VAULT_META, VAULT_HYP, VAULT_SYNTH):
    d.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text[:80]


def tag_list(tags: list[str]) -> str:
    return " ".join(f"#{t.replace('-', '_')}" for t in tags[:8])


# ── Theme template ─────────────────────────────────────────────────────────────

def render_theme(t: dict, theme_edges: list[dict], meta_titles: dict[str, str]) -> str:
    status_badge = {"provisional": "🟡", "active": "🟢", "confirmed": "✅",
                    "needs_review": "🔴", "merged": "⚫", "retired": "⚪"}.get(t["status"], "")

    related = []
    for te in theme_edges:
        other_id = None
        if te["from_theme_id"] == t["theme_id"]:
            other_id = te["to_theme_id"]
            other_title = te.get("to_theme_title", other_id)
        elif te["to_theme_id"] == t["theme_id"]:
            other_id = te["from_theme_id"]
            other_title = te.get("from_theme_title", other_id)
        if other_id:
            related.append(f"- [[{other_title}]] — {te['relation_type']} (score {te['confidence']:.2f})")

    meta_refs = ""
    if t["theme_id"] in meta_titles:
        meta_refs = f"\n**Part of meta-theme:** [[{meta_titles[t['theme_id']]}]]\n"

    nr = ""
    if t.get("needs_review_reason"):
        nr = f"\n> ⚠️ **Needs review:** {t['needs_review_reason']}\n"

    tags_line = tag_list(t["top_tags"])

    related_str = "\n".join(related) if related else "_No high-confidence connections found._"

    return f"""---
theme_id: {t["theme_id"]}
status: {t["status"]}
card_count: {t["card_count"]}
book_count: {t["book_count"]}
avg_edge_confidence: {t["avg_edge_confidence"]}
tags: {t["top_tags"]}
created_at: {t["created_at"]}
---

# {t["title"]}

{status_badge} **Status:** {t["status"]} | **Cards:** {t["card_count"]} | **Books:** {t["book_count"]} | **Avg edge confidence:** {t["avg_edge_confidence"]:.3f}
{meta_refs}{nr}
{tags_line}

## Summary

{t["summary"]}

## Top Tags

{chr(10).join(f"- `{tag}`" for tag in t["top_tags"])}

## Related Themes

{related_str}

## Source Books

{chr(10).join(f"- `{doc_id}`" for doc_id in t["source_doc_ids"])}

## Linked Cards

{t["card_count"]} cards linked. See `source_card_ids` in `themes/themes.json`.
"""


# ── MetaTheme template ─────────────────────────────────────────────────────────

def render_meta_theme(m: dict) -> str:
    parents = "\n".join(f"- [[{title}]]" for title in m.get("parent_theme_titles", []))
    tags_line = tag_list(m["top_tags"])

    return f"""---
meta_theme_id: {m["meta_theme_id"]}
status: {m["status"]}
card_count: {m["card_count"]}
book_count: {m["book_count"]}
confidence: {m["confidence"]}
critic_composite_score: {m["critic_composite_score"]}
critic_cross_edge_count: {m["critic_cross_edge_count"]}
critic_centroid_cosine: {m["critic_centroid_cosine"]}
tags: {m["top_tags"]}
created_at: {m["created_at"]}
---

# {m["title"]}

🔗 **Meta-Theme** | **Cards:** {m["card_count"]} | **Books:** {m["book_count"]} | **Confidence:** {m["confidence"]:.3f}

{tags_line}

## Summary

{m["summary"]}

## Why These Themes Were Merged

{m["merge_reason"]}

## Parent Themes

{parents}

## Critic Gate Results

| Gate | Value | Threshold | Result |
|------|-------|-----------|--------|
| Composite score | {m["critic_composite_score"]:.3f} | ≥ 0.45 | ✅ |
| Cross-theme edges | {m["critic_cross_edge_count"]} | ≥ 3 | ✅ |
| Centroid cosine | {m["critic_centroid_cosine"]:.3f} | ≥ 0.62 | ✅ |

## Top Tags

{chr(10).join(f"- `{tag}`" for tag in m["top_tags"])}

## Source Books

{chr(10).join(f"- `{doc_id}`" for doc_id in m["source_doc_ids"])}
"""


# ── Hypothesis template ────────────────────────────────────────────────────────

def render_hypothesis(h: dict, theme_map: dict[str, str]) -> str:
    conf_bar = "█" * int(h.get("confidence", 0) * 10) + "░" * (10 - int(h.get("confidence", 0) * 10))
    tags_line = tag_list(h.get("tags", []))

    theme_links = []
    for tid in h.get("source_theme_ids", []):
        title = theme_map.get(tid, tid)
        if title != tid:
            theme_links.append(f"- [[{title}]]")
    theme_links_str = "\n".join(theme_links) if theme_links else "_None specified_"

    vars_str = "\n".join(f"- `{v}`" for v in h.get("variables_needed", []))
    support = h.get("what_would_support", "_Not specified_")
    reject = h.get("what_would_reject", "_Not specified_")

    return f"""---
hypothesis_id: {h["hypothesis_id"]}
status: {h["status"]}
confidence: {h["confidence"]}
tags: {h.get("tags", [])}
created_at: {h["created_at"]}
model_used: {h["model_used"]}
---

# {h["title"]}

**Status:** {h["status"]} | **Confidence:** {conf_bar} {h["confidence"]:.0%}

{tags_line}

## Claim

{h["claim"]}

## Rationale

{h["rationale"]}

## How to Test

{h["testability_notes"]}

**Data required:** {h.get("data_required", "_Not specified_")}

### Variables Needed

{vars_str if vars_str else "_Not specified_"}

### What Would Support It

{support}

### What Would Falsify It

{reject}

## Source Themes

{theme_links_str}

## Source Books

{chr(10).join(f"- `{doc_id}`" for doc_id in h.get("source_doc_ids", []))}
"""


# ── Research Map ───────────────────────────────────────────────────────────────

def render_research_map(themes: list, meta_themes: list, hypotheses: list, theme_edges: list) -> str:
    prov = [t for t in themes if t["status"] == "provisional"]
    nr = [t for t in themes if t["status"] == "needs_review"]

    theme_rows = "\n".join(
        f"| [[{t['title']}]] | {t['card_count']} | {t['book_count']} | {t['avg_edge_confidence']:.3f} | {t['status']} |"
        for t in themes
    )

    meta_rows = "\n".join(
        f"| [[{m['title']}]] | {m['card_count']} | {m['book_count']} | {', '.join(f'[[{p}]]' for p in m.get('parent_theme_titles', []))} |"
        for m in meta_themes
    )

    hyp_rows = "\n".join(
        f"| [[{h['title']}]] | {h.get('confidence', 0):.0%} | {h['status']} |"
        for h in hypotheses
    )

    edge_rows = "\n".join(
        f"| [[{te['from_theme_title']}]] | {te['relation_type']} | [[{te['to_theme_title']}]] | {te['confidence']:.3f} |"
        for te in sorted(theme_edges, key=lambda e: -e["confidence"])[:15]
    )

    total_cards = sum(t["card_count"] for t in themes)

    return f"""# Research Knowledge Graph — Map

Generated from the Options Research Brain pipeline.

## Summary Statistics

| Metric | Count |
|--------|-------|
| Themes | {len(themes)} ({len(prov)} provisional, {len(nr)} needs review) |
| Meta-Themes | {len(meta_themes)} |
| Hypotheses | {len(hypotheses)} |
| Theme Edges | {len(theme_edges)} |
| Total Cards in Themes | {total_cards} |

---

## Themes

| Theme | Cards | Books | Avg Confidence | Status |
|-------|-------|-------|----------------|--------|
{theme_rows}

---

## Meta-Themes

| Meta-Theme | Cards | Books | Parent Themes |
|------------|-------|-------|--------------|
{meta_rows}

---

## Top Theme Connections (by composite score)

| From | Relation | To | Score |
|------|----------|----|-------|
{edge_rows}

---

## Hypotheses

| Hypothesis | Confidence | Status |
|------------|------------|--------|
{hyp_rows}

---

## How to Navigate

- Click any [[Theme]] link to open the theme note
- Themes contain links to related themes and their source books
- Meta-themes show merged themes and the critic gate results
- Hypotheses contain full testability notes and data requirements
"""


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    for path in (THEMES_FILE, META_THEMES_FILE, HYPOTHESES_FILE, THEME_EDGES_FILE):
        if not path.exists():
            raise SystemExit(f"{path.name} not found. Run prior pipeline steps first.")

    themes = json.loads(THEMES_FILE.read_text())
    meta_themes = json.loads(META_THEMES_FILE.read_text())
    hypotheses = json.loads(HYPOTHESES_FILE.read_text())
    theme_edges = json.loads(THEME_EDGES_FILE.read_text())

    theme_map: dict[str, str] = {t["theme_id"]: t["title"] for t in themes}
    meta_titles: dict[str, str] = {}
    for m in meta_themes:
        for pid in m.get("parent_theme_ids", []):
            meta_titles[pid] = m["title"]

    written = 0

    # Themes
    for t in themes:
        slug = slugify(t["title"])
        out = VAULT_THEMES / f"{slug}.md"
        if out.exists() and not args.force:
            continue
        out.write_text(render_theme(t, theme_edges, meta_titles))
        written += 1

    print(f"Wrote {len(themes)} theme notes → {VAULT_THEMES}")

    # Meta-themes
    for m in meta_themes:
        slug = slugify(m["title"])
        out = VAULT_META / f"{slug}.md"
        if out.exists() and not args.force:
            continue
        out.write_text(render_meta_theme(m))
        written += 1

    print(f"Wrote {len(meta_themes)} meta-theme notes → {VAULT_META}")

    # Hypotheses
    for h in hypotheses:
        slug = slugify(h["title"])
        out = VAULT_HYP / f"{slug}.md"
        if out.exists() and not args.force:
            continue
        out.write_text(render_hypothesis(h, theme_map))
        written += 1

    print(f"Wrote {len(hypotheses)} hypothesis notes → {VAULT_HYP}")

    # Research Map
    map_path = VAULT_SYNTH / "Research Map.md"
    if not map_path.exists() or args.force:
        map_path.write_text(render_research_map(themes, meta_themes, hypotheses, theme_edges))
        print(f"Wrote Research Map → {map_path}")
        written += 1

    print(f"\nTotal files written: {written}")


if __name__ == "__main__":
    main()
