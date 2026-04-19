#!/usr/bin/env python3
"""
Phase 1 Hypothesis Screening Framework.

Reads experiments/backtest_results.json.
Computes a composite Phase 1 score (0-100) and priority (promote/watchlist/deprioritize/blocked)
for each hypothesis. Writes experiments/phase1_scores.json.

Classification pipeline for metric_family:
  1. Explicit field in result (runner-set) → use directly
  2. Pattern match on metric_name → assign family
  3. If ambiguous ("needs_review") → Haiku AI call (max 5, cached)
  4. Still unresolved → "other" (0 effect score, flagged)

Evidence tier uses data_fidelity field (runner-set preferred) with conservative fallback from
data_notes + data_source. AI is NOT used for tier — downgrade when uncertain.

Usage:
    python scripts/19b_score_phase1.py
    python scripts/19b_score_phase1.py --force
    python scripts/19b_score_phase1.py --dry-run
    python scripts/19b_score_phase1.py --no-ai
    python scripts/19b_score_phase1.py --reclassify   # redo AI classifications too
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

EXPERIMENTS_DIR = BASE / "experiments"
RESULTS_FILE = EXPERIMENTS_DIR / "backtest_results.json"
SCORES_FILE = EXPERIMENTS_DIR / "phase1_scores.json"
LOGS_DIR = BASE / "logs"
LOGS_DIR.mkdir(exist_ok=True)

HAIKU_MODEL = "claude-haiku-4-5-20251001"

# ── metric_family pattern matching ──────────────────────────────────────────
METRIC_FAMILY_PATTERNS = [
    ("rmse",                "estimator_accuracy"),
    ("dm_test",             "estimator_accuracy"),
    ("hurst",               "persistence"),
    ("spearman_r",          "correlation"),
    ("sharpe_ratio",        "strategy_sharpe"),
    ("win_rate",            "strategy_win_rate"),
    ("var_ratio",           "strategy_win_rate"),
    ("variance_premium",    "premium_mean"),
    ("garch_vp",            "premium_mean"),
    ("implied_minus_real",  "premium_mean"),
    ("mean_iv_drop",        "iv_level_change"),
    ("mean_iv_change",      "iv_level_change"),
    ("mean_skew_change",    "iv_level_change"),
    ("ar1_reversion",       "regime_comparison"),
    ("kurtosis",            "distribution"),
    ("dd_reduction",        "risk_sizing"),
    ("gamma_pnl",           "mean_difference"),
    ("reversal",            "mean_difference"),
    ("pnl",                 "mean_difference"),
    ("u_shape",             "intraday_pattern"),
    ("rv_open_close",       "intraday_pattern"),
    ("mean_reversion",      "intraday_pattern"),
    ("spread_open",         "spread_comparison"),
    ("spread_after",        "spread_comparison"),
    ("hedge_cost",          "cost_ratio"),
]

VALID_FAMILIES = {
    "estimator_accuracy", "persistence", "correlation", "strategy_sharpe",
    "strategy_win_rate", "premium_mean", "iv_level_change", "regime_comparison",
    "distribution", "risk_sizing", "mean_difference", "intraday_pattern",
    "spread_comparison", "cost_ratio", "other",
}

# ── effect size thresholds ───────────────────────────────────────────────────
EFFECT_THRESHOLDS: dict[str, tuple[str, float]] = {
    "correlation":        ("abs_r",        0.30),
    "persistence":        ("hurst_dev",    0.10),
    "estimator_accuracy": ("rmse_improv",  0.20),
    "strategy_sharpe":    ("sharpe",       0.50),
    "strategy_win_rate":  ("wr_excess",    0.10),
    "premium_mean":       ("vp_pts",       1.50),
    "iv_level_change":    ("abs_iv_chg",   1.00),
    "mean_difference":    ("abs_diff",     0.50),
    "regime_comparison":  ("speed_ratio",  1.50),
    "distribution":       ("excess_kurt",  3.00),
    "risk_sizing":        ("dd_reduction", 0.10),
    "spread_comparison":  ("ratio_excess", 0.20),
    "intraday_pattern":   ("ratio_excess", 0.20),
    "cost_ratio":         ("cost_improv",  0.20),
}

# ── p-value keys to scan in extra_metrics ───────────────────────────────────
P_KEYS = [
    "p_value", "p_ttest", "p_spearman", "p_dm_test", "p_binomial",
    "p_kurtosis_bootstrap", "bootstrap_p", "p_open_vs_mid",
    "p_garch_vs_zero", "p_mid_vs_others", "p_mannwhitney",
    "p_regime_mannwhitney",
]


# ── helpers ──────────────────────────────────────────────────────────────────

def classify_metric_family_pattern(metric_name: str) -> str:
    mn = metric_name.lower()
    for fragment, family in METRIC_FAMILY_PATTERNS:
        if fragment in mn:
            return family
    return "needs_review"


def classify_metric_family_ai(client, result: dict) -> str:
    """Single Haiku call to classify metric_family. Returns family string."""
    prompt_families = " | ".join(sorted(VALID_FAMILIES))
    try:
        resp = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=20,
            temperature=0.0,
            system=(
                f"Return exactly one value from this list with no other text:\n{prompt_families}"
            ),
            messages=[{"role": "user", "content": (
                f"Hypothesis: {result.get('hypothesis_title', '')}. "
                f"Metric name: {result.get('metric_name', '')}. "
                f"Claim (first 150 chars): {result.get('verdict_reason', '')[:150]}"
            )}],
        )
        family = resp.content[0].text.strip().lower()
        if family in VALID_FAMILIES:
            return family
    except Exception as e:
        print(f"    [AI classify] error: {e}")
    return "other"


def _log_ai_usage(input_tok: int, output_tok: int):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "script": "19b_score_phase1",
        "model": HAIKU_MODEL,
        "input_tokens": input_tok,
        "output_tokens": output_tok,
        "estimated_cost_usd": round(input_tok * 0.0000008 + output_tok * 0.000001, 6),
    }
    with open(LOGS_DIR / "api_usage.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")


def get_metric_family(result: dict, cached_classifications: dict, client, ai_budget: list,
                      allow_ai: bool) -> tuple[str, str]:
    """Returns (metric_family, source: 'stored'|'pattern_match'|'ai_assisted'|'other')."""
    hnum = result.get("hypothesis_number", "")

    # 1. Explicit stored field
    stored = result.get("metric_family") or result.get("extra_metrics", {}).get("metric_family")
    if stored and stored in VALID_FAMILIES:
        return stored, "stored"

    # 2. Check cache (from prior AI calls)
    if hnum in cached_classifications:
        cached = cached_classifications[hnum]
        if cached in VALID_FAMILIES and cached != "needs_review":
            return cached, "ai_assisted"

    # 3. Pattern match
    family = classify_metric_family_pattern(result.get("metric_name", ""))
    if family != "needs_review":
        return family, "pattern_match"

    # 4. AI fallback (budget-limited)
    if allow_ai and client and ai_budget[0] > 0:
        ai_budget[0] -= 1
        family = classify_metric_family_ai(client, result)
        cached_classifications[hnum] = family
        return family, "ai_assisted"

    return "other", "other"


def classify_tier(result: dict) -> tuple[str, str, str]:
    """Returns (tier: A|B|C|D, data_fidelity, fidelity_source: explicit|derived|uncertain)."""
    # 1. Explicit field
    fidelity = result.get("data_fidelity")
    if fidelity:
        source = "explicit"
    else:
        # 2. Conservative derivation
        data_notes = result.get("data_notes", "")
        data_source = result.get("data_source", "")
        if data_notes == "insufficient_data":
            fidelity, source = "insufficient", "derived"
        elif data_notes == "proxy_tested":
            fidelity, source = "index_proxy", "derived"
        elif data_notes == "directly_tested" and "databento" in data_source.lower():
            fidelity, source = "exact_underlying", "derived"
        elif data_notes == "directly_tested" and "ivolatility" in data_source.lower():
            fidelity, source = "constant_maturity_iv", "derived"  # conservative
        else:
            fidelity, source = "uncertain", "uncertain"

    tier_map = {
        "exact_contract":       "A",
        "exact_underlying":     "B",
        "constant_maturity_iv": "B",
        "index_proxy":          "C",
        "uncertain":            "C",
        "insufficient":         "D",
    }
    tier = tier_map.get(fidelity, "C")
    return tier, fidelity, source


def compute_effective_n(metric_family: str, n_obs: int, n_sig: int) -> tuple[int, int]:
    """Returns (n_eff, reference) for sample adequacy scoring."""
    if metric_family in {"estimator_accuracy", "persistence"}:
        return max(n_obs // 20, 1), 15
    if metric_family in {"mean_difference", "iv_level_change", "regime_comparison",
                          "strategy_win_rate", "strategy_sharpe", "spread_comparison",
                          "cost_ratio"}:
        return n_sig, 30
    if metric_family in {"correlation", "premium_mean", "distribution",
                          "risk_sizing", "intraday_pattern"}:
        return n_obs, 200
    # other / needs_review: conservative
    return min(n_obs, n_sig) if n_sig > 0 else n_obs, 200


def compute_effect_score(metric_family: str, metric_value, verdict: str) -> float:
    if verdict == "insufficient_data" or metric_value is None:
        return 0.0
    if metric_family not in EFFECT_THRESHOLDS:
        return 0.0
    _, threshold = EFFECT_THRESHOLDS[metric_family]
    mv = float(metric_value)
    if metric_family == "estimator_accuracy":
        normalized = (1.0 - mv) / threshold
    elif metric_family == "persistence":
        normalized = abs(mv - 0.5) / threshold
    elif metric_family == "strategy_win_rate":
        normalized = (mv - 0.50) / threshold
    elif metric_family in {"spread_comparison", "intraday_pattern", "cost_ratio"}:
        if metric_family == "cost_ratio":
            normalized = (1.0 - mv) / threshold
        else:
            normalized = (mv - 1.0) / threshold
    elif metric_family in {"correlation", "iv_level_change", "mean_difference"}:
        normalized = abs(mv) / threshold
    else:
        normalized = mv / threshold
    return round(min(max(normalized, 0.0), 1.0) * 20.0, 3)


def extract_p_value(extra_metrics: dict) -> tuple[float | None, str | None]:
    """Returns (raw_p, stat_test_name)."""
    for key in P_KEYS:
        val = extra_metrics.get(key)
        if val is not None and isinstance(val, (int, float)) and not math.isnan(val):
            test_name = (
                key.replace("p_", "").replace("_bootstrap", "_bootstrap")
                   .replace("p_value", "ttest")
            )
            return float(val), test_name
    return None, None


def compute_ci(metric_family: str, metric_value, n_eff: int,
               extra_metrics: dict) -> tuple[list | None, str]:
    """Returns ([lo, hi], method_str) or (None, 'not_available:<reason>')."""
    mv = float(metric_value) if metric_value is not None else None

    if metric_family == "correlation" and mv is not None and n_eff > 10:
        r = max(-0.9999, min(0.9999, mv))
        z = math.atanh(r)
        se = 1.0 / math.sqrt(n_eff - 3)
        lo = math.tanh(z - 1.96 * se)
        hi = math.tanh(z + 1.96 * se)
        return [round(lo, 4), round(hi, 4)], "fisher_z_transform"

    if metric_family == "strategy_win_rate" and mv is not None and n_eff > 0:
        p = max(0.0001, min(0.9999, mv))
        margin = 1.96 * math.sqrt(p * (1 - p) / n_eff)
        return [round(max(0.0, p - margin), 4), round(min(1.0, p + margin), 4)], "wilson_interval"

    if metric_family in {"mean_difference", "iv_level_change", "premium_mean", "intraday_pattern"}:
        mean = extra_metrics.get("mean") or extra_metrics.get("mean_diff")
        std = extra_metrics.get("std") or extra_metrics.get("std_diff")
        n = extra_metrics.get("n") or n_eff
        if mean is not None and std is not None and n and n > 1:
            se = std / math.sqrt(n)
            lo = mean - 1.96 * se
            hi = mean + 1.96 * se
            return [round(lo, 4), round(hi, 4)], "normal_ci"
        return None, "not_available:mean_std_not_in_extra_metrics"

    if metric_family == "estimator_accuracy":
        dm = extra_metrics.get("dm_statistic") or extra_metrics.get("dm_stat")
        dm_se = extra_metrics.get("dm_se") or extra_metrics.get("dm_std")
        if dm is not None and dm_se is not None:
            lo = dm - 1.96 * dm_se
            hi = dm + 1.96 * dm_se
            return [round(lo, 4), round(hi, 4)], "dm_test_ci"
        return None, "not_available:dm_se_not_stored"

    if metric_family == "strategy_sharpe":
        return None, "not_available:requires_raw_return_series"
    if metric_family == "persistence":
        return None, "not_available:requires_bootstrap_distribution"
    if metric_family == "distribution":
        return None, "not_available:bootstrap_values_not_stored"
    if metric_family == "risk_sizing":
        return None, "not_applicable:single_path_simulation"

    return None, "not_available:insufficient_extra_metrics"


def classify_inference_quality(metric_family: str, n_eff: int, evidence_tier: str,
                                stat_test_used: str | None, raw_p: float | None) -> str:
    """Returns 'strong' | 'standard' | 'weak'."""
    test = (stat_test_used or "").lower()
    # Weak conditions (first match)
    if raw_p is None:
        return "weak"
    if n_eff < 15:
        return "weak"
    if metric_family == "estimator_accuracy" and "dm_test" not in test and "bootstrap" not in test:
        return "weak"
    if evidence_tier == "D":
        return "weak"
    # Strong conditions
    if "bootstrap" in test or "permutation" in test:
        return "strong"
    if (evidence_tier in {"A", "B"} and n_eff >= 50
            and metric_family not in {"estimator_accuracy", "persistence"}):
        return "strong"
    return "standard"


IQ_MULTIPLIER = {"strong": 1.00, "standard": 0.85, "weak": 0.60}


def compute_stability(metric_value, extra_metrics: dict) -> tuple[float | None, bool, float]:
    """Returns (stability_score [0-1] or None, stability_available, weight)."""
    mv = float(metric_value) if metric_value is not None else None
    overall_sign = (mv > 0) if mv is not None else None

    if "month_summary" in extra_metrics:
        months = extra_metrics["month_summary"]
        valid = [
            v for v in months.values()
            if isinstance(v, dict)
            and v.get("n_days_with_data", 0) >= 5
            and v.get("metric_value") is not None
        ]
        if len(valid) >= 3 and overall_sign is not None:
            consistent = sum(1 for v in valid if (v["metric_value"] > 0) == overall_sign)
            return consistent / len(valid), True, 1.0
        if len(valid) == 2 and overall_sign is not None:
            consistent = sum(1 for v in valid if (v["metric_value"] > 0) == overall_sign)
            return consistent / len(valid), True, 0.5
        return None, False, 0.0

    # Regime-level fallback: look for sub-group metric keys
    if overall_sign is not None:
        regime_vals = []
        for k, v in extra_metrics.items():
            if isinstance(v, (int, float)) and not math.isnan(v):
                # Match keys like excess_kurtosis_low_iv, some_metric_high, etc.
                if re.search(r'_(low|mid|high|fear|calm|normal)(_iv)?$', k):
                    regime_vals.append(v)
        if len(regime_vals) >= 2:
            consistent = sum(1 for v in regime_vals if (v > 0) == overall_sign)
            return consistent / len(regime_vals), True, 1.0

    return None, False, 0.0


def bh_correct(p_list: list[float]) -> list[float]:
    m = len(p_list)
    if m <= 1:
        return list(p_list)
    sorted_idx = sorted(range(m), key=lambda i: p_list[i])
    adj = [0.0] * m
    for rank, i in enumerate(sorted_idx, 1):
        adj[i] = min(1.0, p_list[i] * m / rank)
    running_min = 1.0
    for i in reversed(sorted_idx):
        running_min = min(running_min, adj[i])
        adj[i] = running_min
    return adj


# ── main scoring ─────────────────────────────────────────────────────────────

def score_all(results: list[dict], allow_ai: bool, cached_classifications: dict,
              client) -> list[dict]:
    ai_budget = [5]  # max AI calls
    scored = []

    # Pass 1: classify families, tiers, compute all scores except FDR
    intermediates = []
    for r in results:
        hnum = r.get("hypothesis_number", "?")
        verdict = r.get("verdict", "")
        data_notes = r.get("data_notes", "")
        metric_value = r.get("metric_value")
        metric_name = r.get("metric_name", "")
        n_obs = r.get("n_observations", 0)
        n_sig = r.get("n_signals", 0)
        raw_rows = r.get("raw_rows", 0)
        rows_excl = r.get("rows_excluded", 0)
        extra = r.get("extra_metrics", {})

        # metric_family
        family, family_source = get_metric_family(r, cached_classifications, client,
                                                   ai_budget, allow_ai)

        # evidence tier
        tier, data_fidelity, fidelity_source = classify_tier(r)
        tier_score = {"A": 25, "B": 20, "C": 10, "D": 0}[tier]

        # sample adequacy
        n_eff, ref = compute_effective_n(family, n_obs, n_sig)
        # Clamp excl_rate to [0, 1] — negative values indicate a data counting mismatch
        raw_excl_rate = rows_excl / raw_rows if raw_rows > 0 else 0.0
        excl_rate = max(0.0, min(1.0, raw_excl_rate))
        obs_score = min(n_eff / ref, 1.0)
        excl_penalty = max(0.0, 1.0 - excl_rate * 2.0)
        sample_score = round(min((obs_score * 0.7 + excl_penalty * 0.3) * 25.0, 25.0), 2)

        # effect size
        effect_score = compute_effect_score(family, metric_value, verdict)

        # p-value + CI
        raw_p, stat_test = extract_p_value(extra)
        ci, ci_method = compute_ci(family, metric_value, n_eff, extra)

        # inference quality
        iq = classify_inference_quality(family, n_eff, tier, stat_test, raw_p)
        iq_mult = IQ_MULTIPLIER[iq]

        # stability
        stab_score, stab_avail, stab_weight = compute_stability(metric_value, extra)
        stability_points = round((stab_score * stab_weight * 10.0) if stab_score is not None else 0.0, 2)

        intermediates.append({
            "hypothesis_number": hnum,
            "hypothesis_title": r.get("hypothesis_title", ""),
            "verdict": verdict,
            "metric_family": family,
            "metric_family_source": family_source,
            "evidence_tier": tier,
            "data_fidelity": data_fidelity,
            "data_fidelity_source": fidelity_source,
            "inference_quality": iq,
            "tier_score": tier_score,
            "effective_n": n_eff,
            "effective_n_ref": ref,
            "sample_score": sample_score,
            "effect_score": effect_score,
            "raw_p_value": raw_p,
            "stat_test_used": stat_test,
            "confidence_interval": ci,
            "ci_method": ci_method,
            "stability_score": stab_score,
            "stability_available": stab_avail,
            "stability_points": stability_points,
            "iq_multiplier": iq_mult,
            "data_notes": data_notes,
            "n_observations": n_obs,
            "n_signals": n_sig,
        })

    # Pass 2: FDR correction within metric_family groups, then globally
    # Within-family
    family_groups: dict[str, list[int]] = defaultdict(list)
    for idx, item in enumerate(intermediates):
        if item["data_notes"] != "insufficient_data" and item["raw_p_value"] is not None:
            family_groups[item["metric_family"]].append(idx)

    fdr_within: dict[int, float] = {}
    for family, idxs in family_groups.items():
        ps = [intermediates[i]["raw_p_value"] for i in idxs]
        adj = bh_correct(ps)
        for i, adj_p in zip(idxs, adj):
            fdr_within[i] = round(adj_p, 6)

    # Global FDR (reference only)
    all_testable = [(idx, item["raw_p_value"]) for idx, item in enumerate(intermediates)
                    if item["data_notes"] != "insufficient_data" and item["raw_p_value"] is not None]
    global_fdr: dict[int, float] = {}
    if all_testable:
        all_ps = [p for _, p in all_testable]
        all_adj = bh_correct(all_ps)
        for (idx, _), adj_p in zip(all_testable, all_adj):
            global_fdr[idx] = round(adj_p, 6)

    # Pass 3: compute final scores
    for idx, item in enumerate(intermediates):
        verdict = item["verdict"]
        fdr_p = fdr_within.get(idx)
        global_p = global_fdr.get(idx)
        raw_p = item["raw_p_value"]
        iq_mult = item["iq_multiplier"]

        # stat score using FDR-adjusted p
        p_for_score = fdr_p if fdr_p is not None else raw_p
        if p_for_score is None:
            base_stat = 0
        elif p_for_score <= 0.01:
            base_stat = 20
        elif p_for_score <= 0.05:
            base_stat = 15
        elif p_for_score <= 0.10:
            base_stat = 10
        elif p_for_score <= 0.20:
            base_stat = 5
        else:
            base_stat = 0
        stat_score = round(base_stat * iq_mult, 2)

        phase1_score = round(
            item["tier_score"] + item["sample_score"] +
            item["effect_score"] + stat_score + item["stability_points"],
            2,
        )

        if verdict == "insufficient_data":
            priority = "blocked"
        elif phase1_score >= 80:
            priority = "promote"
        elif phase1_score >= 65:
            priority = "watchlist"
        else:
            priority = "deprioritize"

        scored.append({
            "hypothesis_number": item["hypothesis_number"],
            "hypothesis_title": item["hypothesis_title"],
            "verdict": verdict,
            "metric_family": item["metric_family"],
            "metric_family_source": item["metric_family_source"],
            "evidence_tier": item["evidence_tier"],
            "data_fidelity": item["data_fidelity"],
            "data_fidelity_source": item["data_fidelity_source"],
            "inference_quality": item["inference_quality"],
            "tier_score": item["tier_score"],
            "effective_n": item["effective_n"],
            "effective_n_ref": item["effective_n_ref"],
            "sample_score": item["sample_score"],
            "effect_score": item["effect_score"],
            "stat_score": stat_score,
            "stability_score": item["stability_score"],
            "stability_available": item["stability_available"],
            "stability_points": item["stability_points"],
            "phase1_score": phase1_score,
            "phase1_priority": priority,
            "raw_p_value": raw_p,
            "fdr_adjusted_p": fdr_p,
            "global_fdr_p": global_p,
            "confidence_interval": item["confidence_interval"],
            "ci_method": item["ci_method"],
            "stat_test_used": item["stat_test_used"],
            "n_observations": item["n_observations"],
            "n_signals": item["n_signals"],
            "data_notes": item["data_notes"],
        })

    scored.sort(key=lambda x: x.get("hypothesis_number", ""))
    return scored


def print_audit_table(scored: list[dict]):
    PRIORITY_BADGE = {
        "promote":      "🟢 PROMOTE",
        "watchlist":    "🟡 watchlist",
        "deprioritize": "🔴 deprioritize",
        "blocked":      "⬜ BLOCKED",
    }
    print(f"\n{'─'*100}")
    print(f"Phase 1 Screening — {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'─'*100}")
    hdr = f"{'#':<5} {'Title':<35} {'Family':<20} {'Tier':<4} {'IQ':<4} {'Score':>6}  {'Priority':<18} {'FDR-p':<8}"
    print(hdr)
    print(f"{'─'*100}")

    counts = {"promote": 0, "watchlist": 0, "deprioritize": 0, "blocked": 0}
    fdr_survivors = 0
    ai_count = sum(1 for s in scored if s["metric_family_source"] == "ai_assisted")
    other_count = sum(1 for s in scored if s["metric_family_source"] == "other")

    for s in scored:
        hnum = s["hypothesis_number"]
        title = s["hypothesis_title"][:33]
        family = s["metric_family"][:18]
        tier = s["evidence_tier"]
        iq = s["inference_quality"][:3]
        score = f"{s['phase1_score']:.1f}"
        priority = s["phase1_priority"]
        badge = PRIORITY_BADGE.get(priority, priority)
        fdr_p = s["fdr_adjusted_p"]
        fdr_str = f"{fdr_p:.3f}" if fdr_p is not None else "  —  "
        if fdr_p is not None and fdr_p <= 0.05:
            fdr_survivors += 1
        counts[priority] = counts.get(priority, 0) + 1
        print(f"{hnum:<5} {title:<35} {family:<20} {tier:<4} {iq:<4} {score:>6}  {badge:<18} {fdr_str:<8}")

    print(f"{'─'*100}")
    print(f"Promoted: {counts['promote']}  Watchlist: {counts['watchlist']}  "
          f"Deprioritized: {counts['deprioritize']}  Blocked: {counts['blocked']}")
    print(f"FDR within-family survivors (α=0.05): {fdr_survivors} of {len(scored)}")
    if ai_count:
        print(f"AI-classified families: {ai_count}  Other/unresolved: {other_count}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Recompute even if scores exist")
    parser.add_argument("--dry-run", action="store_true", help="Print table, no write")
    parser.add_argument("--no-ai", action="store_true", help="Skip AI fallback classification")
    parser.add_argument("--reclassify", action="store_true", help="Redo AI classifications")
    args = parser.parse_args()

    if not RESULTS_FILE.exists():
        raise SystemExit(f"{RESULTS_FILE.name} not found. Run backtests first.")

    if SCORES_FILE.exists() and not args.force and not args.dry_run:
        existing = json.loads(SCORES_FILE.read_text())
        print(f"phase1_scores.json exists ({len(existing)} entries). Use --force to recompute.")
        return

    results = json.loads(RESULTS_FILE.read_text())
    if not results:
        raise SystemExit("backtest_results.json is empty.")

    # Load cached AI classifications (to avoid re-calling API unnecessarily)
    cached_classifications: dict[str, str] = {}
    if SCORES_FILE.exists() and not args.reclassify:
        try:
            existing = json.loads(SCORES_FILE.read_text())
            for s in existing:
                if s.get("metric_family_source") == "ai_assisted":
                    cached_classifications[s["hypothesis_number"]] = s["metric_family"]
        except Exception:
            pass

    allow_ai = not args.no_ai
    client = None
    if allow_ai:
        try:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            pass

    scored = score_all(results, allow_ai, cached_classifications, client)
    print_audit_table(scored)

    if not args.dry_run:
        SCORES_FILE.write_text(json.dumps(scored, indent=2))
        print(f"\nWrote {len(scored)} Phase 1 scores → {SCORES_FILE}")


if __name__ == "__main__":
    main()
