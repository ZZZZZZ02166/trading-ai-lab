#!/usr/bin/env python3
"""
Phase 18: Export backtest results to Obsidian vault.

Reads experiments/backtest_results.json + experiments/backtest_summary.json.
Writes:
  vault/Backtests/<hypothesis-slug>.md  — one per hypothesis with full result
  vault/Backtests/Backtest Summary.md   — aggregate table + verdicts

Links back to existing vault/Hypotheses/<slug>.md notes where they exist.

Usage:
    python scripts/18_export_backtest_vault.py
    python scripts/18_export_backtest_vault.py --force
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

EXPERIMENTS_DIR = BASE / "experiments"
RESULTS_FILE = EXPERIMENTS_DIR / "backtest_results.json"
SUMMARY_FILE = EXPERIMENTS_DIR / "backtest_summary.json"

VAULT_BACKTESTS = BASE / "vault" / "Backtests"
VAULT_HYPOTHESES = BASE / "vault" / "Hypotheses"

VAULT_BACKTESTS.mkdir(parents=True, exist_ok=True)

VERDICT_BADGE = {
    "supported": "✅ SUPPORTED",
    "inconclusive": "🟡 INCONCLUSIVE",
    "rejected": "❌ REJECTED",
    "insufficient_data": "⬜ INSUFFICIENT DATA",
}


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text[:80]


def hypothesis_note_link(hypothesis_title: str) -> str:
    """Return an Obsidian wikilink to the hypothesis vault note if it exists."""
    slug = slugify(hypothesis_title)
    hyp_path = VAULT_HYPOTHESES / f"{slug}.md"
    if hyp_path.exists():
        return f"[[{hypothesis_title}]]"
    return f"_{hypothesis_title}_"


def _phase1_section(p1: dict | None) -> str:
    """Render the Phase 1 Screening section for a vault note."""
    if not p1:
        return ""
    tier = p1.get("evidence_tier", "?")
    fidelity = p1.get("data_fidelity", "unknown")
    fidelity_src = p1.get("data_fidelity_source", "?")
    n_eff = p1.get("effective_n", 0)
    family = p1.get("metric_family", "?")
    family_src = p1.get("metric_family_source", "?")
    iq = p1.get("inference_quality", "?")
    fdr_p = p1.get("fdr_adjusted_p")
    fdr_str = f"{fdr_p:.4f}" if fdr_p is not None else "—"
    tier_score = p1.get("tier_score", 0)
    sample_score = p1.get("sample_score", 0)
    effect_score = p1.get("effect_score", 0)
    stat_score = p1.get("stat_score", 0)
    stab_points = p1.get("stability_points", 0)
    phase1_score = p1.get("phase1_score", 0)
    priority = p1.get("phase1_priority", "?")
    ci = p1.get("confidence_interval")
    ci_method = p1.get("ci_method", "")
    stat_test = p1.get("stat_test_used") or "—"
    stab_avail = p1.get("stability_available", False)
    stab_note = f"Measured (consistency: {p1.get('stability_score', 0):.0%})" if stab_avail else "Not measured (0 pts)"

    ci_disp = f"[{ci[0]:.4f}, {ci[1]:.4f}] ({ci_method})" if ci else f"Not available ({ci_method.replace('not_available:', '').replace('not_applicable:', 'N/A: ')})"

    PRIORITY_BADGE = {
        "promote":      "🟢 PROMOTE",
        "watchlist":    "🟡 WATCHLIST",
        "deprioritize": "🔴 DEPRIORITIZE",
        "blocked":      "⬜ BLOCKED",
    }
    badge = PRIORITY_BADGE.get(priority, priority.upper())

    return f"""
## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier ({tier}) | {tier_score:.0f} | 25 | Data fidelity: `{fidelity}` ({fidelity_src}) |
| Sample Adequacy (N_eff={n_eff}) | {sample_score:.1f} | 25 | Independence-adjusted count |
| Effect Size | {effect_score:.1f} | 20 | Family: `{family}` ({family_src}) |
| Statistical Reliability | {stat_score:.1f} | 20 | FDR-within-family p: {fdr_str} · IQ: {iq} |
| Stability | {stab_points:.1f} | 10 | {stab_note} |
| **Phase 1 Score** | **{phase1_score:.1f}** | **100** | |

**Priority: {badge}**  Stat test: `{stat_test}`
CI: {ci_disp}
"""


def render_backtest_note(r: dict, phase1: dict | None = None) -> str:
    hnum = r.get("hypothesis_number", "?")
    title = r.get("hypothesis_title", "")
    verdict = r.get("verdict", "unknown")
    badge = VERDICT_BADGE.get(verdict, verdict.upper())
    metric_name = r.get("metric_name", "")
    metric_val = r.get("metric_value")
    metric_disp = f"{metric_val:.4f}" if isinstance(metric_val, (int, float)) and metric_val == metric_val else "N/A"
    data_notes = r.get("data_notes", "")
    reason = r.get("verdict_reason", "")
    n_obs = r.get("n_observations", 0)
    n_sig = r.get("n_signals", 0)
    period_start = r.get("period_start", "")
    period_end = r.get("period_end", "")
    ticker = r.get("ticker", "QQQ")
    source = r.get("data_source", "ivolatility")
    raw_rows = r.get("raw_rows", 0)
    rows_after = r.get("rows_after_validation", n_obs)
    rows_excl = r.get("rows_excluded", raw_rows - rows_after if raw_rows else 0)
    excl_reason = r.get("exclusion_reason", "") or "—"

    hyp_link = hypothesis_note_link(title)

    # Extra metrics table
    extra = r.get("extra_metrics", {})
    extra_rows = "\n".join(f"| {k} | {v} |" for k, v in extra.items() if v is not None)
    extra_section = ""
    if extra_rows:
        extra_section = f"""
## Extra Metrics

| Metric | Value |
|--------|-------|
{extra_rows}
"""

    # Trades table
    trades = r.get("trades", [])
    trade_rows = "\n".join(
        f"| {t['date']} | {t['signal']:.4f} | {t['outcome']:.4f} | {t['notes']} |"
        for t in trades[:20]  # cap at 20 rows for readability
    )
    trades_section = ""
    if trade_rows:
        trades_section = f"""
## Event Records (up to 20)

| Date | Signal | Outcome | Notes |
|------|--------|---------|-------|
{trade_rows}
"""

    # Evidence-strength annotation
    data_flag = {
        "directly_tested": "> 🔬 **Directly tested** on live {ticker} price/options data.",
        "proxy_tested": "> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.",
        "insufficient_data": "> ❓ **Insufficient data** — required data was unavailable (endpoint entitlement or coverage gap). No verdict can be drawn.",
    }.get(data_notes, f"> ℹ️ data_notes: {data_notes}").replace("{ticker}", ticker)

    # Instrument mismatch annotation
    instrument_note = ""
    if "SPX" in title.upper() and ticker.upper() != "SPX":
        instrument_note = (
            f"\n> ⚠️ **Instrument note**: Original hypothesis references SPX. "
            f"This test was run on **{ticker}** as an adaptation. "
            f"QQQ tracks Nasdaq-100; SPX-specific microstructure effects may differ.\n"
        )

    return f"""---
hypothesis_number: {hnum}
verdict: {verdict}
ticker: {ticker}
start_date: {period_start}
end_date: {period_end}
data_source: {source}
data_notes: {data_notes}
observations: {n_obs}
signals: {n_sig}
primary_metric: {metric_name}
metric_value: {metric_disp}
---

# {hnum}: {title}

**{badge}**

{data_flag}
{instrument_note}
**Linked hypothesis:** {hyp_link}

## Data Coverage

| | |
|---|---|
| Tested window | {period_start} → {period_end} |
| Raw rows loaded | {raw_rows:,} |
| Rows after validation | {rows_after:,} |
| Rows excluded | {rows_excl:,} |
| Exclusion reason | {excl_reason} |
| Final observations tested | {n_obs:,} |
| Signal days | {n_sig:,} |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | {ticker} |
| Start Date | {period_start} |
| End Date | {period_end} |
| Observations | {n_obs:,} |
| Signals | {n_sig:,} |
| Primary Metric | {metric_name} |
| Metric Value | {metric_disp} |
| Data Source | {source} |
| Data Notes | {data_notes} |
| Support Threshold | {r.get("support_threshold", "—")} |
| Reject Threshold | {r.get("reject_threshold", "—")} |

## Verdict

**{badge}**

{reason}
{extra_section}{trades_section}{_phase1_section(phase1)}
## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: {ticker} only, {period_start} → {period_end}. Results may not generalise to other tickers, regimes, or time periods without further testing.
"""


def render_summary(summary: dict, results: list[dict],
                    phase1_lookup: dict | None = None) -> str:
    total = summary.get("total", 0)
    supported = summary.get("supported", 0)
    inconclusive = summary.get("inconclusive", 0)
    rejected = summary.get("rejected", 0)
    insuf = summary.get("insufficient_data", 0)

    PRIORITY_BADGE_SHORT = {
        "promote": "🟢",
        "watchlist": "🟡",
        "deprioritize": "🔴",
        "blocked": "⬜",
    }

    sorted_results = sorted(results, key=lambda x: x.get("hypothesis_number", ""))
    if phase1_lookup:
        # Sort promoted first, then watchlist, then deprioritize, then blocked
        priority_order = {"promote": 0, "watchlist": 1, "deprioritize": 2, "blocked": 3}
        sorted_results = sorted(
            sorted_results,
            key=lambda x: (
                priority_order.get(
                    (phase1_lookup.get(x.get("hypothesis_number", "")) or {}).get("phase1_priority", "deprioritize"),
                    2
                ),
                x.get("hypothesis_number", ""),
            )
        )

    row_parts = []
    for r in sorted_results:
        hnum = r["hypothesis_number"]
        p1 = (phase1_lookup or {}).get(hnum, {})
        score_str = f"{p1['phase1_score']:.0f}" if p1.get("phase1_score") is not None else "—"
        pri_badge = PRIORITY_BADGE_SHORT.get(p1.get("phase1_priority", ""), "")
        row_parts.append(
            f"| {hnum} | [[{hnum}: {r['hypothesis_title'][:38]}]] | "
            f"{VERDICT_BADGE.get(r['verdict'], r['verdict'])} | "
            f"{score_str} | {pri_badge} {p1.get('phase1_priority', '—')} | "
            f"{r.get('metric_value', 'N/A')} | {r.get('data_notes', '')} |"
        )
    rows = "\n".join(row_parts)

    phase1_note = ""
    if phase1_lookup:
        n_promote = sum(1 for v in phase1_lookup.values() if v.get("phase1_priority") == "promote")
        n_watch = sum(1 for v in phase1_lookup.values() if v.get("phase1_priority") == "watchlist")
        phase1_note = f"\n🟢 **{n_promote} promoted** · 🟡 **{n_watch} watchlist** — sorted by Phase 1 priority\n"

    return f"""# Backtest Summary — QQQ Options Research

Results from iVolatility data, all hypotheses tested on QQQ.
{phase1_note}
## Aggregate Verdicts

| Verdict | Count |
|---------|-------|
| ✅ Supported | {supported} |
| 🟡 Inconclusive | {inconclusive} |
| ❌ Rejected | {rejected} |
| ⬜ Insufficient Data | {insuf} |
| **Total** | **{total}** |

---

## Full Results

| # | Hypothesis | Verdict | P1 Score | Priority | Primary Metric | Data Notes |
|---|-----------|---------|----------|----------|----------------|-----------|
{rows}

---

## Navigation

- Click any hypothesis link to open its full backtest note
- Hypothesis notes link back to the source [[vault/Hypotheses/]] notes
- Source hypotheses are in [[Research Map]]
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    for path in (RESULTS_FILE, SUMMARY_FILE):
        if not path.exists():
            raise SystemExit(
                f"{path.name} not found. Run scripts/17_score_and_report.py first."
            )

    results = json.loads(RESULTS_FILE.read_text())
    summary = json.loads(SUMMARY_FILE.read_text())

    # Load Phase 1 scores if available
    phase1_file = BASE / "experiments" / "phase1_scores.json"
    phase1_lookup: dict | None = None
    if phase1_file.exists():
        try:
            phase1_lookup = {s["hypothesis_number"]: s
                             for s in json.loads(phase1_file.read_text())}
        except Exception:
            pass

    written = 0
    for r in results:
        hnum = r.get("hypothesis_number", "?")
        title = r.get("hypothesis_title", hnum)
        slug = slugify(f"{hnum}-{title}")
        out = VAULT_BACKTESTS / f"{slug}.md"

        p1 = (phase1_lookup or {}).get(hnum)
        out.write_text(render_backtest_note(r, phase1=p1))
        written += 1

    print(f"Wrote {written} backtest notes → {VAULT_BACKTESTS}")

    summary_path = VAULT_BACKTESTS / "Backtest Summary.md"
    summary_path.write_text(render_summary(summary, results, phase1_lookup=phase1_lookup))
    print(f"Wrote Backtest Summary → {summary_path}")

    print(f"\nTotal files in vault/Backtests/: {len(list(VAULT_BACKTESTS.glob('*.md')))}")


if __name__ == "__main__":
    main()
