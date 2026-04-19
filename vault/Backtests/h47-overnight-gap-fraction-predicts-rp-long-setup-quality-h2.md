---
hypothesis_number: H47
verdict: inconclusive
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: directly_tested
observations: 88
signals: 58
primary_metric: win_rate_diff_small_vs_large_gap
metric_value: 0.1593
---

# H47: Overnight Gap Fraction Predicts RP-Long Setup Quality (H2)

**🟡 INCONCLUSIVE**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Overnight Gap Fraction Predicts RP-Long Setup Quality (H2)_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 88 |
| Rows after validation | 88 |
| Rows excluded | 0 |
| Exclusion reason | missing gap_fraction or ret_60m |
| Final observations tested | 88 |
| Signal days | 58 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 88 |
| Signals | 58 |
| Primary Metric | win_rate_diff_small_vs_large_gap |
| Metric Value | 0.1593 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.05 |
| Reject Threshold | 0.0 |

## Verdict

**🟡 INCONCLUSIVE**

Direction present but criteria not met: diff=0.159 (p=0.1328)

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_small | 34 |
| n_mid | 30 |
| n_large | 24 |
| win_rate_small | 0.6176 |
| win_rate_mid | 0.6 |
| win_rate_large | 0.4583 |
| cliffs_delta | 0.174 |
| p_mannwhitney | 0.1328 |
| is_monotonic | True |
| kruskal_p | 0.2608 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=58) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `strategy_win_rate` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.3099 · IQ: strong |
| Stability | 10.0 | 10 | Measured (consistency: 100%) |
| **Phase 1 Score** | **55.0** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: [0.0651, 0.2535] (wilson_interval)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
