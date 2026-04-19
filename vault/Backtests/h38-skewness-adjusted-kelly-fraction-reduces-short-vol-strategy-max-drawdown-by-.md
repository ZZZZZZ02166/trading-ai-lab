---
hypothesis_number: H38
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: directly_tested
observations: 545
signals: 545
primary_metric: dd_reduction_pct_skew_kelly_vs_standard
metric_value: 0.1076
---

# H38: Skewness-Adjusted Kelly Fraction Reduces Short-Vol Strategy Max Drawdown by More Than 25% vs Standard Kelly With Less Than 20% Return Sacrifice

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Skewness-Adjusted Kelly Fraction Reduces Short-Vol Strategy Max Drawdown by More Than 25% vs Standard Kelly With Less Than 20% Return Sacrifice_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 564 |
| Rows after validation | 545 |
| Rows excluded | 19 |
| Exclusion reason | rows with missing iv_30d or fwd_rv_20 excluded |
| Final observations tested | 545 |
| Signal days | 545 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 545 |
| Signals | 545 |
| Primary Metric | dd_reduction_pct_skew_kelly_vs_standard |
| Metric Value | 0.1076 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 25.0 |
| Reject Threshold | 10.0 |

## Verdict

**❌ REJECTED**

DD reduction only 0.1% < 10% threshold. Skewness correction provides minimal benefit.

## Extra Metrics

| Metric | Value |
|--------|-------|
| f_standard_kelly | 0.8348 |
| f_skew_adjusted_kelly | 0.6872 |
| lambda3_skewness_moment | -0.001301 |
| max_dd_standard | 0.9997 |
| max_dd_skew_adjusted | 0.9987 |
| dd_reduction_pct | 0.11 |
| cum_return_standard | 1.7473 |
| cum_return_skew_adjusted | 1.867 |
| return_sacrifice_pct | -6.85 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=545) | 24.5 | 25 | Independence-adjusted count |
| Effect Size | 20.0 | 20 | Family: `risk_sizing` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **64.5** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: Not available (N/A: single_path_simulation)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
