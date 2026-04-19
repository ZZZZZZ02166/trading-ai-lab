---
hypothesis_id: 54d9acc8-4931-4e17-835d-a6d0e66239a2
status: candidate
confidence: 0.79
tags: ['intraday', 'pin-risk', 'expiration', 'open-interest', 'dealer-hedging', '0dte']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# SPX Pin Risk Is Elevated in the Final 30 Minutes on Expiration Fridays Near Large Open-Interest Strikes

**Status:** candidate | **Confidence:** ███████░░░ 79%

#intraday #pin_risk #expiration #open_interest #dealer_hedging #0dte

## Claim

On SPX weekly expiration Fridays, the probability of SPX closing within 5 points of the largest open-interest strike is significantly higher than on non-expiration days, and this clustering effect intensifies in the final 30 minutes of trading. The probability of a 5-point or less close-to-strike gap is at least 3× higher than a random distribution would predict, creating predictable intraday price dynamics near large strikes.

## Rationale

The expiration risk theme in this knowledge base covers pin risk: the tendency for spot to cluster near a large-open-interest strike at expiration due to dealer delta-hedging flows. As expiration approaches, dealers who are short large OI strikes become long or short large gamma quantities that flip sign around the strike. Their hedging flows act as a gravitational attractor — if spot is above the strike, dealers are short delta (from short calls) and buy spot as it falls, stabilising near the strike. This pinning effect is well-documented in SPX weekly expirations and creates intraday momentum-then-reversion patterns near expiration.

## How to Test

Using SPX options open interest data (CBOE) and SPX 1-minute prices on weekly expiration Fridays 2018–2023: identify the largest OI strike for each expiration. Compute the final closing price vs. the largest OI strike. Compare the distribution of |SPX close - largest OI strike| on expiration Fridays vs. matched non-expiration Fridays. Test whether the distribution is significantly more concentrated near zero on expiration days. Falsified if the distribution of close-to-strike distances on expiration Fridays is not significantly different from non-expiration days.

**Data required:** CBOE SPX options open interest by strike, SPX 1-minute prices on weekly expiration Fridays 2018–2023

### Variables Needed

- `pin_risk`
- `open_interest`
- `expiration_price`
- `intraday_returns`

### What Would Support It

Probability of |close - largest OI strike| < 5 points on expiration Friday > 3× non-expiration baseline; effect strengthens in final 30 minutes

### What Would Falsify It

No significant clustering of close prices near largest OI strikes on expiration Fridays vs. other Fridays

## Source Themes

- [[Expiration Risk: Pin Risk, Assignment, and Automatic Exercise]]
- [[Gamma and Theta: The Core Greeks Tradeoff]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `ddc2a298cd88`
