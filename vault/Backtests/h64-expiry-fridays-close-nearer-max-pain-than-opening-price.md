---
hypothesis_number: H64
verdict: rejected
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: directly_tested
observations: 37
signals: 37
primary_metric: max_pain_approach_win_rate_expiry_fridays
metric_value: 0.4054
---

# H64: Expiry Fridays Close Nearer Max Pain Than Opening Price

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Expiry Fridays Close Nearer Max Pain Than Opening Price_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 190 |
| Rows after validation | 37 |
| Rows excluded | 153 |
| Exclusion reason | Filtered to Fridays (weekly expiry). QQQ has 0DTE options every day, so has_expiry=True for all dates — explicit Friday filter required. max_pain computed from same-day EOD dte=0 OI (minor lookahead for open comparison). |
| Final observations tested | 37 |
| Signal days | 37 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 37 |
| Signals | 37 |
| Primary Metric | max_pain_approach_win_rate_expiry_fridays |
| Metric Value | 0.4054 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.6 |
| Reject Threshold | 0.5 |

## Verdict

**❌ REJECTED**

Rejected (corrected test — Friday filter applied): win_rate=40.5%% on 37 expiry Fridays (n=37, wins=15, p_binomial=0.9061 one-sided). Price moves AWAY from max pain more often than toward it. Mean dist: open=8.794 -> close=10.161 (improvement=-1.367). No max-pain magnetism on weekly expiry Fridays. BUG FIX NOTE: Prior run used n=190 (all sessions) because QQQ has 0DTE options every day; has_expiry=True for all 190 dates. Corrected to filter dayofweek==4 (Fridays only).

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_expiry_fridays | 37 |
| n_moved_toward | 15 |
| win_rate | 0.4054 |
| p_binomial_one_sided | 0.9061 |
| mean_dist_open | 8.794 |
| mean_dist_close | 10.161 |
| mean_improvement | -1.367 |
| filter_note | Fridays only (dayofweek==4). QQQ has 0DTE every day; Friday filter required. |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=37) | 17.5 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `strategy_win_rate` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **37.5** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: [0.2472, 0.5636] (wilson_interval)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
