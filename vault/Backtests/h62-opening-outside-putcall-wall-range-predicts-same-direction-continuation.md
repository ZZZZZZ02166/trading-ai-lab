---
hypothesis_number: H62
verdict: rejected
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: directly_tested
observations: 190
signals: 15
primary_metric: continuation_rate_outside_open_minus_0_5
metric_value: -0.5000
---

# H62: Opening Outside Put/Call Wall Range Predicts Same-Direction Continuation

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Opening Outside Put/Call Wall Range Predicts Same-Direction Continuation_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 190 |
| Rows after validation | 190 |
| Rows excluded | 0 |
| Exclusion reason | Requires valid put_wall and call_wall; OHLC from daily_series |
| Final observations tested | 190 |
| Signal days | 15 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 190 |
| Signals | 15 |
| Primary Metric | continuation_rate_outside_open_minus_0_5 |
| Metric Value | -0.5000 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.1 |
| Reject Threshold | -0.05 |

## Verdict

**❌ REJECTED**

Rejection confirmed in the claimed direction: 0.0% continuation rate on 15 outside-wall opens (12 above call_wall, 3 below put_wall). All 15 outside-wall opens reversed back inside the wall by close — consistent with walls acting as mean-reversion boundaries, not breakout levels. N=15 is too small for statistical inference (binomial p=1.0000 is misleading for a one-sided test at the claimed threshold; the data goes opposite to the claim). Lookahead note: walls use same-day EOD OI; the open classification may be slightly contaminated. p_binomial is one-sided (alternative: rate > 50%).

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_outside_open | 15 |
| n_above_call_wall | 12 |
| n_below_put_wall | 3 |
| continuation_rate | 0.0 |
| p_binomial | 1.0 |
| pct_outside_open | 0.079 |
| review_note | 100% reversal rate (opposite of continuation hypothesis) on n=15 outside-open days. Suggestive of wall-as-resistance but too few events for statistical confidence. |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=15) | 16.2 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `strategy_win_rate` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 1.0000 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **36.2** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `binomial`
CI: [0.0000, 0.0052] (wilson_interval)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
