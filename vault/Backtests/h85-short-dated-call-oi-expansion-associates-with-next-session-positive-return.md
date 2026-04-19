---
hypothesis_number: H85
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 244
signals: 42
primary_metric: win_rate_call_oi_expansion
metric_value: 0.4762
---

# H85: Short-Dated Call OI Expansion Associates with Next-Session Positive Return

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Short-Dated Call OI Expansion Associates with Next-Session Positive Return_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 317 |
| Rows after validation | 244 |
| Rows excluded | 73 |
| Exclusion reason | Requires consecutive call param file dates; next-session log_return from daily_series |
| Final observations tested | 244 |
| Signal days | 42 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 244 |
| Signals | 42 |
| Primary Metric | win_rate_call_oi_expansion |
| Metric Value | 0.4762 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.55 |
| Reject Threshold | 0.5 |

## Verdict

**❌ REJECTED**

win_rate=47.6% (n_signal=42, wins=20), p_binomial=0.6780, win_rate_control=57.1%. n_expiry_filtered=71 (22.4% of dates). Call OI expansion reflects covered call writing, roll activity, spread construction, and dealer inventory changes alongside directional long-call positioning. Net position direction is unknown. Exploratory association only.

## Extra Metrics

| Metric | Value |
|--------|-------|
| win_rate_signal | 0.4762 |
| win_rate_control | 0.5714 |
| n_signal | 42 |
| n_wins_signal | 20 |
| p_binomial | 0.678016 |
| p_mannwhitney | 0.714346 |
| n_control | 98 |
| n_expiry_filtered | 71 |
| pct_expiry_filtered | 0.224 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=42) | 21.6 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `strategy_win_rate` (pattern_match) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 1.0000 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **41.5** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `binomial`
CI: [0.3252, 0.6272] (wilson_interval)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
