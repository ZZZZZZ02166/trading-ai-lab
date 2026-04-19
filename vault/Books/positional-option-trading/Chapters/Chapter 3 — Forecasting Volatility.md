# Chapter 3: Forecasting Volatility
*Positional Option Trading, Euan Sinclair — pp. 56–66*

---

## Chapter Summary

Every option trade is implicitly a volatility forecast. This chapter covers the mechanics of forecasting realized volatility — from simple historical methods through EWMA and GARCH family models — and argues that the best practical approach is **ensemble prediction** (averaging multiple models). The chapter also introduces a critical observation: once a methodology is widely known and data is freely available, the edge often lies not in the model but in information collection and processing.

---

## Key Concepts

### Model-Driven vs Event-Driven Trades
- **Model-driven**: A formal model generates a fair value at any moment (e.g., an IV pricing model). Scalable, broad applicability, but models oversimplify reality.
- **Event-driven**: Based on specific unusual situations (e.g., VIX behavior after FOMC, IV decay post-earnings). Simple to find and test, potentially very profitable, but requires waiting for the event.
- Neither is universally superior. The best traders combine both.

### Rolling Historical Volatility: The Windowing Problem
- Simple formula: σ_N = sqrt(sum of r² over N days × 252/N)
- **Problem**: A single large return (e.g., earnings day) affects the volatility reading for N days then suddenly drops out, creating artificial jumps in the forecast
- Fix: identify and remove known outliers (earnings day returns) before calculating

### EWMA: Exponentially Weighted Moving Average
- **Equation 3.2**: σ²_t = λ·σ²_{t-1} + (1−λ)·r²_{t-1}
- λ typically 0.90–0.95 for daily data
- **Advantage**: More recent returns weighted more heavily → faster adaptation to regime changes → no sudden drop-off when old returns leave window
- **Practical guidance**: For indices, λ = 0.90–0.95 works. Choose and stick with it consistently — you'll develop intuition for the market through your model.

### GARCH(1,1): Captures Vol Clustering + Mean Reversion
- **Equation 3.3**: σ²_t = ω + α·r²_{t-1} + β·σ²_{t-1}   (where α + β + γ = 1, γV = long-run variance)
- **What it captures**: Vol clustering (tomorrow's vol ≈ today's) AND mean reversion (long-run level pull)
- **Fig 3.2 (SPY, Aug 2019)**: GARCH(1,1) and GJR-GARCH term structures start at ~20% and decay toward ~10% over 120 days — mean reversion dominates the long-horizon forecast
- **Reality**: Thousands of GARCH variants exist but none is clearly better. "One Schrödinger equation, many GARCH models." In practice, GARCH is no better than EWMA and is harder to use (unstable MLE parameters, needs 4 years of data).

### Implied Vol as Predictor
- IV predicts realized vol well IF you subtract the variance premium: RV_forecast ≈ VIX − variance_premium(VIX level)
- For underlyings without a VIX: compute weighted average of ATM IVs (equivalent to VXO methodology)
- This combined approach (model + IV − premium adjustment) is generally the best available

### Ensemble Prediction: The Right Approach
- **Key finding** (Table 3.1, 1990–2018 S&P 500): The simple average of 5 models (30-day historical, EWMA 0.9, EWMA 0.95, VIX, GARCH(1,1)) has lower error SD than any individual model except the simplest
- Even averaging very similar models (EWMA 0.9 and EWMA 0.95) produces slight improvement
- **Why it works**: Diverse errors cancel (similar to wisdom-of-crowds effect). Works even with correlated models.
- **Practical recipe**: Average over every reasonable GARCH variant, range of time scales, range of λ parameters. Include IV-based forecast. Take the mean.

---

## Key Lessons

1. **You are always making a volatility forecast.** Even if you don't formalize it. Make it explicit and testable.
2. **EWMA is usually good enough for vol forecasting.** Choose λ, use it consistently, develop intuition. GARCH adds complexity with minimal benefit.
3. **Ensemble beats any single model.** Average multiple simple forecasts. This is the single best improvement you can make to a vol forecasting system.
4. **Volatility is reasonably forecastable for a financial time series** — more so than returns. This is the structural advantage of vol trading over directional trading.
5. **Even a good vol forecast doesn't guarantee edge.** The consensus (IV) already incorporates a good forecast. Your edge requires being *better* than the market, not just making a forecast.

---

## Data from Tables

**Table 3.1 — 30-Day Vol Forecasts, S&P 500, 1990–2018:**

| Model | Avg Error | SD Error | R² |
|-------|-----------|----------|----|
| 30-day historical | 0.27 | 5.2 | 0.65 |
| EWMA (λ=0.9) | -0.10 | 6.0 | 0.62 |
| EWMA (λ=0.95) | -0.92 | 5.8 | 0.62 |
| VIX | -0.76 | 5.9 | 0.60 |
| GARCH(1,1) | 0.30 | 5.2 | 0.64 |
| **Average** | 0.44 | **5.9** | 0.60 |

Average has highest error but second-lowest SD (after 30-day historical). VIX-based forecast is notably biased (variance premium).

---

## Connections

- **Ch. 4**: Uses IV − variance premium as the central analytical framework for the variance premium itself
- **Ch. 9**: Volatility forecasting feeds directly into Kelly sizing — you need a vol forecast to compute f*
- The ensemble prediction concept extends naturally to combining fundamental and event-driven signals

---

## Source Pages

- Model vs event-driven trade classification: pp. 56–61
- EWMA formula and rolling vol chart (Fig 3.1, Eq 3.2): pp. 61–63
- GARCH(1,1) and term structure (Fig 3.2, Eq 3.3): pp. 63–65
- Ensemble prediction / Tables 3.1–3.2: pp. 64–66
