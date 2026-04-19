---
hypothesis_number: H74
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 564
signals: 87
primary_metric: win_rate_positive_3d
metric_value: 0.6437
---

# H74: Buy-the-Dip 3-Session Swing: After -1% Sessions, Cumulative 3-Session Return Is Positive

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Buy-the-Dip 3-Session Swing: After -1% Sessions, Cumulative 3-Session Return Is Positive_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 564 |
| Rows excluded | 1 |
| Exclusion reason | 3-day forward cumsum NaN for last 3 rows |
| Final observations tested | 564 |
| Signal days | 87 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 564 |
| Signals | 87 |
| Primary Metric | win_rate_positive_3d |
| Metric Value | 0.6437 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.55 |
| Reject Threshold | 0.5 |

## Verdict

**✅ SUPPORTED**

3-day win rate=0.644 (56/87) > 0.55 threshold, p_binomial=0.0048. mean_3d_return=0.0050, median_3d_return=0.0073. Signal: log_return < -1% (87 occurrences).

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_signal_days | 87 |
| n_wins | 56 |
| p_binomial | 0.0048 |
| mean_3d_return | 0.00496 |
| median_3d_return | 0.00735 |
| pct_signal_days | 0.154 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=87) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 20.0 | 20 | Family: `strategy_win_rate` (pattern_match) |
| Statistical Reliability | 20.0 | 20 | FDR-within-family p: 0.0096 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **85.0** | **100** | |

**Priority: 🟢 PROMOTE**  Stat test: `binomial`
CI: [0.5431, 0.7443] (wilson_interval)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
