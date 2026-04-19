---
hypothesis_number: H68
verdict: supported
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: directly_tested
observations: 190
signals: 37
primary_metric: median_dist_to_nearest_wall_friday_vs_non_friday
metric_value: -0.0013
---

# H68: Expiry Pinning at High-OI Strikes: Fridays vs Non-Friday Sessions

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Expiry Pinning at High-OI Strikes: Fridays vs Non-Friday Sessions_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 190 |
| Rows after validation | 190 |
| Rows excluded | 0 |
| Exclusion reason | Requires call_wall and put_wall; close from daily_series |
| Final observations tested | 190 |
| Signal days | 37 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 190 |
| Signals | 37 |
| Primary Metric | median_dist_to_nearest_wall_friday_vs_non_friday |
| Metric Value | -0.0013 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | -0.001 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

Fridays settle closer to nearest wall: 0.0105 vs 0.0117 (diff=-0.0013, p_mw=0.0387 one-sided, Cliff's d=-0.187). n_fri=37, n_nfri=153. Note: QQQ has 0DTE options every session — Friday vs non-Friday is the expiry-weight comparison (Fridays carry daily + weekly series). Walls average $36 wide; normalized dist is relative to underlying price (~$573 mean close).

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_fridays | 37 |
| n_non_fridays | 153 |
| median_dist_normalized_fri | 0.01047 |
| median_dist_normalized_nfri | 0.01174 |
| p_mannwhitney_one_sided | 0.0387 |
| cliffs_delta | -0.1874 |
| pct_within_3pts_friday | 0.324 |
| pct_within_3pts_non_friday | 0.157 |
| mean_wall_width | 35.93 |
| note | QQQ has 0DTE every session; Friday vs non-Friday is expiry-weight proxy |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=37) | 25.0 | 25 | Independence-adjusted count |
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
