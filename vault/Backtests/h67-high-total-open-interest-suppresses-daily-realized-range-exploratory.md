---
hypothesis_number: H67
verdict: rejected
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: directly_tested
observations: 190
signals: 38
primary_metric: median_range_diff_high_oi_vs_low_oi
metric_value: 0.0001
---

# H67: High Total Open Interest Suppresses Daily Realized Range (Exploratory)

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _High Total Open Interest Suppresses Daily Realized Range (Exploratory)_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 190 |
| Rows after validation | 190 |
| Rows excluded | 0 |
| Exclusion reason | Requires total_oi (dte>0) from param files and OHLC from daily_series. EXPLORATORY — result may reflect regime co-variation, not dealer gamma causation. |
| Final observations tested | 190 |
| Signal days | 38 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 190 |
| Signals | 38 |
| Primary Metric | median_range_diff_high_oi_vs_low_oi |
| Metric Value | 0.0001 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | -0.001 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

No OI-range suppression: high-OI range=0.0116 vs low-OI=0.0115 (diff=0.0001, p_mw=0.6322 one-sided). EXPLORATORY: High OI may co-occur with volatile regimes rather than causing suppression. Excluding dte=0 OI reduces but does not eliminate this confound. Total-OI version also reported for comparison.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_top_oi_quintile | 38 |
| n_bot_oi_quintile | 38 |
| oi_dte_gt1_q80 | 1141751.0 |
| oi_dte_gt1_q20 | 418811.0 |
| median_range_high_oi | 0.01161 |
| median_range_low_oi | 0.01151 |
| p_mannwhitney_one_sided | 0.6322 |
| cliffs_delta | 0.0443 |
| total_oi_version_diff | 0.00328 |
| exploratory | True |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=38) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `regime_comparison` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **45.0** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
