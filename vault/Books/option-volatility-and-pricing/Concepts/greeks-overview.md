# The Greeks — Complete Overview
*Source: Option Volatility and Pricing — Chs. 8-13*

---

## Definition

The Greeks are partial derivatives of the option pricing function. Each measures the sensitivity of an option's theoretical value to a change in one input while all other inputs remain constant. They are the primary tools for understanding and managing options risk.

---

## The Five Standard Greeks

### Delta (Δ)
- **Definition**: ∂V/∂S — change in option value per $1 change in underlying
- **Range**: 0 to +1 for calls; −1 to 0 for puts
- **ATM**: call delta ≈ +0.50; put delta ≈ −0.50
- **In Black-Scholes**: call delta = N(d₁) ≈ risk-neutral probability of expiring ITM
- **Delta relationship**: |delta_call| + |delta_put| ≈ 100 for same strike/expiry
- **Volatility effect**: High vol pulls all deltas toward ±50; low vol pushes toward 0 or ±100
- **Position delta**: Σ(option delta × contracts × 100) = underlying equivalents

### Gamma (Γ)
- **Definition**: ∂²V/∂S² — rate of delta change per $1 underlying move
- **Sign**: Always positive for long options (calls or puts)
- **ATM**: Peak gamma (highest for all same-expiry options)
- **Expiry effect**: ATM gamma spikes near expiry; ITM/OTM gamma decreases
- **Volatility effect**: Higher vol → lower gamma (underlying expected to move anyway)
- **Practical use**: Add gamma to delta on up moves; subtract on down moves
- **Better P/L estimate**: ΔV ≈ delta × ΔS + ½ × gamma × ΔS²

### Theta (Θ)
- **Definition**: ∂V/∂t — daily time value decay (typically quoted as $/day)
- **Sign**: Negative for long options; positive for short options
- **ATM**: Maximum theta; accelerates toward expiry
- **Proportionality**: ATM theta ∝ IV (double IV → double ATM theta)
- **ITM/OTM**: Theta slows near expiry for non-ATM options
- **Theta-gamma link**: Inescapable — +gamma means −theta; cannot have both positive

### Vega (ν or κ)
- **Definition**: ∂V/∂σ — $ change in value per 1% change in IV
- **Sign**: Positive for long options; negative for short options
- **ATM**: Peak vega
- **Time effect**: Longer-dated options have higher vega (LEAPS = highest)
- **ATM linearity**: ATM option value vs. IV is nearly linear → ATM vega ≈ constant across vol levels
- **OTM/ITM**: Volga > 0 — vega increases as vol rises
- **Caveat**: Stock option vega can decrease with time (forward price effect)

### Rho (ρ)
- **Definition**: ∂V/∂r — change in value per 1% change in interest rates
- **Sign**: Positive for calls, negative for puts (stock-type settlement)
- **Size**: Small for short-dated options; significant for LEAPS and deep ITM
- **Deep ITM calls**: Highest rho (most benefit from rising rates)
- **Practical**: Often ignored for short-term positions; must monitor for LEAPS

---

## Higher-Order Greeks

| Name | Definition | When It Matters |
|------|-----------|----------------|
| Speed | dGamma/dS | Large moves; positions with many short-dated options |
| Vanna | dDelta/dVol = dVega/dS | Vol spikes that change delta; delta hedging in volatile vol environment |
| Charm | dDelta/dTime | Positions held overnight or over weekends |
| Volga/Vomma | dVega/dVol | Deep OTM positions; long-vol bets; positions with high volga benefit from vol-of-vol |
| Veta | dVega/dTime | Long-dated positions |

---

## Greeks Across Market Conditions

| Condition | Key Greek Change | Implication |
|-----------|----------------|------------|
| Underlying moves far from strike | Gamma drops; delta moves toward 0 or ±1 | OTM/ITM options lose sensitivity |
| Approaching expiry (ATM) | Gamma spikes; theta accelerates | ATM short options most dangerous near expiry |
| Approaching expiry (OTM/ITM) | Gamma drops; theta falls | Less dynamic hedging needed for OTM positions |
| Vol rises | Deltas converge toward ±50 | OTM options become more active; ITM options less extreme |
| Vol falls | Deltas diverge (0 and ±1) | OTM options become "inactive"; delta hedging less frequent |

---

## Position Greeks

**Position delta** = Σ(individual delta × contracts × 100) = total underlying equivalents
**Position gamma** = Σ(individual gamma × contracts × 100) = sensitivity of position delta
**Position theta** = Σ(individual theta × contracts × 100) = daily P/L from time alone
**Position vega** = Σ(individual vega × contracts × 100) = $ change per 1% IV change

All Greeks are additive across positions within a portfolio.

---

## The Gamma-Theta Inescapable Tradeoff

No strategy escapes this:
- **+gamma** (long options): buy insurance against large moves, pay daily theta
- **−gamma** (short options): earn daily theta, exposed to large moves

This is not a solvable optimization problem — it is a structural feature of options. The only question is: at what level of theta income does the gamma risk become acceptable? Answer: when realized vol < IV (for short gamma) or when realized vol > IV (for long gamma).

---

## Critical Rules

1. **Greeks are instantaneous** — valid only for small changes. Recalculate after significant underlying moves.
2. **All Greeks change dynamically** — a static snapshot from morning is not valid after a 2% underlying move.
3. **Gamma compounds losses for short positions** — don't estimate P/L using delta alone on large moves.
4. **ATM options are most sensitive** — maximum gamma, theta, and vega all at ATM.
5. **Long options = positive gamma + positive vega + negative theta** — always, without exception.
6. **Short options = negative gamma + negative vega + positive theta** — always, without exception.
