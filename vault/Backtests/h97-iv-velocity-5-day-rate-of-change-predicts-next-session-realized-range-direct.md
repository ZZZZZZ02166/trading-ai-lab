---
hypothesis_number: H97
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 559
signals: 125
primary_metric: median_range_diff_rising_vs_falling_iv
metric_value: 0.0067
---

# H97: IV Velocity (5-Day Rate of Change) Predicts Next-Session Realized Range Direction

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _IV Velocity (5-Day Rate of Change) Predicts Next-Session Realized Range Direction_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 559 |
| Rows excluded | 6 |
| Exclusion reason | 5-day IV pct_change warmup + 1-day forward range |
| Final observations tested | 559 |
| Signal days | 125 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 559 |
| Signals | 125 |
| Primary Metric | median_range_diff_rising_vs_falling_iv |
| Metric Value | 0.0067 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.003 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

diff_median_range=0.00674 (rising=0.01683, falling=0.01009), p_mannwhitney=0.0000, n_rising=125, n_falling=123, pct_rising=0.224, pct_falling=0.220.

## Extra Metrics

| Metric | Value |
|--------|-------|
| median_range_rising | 0.016833 |
| median_range_falling | 0.010094 |
| n_rising | 125 |
| n_falling | 123 |
| pct_days_rising | 0.2236 |
| pct_days_falling | 0.22 |
| p_mannwhitney | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (derived) |
| Sample Adequacy (N_eff=125) | 18.3 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **45.3** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.

---

## Phase 2 — Intraday Robustness

**Classification:** hybrid  
**Phase 2 Verdict:** ✅ SUPPORTED  
**Reason:** diff=0.0068 > 0.003, p=0.0000 < 0.1, consistent  
**Phase 1 Alignment:** confirmed

> Phase 1 used EOD daily range. Phase 2 validates velocity signal vs 1m intraday range windows.

### Walk Forward Session

| Split | diff | p | cliff_d | n_a | n_b |
|---|---|---|---|---|---|
| full | 0.0068 | 0.0000 | 0.503 | 125 | 123 |
| train | 0.0039 | 0.0000 | 0.452 | 49 | 54 |
| val | 0.0088 | 0.0000 | 0.561 | 62 | 63 |
| holdout | 0.0029 | 0.2221 | 0.238 | 14 | 6 |
**Consistency:** consistent (3/3 splits positive)

### Intraday Window Breakdown

| Window | diff | p | cliff_d | n_a | n_b |
|---|---|---|---|---|---|
| range_30m | 0.0020 | 0.0000 | 0.460 | 125 | 123 |
| range_60m | 0.0027 | 0.0000 | 0.506 | 125 | 123 |
| range_session | 0.0068 | 0.0000 | 0.503 | 125 | 123 |

---

## Phase 3 — Trading Utility Test

**Verdict:** ✅ SUPPORTED — Trading Useful
**Signal Strength Tier:** core-fragile
**Role:** premarket_framing
**Signal:** iv_30d.pct_change(5) prior day (continuous); binary > 0
**Primary Outcome:** w150_range
**n:** 557
**Verdict Reason:** rho=0.331, p_nw=0.0000, peak=w150, sign_ok=True

| Split | rho | p_nw | n |
|---|---|---|---|
| full | 0.331 | 0.0000 | 557 |
| train | 0.316 | 0.0000 | 246 |
| val | 0.352 | 0.0000 | 250 |
| holdout | 0.072 | 0.6239 | 61 |
**Consistency:** consistent (3/3)

**Effect by window (rho vs signal):**

| Window | rho | p_nw |
|---|---|---|
| w30 | 0.283 | 0.0000 |
| w60 | 0.322 | 0.0000 |
| w120 | 0.329 | 0.0000 |
| w150 | 0.331 | 0.0000 |
| w210 | 0.314 | 0.0000 |
**Peak window:** w150 | **Early enough for style:** True
