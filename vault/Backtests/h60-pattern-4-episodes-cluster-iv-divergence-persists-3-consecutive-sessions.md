---
hypothesis_number: H60
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 555
signals: 73
primary_metric: pct_pattern4_runs_ge_3_days
metric_value: 0.2750
---

# H60: Pattern 4 Episodes Cluster: IV Divergence Persists 3+ Consecutive Sessions

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Pattern 4 Episodes Cluster: IV Divergence Persists 3+ Consecutive Sessions_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 555 |
| Rows excluded | 10 |
| Exclusion reason | 5-day rolling warmup for IV/HV change |
| Final observations tested | 555 |
| Signal days | 73 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 555 |
| Signals | 73 |
| Primary Metric | pct_pattern4_runs_ge_3_days |
| Metric Value | 0.2750 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.5 |
| Reject Threshold | 0.3 |

## Verdict

**❌ REJECTED**

Pattern 4 does not cluster: only 27.5% of 40 episodes last >= 3 days (median run=1.0). Signal resolves quickly.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_runs | 40 |
| pct_runs_ge_3 | 0.275 |
| median_run_length | 1.0 |
| mean_run_length | 1.82 |
| max_run_length | 5 |
| pct_pattern4_days | 0.132 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=27) | 24.7 | 25 | Independence-adjusted count |
| Effect Size | 20.0 | 20 | Family: `persistence` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **64.7** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: Not available (requires_bootstrap_distribution)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
