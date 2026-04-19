---
hypothesis_number: H54
verdict: inconclusive
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: directly_tested
observations: 190
signals: 11
primary_metric: median_range_diff_urgency_vs_baseline
metric_value: 0.0014
---

# H54: Intraday Option Volume Spike Without Price Move Is an Urgency Signal for Next-Session Range

**🟡 INCONCLUSIVE**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Intraday Option Volume Spike Without Price Move Is an Urgency Signal for Next-Session Range_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 190 |
| Rows after validation | 190 |
| Rows excluded | 0 |
| Exclusion reason | 20-day rolling volume baseline warmup; 1-day forward shift for next-session range |
| Final observations tested | 190 |
| Signal days | 11 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 190 |
| Signals | 11 |
| Primary Metric | median_range_diff_urgency_vs_baseline |
| Metric Value | 0.0014 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.002 |
| Reject Threshold | 0.0 |

## Verdict

**🟡 INCONCLUSIVE**

Direction present (diff=0.0014) but not significant (p=0.1134, Cliff's d=0.218)

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_urgency | 11 |
| n_baseline | 179 |
| pct_urgency_days | 0.058 |
| median_range_urgency | 0.0122 |
| median_range_baseline | 0.0107 |
| cliffs_delta | 0.2179 |
| p_mannwhitney | 0.1134 |
| u_stat | 1199.0 |
| vol_q80_threshold | 4302228.0 |
| signal_method | top_quintile_volume_AND_abs_return_lt_0.5pct |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=11) | 13.9 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `regime_comparison` (stored) |
| Statistical Reliability | 3.0 | 20 | FDR-within-family p: 0.1984 · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **36.9** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
