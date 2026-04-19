# Chapter 10: Meta Risks
*Positional Option Trading, Euan Sinclair — pp. 216–225*

---

## Chapter Summary

Market risk can be managed and controlled — if you blow up from a market move, it's ignorance or overconfidence. The risks that are harder to anticipate and harder to survive come from **outside the market**: fraud, counterparty failure, currency collapse, index restructuring, regulatory changes, and theft. This chapter is a catalog of real examples showing how professionals have been destroyed by forces beyond their market models.

---

## Currency Risk

- All option trading uses fiat currency. Even in a "stable" country, inflation erodes real returns.
- Historical hyperinflation: Zimbabwe (98%/day), Germany 1923, Hungary 1946, Venezuela 2018
- **Lesson**: When active trading is not producing real returns after adjusting for inflation, stop.

### Bitcoin / Cryptocurrencies (Fig 10.1)
- Bitcoin 2018: high $17,700, low $3,190 — annualized vol **68%** vs EUR/USD 7%, USD/JPY 6%
- Crypto exchanges are not regulated like traditional exchanges — QuadrigaCX (2018): owner died, customers couldn't access $190M
- Bitcoin fails as currency: too volatile, not widely accepted, $64B total market cap vs $16T for USD
- Banks actively avoid crypto clients (KYC and regulatory uncertainty)
- **For options traders**: crypto has a large variance premium in theory, but counterparty and regulatory risks dwarf any tradeable edge

---

## Fraud and Theft

### Baring's Bank — Nick Leeson (1995)
- Leeson authorized as a floor broker for Nikkei arb; hid error account losses from head office
- Built large short Nikkei straddle position; Kobe earthquake dropped Nikkei 16% in 4 days
- Final loss: £827M (~$2.5B). Barings sold to ING for £1.

**Key failures that enabled this:**
- One person was both trader and risk manager
- Trader had ability to create/hide accounts
- London office trusted falsified P/L numbers they couldn't independently verify

### Sumitomo Bank — Yasumo Hamanaka, "Mr. Copper" (1995)
- Accumulated 5% of world's copper over 10 years, manipulating prices
- Lost $1.8B when Chinese supply increase overwhelmed his ability to hold the price up
- London Metal Exchange had no position limits and didn't publish open interest

**Key failures:**
- Treasury and management didn't understand how much margin was supporting the trade
- Illiquid, opaque instrument with no position transparency

### Bernie Madoff ($50B Ponzi Scheme, 2008)
- Claimed consistent 12%/year returns through all market conditions using a collar strategy
- Harry Markopolos identified the fraud in 5 minutes, proved it in 4 hours, notified SEC in 2000 — not acted on until 2008
- No real trades were made; confirmations were fabricated based on idealized prices
- Only $11B of $17.5B eventually recovered

**Red flags (all avoidable)**:
- No independent third-party administrator (TPA)
- Returns implausible against the claimed strategy's theoretical limits
- No separation of trading, compliance, and risk management
- Relied on reputation rather than verifiable evidence

---

## Index Restructuring Risk

- Indices are just numbers calculated by a third party — methodology can change
- **EuroSTOXX 50**: changed from country-based to pan-eurozone composition. Dividend yield changed ~50%. Option traders with forward basis positions lost large sums. (Sinclair's largest 1-day loss.)
- **UVXY (Feb 2018)**: ProShares reduced leverage from 2× to 1.5× during the VIX spike event. Expected future vol dropped 25% — all long-vega traders hurt. Lawsuits still unresolved.
- **Lesson**: Read the prospectus. Know what the contract owner is permitted to change. Never assume specifications are permanent.

---

## Counterparty Risk

- Spread arbitrageurs can have large profits at one counterparty and large losses at another
- If the winning counterparty defaults, the losses at the other leg still stand
- Even legally, gambling debts may be unenforceable in some jurisdictions
- **Lesson**: Stay flat across counterparties. Do not accumulate large one-directional counterparty exposure.

---

## Practical Checklist for Meta Risk Management

1. **Use multiple brokers and exchanges.** No single point of failure.
2. **Always have an independent third-party administrator.** Non-negotiable for any fund. Would have immediately exposed Madoff.
3. **Never let one person be both trader and risk manager.** Barings proved this.
4. **Understand the products you trade.** Can you independently verify that the returns are plausible?
5. **Diversify across currencies, institutions, and countries.** No concentration of settlement/custody risk.
6. **Know your index's terms.** What can the publisher change? What are the contract specs?
7. **Check position limits and open interest data** for any illiquid product you hold a large position in.

---

## Floor Trader Wisdom

> "If you have anything to do with crypto, this conversation is over." — Senior US clearing bank

> "You can't cheat an honest man." — Popular saying about Madoff's clients who thought they were the "smart insiders"

---

## Source Pages

- Currency risk and Bitcoin (Fig 10.1): pp. 216–218
- Fraud examples (Leeson, Hamanaka, Madoff): pp. 218–224
- Index restructuring risk: pp. 224–225
- Counterparty risk: p. 225
