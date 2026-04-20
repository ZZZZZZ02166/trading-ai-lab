---
hypothesis_number: H76
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 564
signals: 99
primary_metric: gap_fill_rate_backw_minus_contango
metric_value: 0.1320
---

# H76: Gap Days in Backwardation Fill More Frequently Than Gap Days in Contango

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Gap Days in Backwardation Fill More Frequently Than Gap Days in Contango_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 564 |
| Rows excluded | 1 |
| Exclusion reason | Gap > 0.5% filter + backwardation/contango split |
| Final observations tested | 564 |
| Signal days | 99 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 564 |
| Signals | 99 |
| Primary Metric | gap_fill_rate_backw_minus_contango |
| Metric Value | 0.1320 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.08 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

Gap fill rate: backwardation=0.404 vs contango=0.272 (diff=0.132), p_fisher=0.0261. n_backw=99, n_contango=125.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_backwardation_gaps | 99 |
| n_contango_gaps | 125 |
| fill_rate_backwardation | 0.404 |
| fill_rate_contango | 0.272 |
| p_fisher_exact | 0.0261 |
| total_gap_days | 224 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=99) | 16.1 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **36.1** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.


## Phase 2 — Intraday Robustness (Batch 2)

**Verdict: INCONCLUSIVE**
fill_diff=0.006, p_boot=0.9985, p_fisher=0.5168, mixed

**Critical finding:** Phase 1 fill rate diff=0.132 collapsed to **0.006** when fill is measured using 1m bars (exact intraday touch of prior close). The Phase 1 result was entirely an artifact of the loose EOD fill proxy.

### Fill Rate Comparison (1m-bar corrected definition)

| Metric | Backwardation | Contango | Diff | p |
|---|---|---|---|---|
| Fill by Close | 0.359 | 0.353 | 0.006 | Fisher: 0.5168, Boot: 0.9985 |
| Fill by 11:30 | 0.223 | 0.185 | 0.038 | n/a |

Total gap days: 222 (backw: 103, contango: 119)

### Gap Direction × Regime Fill Rates

| Cell | n | Fill by Close | Fill by 11:30 |
|---|---|---|---|
| up_backwardation | 60 | 0.350 | 0.217 |
| up_contango | 72 | 0.375 | 0.222 |
| down_backwardation | 43 | 0.372 | 0.233 |
| down_contango | 47 | 0.319 | 0.128 |

**Note:** No consistent backwardation advantage across any direction/regime cell.

### Gap Size Control

| Size | n_backw | n_cont | Fill diff |
|---|---|---|---|
| small | 55 | 81 | 0.071 |
| medium | 37 | 36 | -0.033 |
| large | 11 | 2 | n<5 flagged |

**Small gaps:** backw fills 7% more (0.491 vs 0.420), but this is the only consistent sub-group.

### Time-to-Fill (filled days only)

Mann-Whitney on minutes from 09:30 to first fill — backw median: 73.0 min vs contango: 91.5 min
p=0.1192, Cliff's d=-0.155 (backwardation fills ~18 min faster, not significant)

### First 2-Hour Range: Backwardation vs Contango

Backwardation shows materially larger 2h range: median=0.01177 vs 0.00866, p<0.001, Cliff's d=0.444. This suggests backwardation days are more volatile, not better gap-fillers.

### Walk-Forward Fill Rate

| Split | n_backw | n_cont | fill_rate_backw | fill_rate_cont | diff |
|---|---|---|---|---|---|
| full | 103 | 119 | 0.359 | 0.353 | 0.006 |
| train | 35 | 53 | 0.343 | 0.340 | 0.003 |
| val | 50 | 51 | 0.380 | 0.373 | 0.007 |
| holdout | 18 | 15 | 0.333 | 0.333 | 0.000 |

**Consistency:** mixed — fill diff hovers near 0 in every split.

**Conclusion:** H76's Phase 1 result does not replicate with a rigorous fill definition. The hypothesis as stated (backwardation → higher gap fill rate) is not supported. The correct finding is that **backwardation gap days have larger early-session ranges**, which is a different (and separately testable) phenomenon.

---

## Phase 3 — Trading Utility Test

**Verdict:** ❌ REJECTED
**Signal Strength Tier:** exploratory
**Role:** hybrid_preopen_plus_gap
**Signal:** bkwd_binary (iv_30d > iv_60d, prior day) × overnight_gap_dir
**Primary Outcome:** gap_fill_30 (binary)
**n:** 401
**Verdict Reason:** fisher_p_two_sided=0.8895, logit_bkwd_p=0.0015155927011670752, n=401
