#!/usr/bin/env python3
"""
Phase 17: Score all backtest results and write summary.

Reads experiments/backtest_results.json.
Prints a verdict table to stdout.
Writes experiments/backtest_summary.json.

Usage:
    python scripts/17_score_and_report.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from app.models.backtest_result import BacktestVerdict

EXPERIMENTS_DIR = BASE / "experiments"
RESULTS_FILE = EXPERIMENTS_DIR / "backtest_results.json"
SUMMARY_FILE = EXPERIMENTS_DIR / "backtest_summary.json"

VERDICT_SCORE = {
    BacktestVerdict.SUPPORTED: 1,
    BacktestVerdict.INCONCLUSIVE: 0,
    BacktestVerdict.REJECTED: -1,
    BacktestVerdict.INSUFFICIENT_DATA: None,
}

VERDICT_EMOJI = {
    "supported": "✅",
    "inconclusive": "🟡",
    "rejected": "❌",
    "insufficient_data": "⬜",
}


def main():
    if not RESULTS_FILE.exists():
        raise SystemExit(
            f"backtest_results.json not found at {RESULTS_FILE}.\n"
            "Run scripts/15_run_daily_backtests.py and scripts/16_run_intraday_backtests.py first."
        )

    results = json.loads(RESULTS_FILE.read_text())
    if not results:
        raise SystemExit("backtest_results.json is empty.")

    results.sort(key=lambda r: r.get("hypothesis_number", ""))

    counts = {v.value: 0 for v in BacktestVerdict}
    summary_rows = []

    print(f"\n{'─'*90}")
    print(f"{'Hyp':<5} {'Verdict':<16} {'Metric':<30} {'Value':>10} {'N_sig':>6}  {'Data notes':<25}")
    print(f"{'─'*90}")

    for r in results:
        hnum = r.get("hypothesis_number", "?")
        verdict_str = r.get("verdict", "?")
        emoji = VERDICT_EMOJI.get(verdict_str, "?")
        metric_name = r.get("metric_name", "?")[:28]
        metric_val = r.get("metric_value")
        metric_disp = f"{metric_val:.4f}" if isinstance(metric_val, (int, float)) and metric_val == metric_val else "N/A"
        n_sig = r.get("n_signals", 0)
        data_notes = r.get("data_notes", "")[:23]

        print(f"{hnum:<5} {emoji} {verdict_str:<14} {metric_name:<30} {metric_disp:>10} {n_sig:>6}  {data_notes:<25}")

        if verdict_str in counts:
            counts[verdict_str] += 1

        summary_rows.append({
            "hypothesis_number": hnum,
            "hypothesis_title": r.get("hypothesis_title", ""),
            "verdict": verdict_str,
            "metric_name": r.get("metric_name", ""),
            "metric_value": metric_val,
            "n_observations": r.get("n_observations", 0),
            "n_signals": n_sig,
            "data_notes": r.get("data_notes", ""),
            "verdict_reason": r.get("verdict_reason", ""),
            "period_start": r.get("period_start", ""),
            "period_end": r.get("period_end", ""),
        })

    print(f"{'─'*90}")
    print(f"\nSummary ({len(results)} hypotheses):")
    print(f"  ✅ Supported:          {counts['supported']}")
    print(f"  🟡 Inconclusive:       {counts['inconclusive']}")
    print(f"  ❌ Rejected:           {counts['rejected']}")
    print(f"  ⬜ Insufficient data:  {counts['insufficient_data']}")

    summary = {
        "total": len(results),
        "supported": counts["supported"],
        "inconclusive": counts["inconclusive"],
        "rejected": counts["rejected"],
        "insufficient_data": counts["insufficient_data"],
        "hypotheses": summary_rows,
    }
    SUMMARY_FILE.write_text(json.dumps(summary, indent=2))
    print(f"\nWrote summary → {SUMMARY_FILE}")

    # Run Phase 1 screening scorer
    scorer = BASE / "scripts" / "19b_score_phase1.py"
    if scorer.exists():
        print("\n[phase1] Running 19b_score_phase1.py...")
        subprocess.run([sys.executable, str(scorer), "--force"], check=False)

    # Enrich backtest_summary.json with phase1 fields if scores are available
    phase1_file = EXPERIMENTS_DIR / "phase1_scores.json"
    if phase1_file.exists():
        try:
            phase1_lookup = {s["hypothesis_number"]: s
                             for s in json.loads(phase1_file.read_text())}
            for row in summary_rows:
                p1 = phase1_lookup.get(row["hypothesis_number"], {})
                row["phase1_score"] = p1.get("phase1_score")
                row["phase1_priority"] = p1.get("phase1_priority")
                row["evidence_tier"] = p1.get("evidence_tier")
                row["inference_quality"] = p1.get("inference_quality")
            summary["hypotheses"] = summary_rows
            SUMMARY_FILE.write_text(json.dumps(summary, indent=2))
        except Exception as e:
            print(f"[phase1] Could not enrich summary: {e}")

    print("Next: run scripts/18_export_backtest_vault.py")


if __name__ == "__main__":
    main()
