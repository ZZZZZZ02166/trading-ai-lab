---
hypothesis_number: H53
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 554
signals: 73
primary_metric: median_range_diff_pattern4_vs_control
metric_value: 0.0038
---

# H53: IV Rising While Realized Vol Flat Predicts Next-Session Range Expansion (Passarelli Pattern 4)

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _IV Rising While Realized Vol Flat Predicts Next-Session Range Expansion (Passarelli Pattern 4)_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 554 |
| Rows excluded | 11 |
| Exclusion reason | 5-day rolling warmup for IV/HV change; 1-day forward shift for next-session range |
| Final observations tested | 554 |
| Signal days | 73 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 554 |
| Signals | 73 |
| Primary Metric | median_range_diff_pattern4_vs_control |
| Metric Value | 0.0038 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.002 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

Pattern 4 sessions show higher next-day range: median_p4=0.0140 vs median_ctrl=0.0102 (diff=0.0038, p=0.0000, Cliff's d=0.414)

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_pattern4 | 73 |
| n_control | 177 |
| median_range_pattern4 | 0.014 |
| median_range_control | 0.0102 |
| cliffs_delta | 0.4137 |
| p_mannwhitney | 0.0 |
| u_stat | 9133.0 |
| pct_pattern4_days | 0.132 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=73) | 24.7 | 25 | Independence-adjusted count |
| Effect Size | 0.1 | 20 | Family: `regime_comparison` (stored) |
| Statistical Reliability | 20.0 | 20 | FDR-within-family p: 0.0000 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **64.8** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
