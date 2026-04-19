---
hypothesis_number: H59
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 565
signals: 110
primary_metric: thursday_slope_predicts_monday_iv_win_rate
metric_value: 0.6545
---

# H59: Thursday IV Term Structure Predicts Monday IV Direction (Weekly Expiry Roll Effect)

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Thursday IV Term Structure Predicts Monday IV Direction (Weekly Expiry Roll Effect)_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 565 |
| Rows excluded | 0 |
| Exclusion reason | Requires matching Thursday-to-Monday pairs; day-of-week filtering |
| Final observations tested | 565 |
| Signal days | 110 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 565 |
| Signals | 110 |
| Primary Metric | thursday_slope_predicts_monday_iv_win_rate |
| Metric Value | 0.6545 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.6 |
| Reject Threshold | 0.5 |

## Verdict

**✅ SUPPORTED**

Thursday slope correctly predicts Monday IV direction 65.5% of weeks (n=110, wins=72, p_binomial=0.0008) — consistent with weekly expiry roll compression.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_weeks | 110 |
| n_wins | 72 |
| win_rate | 0.6545 |
| p_binomial | 0.0008 |
| mean_monday_change_contango | 0.0048 |
| mean_monday_change_backwardation | -0.0051 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=565) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `intraday_pattern` (stored) |
| Statistical Reliability | 20.0 | 20 | FDR-within-family p: 0.0011 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **65.0** | **100** | |

**Priority: 🟡 WATCHLIST**  Stat test: `binomial`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
