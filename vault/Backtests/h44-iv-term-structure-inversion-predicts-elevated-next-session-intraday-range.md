---
hypothesis_number: H44
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 564
signals: 190
primary_metric: median_next_range_diff_backwardation_vs_contango
metric_value: 0.0058
---

# H44: IV Term Structure Inversion Predicts Elevated Next-Session Intraday Range

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _IV Term Structure Inversion Predicts Elevated Next-Session Intraday Range_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 564 |
| Rows excluded | 1 |
| Exclusion reason | 1-day forward shift for next-session range; missing iv_30d/iv_60d or OHLC |
| Final observations tested | 564 |
| Signal days | 190 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 564 |
| Signals | 190 |
| Primary Metric | median_next_range_diff_backwardation_vs_contango |
| Metric Value | 0.0058 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.001 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

Backwardation days have higher next-session range: median_back=0.0163 vs median_cont=0.0106 (diff=0.0058, p=0.0000, Cliff's d=0.550)

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_backwardation | 190 |
| n_contango | 374 |
| median_range_backwardation | 0.0163 |
| median_range_contango | 0.0106 |
| cliffs_delta | 0.5498 |
| p_mannwhitney | 0.0 |
| u_stat | 55065.0 |
| pct_backwardation_days | 0.337 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=190) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.1 | 20 | Family: `regime_comparison` (stored) |
| Statistical Reliability | 20.0 | 20 | FDR-within-family p: 0.0000 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **65.0** | **100** | |

**Priority: 🟡 WATCHLIST**  Stat test: `mannwhitney`
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
**Reason:** diff=0.0058 > 0.003, p=0.0000 < 0.1, consistent  
**Phase 1 Alignment:** confirmed

> Phase 1 used daily_series EOD range. Phase 2 validates against 1m intraday range windows.

### Walk Forward Range Session

| Split | diff | p | cliff_d | n_a | n_b |
|---|---|---|---|---|---|
| full | 0.0058 | 0.0000 | 0.551 | 188 | 374 |
| train | 0.0027 | 0.0000 | 0.361 | 71 | 181 |
| val | 0.0093 | 0.0000 | 0.720 | 84 | 166 |
| holdout | 0.0052 | 0.0036 | 0.407 | 33 | 27 |
**Consistency:** consistent (3/3 splits positive)

### Intraday Window Breakdown

| Window | diff | p | cliff_d | n_a | n_b |
|---|---|---|---|---|---|
| range_30m | 0.0025 | 0.0000 | 0.538 | 188 | 374 |
| range_60m | 0.0029 | 0.0000 | 0.528 | 188 | 374 |
| range_120m | 0.0039 | 0.0000 | 0.536 | 188 | 374 |
| range_session | 0.0058 | 0.0000 | 0.551 | 188 | 374 |

---

## Phase 3 — Trading Utility Test

**Verdict:** ⏰ TOO LATE FOR STYLE
**Signal Strength Tier:** core-strong
**Role:** premarket_framing
**Signal:** iv_30d - iv_60d (continuous); binary iv_30d > iv_60d
**Primary Outcome:** w150_range
**n:** 562
**Verdict Reason:** rho=0.487, p_nw=0.0000, peak=w210, sign_ok=True

| Split | rho | p_nw | n |
|---|---|---|---|
| full | 0.487 | 0.0000 | 562 |
| train | 0.283 | 0.0003 | 251 |
| val | 0.636 | 0.0000 | 250 |
| holdout | 0.363 | 0.0000 | 61 |
**Consistency:** consistent (3/3)

**Effect by window (rho vs signal):**

| Window | rho | p_nw |
|---|---|---|
| w30 | 0.467 | 0.0000 |
| w60 | 0.471 | 0.0000 |
| w120 | 0.481 | 0.0000 |
| w150 | 0.487 | 0.0000 |
| w210 | 0.493 | 0.0000 |
**Peak window:** w210 | **Early enough for style:** False
