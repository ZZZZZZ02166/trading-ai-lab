"""
H58-ATM-PROXY Phase 2B — Incremental value beyond early price action.

Phase 2A finding: rho=0.86 between call_pct and rod_return, but likely
momentum-proxy contamination (ATM flow mirrors first-30-min price direction,
which continues into rest of day).

This script tests whether the ATM-flow proxy adds predictive value BEYOND
early underlying price action.

Signal timing (unchanged from Phase 2A):
  call_pct at 10:00 bar = cumulative first-30-min option flow
  Entry: Databento 1m open at 10:01 ET
  Exit:  Databento 1m close at 15:59 ET

New price-action controls (all knowable at 10:00:00):
  first_30m_return   = (close_09:59 - open_09:30) / open_09:30
  first_30m_range    = (max_high - min_low from 09:30-09:59) / open_09:30
  first_30m_abs_ret  = abs(first_30m_return)
  overnight_gap      = (open_09:30 / prev_session_close_15:59) - 1

Internal 2025 split (no 2024 data qualifies):
  TRAIN = 2025-04-01 to 2025-08-31 (~105 qualifying dates)
  VAL   = 2025-09-01 to 2025-12-31 (~85 qualifying dates)
  Dates before 2025-04-01 excluded from train/val comparison.

Tests:
  A. Baseline OLS: rod_return ~ first_30m_return + first_30m_range + overnight_gap
  B. Full OLS:     rod_return ~ [baseline] + call_pct
  C. Partial Spearman: call_pct | rod_return controlling for price controls
  D. Residual test: regress rod_return on price controls, test call_pct vs residual
  E. Quintile table conditioned on first_30m direction (up / down)

Output:
  experiments/phase2_results/H58_atm_proxy_phase2b.json
  vault/Backtests/h58-*.md (Phase 2B section appended)
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
CHAINS_DIR    = BASE / "data" / "raw" / "chains"
DATABENTO_DIR = BASE / "data" / "raw" / "databento"
RESULTS_DIR   = BASE / "experiments" / "phase2_results"
SIG_CACHE     = RESULTS_DIR / "h58_signal_table.parquet"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

_ET = "America/New_York"

# Internal 2025 split
TRAIN_START = "2025-04-01"; TRAIN_END = "2025-08-31"
VAL_START   = "2025-09-01"; VAL_END   = "2025-12-31"

MIN_CALL_FILES          = 4
MIN_PUT_FILES           = 4
HIGH_COVERAGE_THRESHOLD = 0.20
HIGH_COVERAGE_LABEL     = "high_coverage"
ALL_DATES_LABEL         = "all_dates"


# ── Statistical utilities ─────────────────────────────────────────────────────

def nw_spearman(x, y, maxlags=3):
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    n = len(x)
    if n < 15:
        return {"rho": None, "p_nw": None, "n": int(n)}
    rho, p_scipy = spearmanr(x, y)
    if HAS_SM:
        rx = scipy_rankdata(x) / n
        ry = scipy_rankdata(y) / n
        X = sm.add_constant(rx)
        p_nw = float(sm.OLS(ry, X).fit(
            cov_type="HAC", cov_kwds={"maxlags": maxlags}
        ).pvalues[1])
    else:
        p_nw = float(p_scipy)
    return {"rho": float(rho), "p_nw": float(p_nw), "n": int(n)}


def hac_ols(y, X_df, maxlags=3):
    """HAC OLS. y: np array. X_df: DataFrame of predictors (no constant)."""
    mask = np.isfinite(y)
    for col in X_df.columns:
        mask &= np.isfinite(X_df[col].values)
    y_c = y[mask]; X_c = X_df.loc[mask].copy()
    n = int(mask.sum())
    if n < 15 or not HAS_SM:
        return {"n": n, "betas": {}, "pvalues": {}, "r2": None, "r2_adj": None}
    X_sm = sm.add_constant(X_c)
    res = sm.OLS(y_c, X_sm).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
    return {
        "n": n,
        "betas": {k: float(v) for k, v in res.params.items()},
        "pvalues": {k: float(v) for k, v in res.pvalues.items()},
        "r2": float(res.rsquared),
        "r2_adj": float(res.rsquared_adj),
    }


def partial_spearman(x, y, Z_df):
    """Partial Spearman rho(x, y | Z) via rank-OLS residualisation."""
    cols = list(Z_df.columns)
    mask = np.isfinite(x) & np.isfinite(y)
    for col in cols:
        mask &= np.isfinite(Z_df[col].values)
    x, y = x[mask], y[mask]
    Z = Z_df.loc[mask].copy()
    n = int(mask.sum())
    if n < 15 or not HAS_SM:
        rho, p = spearmanr(x, y)
        return {"partial_rho": float(rho), "partial_p": float(p), "n": n, "method": "fallback_full"}
    rx = scipy_rankdata(x) / n
    ry = scipy_rankdata(y) / n
    rZ = pd.DataFrame({c: scipy_rankdata(Z[c].values) / n for c in cols})
    Zsm = sm.add_constant(rZ)
    resid_x = sm.OLS(rx, Zsm).fit().resid
    resid_y = sm.OLS(ry, Zsm).fit().resid
    rho, p = spearmanr(resid_x, resid_y)
    return {"partial_rho": float(rho), "partial_p": float(p), "n": n, "method": "rank_ols_residual"}


def mw_test(g1, g2, alternative="two-sided"):
    g1 = np.asarray(g1, float); g1 = g1[np.isfinite(g1)]
    g2 = np.asarray(g2, float); g2 = g2[np.isfinite(g2)]
    if len(g1) < 5 or len(g2) < 5:
        return {"n_a": len(g1), "n_b": len(g2), "stat": None, "p": None,
                "median_a": float(np.median(g1)) if len(g1) else None,
                "median_b": float(np.median(g2)) if len(g2) else None,
                "diff": None}
    stat, p = mannwhitneyu(g1, g2, alternative=alternative)
    return {
        "n_a": int(len(g1)), "n_b": int(len(g2)),
        "stat": float(stat), "p": float(p),
        "median_a": float(np.median(g1)), "median_b": float(np.median(g2)),
        "diff": float(np.median(g1) - np.median(g2)),
    }


# ── Signal table (with parquet cache) ─────────────────────────────────────────

def _get_vol_at_signal_bar(files):
    total = 0.0
    for f in files:
        df = pd.read_parquet(f)
        df["_ts"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("_ts").reset_index(drop=True)
        bar = df[df["_ts"].dt.strftime("%H:%M:%S") == "10:00:00"]
        if bar.empty:
            bar = df[df["_ts"].dt.strftime("%H:%M:%S") <= "09:55:00"]
            if bar.empty:
                continue
            bar = bar.iloc[[-1]]
        total += float(bar["optionVolume"].iloc[0])
    return total


def _get_eod_vol(files):
    total = 0.0
    for f in files:
        df = pd.read_parquet(f)
        if not df.empty:
            total += float(df["optionVolume"].iloc[-1])
    return total


def build_signal_table():
    """Build or load cached signal table."""
    if SIG_CACHE.exists():
        print(f"  Loading cached signal table from {SIG_CACHE.name}...")
        return pd.read_parquet(SIG_CACHE)

    print("  Building signal table (scanning chain files)...")
    all_files = sorted(CHAINS_DIR.glob("intraday_QQQ___*_MINUTE_5.parquet"))
    by_date: dict[str, dict] = {}
    for f in all_files:
        tokens = f.stem.split("_")
        trade_date = next((t for t in tokens if len(t) == 8 and t.isdigit()), None)
        if not trade_date:
            continue
        cp = None
        for t in tokens:
            if len(t) >= 12:
                for ch in t:
                    if ch == "C": cp = "C"; break
                    if ch == "P": cp = "P"; break
                if cp:
                    break
        if cp and trade_date:
            if trade_date not in by_date:
                by_date[trade_date] = {"C": [], "P": []}
            by_date[trade_date][cp].append(f)

    rows = []
    for date_str in sorted(by_date.keys()):
        call_files = by_date[date_str]["C"]
        put_files  = by_date[date_str]["P"]
        if len(call_files) < MIN_CALL_FILES or len(put_files) < MIN_PUT_FILES:
            continue
        call_vol_30m = _get_vol_at_signal_bar(call_files)
        put_vol_30m  = _get_vol_at_signal_bar(put_files)
        total_30m = call_vol_30m + put_vol_30m
        if total_30m == 0:
            continue
        call_pct = call_vol_30m / total_30m
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
            "coverage_pct": coverage_pct,
        })

    df = pd.DataFrame(rows).set_index("date").sort_index()
    df.to_parquet(SIG_CACHE)
    print(f"  Saved to {SIG_CACHE.name}")
    return df


# ── Price-action controls from Databento 1m ────────────────────────────────────

def load_all_1m():
    files = sorted(DATABENTO_DIR.glob("qqq_1m_*.parquet"))
    df = pd.concat([pd.read_parquet(f) for f in files]).sort_index()
    if df.index.tzinfo is None:
        df.index = df.index.tz_localize(_ET)
    return df


def build_price_controls(bars_1m: pd.DataFrame) -> pd.DataFrame:
    """
    Per-day price-action controls (all knowable at 10:00:00):
      first_30m_return  = (close_09:59 - open_09:30) / open_09:30
      first_30m_range   = (max_high - min_low in 09:30–09:59) / open_09:30
      first_30m_abs_ret = |first_30m_return|
      overnight_gap     = (open_09:30 / prev_close_15:59) - 1
      open_1001_price   = 1m bar open at 10:01 (entry)
      close_1559_price  = 1m bar close at 15:59 (exit)
      rod_return        = (close_1559 - open_1001) / open_1001
    """
    rows = []
    dates = sorted(set(bars_1m.index.date))
    for i, d in enumerate(dates):
        mask = bars_1m.index.date == d
        day = bars_1m.loc[mask]
        if day.empty:
            continue

        # Open at 09:30
        bar_0930 = day[day.index.time == pd.Timestamp("09:30").time()]
        # 1m bars 09:30-09:59 (first 30 min of underlying)
        first30 = day.between_time("09:30", "09:59")
        # Close at 09:59
        bar_0959 = day[day.index.time == pd.Timestamp("09:59").time()]
        # Entry: open at 10:01
        bar_1001 = day[day.index.time == pd.Timestamp("10:01").time()]
        # Exit: close at 15:59
        bar_1559 = day[day.index.time == pd.Timestamp("15:59").time()]

        if bar_0930.empty or bar_0959.empty or bar_1001.empty or bar_1559.empty or first30.empty:
            continue

        open_0930  = float(bar_0930["open"].iloc[0])
        close_0959 = float(bar_0959["close"].iloc[0])
        max_high   = float(first30["high"].max())
        min_low    = float(first30["low"].min())
        open_1001  = float(bar_1001["open"].iloc[0])
        close_1559 = float(bar_1559["close"].iloc[0])

        first_30m_return = (close_0959 - open_0930) / open_0930
        first_30m_range  = (max_high - min_low) / open_0930

        # Overnight gap: need prior session close
        if i > 0:
            prev_d = dates[i - 1]
            prev_mask = bars_1m.index.date == prev_d
            prev_day = bars_1m.loc[prev_mask]
            prev_1559 = prev_day[prev_day.index.time == pd.Timestamp("15:59").time()]
            prev_close = float(prev_1559["close"].iloc[0]) if not prev_1559.empty else np.nan
        else:
            prev_close = np.nan

        overnight_gap = (open_0930 / prev_close - 1) if prev_close and prev_close > 0 else np.nan
        rod_return    = (close_1559 - open_1001) / open_1001

        rows.append({
            "date": pd.Timestamp(d),
            "open_0930":        open_0930,
            "close_0959":       close_0959,
            "open_1001":        open_1001,
            "close_1559":       close_1559,
            "first_30m_return": first_30m_return,
            "first_30m_range":  first_30m_range,
            "first_30m_abs_ret": abs(first_30m_return),
            "overnight_gap":    overnight_gap,
            "rod_return":       rod_return,
        })

    return pd.DataFrame(rows).set_index("date").sort_index()


# ── Analysis ───────────────────────────────────────────────────────────────────

CTRL_COLS = ["first_30m_return", "first_30m_range", "overnight_gap"]


def _split(df, label):
    if label == "train":
        return df.loc[TRAIN_START:TRAIN_END]
    elif label == "val":
        return df.loc[VAL_START:VAL_END]
    else:
        return df


def run_full_analysis(df: pd.DataFrame, dataset_label: str) -> dict:
    df = df.dropna(subset=["call_pct", "rod_return"] + CTRL_COLS)
    n = len(df)
    if n < 15:
        return {"label": dataset_label, "n": n, "insufficient": True}

    y = df["rod_return"].values
    x_call = df["call_pct"].values
    X_ctrl = df[CTRL_COLS]

    # ── Test A: Baseline OLS (price controls only) ─────────────────────────
    model_A = hac_ols(y, X_ctrl)

    # ── Test B: Full OLS (baseline + call_pct) ────────────────────────────
    X_full = df[CTRL_COLS + ["call_pct"]].copy()
    model_B = hac_ols(y, X_full)

    # Incremental R²
    r2_baseline = model_A["r2"] if model_A["r2"] is not None else None
    r2_full     = model_B["r2"] if model_B["r2"] is not None else None
    delta_r2 = (r2_full - r2_baseline) if (r2_full is not None and r2_baseline is not None) else None
    call_pct_beta  = model_B["betas"].get("call_pct")
    call_pct_p     = model_B["pvalues"].get("call_pct")

    # ── Test C: Partial Spearman (call_pct | rod_return, controlling Z) ───
    partial_sp = partial_spearman(x_call, y, X_ctrl)

    # ── Test D: Residual test ─────────────────────────────────────────────
    # Residualize rod_return on price controls; test call_pct vs residual
    resid_rod = None
    residual_test = {}
    if HAS_SM and n >= 15:
        mask_ctrl = np.all(np.isfinite(X_ctrl.values), axis=1) & np.isfinite(y)
        y_c = y[mask_ctrl]; Xc = X_ctrl.loc[mask_ctrl]
        resid_rod_arr = sm.OLS(y_c, sm.add_constant(Xc)).fit().resid
        # Align call_pct to same mask
        call_masked = x_call[mask_ctrl]
        residual_test = nw_spearman(call_masked, resid_rod_arr, maxlags=3)
        residual_test["interpretation"] = (
            "Spearman(call_pct, residual_rod_return) after partialling out price controls"
        )
    else:
        residual_test = {"rho": None, "p_nw": None, "n": n, "note": "statsmodels unavailable"}

    # Raw Spearman for reference
    raw_sp = nw_spearman(x_call, y, maxlags=3)

    # ── Test E: Quintile table conditioned on first_30m direction ─────────
    df["q_call_pct"] = pd.qcut(df["call_pct"], 5, labels=["Q1","Q2","Q3","Q4","Q5"])
    df["up_day"] = df["first_30m_return"] > 0

    cond_table = {}
    for direction_label, direction_mask in [("up_30m", df["up_day"]), ("down_30m", ~df["up_day"])]:
        sub = df[direction_mask]
        qt = {}
        for q in ["Q1","Q2","Q3","Q4","Q5"]:
            s = sub[sub["q_call_pct"] == q]["rod_return"]
            qt[q] = {
                "n": int(len(s)),
                "median_rod": float(np.median(s)) if len(s) > 0 else None,
                "mean_rod":   float(np.mean(s))   if len(s) > 0 else None,
            }
        cond_table[direction_label] = {
            "n_days": int(direction_mask.sum()),
            "quintiles": qt,
        }

    # ── Train/Val internal split ──────────────────────────────────────────
    split_results = {}
    signs_partial = []
    signs_resid   = []
    for split_name in ["train", "val"]:
        sub = _split(df, split_name).dropna(subset=["call_pct", "rod_return"] + CTRL_COLS)
        n_sub = len(sub)
        if n_sub < 15:
            split_results[split_name] = {"n": n_sub, "insufficient": True}
            continue
        ys = sub["rod_return"].values
        xs = sub["call_pct"].values
        Xs = sub[CTRL_COLS]
        Xfs = sub[CTRL_COLS + ["call_pct"]].copy()

        sp_sub      = nw_spearman(xs, ys, maxlags=3)
        partial_sub = partial_spearman(xs, ys, Xs)
        mB_sub      = hac_ols(ys, Xfs)
        mA_sub      = hac_ols(ys, Xs)

        # Residual test per split
        if HAS_SM and n_sub >= 15:
            mask_s = np.all(np.isfinite(Xs.values), axis=1) & np.isfinite(ys)
            ys_c = ys[mask_s]; Xsc = Xs.loc[mask_s]
            resid_s = sm.OLS(ys_c, sm.add_constant(Xsc)).fit().resid
            xs_c = xs[mask_s]
            resid_sp = nw_spearman(xs_c, resid_s, maxlags=3)
        else:
            resid_sp = {"rho": None, "p_nw": None, "n": n_sub}

        split_results[split_name] = {
            "n": n_sub,
            "raw_spearman": sp_sub,
            "partial_spearman": partial_sub,
            "model_B_call_pct_beta": mB_sub["betas"].get("call_pct"),
            "model_B_call_pct_p": mB_sub["pvalues"].get("call_pct"),
            "model_A_r2": mA_sub["r2"],
            "model_B_r2": mB_sub["r2"],
            "residual_spearman": resid_sp,
        }
        if partial_sub.get("partial_rho") is not None:
            signs_partial.append(np.sign(partial_sub["partial_rho"]))
        if resid_sp.get("rho") is not None:
            signs_resid.append(np.sign(resid_sp["rho"]))

    same_sign_partial = len(signs_partial) == 2 and signs_partial[0] == signs_partial[1]
    same_sign_resid   = len(signs_resid)   == 2 and signs_resid[0]   == signs_resid[1]

    return {
        "label": dataset_label,
        "n": int(n),
        "n_train": int(len(_split(df, "train").dropna(subset=["call_pct","rod_return"]+CTRL_COLS))),
        "n_val":   int(len(_split(df, "val").dropna(subset=["call_pct","rod_return"]+CTRL_COLS))),
        "raw_spearman": raw_sp,
        "model_A_baseline": model_A,
        "model_B_full": model_B,
        "delta_r2": float(delta_r2) if delta_r2 is not None else None,
        "call_pct_beta": float(call_pct_beta) if call_pct_beta is not None else None,
        "call_pct_p_hac": float(call_pct_p) if call_pct_p is not None else None,
        "partial_spearman": partial_sp,
        "residual_spearman": residual_test,
        "conditional_quintile_table": cond_table,
        "internal_split": split_results,
        "same_sign_partial_train_val": same_sign_partial,
        "same_sign_residual_train_val": same_sign_resid,
    }


# ── Verdict ────────────────────────────────────────────────────────────────────

def compute_verdict(a: dict, dataset_label: str) -> tuple[str, str]:
    if a.get("insufficient"):
        return "insufficient_data", f"n={a.get('n')} — too few"

    n_train = a.get("n_train", 0)
    n_val   = a.get("n_val", 0)
    if n_train < 15 or n_val < 15:
        return "insufficient_data", (
            f"Internal split too thin: train n={n_train}, val n={n_val}. "
            "Cannot assess temporal consistency."
        )

    call_pct_p  = a.get("call_pct_p_hac")
    partial_rho = (a.get("partial_spearman") or {}).get("partial_rho")
    partial_p   = (a.get("partial_spearman") or {}).get("partial_p")
    resid_rho   = (a.get("residual_spearman") or {}).get("rho")
    resid_p     = (a.get("residual_spearman") or {}).get("p_nw")
    same_partial = a.get("same_sign_partial_train_val", False)
    same_resid   = a.get("same_sign_residual_train_val", False)

    # SUPPORTED: call_pct is significant after controls AND consistent
    if (
        call_pct_p is not None and call_pct_p < 0.10
        and partial_rho is not None and abs(partial_rho) > 0.08
        and partial_p is not None and partial_p < 0.20
        and same_partial
    ):
        return "supported", (
            f"call_pct survives price controls: beta_p={call_pct_p:.4f}, "
            f"partial_rho={partial_rho:.3f} (p={partial_p:.4f}), "
            f"same_sign_train_val={same_partial}"
        )

    # REJECTED: call_pct adds nothing after controls
    if (
        (call_pct_p is None or call_pct_p > 0.30)
        and (resid_rho is None or abs(resid_rho) < 0.05)
    ):
        return "rejected", (
            f"call_pct adds no incremental value after price controls: "
            f"beta_p={call_pct_p}, residual_rho={resid_rho}. "
            "Raw rho=0.86 was momentum contamination."
        )

    # INCONCLUSIVE: intermediate
    return "inconclusive", (
        f"call_pct beta_p={call_pct_p}, partial_rho={partial_rho} "
        f"(p={partial_p}), same_sign_partial={same_partial}, "
        f"same_sign_residual={same_resid}. "
        "Incremental value unclear after price controls."
    )


# ── Vault output ───────────────────────────────────────────────────────────────

def append_vault_note(result: dict) -> None:
    vault_files = sorted((BASE / "vault" / "Backtests").glob("h58-*.md"))
    if not vault_files:
        print("  [warn] No vault/Backtests/h58-*.md found")
        return
    target = vault_files[0]

    a_hc    = result.get("analysis_high_coverage", {})
    a_all   = result.get("analysis_all_dates", {})
    v_hc    = result.get("verdict_high_coverage", "n/a")
    v_all   = result.get("verdict_all_dates", "n/a")
    final   = result.get("final_verdict", "n/a")

    def _sp(a, key):
        d = (a.get(key) or {})
        rho = d.get("rho") or d.get("partial_rho")
        p   = d.get("p_nw") or d.get("partial_p")
        n   = d.get("n")
        r = f"rho={rho:.3f}" if isinstance(rho, float) else "rho=n/a"
        p_ = f"p={p:.4f}" if isinstance(p, float) else "p=n/a"
        return f"{r}, {p_}, n={n}"

    lines = [
        "",
        "## H58-ATM-PROXY Phase 2B — Momentum Control Test",
        "",
        "**Purpose:** Test whether ATM option flow adds incremental value beyond first-30-min price action.",
        f"**Original H58:** Still BLOCKED (full-chain PCR unavailable).",
        "",
        "### Internal 2025 Split",
        f"| Split | all_dates n | high_cov n |",
        f"|---|---|---|",
        f"| Train (Apr–Aug 2025) | {a_all.get('n_train','n/a')} | {a_hc.get('n_train','n/a')} |",
        f"| Val   (Sep–Dec 2025) | {a_all.get('n_val','n/a')}   | {a_hc.get('n_val','n/a')} |",
        "",
        "### Price-Action Controls",
        "Controls: `first_30m_return`, `first_30m_range`, `overnight_gap`",
        "",
        "#### Model A — Baseline (price controls only)",
    ]

    for label, a in [("all_dates", a_all), ("high_coverage", a_hc)]:
        mA = a.get("model_A_baseline", {})
        lines.append(
            f"| {label} | n={mA.get('n','n/a')}, R²={mA.get('r2','n/a'):.4f} |"
            if isinstance(mA.get("r2"), float) else
            f"| {label} | n={mA.get('n','n/a')}, R²=n/a |"
        )

    lines += [
        "",
        "#### Model B — Baseline + call_pct",
        f"| Dataset | call_pct beta | p (HAC) | ΔR² | Verdict |",
        f"|---|---|---|---|---|",
    ]

    for label, a in [("all_dates", a_all), ("high_coverage", a_hc)]:
        mB = a.get("model_B_full", {})
        beta = mB.get("betas", {}).get("call_pct")
        p    = mB.get("pvalues", {}).get("call_pct")
        dr2  = a.get("delta_r2")
        v    = result.get(f"verdict_{label}", "n/a")
        b_s = f"{beta:.4f}" if isinstance(beta, float) else "n/a"
        p_s = f"{p:.4f}" if isinstance(p, float) else "n/a"
        d_s = f"{dr2:.4f}" if isinstance(dr2, float) else "n/a"
        lines.append(f"| {label} | {b_s} | {p_s} | {d_s} | {v.upper()} |")

    lines += [
        "",
        "#### Partial Spearman (call_pct | rod_return, controlling for price controls)",
        f"| Dataset | partial_rho | p | same_sign_train_val |",
        f"|---|---|---|---|",
    ]
    for label, a in [("all_dates", a_all), ("high_coverage", a_hc)]:
        ps = a.get("partial_spearman", {})
        rho = ps.get("partial_rho"); p = ps.get("partial_p")
        ss = a.get("same_sign_partial_train_val", "n/a")
        r_s = f"{rho:.3f}" if isinstance(rho, float) else "n/a"
        p_s = f"{p:.4f}" if isinstance(p, float) else "n/a"
        lines.append(f"| {label} | {r_s} | {p_s} | {ss} |")

    lines += [
        "",
        "#### Residual Spearman (call_pct vs rod_return after removing price-control fit)",
        f"| Dataset | residual_rho | p | same_sign_train_val |",
        f"|---|---|---|---|",
    ]
    for label, a in [("all_dates", a_all), ("high_coverage", a_hc)]:
        rs = a.get("residual_spearman", {})
        rho = rs.get("rho"); p = rs.get("p_nw")
        ss = a.get("same_sign_residual_train_val", "n/a")
        r_s = f"{rho:.3f}" if isinstance(rho, float) else "n/a"
        p_s = f"{p:.4f}" if isinstance(p, float) else "n/a"
        lines.append(f"| {label} | {r_s} | {p_s} | {ss} |")

    lines += [
        "",
        "### Conditional Quintile Table (high_coverage, by first-30-min direction)",
        "",
        "| Direction | Q1 (put-heavy) n | median ROD | Q5 (call-heavy) n | median ROD |",
        "|---|---|---|---|---|",
    ]
    cqt = a_hc.get("conditional_quintile_table", {})
    for dir_label in ["up_30m", "down_30m"]:
        dt = cqt.get(dir_label, {})
        q1 = dt.get("quintiles", {}).get("Q1", {}); q5 = dt.get("quintiles", {}).get("Q5", {})
        q1_rod = f"{q1.get('median_rod'):.4f}" if isinstance(q1.get("median_rod"), float) else "n/a"
        q5_rod = f"{q5.get('median_rod'):.4f}" if isinstance(q5.get("median_rod"), float) else "n/a"
        lines.append(
            f"| {dir_label} (n={dt.get('n_days','?')}) | "
            f"{q1.get('n','?')} | {q1_rod} | {q5.get('n','?')} | {q5_rod} |"
        )

    lines += [
        "",
        "### Final Summary",
        "",
        f"**Raw Spearman (Phase 2A):** rho=0.86, p≈0 — likely momentum-proxy contamination",
        f"**After price controls:** see table above",
        f"",
        f"| Dataset | Verdict |",
        f"|---|---|",
        f"| all_dates | {result.get('verdict_all_dates','n/a').upper()} |",
        f"| high_coverage | {result.get('verdict_high_coverage','n/a').upper()} |",
        f"| **Final (Phase 2B)** | **{final.upper()}** |",
        "",
        f"**{result.get('final_verdict_reason','')}**",
        "",
        "**Recommendation:** " + result.get("recommendation", "See JSON for details."),
        "",
    ]

    with open(target, "a") as f:
        f.write("\n".join(lines))
    print(f"  [vault] Appended Phase 2B section to {target.name}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("H58-ATM-PROXY Phase 2B — Momentum Control Test")
    print("=" * 55)
    print(f"Internal 2025 split: train={TRAIN_START}→{TRAIN_END}, val={VAL_START}→{VAL_END}")

    # Signal table
    print("\nLoading signal table...")
    sig_df = build_signal_table()
    print(f"  {len(sig_df)} qualifying dates")

    # Price-action controls
    print("\nLoading Databento 1m bars and building price controls...")
    bars_1m = load_all_1m()
    price_df = build_price_controls(bars_1m)
    print(f"  Price controls computed for {len(price_df)} trading days")

    # Merge
    merged = sig_df.join(price_df[["first_30m_return","first_30m_range",
                                    "first_30m_abs_ret","overnight_gap","rod_return"]],
                         how="inner")
    merged = merged.dropna(subset=["call_pct","rod_return","first_30m_return",
                                    "first_30m_range","overnight_gap"])
    print(f"  {len(merged)} days after merge and dropna")

    # Coverage split
    hc_mask = merged["coverage_pct"] >= HIGH_COVERAGE_THRESHOLD
    df_all = merged
    df_hc  = merged[hc_mask]
    print(f"  all_dates: n={len(df_all)}, high_coverage: n={len(df_hc)}")

    # Diagnostic: internal split sizes
    for lab, df_ in [("all_dates", df_all), ("high_cov", df_hc)]:
        tr = df_.loc[TRAIN_START:TRAIN_END].dropna(subset=["call_pct","rod_return"]+CTRL_COLS)
        va = df_.loc[VAL_START:VAL_END].dropna(subset=["call_pct","rod_return"]+CTRL_COLS)
        print(f"  [{lab}] train n={len(tr)}, val n={len(va)}")

    # Analysis
    print("\nRunning analysis (all_dates)...")
    a_all = run_full_analysis(df_all.copy(), ALL_DATES_LABEL)
    print(f"  call_pct_p_hac (model B): {a_all.get('call_pct_p_hac')}")
    print(f"  partial_rho: {(a_all.get('partial_spearman') or {}).get('partial_rho')}")
    print(f"  residual_rho: {(a_all.get('residual_spearman') or {}).get('rho')}")

    print("\nRunning analysis (high_coverage)...")
    a_hc = run_full_analysis(df_hc.copy(), HIGH_COVERAGE_LABEL)
    print(f"  call_pct_p_hac (model B): {a_hc.get('call_pct_p_hac')}")
    print(f"  partial_rho: {(a_hc.get('partial_spearman') or {}).get('partial_rho')}")
    print(f"  residual_rho: {(a_hc.get('residual_spearman') or {}).get('rho')}")

    # Verdicts
    v_all, r_all = compute_verdict(a_all, ALL_DATES_LABEL)
    v_hc,  r_hc  = compute_verdict(a_hc,  HIGH_COVERAGE_LABEL)

    # Primary verdict: high_coverage if adequate, else all_dates
    if not a_hc.get("insufficient") and a_hc.get("n_train", 0) >= 15 and a_hc.get("n_val", 0) >= 15:
        final_verdict = v_hc
        final_reason  = f"[high_coverage primary] {r_hc}"
    else:
        final_verdict = v_all
        final_reason  = f"[all_dates fallback] {r_all}"

    # Recommendation based on verdict
    if final_verdict == "rejected":
        recommendation = (
            "Retire H58-ATM-PROXY. The proxy signal has no incremental value beyond "
            "first-30-min price momentum. The raw rho=0.86 was a momentum echo, not option-flow prediction. "
            "Original H58 remains BLOCKED."
        )
    elif final_verdict == "supported":
        recommendation = (
            "H58-ATM-PROXY Phase 2B shows genuine incremental value beyond early price action. "
            "Consider a Phase 3 study with a cleaner option-flow measure. "
            "Original H58 remains BLOCKED (full chain unavailable)."
        )
    else:
        recommendation = (
            "H58-ATM-PROXY incremental value is unclear. Results are ambiguous after price controls. "
            "Evidence is insufficient to either retire or promote this proxy. "
            "Original H58 remains BLOCKED."
        )

    print(f"\nVerdicts:")
    print(f"  all_dates:    {v_all.upper()}")
    print(f"  high_coverage: {v_hc.upper()}")
    print(f"  Final: {final_verdict.upper()}")

    result = {
        "study": "H58-ATM-PROXY Phase 2B",
        "proxy_label": "H58_atm_proxy_phase2b",
        "original_h58_status": "BLOCKED — full-chain intraday volume unavailable (iVol 403). This is a proxy study only.",
        "phase2a_finding": "Raw Spearman rho=0.86 between ATM call_pct and rod_return — suspected momentum-proxy contamination.",
        "phase2b_purpose": "Test incremental value of call_pct beyond first-30-min underlying price action.",
        "internal_split": {
            "train": f"{TRAIN_START} to {TRAIN_END}",
            "val":   f"{VAL_START} to {VAL_END}",
            "note":  "All qualifying dates are in 2025 (2024 chain files <4C+4P per day). Internal split uses 2025 only.",
        },
        "price_controls": CTRL_COLS,
        "verdict_all_dates": v_all,
        "verdict_all_dates_reason": r_all,
        "verdict_high_coverage": v_hc,
        "verdict_high_coverage_reason": r_hc,
        "final_verdict": final_verdict,
        "final_verdict_reason": final_reason,
        "recommendation": recommendation,
        "analysis_all_dates": a_all,
        "analysis_high_coverage": a_hc,
    }

    out_path = RESULTS_DIR / "H58_atm_proxy_phase2b.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nSaved → {out_path.relative_to(BASE)}")

    append_vault_note(result)
    print("Done.")


if __name__ == "__main__":
    main()
