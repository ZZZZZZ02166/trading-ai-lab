"""
Phase 3B — Composite Premarket Signal

Builds and tests a composite from the 5 non-redundant premarket survivors
identified in the Phase 3 redundancy audit:
  H44  iv_spread_30_60   (IV term structure slope)
  H94  ivx_spread_7_30   (IVX 7d–30d spread)
  H97  iv_velocity_5d    (5-day IV rate of change)
  H70  range_pct_rank    (prior-day range percentile)
  H99  spread_pct_rank   (EOD spread percentile — caution weight, range only)

All signals point the same direction: higher = wider expected day.
All are pre-open (available before market open).

Composite variants tested:
  A. Equal-weight:   rank-normalize each signal [0,1], simple average
  B. Partial-ρ weighted: weight by partial Spearman vs w150_range from audit
  C. Core-4 equal:  exclude H94 (most correlated with H44, lowest partial ρ)

Output:
  experiments/phase3_results/phase3b_composite.json
  vault/Phase3/Phase3B-Composite-Signal.md

Usage:
  python scripts/30_run_phase3b.py
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE          = Path(__file__).resolve().parent.parent
DATABENTO_DIR = BASE / "data" / "raw" / "databento"
DAILY_SERIES  = BASE / "data" / "processed" / "daily_series.parquet"
IVX_PATH      = BASE / "data" / "raw" / "qqq_ivx.parquet"
RESULTS_DIR   = BASE / "experiments" / "phase3_results"
VAULT_P3      = BASE / "vault" / "Phase3"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
VAULT_P3.mkdir(parents=True, exist_ok=True)

# ── Splits ─────────────────────────────────────────────────────────────────────
TRAIN_START, TRAIN_END = "2024-01-01", "2024-12-31"
VAL_START,   VAL_END   = "2025-01-01", "2025-12-31"
HOLD_START,  HOLD_END  = "2026-01-01", "2026-03-31"
_ET = "America/New_York"

_WINDOW_ENDS = {
    "w30":  "09:59",
    "w60":  "10:29",
    "w120": "11:29",
    "w150": "11:59",
    "w210": "12:59",
}

# Partial ρ weights from Phase 3 redundancy audit (higher = more distinct contribution)
PARTIAL_RHO_WEIGHTS = {
    "iv_spread_30_60": 0.433,
    "ivx_spread_7_30": 0.138,
    "iv_velocity_5d":  0.168,
    "range_pct_rank":  0.131,
    "spread_pct_rank": 0.144,
}


# ── Data loading (mirrors 29_run_phase3.py) ────────────────────────────────────

def load_all_1m() -> pd.DataFrame:
    files = sorted(DATABENTO_DIR.glob("qqq_1m_*.parquet"))
    df = pd.concat([pd.read_parquet(f) for f in files]).sort_index()
    if df.index.tzinfo is None:
        df.index = df.index.tz_localize(_ET)
    return df


def load_daily() -> pd.DataFrame:
    df = pd.read_parquet(DAILY_SERIES)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")
    df["daily_range"] = (df["high"] - df["low"]) / df["close"]
    df["spread_pct"]  = (df["ask"] - df["bid"]) / df["close"]
    return df


def load_ivx() -> pd.DataFrame:
    df = pd.read_parquet(IVX_PATH)
    df = df.iloc[::-1].reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")
    df["ivx_7d"]          = df["7d IV Mean"]
    df["ivx_30d"]         = df["30d IV Mean"]
    df["ivx_spread_7_30"] = df["ivx_7d"] - df["ivx_30d"]
    return df[["ivx_7d", "ivx_30d", "ivx_spread_7_30"]]


def build_window_table(bars_1m: pd.DataFrame) -> pd.DataFrame:
    bars_et = bars_1m.tz_convert(_ET) if bars_1m.index.tzinfo else bars_1m
    rows = []
    days = sorted(set(bars_et.index.date))
    last_close: dict = {}

    for i, d in enumerate(days):
        day = bars_et[bars_et.index.date == d]
        if day.empty:
            continue
        prev_close = last_close.get(days[i - 1]) if i > 0 else np.nan
        last_close[d] = float(day["close"].iloc[-1])

        first_bar = day.between_time("09:30", "09:30")
        if first_bar.empty:
            continue
        open_0930 = float(first_bar["open"].iloc[0])

        row: dict = {"date": pd.Timestamp(d), "open_0930": open_0930}

        for wname, wend in _WINDOW_ENDS.items():
            sub = day.between_time("09:30", wend)
            if len(sub) < 3:
                row[f"{wname}_range"] = np.nan
            else:
                wh = float(sub["high"].max())
                wl = float(sub["low"].min())
                row[f"{wname}_range"] = (wh - wl) / open_0930

        rows.append(row)

    wt = pd.DataFrame(rows).set_index("date").sort_index()
    wt.index = pd.to_datetime(wt.index)
    return wt


def build_signal_df(wt: pd.DataFrame, daily: pd.DataFrame, ivx: pd.DataFrame) -> pd.DataFrame:
    eod_cols = ["iv_30d", "iv_60d", "daily_range", "spread_pct"]
    sig_eod = daily[eod_cols].shift(1)
    sig_eod.columns = ["sig_" + c for c in eod_cols]

    sig_ivx = ivx.shift(1)

    df = wt.join(sig_eod, how="inner").join(sig_ivx, how="left")

    # H44
    df["iv_spread_30_60"] = df["sig_iv_30d"] - df["sig_iv_60d"]
    # H94
    df["ivx_spread_7_30"] = df["ivx_spread_7_30"]  # already shifted
    # H97
    iv_vel = daily["iv_30d"].pct_change(5).shift(1)
    df["iv_velocity_5d"] = iv_vel.reindex(df.index)
    # H70 — global rolling rank, burn-in: first 252 rows NaN
    prior_range = daily["daily_range"].shift(1)
    df["range_pct_rank"] = prior_range.rolling(252, min_periods=252).rank(pct=True).reindex(df.index)
    # H99
    spread_rank = daily["spread_pct"].rolling(60, min_periods=20).rank(pct=True).shift(1)
    df["spread_pct_rank"] = spread_rank.reindex(df.index)

    return df


# ── Stats ──────────────────────────────────────────────────────────────────────

def nw_spearman(x: np.ndarray, y: np.ndarray, maxlags: int = 5) -> dict:
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    n = len(x)
    if n < 20:
        return {"rho": None, "p_nw": None, "n": n}
    rx = spearmanr(x, y).statistic
    # Newey-West standard error on the rank series
    xr = pd.Series(x).rank().values
    yr = pd.Series(y).rank().values
    xr = (xr - xr.mean()) / (xr.std() + 1e-12)
    yr = (yr - yr.mean()) / (yr.std() + 1e-12)
    e = xr * yr
    s0 = float(np.sum(e**2))
    for lag in range(1, maxlags + 1):
        g = float(np.sum(e[lag:] * e[:-lag]))
        s0 += 2 * (1 - lag / (maxlags + 1)) * g
    var_rho = s0 / (n**2)
    t = rx / np.sqrt(max(var_rho, 1e-16))
    from scipy.stats import t as tdist
    p = float(2 * tdist.sf(abs(t), df=n - 2))
    return {"rho": round(float(rx), 4), "p_nw": float(p), "n": int(n)}


def mw_cliff(g1: np.ndarray, g2: np.ndarray) -> dict:
    g1 = np.asarray(g1, float)
    g2 = np.asarray(g2, float)
    g1 = g1[np.isfinite(g1)]
    g2 = g2[np.isfinite(g2)]
    if len(g1) < 5 or len(g2) < 5:
        return {"n_high": int(len(g1)), "n_low": int(len(g2)), "cliff_d": None, "p": None,
                "median_high": None, "median_low": None}
    stat, p = mannwhitneyu(g1, g2, alternative="two-sided")
    dom = int((g1[:, None] > g2[None, :]).sum()) - int((g1[:, None] < g2[None, :]).sum())
    d = dom / (len(g1) * len(g2))
    return {
        "n_high": int(len(g1)), "n_low": int(len(g2)),
        "cliff_d": round(float(d), 4),
        "p": float(p),
        "median_high": round(float(np.median(g1)), 6),
        "median_low":  round(float(np.median(g2)), 6),
    }


def split_df(df: pd.DataFrame, which: str) -> pd.DataFrame:
    ranges = {
        "train":   (TRAIN_START, TRAIN_END),
        "val":     (VAL_START,   VAL_END),
        "holdout": (HOLD_START,  HOLD_END),
    }
    s, e = ranges[which]
    return df[(df.index >= s) & (df.index <= e)]


# ── Rank-normalize a signal ────────────────────────────────────────────────────

def rank_norm(s: pd.Series) -> pd.Series:
    """Rank-normalize to [0,1] preserving NaN positions."""
    out = s.copy().astype(float)
    valid = out.notna()
    out[valid] = pd.Series(
        pd.Series(out[valid].values).rank(pct=True).values,
        index=out[valid].index
    )
    return out


# ── Build composites ───────────────────────────────────────────────────────────

SIGNAL_COLS = ["iv_spread_30_60", "ivx_spread_7_30", "iv_velocity_5d",
               "range_pct_rank", "spread_pct_rank"]
CORE4_COLS  = ["iv_spread_30_60", "iv_velocity_5d", "range_pct_rank", "spread_pct_rank"]


def build_composites(df: pd.DataFrame) -> pd.DataFrame:
    normed = {}
    for col in SIGNAL_COLS:
        normed[col] = rank_norm(df[col])

    # A — equal-weight all 5
    stack = pd.DataFrame(normed)
    df["composite_eq5"] = stack.mean(axis=1)

    # B — partial-ρ weighted all 5
    total_w = sum(PARTIAL_RHO_WEIGHTS[c] for c in SIGNAL_COLS)
    weighted = sum(normed[c] * (PARTIAL_RHO_WEIGHTS[c] / total_w) for c in SIGNAL_COLS)
    df["composite_wt5"] = weighted

    # C — equal-weight core-4 (exclude H94 ivx_spread_7_30 — most correlated with H44)
    stack4 = pd.DataFrame({c: normed[c] for c in CORE4_COLS})
    df["composite_eq4"] = stack4.mean(axis=1)

    return df


# ── Test one composite ─────────────────────────────────────────────────────────

def test_composite(df: pd.DataFrame, comp_col: str, label: str) -> dict:
    df_c = df.dropna(subset=[comp_col, "w150_range"]).copy()

    # Timing gate: Spearman vs each window
    window_rhos = {}
    for wname in _WINDOW_ENDS:
        sub = df_c.dropna(subset=[f"{wname}_range"])
        res = nw_spearman(sub[comp_col].values, sub[f"{wname}_range"].values)
        window_rhos[wname] = res

    eff = {w: abs(r["rho"] or 0) for w, r in window_rhos.items()}
    peak_window = max(eff, key=eff.get)
    eff_w150 = eff.get("w150", 0)
    eff_w210 = eff.get("w210", 0)
    early_enough = (
        peak_window in ["w30", "w60", "w120", "w150"]
        and eff_w150 >= 0.5 * (eff_w210 or 1e-9)
    )

    # Primary Spearman full + walk-forward
    full_sp = nw_spearman(df_c[comp_col].values, df_c["w150_range"].values)

    wf = {}
    for split in ["train", "val", "holdout"]:
        sub = split_df(df_c, split).dropna(subset=[comp_col, "w150_range"])
        wf[split] = nw_spearman(sub[comp_col].values, sub["w150_range"].values)

    sign_ok = all(
        (wf[s]["rho"] or 0) > 0
        for s in ["train", "val", "holdout"]
        if wf[s]["rho"] is not None
    )

    # MW by quartile: top vs bottom 25%
    q75 = df_c[comp_col].quantile(0.75)
    q25 = df_c[comp_col].quantile(0.25)
    high_days = df_c[df_c[comp_col] >= q75]["w150_range"].values
    low_days  = df_c[df_c[comp_col] <= q25]["w150_range"].values
    mw_q = mw_cliff(high_days, low_days)

    # Walk-forward MW top vs bottom quartile (per-split)
    wf_mw = {}
    for split in ["train", "val", "holdout"]:
        sub = split_df(df_c, split).dropna(subset=[comp_col, "w150_range"])
        if len(sub) < 20:
            wf_mw[split] = None
            continue
        sq75 = sub[comp_col].quantile(0.75)
        sq25 = sub[comp_col].quantile(0.25)
        wf_mw[split] = mw_cliff(
            sub[sub[comp_col] >= sq75]["w150_range"].values,
            sub[sub[comp_col] <= sq25]["w150_range"].values,
        )

    # Verdict
    n_ok = df_c.shape[0] >= 100
    stat_ok = (full_sp["rho"] or 0) > 0.10 and (full_sp["p_nw"] or 1) < 0.10
    if not n_ok:
        verdict = "insufficient_data"
    elif not stat_ok or not sign_ok:
        verdict = "rejected"
    elif not early_enough:
        verdict = "too_late_for_style"
    else:
        verdict = "supported_trading_useful"

    return {
        "composite": label,
        "signals_included": SIGNAL_COLS if "5" in comp_col else CORE4_COLS,
        "n_total": int(df_c.shape[0]),
        "primary_spearman_w150": full_sp,
        "walk_forward_spearman": wf,
        "sign_consistent_across_splits": sign_ok,
        "mw_top_vs_bottom_quartile": mw_q,
        "walk_forward_mw": wf_mw,
        "window_rhos": window_rhos,
        "peak_window": peak_window,
        "early_enough_for_style": early_enough,
        "phase3b_verdict": verdict,
    }


# ── Quintile table ─────────────────────────────────────────────────────────────

def quintile_table(df: pd.DataFrame, comp_col: str) -> list[dict]:
    df_c = df.dropna(subset=[comp_col, "w150_range"]).copy()
    df_c["quintile"] = pd.qcut(df_c[comp_col], 5, labels=False) + 1
    rows = []
    for q in range(1, 6):
        sub = df_c[df_c["quintile"] == q]["w150_range"]
        rows.append({
            "quintile": int(q),
            "n": int(len(sub)),
            "median_w150_range": round(float(sub.median()), 6),
            "mean_w150_range":   round(float(sub.mean()),   6),
        })
    return rows


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Phase 3B — Composite Premarket Signal\n")

    print("Loading 1m bars...")
    bars = load_all_1m()
    print(f"  {len(bars):,} bars")

    print("Building window table...")
    wt = build_window_table(bars)
    print(f"  {len(wt)} trading days")

    print("Loading daily_series and IVX...")
    daily = load_daily()
    ivx   = load_ivx()

    print("Building signal df...")
    df = build_signal_df(wt, daily, ivx)
    print(f"  {len(df)} rows after merge")

    print("Building composites...")
    df = build_composites(df)

    composites = [
        ("composite_eq5", "EqualWeight-5 (H44+H94+H97+H70+H99)"),
        ("composite_wt5", "PartialRho-Weighted-5 (H44+H94+H97+H70+H99)"),
        ("composite_eq4", "EqualWeight-4 (H44+H97+H70+H99, excl H94)"),
    ]

    results = {}
    for col, label in composites:
        print(f"\n  Testing {label}...")
        res = test_composite(df, col, label)
        results[col] = res
        sp = res["primary_spearman_w150"]
        mw = res["mw_top_vs_bottom_quartile"]
        print(f"    Spearman ρ={sp['rho']}, p={sp['p_nw']:.4f}, peak={res['peak_window']}, "
              f"early={res['early_enough_for_style']}, verdict={res['phase3b_verdict']}")
        print(f"    MW top-vs-bottom quartile: Cliff's d={mw['cliff_d']}, p={mw['p']:.4f}")

    # Quintile tables for best composite (highest ρ)
    best_col = max(
        [c for c, _ in composites],
        key=lambda c: abs(results[c]["primary_spearman_w150"]["rho"] or 0)
    )
    print(f"\n  Quintile table for {best_col}:")
    qtable = quintile_table(df, best_col)
    for row in qtable:
        print(f"    Q{row['quintile']} (n={row['n']}): median w150_range={row['median_w150_range']:.5f}")

    # Save JSON
    out = {
        "run_date": str(date.today()),
        "composites": results,
        "quintile_table_best_composite": {
            "composite": best_col,
            "table": qtable,
        },
    }
    out_path = RESULTS_DIR / "phase3b_composite.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n  → saved {out_path.name}")

    write_vault(results, qtable, best_col)
    print(f"  → vault/Phase3/Phase3B-Composite-Signal.md written")


# ── Vault note ─────────────────────────────────────────────────────────────────

def _fmt_sp(d: dict) -> str:
    if d["rho"] is None:
        return "n/a"
    return f"ρ={d['rho']:.3f}, p={d['p_nw']:.4f}, n={d['n']}"


def _fmt_mw(d: dict | None) -> str:
    if d is None or d["cliff_d"] is None:
        return "n/a"
    return f"Cliff's d={d['cliff_d']:.3f}, p={d['p']:.4f}, n_high={d['n_high']}, n_low={d['n_low']}"


def write_vault(results: dict, qtable: list[dict], best_col: str) -> None:
    eq5 = results["composite_eq5"]
    wt5 = results["composite_wt5"]
    eq4 = results["composite_eq4"]

    best_label = {
        "composite_eq5": "EqualWeight-5",
        "composite_wt5": "PartialRho-Weighted-5",
        "composite_eq4": "EqualWeight-4",
    }[best_col]

    def wf_table(res: dict) -> str:
        wf = res["walk_forward_spearman"]
        lines = ["| Split | n | ρ | p |", "|---|---|---|---|"]
        for split in ["train", "val", "holdout"]:
            d = wf[split]
            if d["rho"] is None:
                lines.append(f"| {split.capitalize()} | {d['n']} | n/a (burn-in) | — |")
            else:
                lines.append(f"| {split.capitalize()} | {d['n']} | {d['rho']:.3f} | {d['p_nw']:.4f} |")
        return "\n".join(lines)

    def window_table(res: dict) -> str:
        lines = ["| Window | ρ | p |", "|---|---|---|"]
        for w, d in res["window_rhos"].items():
            pk = " ← peak" if w == res["peak_window"] else ""
            rho = f"{d['rho']:.3f}" if d["rho"] is not None else "n/a"
            p   = f"{d['p_nw']:.4f}" if d["p_nw"] is not None else "—"
            lines.append(f"| {w}{pk} | {rho} | {p} |")
        return "\n".join(lines)

    def quintile_md(rows: list[dict]) -> str:
        lines = ["| Quintile | n | Median w150_range | Mean w150_range |",
                 "|---|---|---|---|"]
        for r in rows:
            lines.append(f"| Q{r['quintile']} | {r['n']} | {r['median_w150_range']:.5f} | {r['mean_w150_range']:.5f} |")
        return "\n".join(lines)

    sp5  = eq5["primary_spearman_w150"]
    sp_w = wt5["primary_spearman_w150"]
    sp4  = eq4["primary_spearman_w150"]
    mw5  = eq5["mw_top_vs_bottom_quartile"]
    mw_w = wt5["mw_top_vs_bottom_quartile"]
    mw4  = eq4["mw_top_vs_bottom_quartile"]

    note = f"""# Phase 3B — Composite Premarket Signal

**Run date:** 2026-04-20
**Script:** `scripts/30_run_phase3b.py`
**Inputs:** 5 non-redundant premarket survivors from Phase 3 redundancy audit
**Outcome tested:** `w150_range` (09:30–11:59 session range, max 2.5h horizon)
**Walk-forward:** train=2024, val=2025, holdout=2026-Q1

---

## Signals Included

All 5 signals are pre-open (prior-day EOD) and point the same direction — higher = wider day expected.

| Signal | Hypothesis | Partial ρ (from audit) | Phase 3 verdict |
|---|---|---|---|
| `iv_spread_30_60` | H44 | 0.433 | too_late_for_style (individually) |
| `range_pct_rank` | H70 | 0.131 | supported_trading_useful |
| `iv_velocity_5d` | H97 | 0.168 | supported_trading_useful |
| `spread_pct_rank` | H99 | 0.144 | supported_trading_useful |
| `ivx_spread_7_30` | H94 | 0.138 | too_late_for_style (individually) |

> H44 and H94 were individually `too_late_for_style` — their peak effect occurs after w210. In the composite, they contribute marginal information but the composite timing gate is tested independently.

---

## Composite Variants

Three composites built, all from rank-normalized [0,1] signals:

| Composite | Signals | Weighting |
|---|---|---|
| EqualWeight-5 | All 5 | Equal (0.20 each) |
| PartialRho-Weighted-5 | All 5 | Weighted by partial ρ from audit |
| EqualWeight-4 | Excl H94 | Equal (0.25 each) — H94 most correlated with H44 |

---

## Results

### EqualWeight-5 (H44 + H94 + H97 + H70 + H99)

**Primary Spearman vs w150_range:** {_fmt_sp(sp5)}
**Verdict:** `{eq5['phase3b_verdict']}` | Peak window: `{eq5['peak_window']}` | Early enough: {eq5['early_enough_for_style']}
**MW top-vs-bottom quartile:** {_fmt_mw(mw5)}

{wf_table(eq5)}

Window ρ by horizon:
{window_table(eq5)}

---

### PartialRho-Weighted-5

**Primary Spearman vs w150_range:** {_fmt_sp(sp_w)}
**Verdict:** `{wt5['phase3b_verdict']}` | Peak window: `{wt5['peak_window']}` | Early enough: {wt5['early_enough_for_style']}
**MW top-vs-bottom quartile:** {_fmt_mw(mw_w)}

{wf_table(wt5)}

Window ρ by horizon:
{window_table(wt5)}

---

### EqualWeight-4 (excl H94)

**Primary Spearman vs w150_range:** {_fmt_sp(sp4)}
**Verdict:** `{eq4['phase3b_verdict']}` | Peak window: `{eq4['peak_window']}` | Early enough: {eq4['early_enough_for_style']}
**MW top-vs-bottom quartile:** {_fmt_mw(mw4)}

{wf_table(eq4)}

Window ρ by horizon:
{window_table(eq4)}

---

## Quintile Breakdown — {best_label}

Range of the 2.5h session by composite score quintile (Q1=lowest signal, Q5=highest):

{quintile_md(qtable)}

---

## Key Takeaways

See verdict fields above for per-composite conclusions. General principles:
- All three composites combine signals that individually had varying timing and strength.
- The quintile table reveals whether the composite produces a monotonic range gradient from Q1→Q5.
- If EqualWeight-4 outperforms EqualWeight-5, excluding H94 reduces noise from the most-correlated signal pair.
- Use the best-performing non-rejected composite as the pre-open vol regime score: high composite → size up, prepare for active day; low composite → reduce size, expect compression.
"""

    out_path = VAULT_P3 / "Phase3B-Composite-Signal.md"
    with open(out_path, "w") as f:
        f.write(note)


if __name__ == "__main__":
    main()
