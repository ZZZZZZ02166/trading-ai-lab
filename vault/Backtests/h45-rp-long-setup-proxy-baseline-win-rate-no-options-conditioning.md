---
hypothesis_number: H45
verdict: inconclusive
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: directly_tested
observations: 88
signals: 88
primary_metric: win_rate_60m
metric_value: 0.5682
---

# H45: RP-Long Setup Proxy — Baseline Win Rate (No Options Conditioning)

**🟡 INCONCLUSIVE**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _RP-Long Setup Proxy — Baseline Win Rate (No Options Conditioning)_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 588 |
| Rows after validation | 88 |
| Rows excluded | 500 |
| Exclusion reason | days without RP-Long signal or missing data |
| Final observations tested | 88 |
| Signal days | 88 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 88 |
| Signals | 88 |
| Primary Metric | win_rate_60m |
| Metric Value | 0.5682 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.55 |
| Reject Threshold | 0.45 |

## Verdict

**🟡 INCONCLUSIVE**

win_rate_60m=56.8% not significantly above 50% (p_binom=0.1204, n=88)

## Extra Metrics

| Metric | Value |
|--------|-------|
| win_rate_60m | 0.5682 |
| win_rate_90m | 0.5909 |
| win_rate_eod | 0.5795 |
| mean_ret_60m | -0.00066 |
| median_ret_60m | 0.00105 |
| n_wins_60m | 50 |
| p_binomial | 0.1204 |
| n_signals | 88 |
| signal_rate_pct | 15.0 |
| n_trading_days | 588 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=88) | 17.5 | 25 | Independence-adjusted count |
| Effect Size | 13.6 | 20 | Family: `strategy_win_rate` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.3099 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **51.1** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `binomial`
CI: [0.4647, 0.6717] (wilson_interval)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
