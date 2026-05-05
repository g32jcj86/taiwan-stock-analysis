---
name: taiwan-stock-analysis
description: 台股分析工作流程。當 Codex 需要篩選低估股票、產生台股個股報告、分析投資組合交易紀錄與損益結構、檢查投組健康度、估算預期報酬與再平衡建議、用集中度、相關性與 VaR 檢查壓力測試，或管理股票觀察名單時使用。支援四個篩選引擎、七個預設策略、TWSE 與 TPEx 台股代碼正規化，以及 yfinance 相容的全球交易所股票代碼。
---

# 台股分析

## 核心規則

提供投資分析，不提供個人化投資建議。說明資料日期、資料缺口、假設條件與下行風險。若價格、申報資料、公司行動、指數、法規、利率或任何近期可能變動的資訊會影響結論，先查證最新資料再使用。

使用者沒有指定其他語言時，報告預設使用繁體中文。公式、股票代碼、指令名稱與欄位名稱維持原始格式。

## 快速開始

使用 `scripts/tw_stock_tool.py` 執行可重複的本地分析。外掛已在 plugin root 的 `vendor/python` 內建 `yfinance`，腳本會自動載入該 vendor 目錄，並將 yfinance 快取寫入 `vendor/cache`。

```bash
python scripts/tw_stock_tool.py normalize 2330 --market twse
python scripts/tw_stock_tool.py quote 2330 --market twse
python scripts/tw_stock_tool.py history 2330 --market twse --period 1y --format csv
python scripts/tw_stock_tool.py screen --input fundamentals.csv --preset deep-value
python scripts/tw_stock_tool.py report 2330.TW
python scripts/tw_stock_tool.py portfolio-summary --ledger trades.csv --prices prices.csv
python scripts/tw_stock_tool.py stress-test --positions positions.csv --scenario semiconductor-downcycle
python scripts/tw_stock_tool.py watchlist add --file watchlist.json --ticker 2330.TW --reason "AI server supply chain"
```

如果 `yfinance` 遺失，從 plugin root 重新安裝：

```bash
python -m pip install -r requirements.txt --target vendor/python
```

選擇篩選引擎、preset、報告章節、投組健康檢查或壓力測試情境時，讀取 `references/methodology.md`。選擇資料來源或股票代碼格式時，讀取 `references/data-sources.md`。

## 股票代碼處理

- TWSE 上市股票正規化為 `<code>.TW`，例如 `2330.TW`。
- TPEx 上櫃股票正規化為 `<code>.TWO`，例如 `6488.TWO`。
- 已經符合 yfinance 格式的代碼保持不變，例如 `AAPL`、`7203.T`、`0700.HK`。
- 全球股票接受有效的 yfinance/Yahoo Finance 代碼。若市場 suffix 不在常用對照表內，不要直接拒絕分析；先向使用者確認或查證交易所 suffix。

## 篩選工作流程

使用四個引擎：

1. Valuation：PE、PB、EV/EBITDA、自由現金流殖利率、股息殖利率，以及相對歷史或同業折價。
2. Quality：ROE、ROA、毛利率、營業利益率、獲利穩定度、槓桿、現金轉換與治理風險。
3. Growth：營收成長、EPS 成長、月營收趨勢、毛利率趨勢、訂單或需求指標。
4. Momentum and risk：價格動能、回撤、波動度、流動性、法人籌碼與事件風險。

使用七個 preset：

- `deep-value`：偏重估值折價的低估股篩選。
- `quality-compounder`：高品質、可持續成長，且估值仍可接受。
- `dividend-income`：股息殖利率、配息安全性與現金流韌性。
- `garp`：合理價格下的成長股。
- `turnaround`：營收、毛利率與資產負債表正在改善的轉機股。
- `small-cap-liquidity-aware`：小型股篩選，對流動性不足加重扣分。
- `risk-defensive`：偏重下行保護、低波動、低槓桿與穩定現金流。

篩選輸出應包含排名、股票代碼、公司名稱、總分、引擎子分數、主要理由、淘汰原因、資料日期與缺漏欄位。

## 個股報告

針對指定股票產生：

- 摘要觀點：評等語氣、投資期間、核心 thesis 與最大風險。
- 商業模式：業務分部、營收驅動因子、終端市場與供應鏈位置。
- 財務分析：營收、毛利率、營益率、EPS、ROE、現金流、負債與股利政策。
- 估值分析：同業比較、歷史區間、隱含上行/下行與主要假設。
- 技術與風險：趨勢、波動度、流動性、事件日程與風險旗標。
- 情境表：bull/base/bear 假設與估值區間。
- 資料品質：資料來源日期、缺漏欄位與是否已查證即時資訊。

不要掩蓋不確定性。若抓不到即時資料，產生清楚標示的報告骨架，並列出完成分析所需的資料。

當使用者明確要求 Yahoo Finance 即時資料，或報告需要市場快照時，使用 `quote` 取得精簡 JSON 快照，使用 `history` 取得 CSV/JSON 歷史股價。

## 投資組合工作流程

有交易紀錄時優先使用 trade ledger。預期 CSV 欄位：

```text
date,ticker,side,quantity,price,currency,fee,tax,account,sector,note
```

報告內容：

- 持股、平均成本、已實現損益、未實現損益、總報酬與現金影響。
- 依股票、產業、帳戶、市場與幣別拆解配置。
- 健康檢查：最大持股權重、最大產業權重、流動性風險、過期價格、槓桿、股息集中度與重疊曝險。
- 預期報酬：個股預期報酬、加權投組預期報酬、信心水準與假設。
- 再平衡：目標權重、交易清單、換手率、預估手續費/稅費與降低的風險。

本地工具預設使用平均成本法，除非使用者提供 tax-lot 規則。報告中要明確標示此假設。

## 壓力測試

除非使用者要求自訂情境，預設執行八個情境：

- `taiex-correction`：台股大盤修正。
- `semiconductor-downcycle`：半導體循環下行。
- `global-recession`：全球景氣衰退與外需衝擊。
- `rate-shock`：利率與折現率上升。
- `twd-appreciation`：新台幣升值壓迫出口毛利。
- `twd-depreciation`：新台幣貶值造成進口成本與外幣負債壓力。
- `liquidity-crunch`：小型股流動性與買賣價差惡化。
- `correlation-spike`：分散效果失效，相關性同步升高。

務必包含集中度、相關性與 VaR 或 VaR proxy 評論。有價格歷史資料時，使用歷史 VaR 或參數法 VaR。沒有價格歷史資料時，使用透明的情境式 proxy VaR，並清楚標示為 proxy。

## 觀察名單

使用 `watchlist` 指令或 JSON 檔：

```json
{
  "items": [
    {
      "ticker": "2330.TW",
      "reason": "AI server supply chain",
      "target_price": 900,
      "stop_loss": 760,
      "catalyst": "monthly revenue",
      "status": "active",
      "updated_at": "2026-05-05"
    }
  ]
}
```

檢視觀察名單時，依優先順序、催化事件日期、風險、估值差距與下一步行動分組。
