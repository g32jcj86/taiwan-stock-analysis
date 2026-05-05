# Data Sources And Symbol Conventions

## Source Priority

Use the most authoritative current source available for the question.

1. Official company filings and announcements.
2. Taiwan official market data from TWSE, TPEx, and MOPS.
3. Company investor relations pages.
4. yfinance or Yahoo Finance for quick quote, history, and global symbol access.
5. Reputable financial data providers or news sources, with date and source noted.

When a source may have changed recently, verify current data before producing conclusions.

## Anti-Anchoring Source Classes

Use source classes to prevent institutional target prices from contaminating analysis.

### Model Inputs

These may affect scores, rankings, valuation ranges, entry triggers, stop-loss levels, and risk/reward:

- official filings, monthly revenue, financial statements, dividends, and company announcements
- TWSE, TPEx, and MOPS market or disclosure data
- price, volume, volatility, liquidity, and historical return data
- verified institutional flow data such as foreign investor, investment trust, and dealer net buy/sell
- company guidance, order, capacity, product cycle, and industry demand indicators when the source and date are clear

### Reference-Only Sources

These must not affect scores, rankings, valuation ranges, entry triggers, stop-loss levels, or risk/reward. Use them only in a final comparison section after the independent result is complete:

- broker target prices
- analyst ratings, upgrades, downgrades, or recommendation changes
- institutional price calls
- media headline targets or social media narratives
- market consensus fair value

When a reference-only source conflicts with the model, report the gap and possible reasons instead of adjusting the model to match the outside target.

## Local yfinance Install

This plugin expects `yfinance` to be available in the plugin-local `vendor/python` directory. The helper script inserts that directory into `sys.path` automatically.

To reinstall or update from the plugin root:

```bash
python -m pip install -r requirements.txt --target vendor/python
```

Record the yfinance version in final notes when reproducibility matters.

## Taiwan Symbols

- TWSE listed stocks: `<code>.TW`
- TPEx listed stocks: `<code>.TWO`
- Taiwan index examples can vary by provider. Verify the exact symbol before use.

Examples:

- `2330.TW`: TSMC on TWSE.
- `2317.TW`: Hon Hai on TWSE.
- `6488.TWO`: GlobalWafers on TPEx.

## yfinance Global Symbols

yfinance accepts Yahoo Finance symbols directly and can therefore cover many global exchanges when the user supplies or verifies the correct suffix. Common suffix examples:

| Market | Example suffix |
| --- | --- |
| United States | no suffix |
| Taiwan TWSE | `.TW` |
| Taiwan TPEx | `.TWO` |
| Japan | `.T` |
| Hong Kong | `.HK` |
| London | `.L` |
| Toronto | `.TO` |
| Australia | `.AX` |
| Singapore | `.SI` |
| Korea | `.KS`, `.KQ` |
| Shanghai | `.SS` |
| Shenzhen | `.SZ` |
| India NSE | `.NS` |
| India BSE | `.BO` |
| Frankfurt | `.F` |
| Paris | `.PA` |
| Amsterdam | `.AS` |
| Milan | `.MI` |
| Madrid | `.MC` |
| Zurich | `.SW` |
| Stockholm | `.ST` |
| Mexico | `.MX` |
| Brazil | `.SA` |

For less common exchanges, keep the user-provided symbol if it already contains a suffix, or verify the Yahoo Finance suffix before fetching data.

## Local CSV Schemas

Fundamental screening CSV:

```text
ticker,name,sector,pe,pb,ev_ebitda,fcf_yield,dividend_yield,roe,roa,gross_margin,operating_margin,debt_to_equity,revenue_growth,eps_growth,monthly_revenue_yoy,margin_trend,price_momentum_6m,price_momentum_12m,volatility,max_drawdown,avg_volume
```

Price CSV:

```text
ticker,price,currency,date
```

Position CSV:

```text
ticker,quantity,price,sector,currency,beta
```

Trade ledger CSV:

```text
date,ticker,side,quantity,price,currency,fee,tax,account,sector,note
```
