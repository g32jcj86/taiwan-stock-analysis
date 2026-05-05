# Taiwan Stock Analysis Methodology

## Anti-Anchoring Mode

Anti-anchoring mode is enabled by default. Build valuation, ranking, entry conditions, stop-loss logic, target zones, and risk/reward conclusions before reading or using external consensus.

Do not use these as model inputs unless the user explicitly asks to follow consensus:

- broker target prices
- analyst ratings or recommendation changes
- institutional price calls
- media headline targets
- market consensus fair value

Allowed workflow:

1. Score and rank candidates using fundamentals, valuation, price/volume, liquidity, risk, and verified event data.
2. Write the independent conclusion, including fair-value range or short-term trade plan.
3. Add an optional "External Consensus Check" at the end.
4. In that section, compare external target prices or ratings against the independent result, explain the gap, and flag possible crowding or narrative risk.
5. Do not revise scores, rankings, target zones, or recommendations after seeing external consensus.

If external consensus is unavailable, state that it was not used and do not infer it from news tone.

## Screening Engines

Use four engines and report both total score and engine subscores.

### Valuation

Prefer relative and historical context over single absolute cutoffs. Useful inputs:

- `pe`, `pb`, `ev_ebitda`
- `fcf_yield`, `dividend_yield`
- peer percentile, 5-year valuation range, asset replacement value

Red flags: negative earnings, one-time gains, high cyclicality at peak margin, accounting changes, and value traps with falling revenue.

### Quality

Useful inputs:

- `roe`, `roa`, `gross_margin`, `operating_margin`
- `debt_to_equity`, interest coverage, net cash
- earnings stability, cash conversion, receivable and inventory trend

Red flags: margin deterioration, low cash conversion, related-party transactions, repeated capital raising, and governance issues.

### Growth

Useful inputs:

- `revenue_growth`, `eps_growth`, `monthly_revenue_yoy`
- margin trend, backlog, capacity expansion, demand cycle
- company guidance, order trend, product cycle, and industry demand indicators when available

Red flags: growth from low-quality acquisitions, channel inventory build, falling orders, and growth with collapsing margins.

### Momentum And Risk

Useful inputs:

- `price_momentum_6m`, `price_momentum_12m`
- `volatility`, `max_drawdown`, `avg_volume`
- foreign/investment trust/dealer flows when available

Red flags: low liquidity, crowded positioning, unresolved litigation, trading suspension risk, and one-customer concentration.

## Seven Presets

| Preset | Primary use | Bias |
| --- | --- | --- |
| `deep-value` | Find undervalued stocks | Valuation, dividend support, balance-sheet safety |
| `quality-compounder` | Find durable long-term winners | Quality, growth, moderate valuation |
| `dividend-income` | Build income candidates | Yield, payout safety, low leverage |
| `garp` | Find growth at reasonable price | Growth and valuation balance |
| `turnaround` | Find improving cyclicals | Growth inflection, margin recovery, solvency |
| `small-cap-liquidity-aware` | Find overlooked names | Valuation and growth with liquidity penalty |
| `risk-defensive` | Find lower drawdown names | Quality, volatility, leverage, stable cash flow |

## Hybrid Undervaluation And Short-Term Opportunity

Use this when the user asks for "被低估且短線有機會", "綜合型", or similar screening.

Default score weights:

| Engine | Weight | Notes |
| --- | ---: | --- |
| Valuation | 35% | Historical and peer discount, FCF yield, dividend support, downside valuation |
| Quality and growth | 25% | Revenue trend, margin resilience, ROE/ROA, balance-sheet safety, catalyst quality |
| Momentum and volume | 25% | 5/20/60-day relative strength, breakout quality, volume expansion, liquidity |
| Risk control | 15% | Volatility, drawdown, concentration, event risk, liquidity, overextension |

Output independent ranking first. External target prices, analyst ratings, and headline-driven calls are reference-only and must not affect these weights or the final rank.

For short-term candidates, avoid "cheap but falling" names unless there is a verified reversal signal. Avoid "strong but crowded" names when the risk/reward depends mainly on target-price narratives.

## Individual Report Checklist

1. Identify the stock, market, data date, and source reliability.
2. Explain the business model and revenue drivers.
3. Compare recent results against trend, peers, and cycle position.
4. Evaluate valuation using at least two methods when data permits.
5. List catalysts and risks with likely timing.
6. Build bull, base, and bear scenarios.
7. Write the independent conclusion before viewing external consensus.
8. End with data gaps, assumptions, monitoring triggers, and optional external consensus check.

## Portfolio Health Checks

Flag:

- Single ticker above 20 percent of portfolio value.
- Single sector above 40 percent.
- Single risk driver, customer, or supply chain exposure above 50 percent.
- Position with daily traded value too small for intended exit size.
- Stale price older than 5 trading days.
- High overlap among stocks that share the same cycle driver.
- Expected return driven by one or two positions.

## Stress Test Scenario Defaults

Use these defaults as a starting point, then adapt to holdings:

| Scenario | Market shock | Typical sector extra shock |
| --- | ---: | --- |
| `taiex-correction` | -15% | Technology -7%, Financials -3% |
| `semiconductor-downcycle` | -10% | Semiconductor -20%, Hardware -12% |
| `global-recession` | -18% | Exporters -10%, Cyclicals -12% |
| `rate-shock` | -8% | High valuation growth -12%, Financials +3% |
| `twd-appreciation` | -6% | Exporters -10%, Importers +3% |
| `twd-depreciation` | -6% | Import-cost-heavy firms -8%, Exporters +4% |
| `liquidity-crunch` | -12% | Small caps -18%, Low volume -15% |
| `correlation-spike` | -14% | All risky assets move closer to market beta |

Report scenario loss, percent drawdown, largest contributors, top concentration risks, and mitigation ideas.
