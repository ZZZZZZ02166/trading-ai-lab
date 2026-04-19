---
hypothesis_number: H39
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: directly_tested
observations: 559
signals: 1
primary_metric: hurst_exponent_5d_rv
metric_value: 0.8275
---

# H39: QQQ Realized Volatility Is Positively Autocorrelated (Hurst Exponent > 0.5) at 5-Day Horizons

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _QQQ Realized Volatility Is Positively Autocorrelated (Hurst Exponent > 0.5) at 5-Day Horizons_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 564 |
| Rows after validation | 559 |
| Rows excluded | 5 |
| Exclusion reason | rows with missing close or insufficient 5-day window excluded |
| Final observations tested | 559 |
| Signal days | 1 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 559 |
| Signals | 1 |
| Primary Metric | hurst_exponent_5d_rv |
| Metric Value | 0.8275 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.55 |
| Reject Threshold | 0.5 |

## Verdict

**✅ SUPPORTED**

Hurst H=0.8275 > 0.55 bootstrap_p=0.0000. Post-spike H=0.8490 calm H=0.7866.

## Extra Metrics

| Metric | Value |
|--------|-------|
| H_full | 0.8275 |
| H_post_spike | 0.849 |
| H_calm_periods | 0.7866 |
| bootstrap_p | 0.0 |
| n_rv_obs | 559 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=27) | 24.9 | 25 | Independence-adjusted count |
| Effect Size | 20.0 | 20 | Family: `persistence` (stored) |
| Statistical Reliability | 20.0 | 20 | FDR-within-family p: 0.0000 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **84.9** | **100** | |

**Priority: 🟢 PROMOTE**  Stat test: `bootstrap`
CI: Not available (requires_bootstrap_distribution)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
