---
hypothesis_number: H70
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 564
signals: 113
primary_metric: win_rate_top_quintile
metric_value: 0.8053
---

# H70: Top-Quintile Daily Range Autocorrelation: High-RV Days Predict High-RV Next Session

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Top-Quintile Daily Range Autocorrelation: High-RV Days Predict High-RV Next Session_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 564 |
| Rows excluded | 1 |
| Exclusion reason | 1-day forward shift; next_range NaN on last row |
| Final observations tested | 564 |
| Signal days | 113 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 564 |
| Signals | 113 |
| Primary Metric | win_rate_top_quintile |
| Metric Value | 0.8053 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.6 |
| Reject Threshold | 0.5 |

## Verdict

**✅ SUPPORTED**

win_rate=0.805 (91/113) > 0.60 threshold, p_binomial=0.0000 < 0.10. Top-quintile range threshold: 0.0184.

## Extra Metrics

| Metric | Value |
|--------|-------|
| q80_threshold | 0.01837 |
| median_range | 0.01192 |
| n_signal | 113 |
| n_wins | 91 |
| p_binomial | 0.0 |
| mean_next_range_signal | 0.02023 |
| mean_next_range_rest | 0.01256 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=113) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 20.0 | 20 | Family: `strategy_win_rate` (pattern_match) |
| Statistical Reliability | 20.0 | 20 | FDR-within-family p: 0.0000 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **85.0** | **100** | |

**Priority: 🟢 PROMOTE**  Stat test: `binomial`
CI: [0.7323, 0.8783] (wilson_interval)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.


## Phase 2 — Intraday Robustness (Batch 2)

**Verdict: SUPPORTED**
rho=0.479, p_nw=0.0000, mixed, monotonic=True

**Burn-in warning:** True — train split has 0 mature rows (rolling-252 mostly immature in 2024). Val/holdout carry the analytical weight.

### Transition Matrix (prior range quintile → next day range quintile)

| Prior Q→ | Next Q1 | Next Q2 | Next Q3 | Next Q4 | Next Q5 |
|---|---|---|---|---|---|
| Q1 | 0.462 | 0.267 | 0.159 | 0.113 | 0.032 |
| Q2 | 0.262 | 0.233 | 0.254 | 0.145 | 0.065 |
| Q3 | 0.108 | 0.267 | 0.238 | 0.226 | 0.161 |
| Q4 | 0.108 | 0.167 | 0.190 | 0.290 | 0.258 |
| Q5 | 0.062 | 0.067 | 0.159 | 0.226 | 0.484 |

**Diagonal dominance confirms persistence:** Q1→Q1=0.462, Q5→Q5=0.484.

### Quintile Gradient (mature rows)

| Quintile | n | Median Next Range |
|---|---|---|
| Q1 | 65 | 0.009078 |
| Q2 | 60 | 0.011290 |
| Q3 | 63 | 0.011938 |
| Q4 | 62 | 0.014716 |
| Q5 | 62 | 0.019362 |

**Monotonic:** True — gradient steps cleanly from Q1 (0.0091) to Q5 (0.0194).

### Walk-Forward Spearman (continuous prior_range_pct → next_day_range)

| Split | rho | p_nw | n |
|---|---|---|---|
| full | 0.479 | 0.0000 | 311 |
| train | n/a (no mature rows) | n/a | 0 |
| val | 0.514 | 0.0000 | 250 |
| holdout | 0.177 | 0.0541 | 61 |

**Consistency:** mixed (2/3 positive splits)
Note: train=0 mature rows due to 252-day burn-in. Val rho=0.514 (p<0.0001), holdout rho=0.177 (p=0.054).

### Binary MW: Q5 vs Rest

| Split | diff | p | Cliff's d | n_Q5 | n_rest |
|---|---|---|---|---|---|
| full | 0.0074 | 0.0000 | 0.515 | 70 | 493 |
| train | n/a | n/a | n/a | 0 | 252 |
| val | 0.0089 | 0.0000 | 0.611 | 57 | 193 |
| holdout | 0.0009 | 0.4060 | 0.045 | 13 | 48 |

**Key finding:** H70 survives outcome correction and holds through val+holdout. Val Cliff's d=0.61 is large. Holdout p=0.406 (only 13 Q5 days) but direction preserved. Training split entirely unusable due to burn-in.

---

## Phase 3 — Trading Utility Test

**Verdict:** ✅ SUPPORTED — Trading Useful
**Signal Strength Tier:** core-fragile/no-train
**Role:** premarket_framing
**Signal:** prior_day_range.rolling(252, min_periods=252).rank(pct=True). Global computation, no split leakage.
**Primary Outcome:** w150_range
**n:** 311
**Verdict Reason:** rho=0.524, p_nw=0.0000, peak=w30, val_rho=0.565, holdout_rho=0.115

| Split | rho | p_nw | n |
|---|---|---|---|
| full | 0.524 | 0.0000 | 311 |
| train | n/a | n/a | 0 |
| val | 0.565 | 0.0000 | 250 |
| holdout | 0.115 | 0.2634 | 61 |
**Consistency:** mixed (2/3)

**Effect by window (rho vs signal):**

| Window | rho | p_nw |
|---|---|---|
| w30 | 0.560 | 0.0000 |
| w60 | 0.558 | 0.0000 |
| w120 | 0.530 | 0.0000 |
| w150 | 0.524 | 0.0000 |
| w210 | 0.532 | 0.0000 |
**Peak window:** w30 | **Early enough for style:** True

> ⚠️ **Burn-in warning:** 252-day rolling window consumes all 2024 training data. n_train=0 (all NaN due to burn-in). Phase 3 conclusions are out-of-sample only (val + holdout). No in-sample reference period. Treat with additional caution.
