"""
H58-ATM-PROXY Feasibility Study.

Original H58 ("First-30-Min Option Volume Direction → ROD") remains BLOCKED
(full-chain intraday volume unavailable; iVol 403 Forbidden).

This script tests an ATM-centric proxy version using the available subset of
intraday contract files. Coverage is variable (median ~49%, min ~3.5%) so
results are run on two datasets:
  - all_dates:     all qualifying dates (≥4 call + ≥4 put files)
  - high_coverage: subset where proxy coverage ≥ 20% of daily chain volume

Signal timing (confirmed, no lookahead):
  - optionVolume at 10:00 bar = cumulative first-30-min (09:30:00–09:59:59)
    (bar-start semantics confirmed: 09:30 bar starts at 0)
  - Outcome entry: Databento 1m open at 10:01 ET
  - Outcome exit:  Databento 1m close at 15:59 ET

Output:
  experiments/phase2_results/H58_atm_proxy.json
  vault/Backtests/h58-*.md  (Phase 2 proxy section appended)
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr
from scipy.stats import rankdata as scipy_rankdata

try:
    import statsmodels.api as sm
    HAS_SM = True
except ImportError:
    HAS_SM = False

# ── Paths ─────────────────────────────────────────────────────────────────────

BASE = Path(__file__).resolve().parent.parent
CHAINS_DIR  = BASE / "data" / "raw" / "chains"
DATABENTO_DIR = BASE / "data" / "raw" / "databento"
RESULTS_DIR = BASE / "experiments" / "phase2_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

_ET = "America/New_York"

# Walk-forward splits (two only — chain data ends 2025-12-31)
TRAIN_START, TRAIN_END = "2024-01-01", "2024-12-31"
VAL_START,   VAL_END   = "2025-01-01", "2025-12-31"

MIN_CALL_FILES = 4
MIN_PUT_FILES  = 4
HIGH_COVERAGE_THRESHOLD = 0.20   # coverage_pct >= 20% to be "high coverage"
MIN_QUALIFYING_FOR_VERDICT = 80  # need ≥80 high-coverage dates for primary verdict

CALL_HEAVY = 0.60
PUT_HEAVY  = 0.40


# ── Utilities (self-contained) ─────────────────────────────────────────────────

def cliff_delta(g1, g2):
    g1, g2 = np.asarray(g1, float), np.asarray(g2, float)
    if len(g1) == 0 or len(g2) == 0:
        return np.nan
    dom = int((g1[:, None] > g2[None, :]).sum()) - int((g1[:, None] < g2[None, :]).sum())
    return dom / (len(g1) * len(g2))


def mw_test(g1, g2, alternative="two-sided"):
    g1 = np.asarray(g1, float); g1 = g1[np.isfinite(g1)]
    g2 = np.asarray(g2, float); g2 = g2[np.isfinite(g2)]
    if len(g1) < 5 or len(g2) < 5:
        return {"n_a": len(g1), "n_b": len(g2), "stat": None, "p": None,
                "cliff_d": None,
                "median_a": float(np.median(g1)) if len(g1) else None,
                "median_b": float(np.median(g2)) if len(g2) else None,
                "diff": None}
    stat, p = mannwhitneyu(g1, g2, alternative=alternative)
    return {
        "n_a": int(len(g1)), "n_b": int(len(g2)),
        "stat": float(stat), "p": float(p),
        "cliff_d": float(cliff_delta(g1, g2)),
        "median_a": float(np.median(g1)), "median_b": float(np.median(g2)),
        "diff": float(np.median(g1) - np.median(g2)),
    }


def nw_spearman(x, y, maxlags=3):
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    n = len(x)
    if n < 20:
        return {"rho": None, "p_nw": None, "n": n}
    rho, p_scipy = spearmanr(x, y)
    if HAS_SM:
        rx = scipy_rankdata(x) / n
        ry = scipy_rankdata(y) / n
        X = sm.add_constant(rx)
        p_nw = float(sm.OLS(ry, X).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags}).pvalues[1])
    else:
        p_nw = float(p_scipy)
    return {"rho": float(rho), "p_nw": float(p_nw), "n": int(n)}


def _cbb_idx(rng, n, block):
    n_blocks = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=n_blocks)
    idx = []
    for s in starts:
        idx.extend([(s + k) % n for k in range(block)])
    return np.array(idx[:n])


def block_bootstrap_diff(outcome, mask_a, mask_b, n_boot=2000, block=5, seed=42):
    rng = np.random.default_rng(seed)
    observed = float(np.median(outcome[mask_a]) - np.median(outcome[mask_b]))
    diffs = []
    n = len(outcome)
    for _ in range(n_boot):
        idx = _cbb_idx(rng, n, block)
        bo = outcome[idx]; bma = mask_a[idx]; bmb = mask_b[idx]
        if bma.sum() > 1 and bmb.sum() > 1:
            diffs.append(float(np.median(bo[bma]) - np.median(bo[bmb])))
    d = np.array(diffs)
    p_boot = float((d <= 0).mean())
    ci = (float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5)))
    return observed, p_boot, ci


def hac_ols(x, y, maxlags=3):
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    n = len(x)
    if n < 20 or not HAS_SM:
        return {"beta": None, "p": None, "r2": None, "n": n}
    X = sm.add_constant(x)
    res = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
    return {
        "beta": float(res.params[1]),
        "p": float(res.pvalues[1]),
        "r2": float(res.rsquared),
        "n": int(n),
    }


# ── Load Databento 1m bars ─────────────────────────────────────────────────────

def load_all_1m() -> pd.DataFrame:
    files = sorted(DATABENTO_DIR.glob("qqq_1m_*.parquet"))
    df = pd.concat([pd.read_parquet(f) for f in files]).sort_index()
    if df.index.tzinfo is None:
        df.index = df.index.tz_localize(_ET)
    return df


def build_rod_features(bars_1m: pd.DataFrame) -> pd.DataFrame:
    """
    For each trading day:
      open_1001  = 1m bar open at 10:01 ET (entry after signal is known)
      close_1559 = 1m bar close at 15:59 ET (exit)
      rod_return = (close_1559 - open_1001) / open_1001
    """
    rows = []
    for d in sorted(set(bars_1m.index.date)):
        mask = bars_1m.index.date == d
        day = bars_1m.loc[mask]
        if day.empty:
            continue
        # Open at 10:01 (entry)
        bar_1001 = day[day.index.time == pd.Timestamp("10:01").time()]
        # Close at 15:59 (exit)
        bar_1559 = day[day.index.time == pd.Timestamp("15:59").time()]
        if bar_1001.empty or bar_1559.empty:
            continue
        open_1001  = float(bar_1001["open"].iloc[0])
        close_1559 = float(bar_1559["close"].iloc[0])
        rod_return = (close_1559 - open_1001) / open_1001
        rows.append({
            "date": pd.Timestamp(d),
            "open_1001":  open_1001,
            "close_1559": close_1559,
            "rod_return": rod_return,
        })
    return pd.DataFrame(rows).set_index("date")


# ── Step 0 — Monotonicity verification ────────────────────────────────────────

def verify_monotonicity(sample_dates: list) -> dict:
    """
    For a sample of dates, check that optionVolume is non-decreasing within each file.
    Also count how many dates lack a 10:00 bar (need 09:55 fallback).
    """
    n_files_checked = 0
    n_files_with_resets = 0
    n_dates_missing_10am = 0
    n_dates_missing_0955 = 0

    for date_str in sample_dates:
        files = list(CHAINS_DIR.glob(f"intraday_QQQ___*_{date_str}_MINUTE_5.parquet"))
        has_10am = False
        has_0955 = False
        for f in files:
            n_files_checked += 1
            df = pd.read_parquet(f)
            df["_ts"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("_ts").reset_index(drop=True)
            # Check monotonicity
            vol = df["optionVolume"].values
            if np.any(np.diff(vol) < 0):
                n_files_with_resets += 1
            # Check for 10:00 bar
            times = df["_ts"].dt.time.astype(str)
            if any("10:00:00" in t for t in times):
                has_10am = True
            if any("09:55:00" in t for t in times):
                has_0955 = True
        if files:
            if not has_10am:
                n_dates_missing_10am += 1
                if not has_0955:
                    n_dates_missing_0955 += 1

    return {
        "n_files_checked": n_files_checked,
        "n_files_with_resets": n_files_with_resets,
        "pct_files_with_resets": round(n_files_with_resets / max(n_files_checked, 1), 4),
        "n_dates_sampled": len(sample_dates),
        "n_dates_missing_10am_bar": n_dates_missing_10am,
        "n_dates_missing_0955_fallback": n_dates_missing_0955,
        "monotonicity_ok": n_files_with_resets <= max(1, int(0.05 * n_files_checked)),
    }


# ── Step 1 — Build signal + coverage table ─────────────────────────────────────

def _get_vol_at_signal_bar(files: list) -> float:
    """Read all files of same type (call or put), return sum of optionVolume at 10:00 bar."""
    total = 0.0
    for f in files:
        df = pd.read_parquet(f)
        df["_ts"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("_ts").reset_index(drop=True)
        # Try 10:00 bar first
        bar = df[df["_ts"].dt.strftime("%H:%M:%S") == "10:00:00"]
        if bar.empty:
            # Fallback: last bar ≤ 09:55
            bar = df[df["_ts"].dt.strftime("%H:%M:%S") <= "09:55:00"]
            if bar.empty:
                continue
            bar = bar.iloc[[-1]]
        total += float(bar["optionVolume"].iloc[0])
    return total


def _get_eod_vol(files: list) -> float:
    """Sum EOD (last bar) optionVolume across all files."""
    total = 0.0
    for f in files:
        df = pd.read_parquet(f)
        if df.empty:
            continue
        total += float(df["optionVolume"].iloc[-1])
    return total


def build_signal_table() -> pd.DataFrame:
    """
    For each trading date with ≥4 call + ≥4 put intraday files:
    - Compute call_pct (first-30-min ATM proxy PCR)
    - Compute coverage_pct vs daily agg call volume
    Returns DataFrame with one row per qualifying date.
    """
    # Group files by date
    all_files = sorted(CHAINS_DIR.glob("intraday_QQQ___*_MINUTE_5.parquet"))
    by_date: dict[str, dict] = {}
    for f in all_files:
        # Filename format: intraday_QQQ___250401C00470000_20250401_MINUTE_5
        # tokens after split('_'): ['intraday','QQQ','','','250401C00470000','20250401','MINUTE','5']
        tokens = f.stem.split("_")
        # Trade date: 8-digit all-numeric token (YYYYMMDD)
        trade_date = None
        for t in tokens:
            if len(t) == 8 and t.isdigit():
                trade_date = t
        if trade_date is None:
            continue
        # Contract segment: token with ≥12 chars containing C or P (e.g. '250401C00470000')
        cp = None
        for t in tokens:
            if len(t) >= 12:
                for ch in t:
                    if ch == "C":
                        cp = "C"
                        break
                    if ch == "P":
                        cp = "P"
                        break
                if cp is not None:
                    break
        if cp is None:
            continue
        if trade_date not in by_date:
            by_date[trade_date] = {"C": [], "P": []}
        by_date[trade_date][cp].append(f)

    rows = []
    for date_str in sorted(by_date.keys()):
        call_files = by_date[date_str]["C"]
        put_files  = by_date[date_str]["P"]
        if len(call_files) < MIN_CALL_FILES or len(put_files) < MIN_PUT_FILES:
            continue

        # Signal: first-30-min ATM call/put volume
        call_vol_30m = _get_vol_at_signal_bar(call_files)
        put_vol_30m  = _get_vol_at_signal_bar(put_files)
        total_30m = call_vol_30m + put_vol_30m
        if total_30m == 0:
            continue
        call_pct = call_vol_30m / total_30m

        # Coverage: compare EOD intraday call vol vs daily agg call vol
        call_eod = _get_eod_vol(call_files)
        agg_path = CHAINS_DIR / f"qqq_opts_by_param_{date_str}_C.parquet"
        if agg_path.exists():
            agg_df = pd.read_parquet(agg_path)
            agg_call_vol = float(agg_df["volume"].sum()) if "volume" in agg_df.columns else np.nan
        else:
            agg_call_vol = np.nan
        coverage_pct = call_eod / agg_call_vol if agg_call_vol and agg_call_vol > 0 else np.nan

        rows.append({
            "date": pd.Timestamp(date_str),
            "n_call_files": len(call_files),
            "n_put_files": len(put_files),
            "call_vol_30m": call_vol_30m,
            "put_vol_30m": put_vol_30m,
            "call_pct": call_pct,
            "call_eod_vol": call_eod,
            "agg_call_vol": agg_call_vol,
            "coverage_pct": coverage_pct,
        })

    df = pd.DataFrame(rows).set_index("date").sort_index()
    return df


# ── Coverage audit stats ───────────────────────────────────────────────────────

def coverage_stats(cov_series: pd.Series) -> dict:
    c = cov_series.dropna()
    return {
        "n_dates_audited": int(len(c)),
        "coverage_pct_min": round(float(c.min()), 4),
        "coverage_pct_p25": round(float(c.quantile(0.25)), 4),
        "coverage_pct_median": round(float(c.median()), 4),
        "coverage_pct_p75": round(float(c.quantile(0.75)), 4),
        "coverage_pct_max": round(float(c.max()), 4),
        "coverage_pct_mean": round(float(c.mean()), 4),
        "coverage_pct_std": round(float(c.std()), 4),
        "coverage_pct_cv": round(float(c.std() / c.mean()), 4) if c.mean() > 0 else None,
        "n_dates_below_10pct": int((c < 0.10).sum()),
        "n_dates_below_20pct": int((c < 0.20).sum()),
    }


# ── Analysis ───────────────────────────────────────────────────────────────────

def run_analysis(df: pd.DataFrame, label: str) -> dict:
    """Run full statistical analysis on a signal_df (with call_pct and rod_return)."""
    df = df.dropna(subset=["call_pct", "rod_return"])
    n = len(df)
    if n < 20:
        return {"label": label, "n": n, "insufficient": True}

    x = df["call_pct"].values
    y = df["rod_return"].values

    # 1. Continuous Spearman + NW-HAC
    sp = nw_spearman(x, y, maxlags=3)
    ols = hac_ols(x, y, maxlags=3)

    # 2. Quintile bucket table
    try:
        df["quintile"] = pd.qcut(df["call_pct"], 5, labels=["Q1","Q2","Q3","Q4","Q5"])
        quintile_table = {}
        for q in ["Q1","Q2","Q3","Q4","Q5"]:
            sub = df[df["quintile"] == q]["rod_return"]
            quintile_table[q] = {
                "n": int(len(sub)),
                "median_rod": float(np.median(sub)) if len(sub) > 0 else None,
                "mean_rod": float(np.mean(sub)) if len(sub) > 0 else None,
            }
    except Exception:
        quintile_table = {}

    # 3. Binary comparison at main threshold
    call_heavy_mask = df["call_pct"] > CALL_HEAVY
    put_heavy_mask  = df["call_pct"] < PUT_HEAVY
    binary_mw = mw_test(y[call_heavy_mask.values], y[put_heavy_mask.values], "two-sided")
    if call_heavy_mask.sum() > 1 and put_heavy_mask.sum() > 1:
        obs, p_boot, ci = block_bootstrap_diff(
            y, call_heavy_mask.values, put_heavy_mask.values
        )
        binary_mw["p_bootstrap"] = float(p_boot)
        binary_mw["ci_95_boot"] = list(ci)
    binary_mw["n_call_heavy"] = int(call_heavy_mask.sum())
    binary_mw["n_put_heavy"] = int(put_heavy_mask.sum())

    # 4. Threshold sensitivity (brief)
    sensitivity = {}
    for lo, hi in [(0.55, 0.45), (0.60, 0.40), (0.65, 0.35)]:
        ch = y[x > hi]
        ph = y[x < lo]
        sensitivity[f"{int(hi*100)}/{int(lo*100)}"] = {
            "n_call_heavy": int(len(ch)),
            "n_put_heavy": int(len(ph)),
            "median_ch": float(np.median(ch)) if len(ch) > 0 else None,
            "median_ph": float(np.median(ph)) if len(ph) > 0 else None,
            "diff": float(np.median(ch) - np.median(ph)) if len(ch) > 0 and len(ph) > 0 else None,
        }

    # 5. Walk-forward (train=2024, val=2025 only)
    wf_splits = {}
    signs = []
    for split_name, (s, e) in [("train", (TRAIN_START, TRAIN_END)), ("val", (VAL_START, VAL_END))]:
        sub = df.loc[s:e].dropna(subset=["call_pct", "rod_return"])
        r = nw_spearman(sub["call_pct"].values, sub["rod_return"].values, maxlags=3)
        wf_splits[split_name] = {**r, "n_qualifying": int(len(sub))}
        if r["rho"] is not None:
            signs.append(np.sign(r["rho"]))
    same_sign = len(signs) == 2 and signs[0] == signs[1]
    wf_splits["same_sign_train_val"] = same_sign

    return {
        "label": label,
        "n": int(n),
        "n_call_heavy": int(call_heavy_mask.sum()),
        "n_put_heavy": int(put_heavy_mask.sum()),
        "continuous_spearman": sp,
        "hac_ols": ols,
        "quintile_table": quintile_table,
        "binary_mw": binary_mw,
        "sensitivity": sensitivity,
        "walk_forward": wf_splits,
    }


# ── Verdict ────────────────────────────────────────────────────────────────────

def compute_verdict(analysis: dict, n_high_coverage: int, using_high_coverage: bool) -> tuple[str, str]:
    if analysis.get("insufficient"):
        return "insufficient_data", f"n={analysis.get('n',0)} qualifying dates — too few for inference"

    sp = analysis.get("continuous_spearman", {})
    rho = sp.get("rho")
    p_nw = sp.get("p_nw")
    n = analysis.get("n", 0)
    wf = analysis.get("walk_forward", {})
    same_sign = wf.get("same_sign_train_val", False)

    if n < 80:
        return "insufficient_data", f"n={n} qualifying dates below minimum of 80"

    rho_train = (wf.get("train") or {}).get("rho")
    rho_val   = (wf.get("val")   or {}).get("rho")

    if rho is None or p_nw is None:
        return "inconclusive", "Could not compute Spearman"

    if abs(rho) > 0.10 and p_nw < 0.10 and same_sign:
        return "supported", f"rho={rho:.3f}, p_nw={p_nw:.4f}, same_sign_train_val=True"
    elif p_nw > 0.30 or (rho_train is not None and rho_val is not None
                          and abs(rho_train) < 0.05 and abs(rho_val) < 0.05):
        return "rejected", f"rho={rho:.3f}, p_nw={p_nw:.4f}, both splits near zero"
    else:
        return "inconclusive", f"rho={rho:.3f}, p_nw={p_nw:.4f}, same_sign={same_sign}"


# ── Vault output ───────────────────────────────────────────────────────────────

def append_vault_note(result: dict) -> None:
    vault_files = sorted((BASE / "vault" / "Backtests").glob("h58-*.md"))
    if not vault_files:
        print("  [warn] No vault/Backtests/h58-*.md found — skipping vault update")
        return
    target = vault_files[0]

    v_all = result.get("verdict_all_dates", "n/a")
    v_hc  = result.get("verdict_high_coverage", "n/a")
    final = result.get("final_verdict", "n/a")
    diag  = result.get("diagnostics", {})
    cov   = diag.get("proxy_coverage", {})
    mono  = diag.get("monotonicity_check", {})
    a_all = result.get("analysis_all_dates", {})
    a_hc  = result.get("analysis_high_coverage", {})

    def sp_line(a):
        sp = a.get("continuous_spearman", {})
        return f"rho={sp.get('rho','n/a')}, p_nw={sp.get('p_nw','n/a')}, n={sp.get('n','n/a')}"

    lines = [
        "",
        "## H58-ATM-PROXY — Feasibility Study (Phase 2 Extension)",
        "",
        "**⚠️ This is NOT the original H58 test.** Original H58 (full-chain PCR) remains BLOCKED.",
        "This is an ATM-centric proxy study using the sparse contract subset in `data/raw/chains/`.",
        "",
        "### Coverage Audit",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Dates audited | {cov.get('n_dates_audited','n/a')} |",
        f"| Coverage min | {cov.get('coverage_pct_min','n/a'):.1%} |" if isinstance(cov.get('coverage_pct_min'), float) else f"| Coverage min | n/a |",
        f"| Coverage 25th pct | {cov.get('coverage_pct_p25','n/a'):.1%} |" if isinstance(cov.get('coverage_pct_p25'), float) else f"| Coverage 25th pct | n/a |",
        f"| Coverage median | {cov.get('coverage_pct_median','n/a'):.1%} |" if isinstance(cov.get('coverage_pct_median'), float) else f"| Coverage median | n/a |",
        f"| Coverage 75th pct | {cov.get('coverage_pct_p75','n/a'):.1%} |" if isinstance(cov.get('coverage_pct_p75'), float) else f"| Coverage 75th pct | n/a |",
        f"| Coverage max | {cov.get('coverage_pct_max','n/a'):.1%} |" if isinstance(cov.get('coverage_pct_max'), float) else f"| Coverage max | n/a |",
        f"| CV (std/mean) | {cov.get('coverage_pct_cv','n/a')} |",
        f"| Dates below 20% | {cov.get('n_dates_below_20pct','n/a')} |",
        "",
        f"**Monotonicity:** {mono.get('n_files_with_resets', 'n/a')} files with resets out of {mono.get('n_files_checked','n/a')} checked.",
        f"Missing 10:00 bar (used 09:55 fallback): {mono.get('n_dates_missing_10am_bar','n/a')} dates.",
        "",
        "### Signal Timing",
        "",
        "- Signal: `optionVolume` at 10:00 bar = cumulative first-30-min flow (09:30–09:59:59, bar-start semantics confirmed)",
        "- Entry: Databento 1m **open at 10:01 ET** (1 min gap after signal is finalized)",
        "- Exit: Databento 1m **close at 15:59 ET**",
        "",
        "### Verdicts",
        "",
        f"| Dataset | n | Verdict | Continuous Spearman |",
        f"|---|---|---|---|",
        f"| all_dates | {a_all.get('n','n/a')} | {v_all.upper()} | {sp_line(a_all)} |",
        f"| high_coverage (≥20%) | {a_hc.get('n','n/a')} | {v_hc.upper()} | {sp_line(a_hc)} |",
        f"| **Final** | — | **{final.upper()}** | — |",
        "",
        "### Walk-Forward Spearman",
        "",
        "| Split | all_dates rho | all_dates p_nw | high_cov rho | high_cov p_nw |",
        "|---|---|---|---|---|",
    ]

    for split in ["train", "val"]:
        wf_all = (a_all.get("walk_forward") or {}).get(split, {})
        wf_hc  = (a_hc.get("walk_forward")  or {}).get(split, {})
        r_all = f"{wf_all.get('rho','n/a'):.3f}" if isinstance(wf_all.get("rho"), float) else "n/a"
        p_all = f"{wf_all.get('p_nw','n/a'):.4f}" if isinstance(wf_all.get("p_nw"), float) else "n/a"
        r_hc  = f"{wf_hc.get('rho','n/a'):.3f}" if isinstance(wf_hc.get("rho"), float) else "n/a"
        p_hc  = f"{wf_hc.get('p_nw','n/a'):.4f}" if isinstance(wf_hc.get("p_nw"), float) else "n/a"
        lines.append(f"| {split} | {r_all} | {p_all} | {r_hc} | {p_hc} |")

    lines += [
        "",
        "### Binary Comparison (call_pct > 0.60 vs < 0.40)",
        "",
    ]
    bm = a_hc.get("binary_mw", {}) or a_all.get("binary_mw", {})
    lines += [
        f"n_call_heavy={bm.get('n_call_heavy','n/a')}, n_put_heavy={bm.get('n_put_heavy','n/a')}, ",
        f"diff={bm.get('diff','n/a')}, p={bm.get('p','n/a')}, Cliff's d={bm.get('cliff_d','n/a')}",
        "",
        "**Conclusion:** ATM-centric proxy coverage is highly variable (CV≈0.49). "
        "Results are exploratory. Original H58 (full-chain PCR) remains BLOCKED.",
        "",
    ]

    with open(target, "a") as f:
        f.write("\n".join(lines))
    print(f"  [vault] Appended proxy section to {target.name}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("H58-ATM-PROXY Feasibility Study")
    print("=" * 50)

    out_path = RESULTS_DIR / "H58_atm_proxy.json"

    # ── Step 0: Monotonicity verification ─────────────────────────────────────
    print("\nStep 0: Monotonicity verification (sample of dates)...")
    all_intraday = sorted(CHAINS_DIR.glob("intraday_QQQ___*_MINUTE_5.parquet"))
    # Extract unique dates from filenames
    all_date_strs = set()
    for f in all_intraday:
        for t in f.stem.split("_"):
            if len(t) == 8 and t.isdigit():
                all_date_strs.add(t)
    sorted_dates = sorted(all_date_strs)
    # Sample 10 from 2024, 10 from 2025
    dates_2024 = [d for d in sorted_dates if d.startswith("2024")]
    dates_2025 = [d for d in sorted_dates if d.startswith("2025")]
    sample = dates_2024[::max(1, len(dates_2024)//10)][:10] + dates_2025[::max(1, len(dates_2025)//10)][:10]
    mono_check = verify_monotonicity(sample)
    if not mono_check["monotonicity_ok"]:
        print(f"  [WARN] {mono_check['n_files_with_resets']} files have decreasing optionVolume!")
    else:
        print(f"  Monotonicity OK — {mono_check['n_files_with_resets']} resets in {mono_check['n_files_checked']} files")
    print(f"  Missing 10:00 bar: {mono_check['n_dates_missing_10am_bar']} dates")

    # ── Step 1: Build signal table ─────────────────────────────────────────────
    print("\nStep 1: Building ATM PCR signal table (scanning all chain files)...")
    sig_df = build_signal_table()
    print(f"  {len(sig_df)} qualifying dates (≥{MIN_CALL_FILES}C + {MIN_PUT_FILES}P files)")

    # Coverage audit
    cov_stats = coverage_stats(sig_df["coverage_pct"])
    print(f"  Coverage: median={cov_stats['coverage_pct_median']:.1%}, "
          f"min={cov_stats['coverage_pct_min']:.1%}, max={cov_stats['coverage_pct_max']:.1%}, "
          f"CV={cov_stats['coverage_pct_cv']}")
    print(f"  Dates below 20% coverage: {cov_stats['n_dates_below_20pct']}")

    # ── Step 2: Load Databento ROD features ───────────────────────────────────
    print("\nStep 2: Loading Databento 1m bars for ROD return...")
    bars_1m = load_all_1m()
    rod_df = build_rod_features(bars_1m)
    print(f"  {len(rod_df)} trading days with 10:01 open and 15:59 close")

    # ── Merge ─────────────────────────────────────────────────────────────────
    merged = sig_df.join(rod_df[["rod_return"]], how="inner")
    merged = merged.dropna(subset=["call_pct", "rod_return"])
    print(f"  {len(merged)} days after merge with ROD data")

    # Two datasets
    high_cov_mask = merged["coverage_pct"] >= HIGH_COVERAGE_THRESHOLD
    df_all = merged
    df_hc  = merged[high_cov_mask]
    print(f"  all_dates: n={len(df_all)}, high_coverage (≥{HIGH_COVERAGE_THRESHOLD:.0%}): n={len(df_hc)}")

    # ── Step 4: Analysis ──────────────────────────────────────────────────────
    print("\nStep 4: Running statistical analysis...")
    analysis_all = run_analysis(df_all, "all_dates")
    analysis_hc  = run_analysis(df_hc,  "high_coverage")

    sp_all = analysis_all.get("continuous_spearman", {})
    sp_hc  = analysis_hc.get("continuous_spearman", {})
    print(f"  all_dates:     rho={sp_all.get('rho','n/a')}, p_nw={sp_all.get('p_nw','n/a')}")
    print(f"  high_coverage: rho={sp_hc.get('rho','n/a')}, p_nw={sp_hc.get('p_nw','n/a')}")

    # ── Verdicts ──────────────────────────────────────────────────────────────
    v_all, r_all = compute_verdict(analysis_all, len(df_hc), using_high_coverage=False)
    v_hc,  r_hc  = compute_verdict(analysis_hc,  len(df_hc), using_high_coverage=True)

    # Final verdict: use high_coverage if adequate, else fall back to all_dates with note
    if len(df_hc) >= MIN_QUALIFYING_FOR_VERDICT:
        final_verdict = v_hc
        final_reason  = f"[high_coverage primary] {r_hc}"
    else:
        final_verdict = v_all
        final_reason  = f"[all_dates fallback — high_coverage n={len(df_hc)} < {MIN_QUALIFYING_FOR_VERDICT}] {r_all}"

    print(f"\n  Verdict all_dates: {v_all.upper()}")
    print(f"  Verdict high_coverage: {v_hc.upper()}")
    print(f"  Final verdict: {final_verdict.upper()}")

    # ── Build result JSON ─────────────────────────────────────────────────────
    result = {
        "hypothesis_number": "H58",
        "proxy_label": "H58_atm_proxy",
        "original_h58_status": "BLOCKED — full chain intraday volume unavailable (iVol 403 Forbidden); this is a proxy/feasibility study only",
        "data_fidelity_label": "atm_chain_proxy",
        "data_fidelity_warning": (
            f"Proxy coverage is highly variable: median={cov_stats['coverage_pct_median']:.1%}, "
            f"CV={cov_stats['coverage_pct_cv']}, min={cov_stats['coverage_pct_min']:.1%}. "
            "Some dates capture <5% of total chain flow. Results reflect near-ATM option flow "
            "only and cannot be generalized to full-chain PCR. This study is exploratory."
        ),
        "signal_timing": (
            "optionVolume at 10:00 bar = cumulative first-30-min flow (09:30:00–09:59:59). "
            "Bar-start semantics confirmed (09:30 bar = 0). "
            "Outcome entry: Databento 1m open at 10:01 ET. Outcome exit: 15:59 close. "
            "1-minute gap between signal finalization and outcome entry — no lookahead."
        ),
        "verdict_all_dates": v_all,
        "verdict_all_dates_reason": r_all,
        "verdict_high_coverage": v_hc,
        "verdict_high_coverage_reason": r_hc,
        "final_verdict": final_verdict,
        "final_verdict_reason": final_reason,
        "diagnostics": {
            "monotonicity_check": mono_check,
            "proxy_coverage": cov_stats,
            "n_qualifying_all": int(len(df_all)),
            "n_qualifying_high_coverage": int(len(df_hc)),
            "high_coverage_threshold": HIGH_COVERAGE_THRESHOLD,
            "min_qualifying_for_primary_verdict": MIN_QUALIFYING_FOR_VERDICT,
        },
        "analysis_all_dates": analysis_all,
        "analysis_high_coverage": analysis_hc,
    }

    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nSaved → {out_path.relative_to(BASE)}")

    append_vault_note(result)
    print("\nDone.")


if __name__ == "__main__":
    main()
