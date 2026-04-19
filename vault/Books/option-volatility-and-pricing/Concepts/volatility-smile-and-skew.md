# Volatility Smile and Skew
*Source: Option Volatility and Pricing — Ch. 25*

---

## Definition

The volatility smile (or volatility skew) is the empirical observation that implied volatility varies systematically across exercise prices for the same expiration. Black-Scholes assumes constant IV, but back-solving IV from market prices at each strike reveals a curve, not a flat line.

---

## Why the Smile Exists

Black-Scholes assumes lognormally distributed future prices (i.e., normally distributed log returns). Real markets deviate from this assumption:

1. **Fat tails**: Large moves occur more frequently than the lognormal predicts (kurtosis > 3)
2. **Jump risk**: Stocks can gap — earnings, news events, financial crises create discontinuous moves
3. **Negative skew**: Stock prices tend to fall faster than they rise (asymmetric volatility)
4. **Structural supply/demand**: Persistent hedging demand (puts) and income selling (calls) create IV differentials unrelated to fair value

---

## Equity Skew: The Most Important Case

For equity indexes and individual stocks: **IV is higher for lower strike prices** (downward-sloping skew).

**Visual**: Plot IV on Y-axis vs. strike price (or delta) on X-axis. For equities: downward sloping from left (OTM puts at high IV) to right (OTM calls at lower IV).

**Two structural forces creating and maintaining equity skew**:

| Force | Effect |
|-------|--------|
| Institutional insurance demand | Continuous put buying → inflates OTM put IV |
| Covered call writing | Continuous call selling → deflates OTM call IV |

Both operate simultaneously. Skew is larger for index options than individual stocks because institutional hedging activity is concentrated at index level.

---

## The Vol Surface

The volatility surface is the full 3D representation: IV as a function of (strike, expiration). It reveals:
- **Skew**: IV slope across strikes at a given expiration
- **Term structure**: IV slope across expirations at a given strike
- **Combined**: How skew changes with time to expiration

Market makers manage the entire vol surface as their primary risk exposure. They do not simply hedge delta — they manage the shape of the surface.

---

## Skew by Asset Class

| Asset | Skew Type | Dominant Fear |
|-------|----------|--------------|
| Equity indexes | Steep downward | Crash/tail risk |
| Individual stocks | Moderate downward | Earnings gaps, M&A risk |
| Commodity agriculture | Upward or symmetric | Supply shock upside |
| Energy | Mixed (upward for crude) | Supply disruption spikes |
| Currencies | Symmetric smile | Two-directional crash risk |
| Interest rates | Depends on product | Context-specific |

**Never assume equity skew behavior applies to other asset classes.**

---

## Risk Reversal: Measuring Skew

**Definition**: Risk reversal = IV(OTM call) − IV(OTM put) at the same delta magnitude and same expiration.

- Negative value: OTM puts more expensive than OTM calls (equity-style downward skew)
- Positive value: OTM calls more expensive than OTM puts (upside skew)
- Zero: symmetric smile

Skew magnitude is measured in vol points (e.g., "the 25-delta risk reversal is −3 vol points" means OTM puts are 3 vol points higher IV than OTM calls).

---

## Trading Skew

### Short Skew (selling the skew premium)
**Position**: short put + long call (= long risk reversal)
- Collect structural premium built into OTM puts
- Profitable when market is calm or rising moderately
- Risk: large downside move causes large loss on short put

### Long Skew (buying skew protection)
**Position**: long put + short call (= short risk reversal)
- Pay structural premium; profit if crash occurs or skew steepens
- Used as portfolio protection or when skew seems cheap historically

### Vega-Neutral Risk Reversal
Adjust quantities of puts and calls so total vega = 0. Isolates skew trade from directional vol bet. A vega-neutral long risk reversal profits only if skew steepens (OTM put IV rises more than OTM call IV).

---

## Common Misunderstandings

- **"Skew is just fear."** Partially — but covered call writing is not fear-based. Both structural forces operate even in calm markets.
- **"You should always sell OTM puts because skew is high."** Skew is a risk premium for crash risk. Selling OTM puts is a legitimate strategy with a structural edge, but the risk is real and can be catastrophic.
- **"All asset classes have downward skew."** False. Commodity upside skew is common; FX smile is symmetric. Verify before trading.
- **"IV reflects actual future crash probability."** IV reflects the risk-neutral probability, which includes a risk premium above the physical probability. OTM put IV overstates the actual probability of a crash.

---

## Page References
- Volatility smile and skew structure: Ch. 25
- Equity skew causes: Ch. 25
- Risk reversals: Ch. 24
- Vol surface concept: Ch. 20-25
