# Volatility Measurement
*Source: Volatility Trading — Ch. 2*

---

## Definition
Standard deviation of log returns, annualized. Must be estimated from price data — five standard estimators, each making different trade-offs.

---

## The Five Estimators

**Close-to-Close**: σ² = [1/(n-1)] Σ(ln Cᵢ/Cᵢ₋₁)²  
Baseline. Misses intraday price action.

**Parkinson (1980)**: σ²_P = [1/(4n ln2)] Σ(ln H/L)²  
4.9× CC. Misses overnight gaps.

**Garman-Klass (1980)**: 0.5[ln(H/L)]² − [2ln2−1][ln(C/O)]²  
7.4× CC. Zero-drift assumption.

**Rogers-Satchell (1991)**: ln(H/C)ln(H/O) + ln(L/C)ln(L/O)  
Drift-independent. Misses overnight gap.

**Yang-Zhang (2000)**: σ²_overnight + k×σ²_RS  
14× CC. Handles overnight gaps + drift. **Recommended.**

---

## Bias Correction
σ_unbiased = σ_sample / c₄(N). Values: N=10→0.973; N=20→0.988; N=100→0.998.

## Common Mistakes
- Single estimator without checking others
- Not applying bias correction
- Ignoring U-shaped intraday vol pattern
- Sample size N < 20

## Page Reference
Ch. 2, pp. 33–53
