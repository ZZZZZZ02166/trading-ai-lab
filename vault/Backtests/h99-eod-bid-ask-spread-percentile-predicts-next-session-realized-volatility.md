---
hypothesis_number: H99
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 545
signals: 112
primary_metric: median_hv_diff_high_vs_low_spread
metric_value: 0.0390
---

# H99: EOD Bid-Ask Spread Percentile Predicts Next-Session Realized Volatility

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _EOD Bid-Ask Spread Percentile Predicts Next-Session Realized Volatility_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 545 |
| Rows excluded | 20 |
| Exclusion reason | bid/ask spread + 60-day rolling rank warmup + hv_20_cc next-day |
| Final observations tested | 545 |
| Signal days | 112 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 545 |
| Signals | 112 |
| Primary Metric | median_hv_diff_high_vs_low_spread |
| Metric Value | 0.0390 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.005 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

diff_median_hv=0.03898 (high_spread=0.18436, low_spread=0.14538), p_mannwhitney=0.0000, n_high=112, n_low=198, median_spread_pct=0.00002. Note: EOD bid/ask is regime proxy — not intraday fill estimate.

## Extra Metrics

| Metric | Value |
|--------|-------|
| median_hv_high_spread | 0.184356 |
| median_hv_low_spread | 0.145378 |
| median_spread_pct | 2.3e-05 |
| n_high_spread | 112 |
| n_low_spread | 198 |
| p_mannwhitney | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (derived) |
| Sample Adequacy (N_eff=112) | 16.8 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (other) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **43.8** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.


## Phase 2 — Intraday Robustness (Batch 2)

**Verdict: SUPPORTED**
rho=0.304, p_nw=0.0000, partial_p_vs_iv30=0.0230, consistent

### Contamination Audit

⚠️ Phase 1 used `hv_20_cc.shift(-1)` as the outcome — a 20-day smoothed HV measure incorporating returns from days t-18 through t+1. This is NOT a forward prediction; it captures regime persistence. Phase 2 replaces it with `next_day_range = (high-low)/close.shift(-1)`.

**Side-by-side comparison:**

| Outcome | Description | rho | p_nw | n |
|---|---|---|---|---|
| Phase 1 (contaminated) | hv_20_cc.shift(-1) — 20d smoothed, includes prior-19-day returns | 0.3202 | 5.86e-07 | 545 |
| Phase 2 (corrected) | next_day_range shift(-1) — clean next-session observation | 0.3041 | 3.45e-09 | 544 |

**Key result:** rho drops slightly from 0.320 to 0.304 — contamination was modest, not dominant. The Phase 2 signal survives with clean outcome.

### Walk-Forward Spearman (spread_rank → next_day_range)

| Split | rho | p_nw | n |
|---|---|---|---|
| full | 0.304 | 0.0000 | 544 |
| train | 0.182 | 0.0247 | 233 |
| val | 0.391 | 0.0000 | 250 |
| holdout | 0.396 | 0.0003 | 61 |

**Consistency:** consistent (3/3 positive splits) — signal strengthens in val (0.391) and holdout (0.396).

### Binary MW: Top 20% vs Bottom 20% Spread

| Split | diff | p | Cliff's d | n_high | n_low |
|---|---|---|---|---|---|
| full | 0.0042 | 0.0000 | 0.434 | 112 | 198 |
| train | 0.0022 | 0.0177 | 0.210 | 53 | 92 |
| val | 0.0084 | 0.0000 | 0.581 | 39 | 104 |
| holdout | n/a | n/a | n/a | 20 | 2 |

### Partial Spearman Controls

- vs iv_30d: partial_rho=0.09740137762938628, p=0.022963185489807237 — spread adds beyond IV level (p=0.023)
- vs prior_range (H70 control): see JSON extras

**Conclusion:** H99 SURVIVES outcome correction. The Phase 1 contamination was smaller than expected — rho=0.304 on clean outcome vs 0.320 on contaminated. Signal is consistent across all 3 splits and shows partial independence from iv_30d. Phase 3 potential: MEDIUM — spread as a liquidity/stress signal distinct from raw IV level.

---

## Phase 3 — Trading Utility Test

**Verdict:** ✅ SUPPORTED — Trading Useful
**Signal Strength Tier:** core-fragile
**Role:** premarket_framing_caution_overlay
**Signal:** rolling 60d rank of (ask-bid)/close (continuous [0,1])
**Primary Outcome:** w150_range
**n:** 543
**Verdict Reason:** rho_range=0.300, p_nw=0.0000, peak=w30, sign_ok=True

| Split | rho | p_nw | n |
|---|---|---|---|
| full | 0.300 | 0.0000 | 543 |
| train | 0.158 | 0.0640 | 232 |
| val | 0.403 | 0.0000 | 250 |
| holdout | 0.340 | 0.0013 | 61 |
**Consistency:** consistent (3/3)

**Effect by window (rho vs signal):**

| Window | rho | p_nw |
|---|---|---|
| w30 | 0.338 | 0.0000 |
| w60 | 0.316 | 0.0000 |
| w120 | 0.304 | 0.0000 |
| w150 | 0.300 | 0.0000 |
| w210 | 0.310 | 0.0000 |
**Peak window:** w30 | **Early enough for style:** True

> ℹ️ Primary interpretation: CAUTION OVERLAY. High spread_pct_rank (>0.75) flags liquidity-constrained days. Directional interpretation (w150_return) is SECONDARY and only reported if range effect is clearly established first. Do not default to direction framing.
