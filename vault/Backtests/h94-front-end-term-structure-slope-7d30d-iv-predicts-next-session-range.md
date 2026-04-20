---
hypothesis_number: H94
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 564
signals: 217
primary_metric: median_range_diff_backwardation_vs_contango
metric_value: 0.0041
---

# H94: Front-End Term Structure Slope (7d/30d IV) Predicts Next-Session Range

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _Front-End Term Structure Slope (7d/30d IV) Predicts Next-Session Range_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 564 |
| Rows excluded | 1 |
| Exclusion reason | 7d IV join + 1-day forward range |
| Final observations tested | 564 |
| Signal days | 217 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 564 |
| Signals | 217 |
| Primary Metric | median_range_diff_backwardation_vs_contango |
| Metric Value | 0.0041 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.003 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

diff_median_range=0.00409 (backwardation=0.01470, contango=0.01061), p_mannwhitney=0.0000, n_backwardation=217, n_contango=347, mean_slope_7_30=0.9649.

## Extra Metrics

| Metric | Value |
|--------|-------|
| median_range_backwardation | 0.014704 |
| median_range_contango | 0.010614 |
| n_backwardation | 217 |
| n_contango | 347 |
| mean_slope_7_30 | 0.9649 |
| p_mannwhitney | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (derived) |
| Sample Adequacy (N_eff=217) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **52.0** | **100** | |

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
**Reason:** diff=0.0042 > 0.003, p=0.0000 < 0.1, consistent  
**Phase 1 Alignment:** confirmed

> Phase 1 used EOD daily range. Phase 2 validates 7d/30d slope signal vs 1m intraday range windows.

### Walk Forward Session

| Split | diff | p | cliff_d | n_a | n_b |
|---|---|---|---|---|---|
| full | 0.0042 | 0.0000 | 0.445 | 217 | 345 |
| train | 0.0030 | 0.0000 | 0.416 | 93 | 159 |
| val | 0.0077 | 0.0000 | 0.550 | 92 | 158 |
| holdout | 0.0005 | 0.3807 | 0.047 | 32 | 28 |
**Consistency:** consistent (3/3 splits positive)

### Intraday Window Breakdown

| Window | diff | p | cliff_d | n_a | n_b |
|---|---|---|---|---|---|
| range_30m | 0.0021 | 0.0000 | 0.407 | 217 | 345 |
| range_60m | 0.0025 | 0.0000 | 0.402 | 217 | 345 |
| range_session | 0.0042 | 0.0000 | 0.445 | 217 | 345 |

---

## Phase 3 — Trading Utility Test

**Verdict:** ⏰ TOO LATE FOR STYLE
**Signal Strength Tier:** core-fragile
**Role:** premarket_framing
**Signal:** IVX_7d - IVX_30d (continuous); binary IVX_7d > IVX_30d
**Primary Outcome:** w150_range
**n:** 562
**Verdict Reason:** rho=0.418, p_nw=0.0000, peak=w210, sign_ok=True

| Split | rho | p_nw | n |
|---|---|---|---|
| full | 0.418 | 0.0000 | 562 |
| train | 0.303 | 0.0001 | 251 |
| val | 0.546 | 0.0000 | 250 |
| holdout | 0.191 | 0.0640 | 61 |
**Consistency:** consistent (3/3)

**Effect by window (rho vs signal):**

| Window | rho | p_nw |
|---|---|---|
| w30 | 0.375 | 0.0000 |
| w60 | 0.400 | 0.0000 |
| w120 | 0.417 | 0.0000 |
| w150 | 0.418 | 0.0000 |
| w210 | 0.434 | 0.0000 |
**Peak window:** w210 | **Early enough for style:** False
