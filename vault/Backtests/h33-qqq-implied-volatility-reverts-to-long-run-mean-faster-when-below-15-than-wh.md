---
hypothesis_number: H33
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: directly_tested
observations: 544
signals: 35
primary_metric: ar1_reversion_speed_low_vs_high
metric_value: -0.4723
---

# H33: QQQ Implied Volatility Reverts to Long-Run Mean Faster When Below 15% Than When Above 30%

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _QQQ Implied Volatility Reverts to Long-Run Mean Faster When Below 15% Than When Above 30%_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 564 |
| Rows after validation | 544 |
| Rows excluded | 20 |
| Exclusion reason | rows with missing iv_30d or insufficient rolling window excluded |
| Final observations tested | 544 |
| Signal days | 35 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 544 |
| Signals | 35 |
| Primary Metric | ar1_reversion_speed_low_vs_high |
| Metric Value | -0.4723 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.02 |
| Reject Threshold | -0.01 |

## Verdict

**❌ REJECTED**

High-regime reverts faster: speed_low=0.2505 speed_high=0.7228 diff=-0.4723.

## Extra Metrics

| Metric | Value |
|--------|-------|
| beta_low | 0.7495 |
| beta_mid | 0.8746 |
| beta_high | 0.2772 |
| speed_low | 0.2505 |
| speed_high | 0.7228 |
| n_low | 35 |
| n_mid | 494 |
| n_high | 15 |
| bootstrap_p | 0.941 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=35) | 24.5 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `regime_comparison` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 1.0000 · IQ: strong |
| Stability | 0.0 | 10 | Measured (consistency: 0%) |
| **Phase 1 Score** | **44.5** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `bootstrap`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
