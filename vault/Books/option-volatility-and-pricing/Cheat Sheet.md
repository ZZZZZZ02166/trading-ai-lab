# Option Volatility and Pricing — Cheat Sheet
*Sheldon Natenberg — Quick Review*

---

## Core Formula Reference

| Formula | Description |
|---------|-------------|
| σ_annual = σ_daily × √252 | Annualize daily vol |
| σ_daily = IV / √252 | Daily 1-sigma expected move (fraction) |
| Daily $ move = IV × S / √252 | Dollar expected 1-sigma daily move |
| N-day move = IV × S × √(N/252) | N-day expected move |
| σ_fwd = √[(σ₂²t₂ − σ₁²t₁)/(t₂−t₁)] | Forward volatility between two dates |
| D = [S × (1+r×t)] − F | Implied dividend from forward price |
| ΔV ≈ δ × ΔS + ½ × γ × ΔS² | Better P/L estimate including gamma |
| |δ_call| + |δ_put| ≈ 100 | Delta sum for same strike call/put pair |

---

## Greeks Quick Reference

| Greek | Long Option Sign | ATM Behavior | Near Expiry (ATM) |
|-------|----------------|-------------|-------------------|
| Delta | + (call) / − (put) | ≈ ±0.50 | Approaches ±1 or 0 |
| Gamma | + (always) | Maximum | Spikes dramatically |
| Theta | − (always) | Most negative | Accelerates to −∞ |
| Vega | + (always) | Maximum | Approaches 0 |
| Rho | + (calls) | Moderate | Rises with time |

---

## Six Synthetic Positions

| Real Position | Synthetic Equivalent |
|--------------|---------------------|
| Long underlying | Long call + Short put (same strike) |
| Short underlying | Short call + Long put |
| Long call | Long underlying + Long put |
| **Short put** | **Long underlying + Short call = COVERED CALL** |
| Long put | Short underlying + Long call |
| Short call | Short underlying + Short put |

**Covered call = synthetic short put. Same downside. Same risk.**

---

## Volatility Spreads Comparison

| Spread | Structure | Greek Profile | Profits When |
|--------|-----------|--------------|-------------|
| Long straddle | Long ATM call + put | +γ, −θ, +ν | Large moves; IV rises |
| Short straddle | Short ATM call + put | −γ, +θ, −ν | Quiet; IV falls |
| Long butterfly | +low / −2mid / +high | −γ, +θ, −ν | Quiet near body |
| Long condor | 4-legged butterfly | −γ, +θ, −ν | Range-bound |
| Ratio spread | +N calls / −2N calls | −γ, +θ, −ν | Small directional move |

---

## Black-Scholes Six Assumptions (All Violated in Practice)

1. Frictionless markets (no costs)
2. Continuous trading possible
3. Constant interest rates
4. **Constant volatility** ← most important violation (skew)
5. Vol independent of price ← violated by leverage effect
6. Small changes normally distributed ← fat tails in reality

---

## Volatility Skew

**Equity skew**: OTM puts > OTM calls in IV (downward-sloping)
- Cause 1: Insurance demand (institutions buy OTM puts)
- Cause 2: Covered call writing (investors sell OTM calls)

**By asset class**:
- Equity: downward skew (crash risk)
- Commodity: often upward (supply shock)
- Currency: symmetric smile (bidirectional risk)

**Risk reversal** = IV(OTM call) − IV(OTM put) at same delta. Negative = downward equity skew.

---

## Delta Hedging Rules

- **Long gamma**: bought options + short underlying → profits when realized vol > IV
- **Short gamma**: short options + long underlying → profits when realized vol < IV
- **Rebalance when**: delta drifts by ~1 standard deviation of expected daily move
- **Breakeven realized vol** ≈ IV at which options were traded
- **Never forget**: gamma scalp P/L − theta paid = net P/L (ignoring vega)

---

## Calendar Spread Rules

- **Long calendar** (short near / long far, same strike): benefits from time passage + IV rise
- **Short calendar**: benefits from large underlying moves + IV fall
- **Pre-event**: long calendar benefits (quiet stock + rising IV = calendar expands)
- **Post-event**: vol crush hurts long calendar (IV collapses)

**Forward vol**: σ_forward = √[(σ₂²t₂ − σ₁²t₁)/(t₂−t₁)] = breakeven vol for the calendar spread period

---

## Key Warnings

⚠️ **Covered call = short put. Same downside. No protection from owning the stock.**

⚠️ **Short gamma loses faster than delta predicts on large moves.** Use: ΔV ≈ δ×ΔS + ½γ×ΔS²

⚠️ **IV can stay elevated.** High IV is a necessary but not sufficient reason to sell vol.

⚠️ **Transaction costs eliminate edge** for frequent-rebalancing strategies. Retail traders need larger edges than market makers.

⚠️ **American puts may warrant early exercise** when deeply ITM in low-vol, high-rate environments. Short put holders: monitor assignment risk.

⚠️ **Equity skew ≠ universal.** Commodity and FX markets have different skew structures.

⚠️ **Vega of stock options can decrease with time.** Don't assume longer = higher vega.

⚠️ **Greeks are instantaneous.** Recalculate after any significant underlying move.
