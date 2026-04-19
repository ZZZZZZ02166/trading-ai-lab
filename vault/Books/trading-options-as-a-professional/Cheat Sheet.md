# Trading Options as a Professional — Cheat Sheet
*James B. Bittman — Quick Review*

---

## Eight Essentials for Professional Trading

1. Option market fundamentals
2. Option price behavior including the Greeks
3. Synthetic relationships
4. Pricing arbitrage strategies
5. Volatility (HV, IV, skew)
6. Delta-neutral trading
7. Setting bid-ask prices
8. Managing position risk

---

## Greeks at a Glance

| Greek | Measures | ATM vs. OTM/ITM | Near Expiry Effect | Long Sign |
|-------|---------|----------------|-------------------|-----------|
| Delta | Stock price sensitivity | ~0.50 at ATM | Minimal change away from ATM | + (call) / − (put) |
| Gamma | Rate of delta change | Peak at ATM | Spikes near expiry (ATM only) | + |
| Vega | IV sensitivity | Peak at ATM | Rises with more time; LEAPS highest | + |
| Theta | Daily time decay | Most negative ATM | Accelerates near expiry (ATM) | − |
| Rho | Rate sensitivity | Most positive deep ITM (calls) | Rises with more time | + (call) |

---

## Position Greeks Formula

> **Position Greek = Option Greek × Contracts × 100**

- Position delta +220 = long 220 shares worth of directional exposure
- Position vega +52 = gain $52 per 1% IV rise
- Position theta −16 = lose $16/day from time decay

---

## Key Volatility Concepts

- **Historical vol**: what the stock did — backward-looking
- **Implied vol (IV)**: what the market prices in — forward-looking
- **Expected vol**: your personal forecast
- **The trade**: your expected vol vs. IV. If expected > IV → buy vol. If expected < IV → sell vol.
- **1-day expected move**: IV / √252 × stock price
- **Skew**: OTM puts have higher IV than OTM calls — they are structurally expensive

---

## Synthetics Reference

| Real Position | Synthetic Equivalent |
|--------------|---------------------|
| Long stock | Long call + Short put |
| Short stock | Short call + Long put |
| Long call | Long stock + Long put |
| **Short put** | **Long stock + Short call (covered call)** |

Covered call = synthetic short put. Same risk. Same P/L.

---

## Arbitrage Formulas

| Strategy | Fair Value Formula |
|---------|-------------------|
| Conversion target call | Strike + (rate × days/365) + Put − Stock |
| Reverse conversion target call | Stock − Put + (rate × days/365) |
| Box spread fair value | (High − Low) × [1 − (rate × days/365)] |

---

## Delta-Neutral Rules

- **Long gamma**: long options + short stock → profits when realized vol > IV
- **Short gamma**: short options + long stock → profits when realized vol < IV
- **Breakeven condition**: gamma scalp profits ≥ theta paid
- **Rebalance when**: delta drifts by ~1 standard deviation of expected daily move

---

## Critical Rules and Principles

1. **Three-part forecast required**: direction, timing, and volatility simultaneously. Getting one right and two wrong loses.
2. **Covered call = short put**. Same downside exposure. No additional protection from the stock you own.
3. **Position Greeks are additive**: total portfolio Greek = sum across all legs × 100.
4. **Greeks change dynamically**: a static snapshot is not sufficient. Re-evaluate after significant moves.
5. **Gamma sign flip at short strike**: bull call spread has positive gamma below lower strike, negative gamma above upper strike.
6. **Short stock rebate matters**: market makers receive 80% of interest on short stock — reverse conversion profitability is not replicable by retail traders.
7. **Pin risk is real**: options at the strike at expiration create unknown assignment exposure.

---

## Key Warnings

⚠️ **Negative gamma compounds losses**: short-gamma positions lose more than delta alone predicts. On a $5 adverse move, the position delta itself changes — creating exponential losses.

⚠️ **IV can stay wrong for extended periods**: just because IV appears too high or low doesn't mean it normalizes before expiration. Vol mean reversion is slow.

⚠️ **Vega and theta both spike near expiry ATM**: selling ATM options near expiration collects maximum theta but accepts maximum gamma risk simultaneously.

⚠️ **OTM puts are structurally expensive**: volatility skew makes OTM puts higher IV than their fair value in most market regimes. Factor this into any short-put strategy.

⚠️ **Market makers close positions quickly by design**: they delta-hedge to neutralize direction, then race to close before conditions change. Retail traders who try to replicate this without fast execution will be caught holding positions longer than intended.
