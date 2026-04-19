---
hypothesis_number: H63
verdict: rejected
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: directly_tested
observations: 188
signals: 52
primary_metric: mean_next_return_diff_rising_vs_falling_oi_on_up_days
metric_value: -0.0025
---

# H63: Rising Price With Rising Open Interest Predicts Next-Session Continuation

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Rising Price With Rising Open Interest Predicts Next-Session Continuation_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 190 |
| Rows after validation | 188 |
| Rows excluded | 2 |
| Exclusion reason | Requires consecutive-date OI data; 1-day forward shift for next return |
| Final observations tested | 188 |
| Signal days | 52 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 188 |
| Signals | 52 |
| Primary Metric | mean_next_return_diff_rising_vs_falling_oi_on_up_days |
| Metric Value | -0.0025 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.001 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

Rejected: rising OI on up days predicts WORSE next-session returns, opposite to hypothesis claim. mean_next_rising=-0.00110 vs mean_next_falling=+0.00137 (diff=-0.00248, Cliff's d=-0.158). Mann-Whitney p=0.9248 (one-sided, alternative: rising > falling) — strongly inconsistent with the claimed direction. Two-sided p ≈ 0.15 (inconclusive for the reverse claim). Methodological note: total_oi includes 0DTE contracts (created and expired same day in QQQ), making oi_change a noisy proxy for multi-day institutional positioning. The result may reflect 0DTE turnover patterns rather than persistent positioning.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_up_days_rising_oi | 52 |
| n_up_days_falling_oi | 60 |
| mean_next_return_rising | -0.001102 |
| mean_next_return_falling | 0.001375 |
| cliffs_delta | -0.1577 |
| p_mannwhitney | 0.9248 |
| u_stat | 1314.0 |
| p_mannwhitney_note | one-sided (alternative: rising_oi > falling_oi) |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=52) | 24.8 | 25 | Independence-adjusted count |
| Effect Size | 0.1 | 20 | Family: `mean_difference` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.9823 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **44.9** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
