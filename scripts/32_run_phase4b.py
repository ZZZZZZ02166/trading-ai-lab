"""
Phase 4B — Intraday Options Chain Factor Tests

Tests 3 intraday factor hypotheses using 5-minute option chain data:

  C1:  Intraday IV Velocity (9:30→10:00) → Afternoon Range
  C1b: Ultra-early IV Velocity (9:30→9:45) → Afternoon Range
  C3:  Near-ATM Call Volume Accumulation (first 30 min) → Range

Data: data/raw/chains/intraday_QQQ___*.parquet (317 dates, Jan 2024–Dec 2025)
Walk-forward: train=2024, val=2025, holdout=NONE (chain data ends Dec 2025)

Output:
  experiments/phase3_results/phase4b_C1_iv_velocity.json
  experiments/phase3_results/phase4b_C1b_iv_velocity_ultra.json
  experiments/phase3_results/phase4b_C3_call_volume.json
  experiments/phase3_results/phase4b_summary.json

Usage:
  python scripts/32_run_phase4b.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr

try:
    import statsmodels.api as sm
    HAS_SM = True
except ImportError:
    HAS_SM = False

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE          = Path(__file__).resolve().parent.parent
CHAIN_DIR     = BASE / "data" / "raw" / "chains"
DATABENTO_DIR = BASE / "data" / "raw" / "databento"
DAILY_SERIES  = BASE / "data" / "processed" / "daily_series.parquet"
RESULTS_DIR   = BASE / "experiments" / "phase3_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Walk-forward splits ────────────────────────────────────────────────────────
# No holdout: chain data ends Dec 2025
TRAIN_START, TRAIN_END = "2024-01-01", "2024-12-31"
VAL_START,   VAL_END   = "2025-01-01", "2025-12-31"
_ET = "America/New_York"


# ── Stats helpers ──────────────────────────────────────────────────────────────

def nw_spearman(x: pd.Series, y: pd.Series, maxlags: int = 5) -> dict:
    mask = x.notna() & y.notna()
    x, y = x[mask], y[mask]
    n = len(x)
    if n < 20:
        return {"rho": None, "p_nw": None, "n": n}
    rho, p_naive = spearmanr(x, y)
    if not HAS_SM:
        return {"rho": round(float(rho), 4), "p_nw": round(float(p_naive), 6), "n": n}
    rx = pd.Series(x.values).rank()
    ry = pd.Series(y.values).rank()
    res = sm.OLS(ry, sm.add_constant(rx)).fit(
        cov_type="HAC", cov_kwds={"maxlags": maxlags}
    )
    p_nw = float(res.pvalues.iloc[1])
    return {"rho": round(float(rho), 4), "p_nw": round(float(p_nw), 6), "n": n}


def mw_test(a: pd.Series, b: pd.Series) -> dict:
    a, b = a.dropna(), b.dropna()
    if len(a) < 5 or len(b) < 5:
        return {"n_a": len(a), "n_b": len(b), "cliff_d": None, "p": None}
    stat, p = mannwhitneyu(a, b, alternative="two-sided")
    cliff_d = (2 * stat / (len(a) * len(b))) - 1
    return {
        "n_a": len(a), "n_b": len(b),
        "stat": float(stat), "p": round(float(p), 6),
        "cliff_d": round(float(cliff_d), 4),
        "median_a": round(float(a.median()), 6),
        "median_b": round(float(b.median()), 6),
    }


def split_by_period(df: pd.DataFrame, date_col: str = "trade_date") -> dict[str, pd.DataFrame]:
    d = pd.to_datetime(df[date_col])
    return {
        "full":    df[(d >= TRAIN_START) & (d <= VAL_END)],
        "train":   df[(d >= TRAIN_START) & (d <= TRAIN_END)],
        "val":     df[(d >= VAL_START)   & (d <= VAL_END)],
    }


def wf_spearman(df: pd.DataFrame, x_col: str, y_col: str) -> dict:
    splits = split_by_period(df)
    out = {}
    all_rhos = []
    for name, sub in splits.items():
        r = nw_spearman(sub[x_col], sub[y_col])
        out[name] = r
        if r["rho"] is not None:
            all_rhos.append(r["rho"])
    n_pos = sum(1 for r in all_rhos if r > 0)
    consistent = (n_pos == len(all_rhos)) or (n_pos == 0)
    return {"splits": out, "consistency": "consistent" if consistent else "mixed",
            "n_positive_splits": n_pos}


# ── Window table (reuse 1m bar logic from script 31) ─────────────────────────

def load_all_1m() -> pd.DataFrame:
    files = sorted(DATABENTO_DIR.glob("qqq_1m_*.parquet"))
    df = pd.concat([pd.read_parquet(f) for f in files]).sort_index()
    if df.index.tzinfo is None:
        df.index = df.index.tz_localize(_ET)
    return df


def build_window_table(bars: pd.DataFrame) -> pd.DataFrame:
    et = bars.index.tz_convert(_ET)
    bars = bars.copy()
    bars.index = et
    rows = []
    for date, day in bars.groupby(bars.index.date):
        sess = day.between_time("09:30", "12:59")
        if len(sess) < 10:
            continue
        open_bar = sess.between_time("09:30", "09:30")
        if open_bar.empty:
            continue
        open_price = float(open_bar["open"].iloc[0])

        def _range(start: str, end: str) -> float | None:
            s = sess.between_time(start, end)
            if s.empty:
                return None
            return float(s["high"].max() - s["low"].min())

        def _rv_window(start: str, end: str) -> float | None:
            s = day.between_time(start, end)
            if len(s) < 2:
                return None
            lrets = np.log(s["close"] / s["close"].shift(1)).dropna()
            if len(lrets) < 2:
                return None
            return float(np.sqrt((lrets ** 2).mean()) * np.sqrt(252 * 390))

        prev_close_bar = day.between_time("15:59", "15:59")
        prev_close = float(prev_close_bar["close"].iloc[-1]) if not prev_close_bar.empty else None

        rows.append({
            "trade_date":    str(date),
            "open_price":    open_price,
            "prev_close":    prev_close,
            "w30_range":     _range("09:30", "09:59"),
            "w60_range":     _range("09:30", "10:29"),
            "w120_range":    _range("09:30", "11:29"),
            "w150_range":    _range("09:30", "11:59"),
            "w210_range":    _range("09:30", "12:59"),
            "aw_range":      _range("10:30", "11:59"),
            "fh_rv":         _rv_window("09:30", "10:29"),
            "late_rv":       _rv_window("15:30", "15:59"),
            "w15_range":     _range("09:30", "09:44"),
        })

    df = pd.DataFrame(rows).sort_values("trade_date").reset_index(drop=True)
    return df


# ── Intraday chain loader ──────────────────────────────────────────────────────

def build_intraday_iv_table(chain_dir: Path) -> pd.DataFrame:
    """For each date: find near-ATM call at 9:30, track IV at 9:30/9:45/10:00.
    Also compute total call volume at 10:00 across all contracts."""
    pattern = re.compile(r"intraday_QQQ___(\d+C\d+)_(\d{8})_MINUTE_5\.parquet")

    # Group files by date
    date_files: dict[str, list[Path]] = {}
    for f in sorted(chain_dir.glob("intraday_QQQ___*.parquet")):
        m = pattern.match(f.name)
        if m:
            date_str = m.group(2)
            date_files.setdefault(date_str, []).append(f)

    TARGET_TIMES = {"09:30", "09:35", "09:40", "09:45", "09:50",
                    "09:55", "10:00"}

    rows = []
    for date_str, flist in sorted(date_files.items()):
        trade_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

        # Load and concatenate all contracts for this date
        frames = []
        for f in flist:
            try:
                df = pd.read_parquet(f, columns=[
                    "timestamp", "optionIv", "optionDelta",
                    "optionVolume", "underlyingPrice", "optionStrike"
                ])
                frames.append(df)
            except Exception:
                continue
        if not frames:
            continue

        day = pd.concat(frames, ignore_index=True)
        day["timestamp"] = pd.to_datetime(day["timestamp"])
        day["time_str"] = day["timestamp"].dt.strftime("%H:%M")
        day = day[day["time_str"].isin(TARGET_TIMES)].copy()

        # At 9:30, find near-ATM contract by |delta - 0.50| minimized
        open_bars = day[day["time_str"] == "09:30"].copy()
        if open_bars.empty or open_bars["optionIv"].isna().all():
            continue

        open_bars = open_bars.dropna(subset=["optionDelta", "optionIv"])
        if open_bars.empty:
            continue

        open_bars["delta_dist"] = (open_bars["optionDelta"] - 0.50).abs()
        atm_row = open_bars.loc[open_bars["delta_dist"].idxmin()]
        atm_strike = float(atm_row["optionStrike"])

        # Track this contract through time
        atm_series = day[day["optionStrike"] == atm_strike].sort_values("time_str")
        atm_by_time = atm_series.set_index("time_str")["optionIv"].to_dict()

        iv_930  = atm_by_time.get("09:30")
        iv_940  = atm_by_time.get("09:40")
        iv_945  = atm_by_time.get("09:45")
        iv_1000 = atm_by_time.get("10:00")

        # IV velocities — guard for missing or zero base
        def vel(iv_t, iv_base):
            if iv_t is None or iv_base is None or iv_base == 0:
                return None
            return (iv_t - iv_base) / iv_base

        iv_vel_30  = vel(iv_1000, iv_930)
        iv_vel_15  = vel(iv_945,  iv_930)
        iv_vel_20  = vel(iv_940,  iv_930)   # 20-min for reference

        # Total call volume accumulated by 10:00 across ALL contracts
        vol_at_1000 = day[day["time_str"] == "10:00"]["optionVolume"].sum()
        vol_at_930  = day[day["time_str"] == "09:30"]["optionVolume"].sum()
        vol_acc_30  = vol_at_1000 - vol_at_930  # new volume in first 30 min

        # ATM delta at open (quality check)
        atm_delta_930 = float(atm_row["optionDelta"])
        underlying_930 = float(atm_row.get("underlyingPrice", np.nan)) if "underlyingPrice" in atm_row.index else np.nan

        rows.append({
            "trade_date":      trade_date,
            "atm_strike":      atm_strike,
            "atm_delta_930":   round(atm_delta_930, 4),
            "underlying_930":  round(underlying_930, 4) if not np.isnan(underlying_930) else None,
            "iv_930":          round(float(iv_930), 4) if iv_930 is not None else None,
            "iv_945":          round(float(iv_945), 4) if iv_945 is not None else None,
            "iv_1000":         round(float(iv_1000), 4) if iv_1000 is not None else None,
            "iv_vel_30":       round(float(iv_vel_30), 6) if iv_vel_30 is not None else None,
            "iv_vel_15":       round(float(iv_vel_15), 6) if iv_vel_15 is not None else None,
            "iv_vel_20":       round(float(iv_vel_20), 6) if iv_vel_20 is not None else None,
            "vol_at_930":      int(vol_at_930),
            "vol_at_1000":     int(vol_at_1000),
            "vol_acc_30":      int(vol_acc_30),
        })

    return pd.DataFrame(rows).sort_values("trade_date").reset_index(drop=True)


# ── Hypothesis runners ─────────────────────────────────────────────────────────

def run_c1(df: pd.DataFrame) -> dict:
    """C1 — Intraday IV Velocity (9:30→10:00) → Afternoon Range."""
    sub = df.dropna(subset=["iv_vel_30", "aw_range"]).copy()

    sp_aw  = nw_spearman(sub["iv_vel_30"], sub["aw_range"])
    sp_w150 = nw_spearman(sub["iv_vel_30"], sub["w150_range"])
    wf_aw  = wf_spearman(sub, "iv_vel_30", "aw_range")
    wf_w150 = wf_spearman(sub, "iv_vel_30", "w150_range")

    # MW: rising IV (vel > 0) vs falling IV (vel < 0)
    rising  = sub[sub["iv_vel_30"] > 0]["aw_range"]
    falling = sub[sub["iv_vel_30"] < 0]["aw_range"]
    mw = mw_test(rising, falling)

    # Window rho (how does the effect build across horizons?)
    window_rho = {}
    for w in ["w30_range", "w60_range", "w120_range", "w150_range", "w210_range"]:
        if w in sub.columns:
            window_rho[w] = nw_spearman(sub["iv_vel_30"], sub[w])
    peak = max(window_rho, key=lambda k: abs(window_rho[k]["rho"] or 0))

    # Timing gate: peak must be within w150 AND eff_w150 >= 0.5 * eff_w210
    rho_150 = abs(window_rho.get("w150_range", {}).get("rho") or 0)
    rho_210 = abs(window_rho.get("w210_range", {}).get("rho") or 0)
    early_enough = (peak in ("w30_range", "w60_range", "w120_range", "w150_range")
                    and (rho_210 == 0 or rho_150 >= 0.5 * rho_210))

    stat_ok   = (sp_aw["rho"] or 0) > 0.05 and (sp_aw["p_nw"] or 1) < 0.10
    sign_ok   = (sp_aw["rho"] or 0) > 0
    n_ok      = (sp_aw["n"] or 0) >= 50

    if stat_ok and sign_ok and n_ok and early_enough:
        verdict = "supported_trading_useful"
    elif stat_ok and sign_ok and n_ok and not early_enough:
        verdict = "too_late_for_style"
    elif stat_ok and not sign_ok:
        verdict = "rejected"
    else:
        verdict = "inconclusive"

    return {
        "hypothesis": "C1",
        "label": "Intraday IV Velocity (9:30→10:00) → Afternoon Range",
        "signal": "iv_vel_30 = (IV_10:00 - IV_9:30) / IV_9:30 for near-ATM call",
        "outcome": "aw_range (10:30–11:59) primary; w150_range secondary",
        "role": "EARLY WARNING (9:30–10:00)",
        "n_total": len(sub),
        "n_rising_iv": int((sub["iv_vel_30"] > 0).sum()),
        "n_falling_iv": int((sub["iv_vel_30"] < 0).sum()),
        "spearman_vs_aw_range": sp_aw,
        "spearman_vs_w150_range": sp_w150,
        "walk_forward_aw_range": wf_aw,
        "walk_forward_w150_range": wf_w150,
        "mw_rising_vs_falling_iv": mw,
        "window_rho": window_rho,
        "peak_window": peak,
        "early_enough_for_style": early_enough,
        "iv_vel_stats": {
            "median": round(float(sub["iv_vel_30"].median()), 4),
            "p25":    round(float(sub["iv_vel_30"].quantile(0.25)), 4),
            "p75":    round(float(sub["iv_vel_30"].quantile(0.75)), 4),
            "pct_rising": round(float((sub["iv_vel_30"] > 0).mean()), 3),
        },
        "holdout_note": "No holdout: chain data ends Dec 2025. Walk-forward train=2024, val=2025 only.",
        "phase4b_verdict": verdict,
    }


def run_c1b(df: pd.DataFrame) -> dict:
    """C1b — Ultra-early IV Velocity (9:30→9:45) → Afternoon Range."""
    sub = df.dropna(subset=["iv_vel_15", "aw_range"]).copy()

    sp_aw   = nw_spearman(sub["iv_vel_15"], sub["aw_range"])
    sp_w150 = nw_spearman(sub["iv_vel_15"], sub["w150_range"])
    wf_aw   = wf_spearman(sub, "iv_vel_15", "aw_range")

    rising  = sub[sub["iv_vel_15"] > 0]["aw_range"]
    falling = sub[sub["iv_vel_15"] < 0]["aw_range"]
    mw = mw_test(rising, falling)

    stat_ok   = (sp_aw["rho"] or 0) > 0.05 and (sp_aw["p_nw"] or 1) < 0.10
    sign_ok   = (sp_aw["rho"] or 0) > 0
    n_ok      = (sp_aw["n"] or 0) >= 50

    if stat_ok and sign_ok and n_ok:
        verdict = "supported_trading_useful"
    elif stat_ok and not sign_ok:
        verdict = "rejected"
    else:
        verdict = "inconclusive"

    return {
        "hypothesis": "C1b",
        "label": "Ultra-early IV Velocity (9:30→9:45) → Afternoon Range",
        "signal": "iv_vel_15 = (IV_9:45 - IV_9:30) / IV_9:30 for near-ATM call",
        "outcome": "aw_range (10:30–11:59) primary",
        "role": "EARLY WARNING (first 15 min)",
        "n_total": len(sub),
        "n_rising_iv": int((sub["iv_vel_15"] > 0).sum()),
        "n_falling_iv": int((sub["iv_vel_15"] < 0).sum()),
        "spearman_vs_aw_range": sp_aw,
        "spearman_vs_w150_range": sp_w150,
        "walk_forward_aw_range": wf_aw,
        "mw_rising_vs_falling_iv": mw,
        "iv_vel_stats": {
            "median": round(float(sub["iv_vel_15"].median()), 4),
            "p25":    round(float(sub["iv_vel_15"].quantile(0.25)), 4),
            "p75":    round(float(sub["iv_vel_15"].quantile(0.75)), 4),
            "pct_rising": round(float((sub["iv_vel_15"] > 0).mean()), 3),
        },
        "holdout_note": "No holdout: chain data ends Dec 2025.",
        "phase4b_verdict": verdict,
    }


def run_c3(df: pd.DataFrame) -> dict:
    """C3 — Near-ATM Call Volume Accumulation (first 30 min) → Range."""
    sub = df.dropna(subset=["vol_acc_30", "aw_range"]).copy()
    sub = sub[sub["vol_acc_30"] > 0].copy()   # exclude zero-vol days

    # Normalize by trailing 252-session median to reduce level effects
    sub = sub.sort_values("trade_date").reset_index(drop=True)
    sub["vol_acc_30_rank"] = sub["vol_acc_30"].rolling(252, min_periods=60).rank(pct=True)

    sub_norm = sub.dropna(subset=["vol_acc_30_rank"])

    sp_raw  = nw_spearman(sub["vol_acc_30"], sub["aw_range"])
    sp_rank = nw_spearman(sub_norm["vol_acc_30_rank"], sub_norm["aw_range"])
    sp_w150 = nw_spearman(sub_norm["vol_acc_30_rank"], sub_norm["w150_range"])
    wf_aw   = wf_spearman(sub_norm, "vol_acc_30_rank", "aw_range")

    # MW: top quartile vs bottom quartile (rank-based)
    top_q  = sub_norm[sub_norm["vol_acc_30_rank"] >= 0.75]["aw_range"]
    bot_q  = sub_norm[sub_norm["vol_acc_30_rank"] <= 0.25]["aw_range"]
    mw = mw_test(top_q, bot_q)

    stat_ok = (sp_rank["rho"] or 0) > 0.05 and (sp_rank["p_nw"] or 1) < 0.10
    sign_ok = (sp_rank["rho"] or 0) > 0
    n_ok    = (sp_rank["n"] or 0) >= 50

    if stat_ok and sign_ok and n_ok:
        verdict = "supported_trading_useful"
    elif stat_ok and not sign_ok:
        verdict = "rejected"
    else:
        verdict = "inconclusive"

    return {
        "hypothesis": "C3",
        "label": "Near-ATM Call Volume Accumulation (first 30 min) → Range",
        "signal": "vol_acc_30 = total optionVolume at 10:00 minus volume at 9:30, across all near-ATM contracts; rank-normalized rolling 252d",
        "outcome": "aw_range (10:30–11:59) primary",
        "role": "EARLY WARNING (9:30–10:00)",
        "n_total_raw": len(sub),
        "n_after_normalization": len(sub_norm),
        "spearman_raw_vs_aw_range": sp_raw,
        "spearman_rank_vs_aw_range": sp_rank,
        "spearman_rank_vs_w150_range": sp_w150,
        "walk_forward_aw_range": wf_aw,
        "mw_top_q_vs_bot_q": mw,
        "vol_acc_stats": {
            "median_raw": int(sub["vol_acc_30"].median()),
            "p25_raw":    int(sub["vol_acc_30"].quantile(0.25)),
            "p75_raw":    int(sub["vol_acc_30"].quantile(0.75)),
        },
        "normalization_note": "Rolling 252d rank (min 60 periods) reduces level-drift effects.",
        "holdout_note": "No holdout: chain data ends Dec 2025.",
        "phase4b_verdict": verdict,
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Phase 4B — Intraday Options Chain Factor Tests\n")

    # ── Step 1: Build intraday IV table ────────────────────────────────────────
    print("Building intraday IV table from 5-min chain data...")
    iv_df = build_intraday_iv_table(CHAIN_DIR)
    print(f"  {len(iv_df)} dates with intraday IV data")
    print(f"  Date range: {iv_df['trade_date'].min()} → {iv_df['trade_date'].max()}")
    print(f"  IV vel 30-min available: {iv_df['iv_vel_30'].notna().sum()}")
    print(f"  IV vel 15-min available: {iv_df['iv_vel_15'].notna().sum()}")
    print()

    # ── Step 2: Build window table from 1m bars ────────────────────────────────
    print("Loading 1m bars and building window table...")
    bars = load_all_1m()
    print(f"  {len(bars):,} bars")
    wt = build_window_table(bars)
    print(f"  {len(wt)} trading days in window table")
    print()

    # ── Step 3: Merge ──────────────────────────────────────────────────────────
    merged = iv_df.merge(wt, on="trade_date", how="inner")
    print(f"Merged: {len(merged)} dates with both chain IV and window data")

    # Chain data only covers Jan 2024–Dec 2025 → no holdout
    merged = merged[(merged["trade_date"] >= "2024-01-01") &
                    (merged["trade_date"] <= "2025-12-31")]
    print(f"  After date filter (2024–2025): {len(merged)}")
    print()

    # ── Step 4: Run hypotheses ─────────────────────────────────────────────────
    runners = [
        ("C1",  "phase4b_C1_iv_velocity.json",       run_c1),
        ("C1b", "phase4b_C1b_iv_velocity_ultra.json", run_c1b),
        ("C3",  "phase4b_C3_call_volume.json",        run_c3),
    ]

    results = {}
    for label, fname, runner in runners:
        print(f"  Running {label}...")
        res = runner(merged)
        out_path = RESULTS_DIR / fname
        out_path.write_text(json.dumps(res, indent=2, default=str))
        verdict = res.get("phase4b_verdict", "?")
        n = res.get("n_total") or res.get("n_total_raw") or res.get("n_after_normalization") or "?"
        sp = (res.get("spearman_vs_aw_range") or
              res.get("spearman_rank_vs_aw_range") or {})
        rho = sp.get("rho", "n/a")
        p   = sp.get("p_nw", "n/a")
        if isinstance(rho, float):
            rho = f"{rho:.3f}"
        if isinstance(p, float):
            p = f"{p:.4f}"
        print(f"    → {fname} | verdict: {verdict}")
        print(f"    ρ={rho}, p={p}, n={n}")
        results[label] = {"verdict": verdict, "file": fname}

    # Summary
    summary = {
        "phase": "4B",
        "description": "Intraday options chain factor tests",
        "data_coverage": "Jan 2024 – Dec 2025 (317 dates, no holdout)",
        "hypotheses": results,
    }
    (RESULTS_DIR / "phase4b_summary.json").write_text(
        json.dumps(summary, indent=2)
    )
    print(f"\n  → phase4b_summary.json")
    print("\nDone.")


if __name__ == "__main__":
    main()
