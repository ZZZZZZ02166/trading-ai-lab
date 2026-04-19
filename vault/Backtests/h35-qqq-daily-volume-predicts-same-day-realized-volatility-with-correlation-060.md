---
hypothesis_number: H35
verdict: inconclusive
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: directly_tested
observations: 563
signals: 281
primary_metric: spearman_r_volume_vs_abs_return
metric_value: 0.3443
---

# H35: QQQ Daily Volume Predicts Same-Day Realized Volatility With Correlation > 0.60

**🟡 INCONCLUSIVE**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _QQQ Daily Volume Predicts Same-Day Realized Volatility With Correlation > 0.60_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 564 |
| Rows after validation | 563 |
| Rows excluded | 1 |
| Exclusion reason | rows with missing volume or close excluded |
| Final observations tested | 563 |
| Signal days | 281 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 563 |
| Signals | 281 |
| Primary Metric | spearman_r_volume_vs_abs_return |
| Metric Value | 0.3443 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.5 |
| Reject Threshold | 0.3 |

## Verdict

**🟡 INCONCLUSIVE**

r=0.3443 direction correct but below threshold 0.5 or p=0.000000 not strong enough.

## Extra Metrics

| Metric | Value |
|--------|-------|
| p_spearman | 0.0 |
| n_high_vol_days | 287 |
| n_low_vol_days | 256 |
| median_abs_return_high | 0.010684 |
| median_abs_return_low | 0.004146 |
| ratio_high_vs_low | 2.5769 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=563) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 20.0 | 20 | Family: `correlation` (stored) |
| Statistical Reliability | 20.0 | 20 | FDR-within-family p: 0.0000 · IQ: strong |
| Stability | 10.0 | 10 | Measured (consistency: 100%) |
| **Phase 1 Score** | **95.0** | **100** | |

**Priority: 🟢 PROMOTE**  Stat test: `spearman`
CI: [0.2693, 0.4151] (fisher_z_transform)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
