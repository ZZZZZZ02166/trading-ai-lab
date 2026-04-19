---
hypothesis_number: H78
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 563
signals: 264
primary_metric: pct_continuation
metric_value: 0.4697
---

# H78: VWAP Reclaim After Open — Confirmed Cross Predicts Next-Bar-Open 30-Minute Continuation

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _VWAP Reclaim After Open — Confirmed Cross Predicts Next-Bar-Open 30-Minute Continuation_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 563 |
| Rows after validation | 563 |
| Rows excluded | 0 |
| Exclusion reason | 5-min bar sessions; 2-bar quality filter + 09:45-10:25 window |
| Final observations tested | 563 |
| Signal days | 264 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 563 |
| Signals | 264 |
| Primary Metric | pct_continuation |
| Metric Value | 0.4697 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.55 |
| Reject Threshold | 0.5 |

## Verdict

**❌ REJECTED**

pct_continuation=0.470 (124/264), p_binomial=0.8523. No reliable 30-min continuation after VWAP reclaim.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_confirmed_reclaims | 264 |
| n_raw_first_crosses | 346 |
| n_wins | 124 |
| filter_reduction_pct | 0.237 |
| pct_days_with_reclaim | 0.4689 |
| mean_return_30min_reclaim | 0.000197 |
| p_binomial | 0.8523 |
| pct_held_2bars | 0.5152 |
| pct_held_5bars | 0.3636 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=264) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.9834 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **45.0** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `binomial`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
