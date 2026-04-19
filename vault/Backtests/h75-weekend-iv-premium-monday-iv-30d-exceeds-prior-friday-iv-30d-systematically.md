---
hypothesis_number: H75
verdict: inconclusive
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 565
signals: 107
primary_metric: mean_iv_change_monday
metric_value: 0.0011
---

# H75: Weekend IV Premium: Monday iv_30d Exceeds Prior-Friday iv_30d Systematically

**🟡 INCONCLUSIVE**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Weekend IV Premium: Monday iv_30d Exceeds Prior-Friday iv_30d Systematically_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 565 |
| Rows excluded | 0 |
| Exclusion reason | Requires matched Monday/Friday pairs |
| Final observations tested | 565 |
| Signal days | 107 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 565 |
| Signals | 107 |
| Primary Metric | mean_iv_change_monday |
| Metric Value | 0.0011 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.003 |
| Reject Threshold | 0.0 |

## Verdict

**🟡 INCONCLUSIVE**

mean_change=0.00105, p_one_sided=0.2647. Some upward bias (62.6% of Mondays higher) but below threshold.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_matched_pairs | 107 |
| mean_iv_change_monday | 0.001052 |
| median_iv_change_monday | 0.00221 |
| pct_mondays_higher | 0.6262 |
| p_ttest_one_sided | 0.2647 |
| t_statistic | 0.631 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=107) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `iv_level_change` (pattern_match) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **45.0** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
