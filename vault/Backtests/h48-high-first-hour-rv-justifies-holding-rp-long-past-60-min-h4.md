---
hypothesis_number: H48
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: directly_tested
observations: 563
signals: 192
primary_metric: spearman_r_fh_rv_vs_session_range
metric_value: 0.6097
---

# H48: High First-Hour RV Justifies Holding RP-Long Past 60 Min (H4)

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _High First-Hour RV Justifies Holding RP-Long Past 60 Min (H4)_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 563 |
| Rows after validation | 563 |
| Rows excluded | 0 |
| Exclusion reason | missing session_range or fh_rv |
| Final observations tested | 563 |
| Signal days | 192 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 563 |
| Signals | 192 |
| Primary Metric | spearman_r_fh_rv_vs_session_range |
| Metric Value | 0.6097 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.15 |
| Reject Threshold | 0.05 |

## Verdict

**✅ SUPPORTED**

First-hour RV predicts session range: r=0.610, p=0.0000, med_diff=0.0077, Cliff's d=0.739

## Extra Metrics

| Metric | Value |
|--------|-------|
| spearman_r | 0.6097 |
| p_spearman | 0.0 |
| n_low_rv | 186 |
| n_mid_rv | 185 |
| n_high_rv | 192 |
| median_range_low_rv | 0.00896 |
| median_range_mid_rv | 0.01132 |
| median_range_high_rv | 0.01663 |
| median_diff_high_vs_low | 0.00767 |
| cliffs_delta | 0.7392 |
| p_mannwhitney | 0.0 |
| is_monotonic | True |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=563) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 20.0 | 20 | Family: `correlation` (stored) |
| Statistical Reliability | 20.0 | 20 | FDR-within-family p: 0.0000 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **85.0** | **100** | |

**Priority: 🟢 PROMOTE**  Stat test: `spearman`
CI: [0.5550, 0.6591] (fisher_z_transform)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
