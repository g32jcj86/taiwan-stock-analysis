# 台股分析 Codex 外掛

這個外掛提供台股篩選、個股報告、投資組合分析、壓力測試與觀察名單工作流程。技能 ID 為 `$taiwan-stock-analysis`，使用介面預設為繁體中文。

## 功能

- 使用四個引擎與七個 preset 篩選被低估或具備特定風格的股票。
- 使用外掛內建 `yfinance` 抓取報價與歷史股價。
- 產生台股個股財務分析報告。
- 彙總交易紀錄，分析損益、配置、集中度與投組健康度。
- 執行八種壓力測試情境，包含集中度、相關性與 VaR proxy。
- 管理 JSON 觀察名單。

## Codex 用法

```text
使用 $taiwan-stock-analysis 分析 2330 台積電，產生個股報告
```

```text
使用 $taiwan-stock-analysis 幫我做台股綜合短線篩選，期間 1 到 6 週，輸出前 10 名與停損/目標區間
```

## CLI 用法

```powershell
$py = "C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
cd .\skills\taiwan-stock-analysis

& $py .\scripts\tw_stock_tool.py quote 2330 --market twse
& $py .\scripts\tw_stock_tool.py history 2330 --market twse --period 1y --format csv
& $py .\scripts\tw_stock_tool.py report 2330 --market twse
& $py .\scripts\tw_stock_tool.py screen --input fundamentals.csv --preset deep-value --limit 20
& $py .\scripts\tw_stock_tool.py portfolio-summary --ledger trades.csv --prices prices.csv
& $py .\scripts\tw_stock_tool.py stress-test --ledger trades.csv --prices prices.csv --scenario semiconductor-downcycle
```

## 依賴

`yfinance==1.3.0` 已 vendored 到 `vendor/python`，並保留 wheels 於 `vendor/wheels`。若需要重建：

```powershell
python -m pip install -r requirements.txt --target vendor/python
```

## 注意

本外掛提供投資分析，不提供個人化投資建議。任何即時價格、財報、公司行動或法規資訊，在用於決策前都應再次查證。
