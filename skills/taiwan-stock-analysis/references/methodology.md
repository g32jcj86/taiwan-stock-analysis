# Taiwan Stock Analysis Methodology

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
- analyst revisions when available

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

## Individual Report Checklist

1. Identify the stock, market, data date, and source reliability.
2. Explain the business model and revenue drivers.
3. Compare recent results against trend, peers, and cycle position.
4. Evaluate valuation using at least two methods when data permits.
5. List catalysts and risks with likely timing.
6. Build bull, base, and bear scenarios.
7. End with data gaps, assumptions, and monitoring triggers.

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
