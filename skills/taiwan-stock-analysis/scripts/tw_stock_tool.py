#!/usr/bin/env python3
"""Local helper for Taiwan stock analysis workflows.

The helper intentionally uses only the Python standard library. yfinance is
used only when present, so portfolio and watchlist workflows still work in
offline or locked-down environments.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


class ChineseArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("add_help", False)
        super().__init__(*args, **kwargs)
        self.add_argument("-h", "--help", action="help", help="顯示此說明訊息並結束")
        self._positionals.title = "位置參數"
        self._optionals.title = "選項"


def add_vendor_path() -> Optional[Path]:
    """Prefer plugin-local vendored dependencies when present."""
    script_path = Path(__file__).resolve()
    try:
        plugin_root = script_path.parents[3]
    except IndexError:
        return None
    vendor = plugin_root / "vendor" / "python"
    if vendor.exists():
        vendor_text = str(vendor)
        if vendor_text not in sys.path:
            sys.path.insert(0, vendor_text)
        return vendor
    return None


VENDOR_PATH = add_vendor_path()
PLUGIN_ROOT = VENDOR_PATH.parents[1] if VENDOR_PATH is not None else Path(__file__).resolve().parents[3]


def configure_yfinance_cache(yf_module: Any) -> None:
    cache_dir = PLUGIN_ROOT / "vendor" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    if hasattr(yf_module, "set_tz_cache_location"):
        yf_module.set_tz_cache_location(str(cache_dir))


TW_SUFFIXES = {
    "twse": ".TW",
    "listed": ".TW",
    "tpex": ".TWO",
    "otc": ".TWO",
    "emerging": ".TWO",
}

COMMON_SUFFIXES = {
    "us": "",
    "nyse": "",
    "nasdaq": "",
    "amex": "",
    "twse": ".TW",
    "tpex": ".TWO",
    "tokyo": ".T",
    "japan": ".T",
    "hkex": ".HK",
    "hong-kong": ".HK",
    "london": ".L",
    "lse": ".L",
    "toronto": ".TO",
    "tsx": ".TO",
    "australia": ".AX",
    "asx": ".AX",
    "singapore": ".SI",
    "sgx": ".SI",
    "korea": ".KS",
    "kospi": ".KS",
    "kosdaq": ".KQ",
    "shanghai": ".SS",
    "shenzhen": ".SZ",
    "india-nse": ".NS",
    "india-bse": ".BO",
    "frankfurt": ".F",
    "paris": ".PA",
    "amsterdam": ".AS",
    "milan": ".MI",
    "madrid": ".MC",
    "zurich": ".SW",
    "stockholm": ".ST",
    "mexico": ".MX",
    "brazil": ".SA",
}

PRESETS = {
    "deep-value": {
        "valuation": 0.55,
        "quality": 0.20,
        "growth": 0.10,
        "momentum_risk": 0.15,
    },
    "quality-compounder": {
        "valuation": 0.20,
        "quality": 0.40,
        "growth": 0.25,
        "momentum_risk": 0.15,
    },
    "dividend-income": {
        "valuation": 0.30,
        "quality": 0.35,
        "growth": 0.05,
        "momentum_risk": 0.30,
    },
    "garp": {
        "valuation": 0.30,
        "quality": 0.25,
        "growth": 0.30,
        "momentum_risk": 0.15,
    },
    "turnaround": {
        "valuation": 0.20,
        "quality": 0.20,
        "growth": 0.40,
        "momentum_risk": 0.20,
    },
    "small-cap-liquidity-aware": {
        "valuation": 0.35,
        "quality": 0.20,
        "growth": 0.25,
        "momentum_risk": 0.20,
    },
    "risk-defensive": {
        "valuation": 0.20,
        "quality": 0.35,
        "growth": 0.05,
        "momentum_risk": 0.40,
    },
}

SCENARIOS = {
    "taiex-correction": {
        "market": -0.15,
        "sector": {"Technology": -0.07, "Financials": -0.03},
    },
    "semiconductor-downcycle": {
        "market": -0.10,
        "sector": {"Semiconductor": -0.20, "Hardware": -0.12, "Technology": -0.12},
    },
    "global-recession": {
        "market": -0.18,
        "sector": {"Exporter": -0.10, "Cyclical": -0.12, "Industrial": -0.08},
    },
    "rate-shock": {
        "market": -0.08,
        "sector": {"Growth": -0.12, "Financials": 0.03, "Real Estate": -0.10},
    },
    "twd-appreciation": {
        "market": -0.06,
        "sector": {"Exporter": -0.10, "Importer": 0.03, "Technology": -0.04},
    },
    "twd-depreciation": {
        "market": -0.06,
        "sector": {"Importer": -0.08, "Exporter": 0.04, "Airline": -0.10},
    },
    "liquidity-crunch": {
        "market": -0.12,
        "sector": {"Small Cap": -0.18, "Low Volume": -0.15},
    },
    "correlation-spike": {
        "market": -0.14,
        "sector": {},
        "correlation_spike": True,
    },
}


def today_iso() -> str:
    return dt.date.today().isoformat()


def normalize_ticker(ticker: str, market: Optional[str] = None) -> str:
    value = ticker.strip().upper()
    if not value:
        raise ValueError("ticker is required")
    if "." in value or market is None:
        return value
    key = market.strip().lower()
    suffix = COMMON_SUFFIXES.get(key)
    if suffix is None and key.startswith("."):
        suffix = key.upper()
    if suffix is None:
        raise ValueError(f"unknown market '{market}'; pass an already-qualified yfinance symbol")
    return f"{value}{suffix}"


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fieldnames})


def f(row: Dict[str, Any], key: str, default: Optional[float] = None) -> Optional[float]:
    raw = row.get(key, "")
    if raw is None or raw == "":
        return default
    try:
        return float(str(raw).replace(",", "").replace("%", "")) / (100 if "%" in str(raw) else 1)
    except ValueError:
        return default


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def score_high(value: Optional[float], good: float, bad: float) -> Optional[float]:
    if value is None:
        return None
    if good == bad:
        return 50.0
    return clamp((value - bad) / (good - bad) * 100)


def score_low(value: Optional[float], good: float, bad: float) -> Optional[float]:
    if value is None:
        return None
    if good == bad:
        return 50.0
    return clamp((bad - value) / (bad - good) * 100)


def mean_present(values: Iterable[Optional[float]]) -> Optional[float]:
    present = [value for value in values if value is not None and not math.isnan(value)]
    if not present:
        return None
    return sum(present) / len(present)


def engine_scores(row: Dict[str, str]) -> Dict[str, Optional[float]]:
    valuation = mean_present(
        [
            score_low(f(row, "pe"), good=8, bad=35),
            score_low(f(row, "pb"), good=0.8, bad=4.0),
            score_low(f(row, "ev_ebitda"), good=6, bad=22),
            score_high(f(row, "fcf_yield"), good=0.08, bad=0.0),
            score_high(f(row, "dividend_yield"), good=0.05, bad=0.0),
        ]
    )
    quality = mean_present(
        [
            score_high(f(row, "roe"), good=0.18, bad=0.0),
            score_high(f(row, "roa"), good=0.10, bad=0.0),
            score_high(f(row, "gross_margin"), good=0.45, bad=0.10),
            score_high(f(row, "operating_margin"), good=0.22, bad=0.02),
            score_low(f(row, "debt_to_equity"), good=0.3, bad=2.0),
        ]
    )
    growth = mean_present(
        [
            score_high(f(row, "revenue_growth"), good=0.20, bad=-0.10),
            score_high(f(row, "eps_growth"), good=0.20, bad=-0.15),
            score_high(f(row, "monthly_revenue_yoy"), good=0.20, bad=-0.15),
            score_high(f(row, "margin_trend"), good=0.05, bad=-0.05),
        ]
    )
    momentum_risk = mean_present(
        [
            score_high(f(row, "price_momentum_6m"), good=0.20, bad=-0.20),
            score_high(f(row, "price_momentum_12m"), good=0.30, bad=-0.25),
            score_low(f(row, "volatility"), good=0.18, bad=0.60),
            score_high(f(row, "max_drawdown"), good=-0.12, bad=-0.55),
            score_high(f(row, "avg_volume"), good=3_000_000, bad=100_000),
        ]
    )
    return {
        "valuation": valuation,
        "quality": quality,
        "growth": growth,
        "momentum_risk": momentum_risk,
    }


def screen(args: argparse.Namespace) -> int:
    preset = PRESETS[args.preset]
    rows = []
    for row in read_csv(Path(args.input)):
        scores = engine_scores(row)
        missing = [name for name, value in scores.items() if value is None]
        total = 0.0
        weight_used = 0.0
        for engine, weight in preset.items():
            if scores[engine] is not None:
                total += scores[engine] * weight
                weight_used += weight
        total_score = total / weight_used if weight_used else 0.0
        reasons = build_reasons(row, scores)
        rows.append(
            {
                "ticker": row.get("ticker", ""),
                "name": row.get("name", ""),
                "sector": row.get("sector", ""),
                "score": round(total_score, 2),
                "valuation": round(scores["valuation"], 2) if scores["valuation"] is not None else "",
                "quality": round(scores["quality"], 2) if scores["quality"] is not None else "",
                "growth": round(scores["growth"], 2) if scores["growth"] is not None else "",
                "momentum_risk": round(scores["momentum_risk"], 2)
                if scores["momentum_risk"] is not None
                else "",
                "reasons": "; ".join(reasons),
                "missing_engines": ",".join(missing),
            }
        )
    rows.sort(key=lambda item: item["score"], reverse=True)
    if args.limit:
        rows = rows[: args.limit]
    write_csv(
        rows,
        [
            "ticker",
            "name",
            "sector",
            "score",
            "valuation",
            "quality",
            "growth",
            "momentum_risk",
            "reasons",
            "missing_engines",
        ],
    )
    return 0


def build_reasons(row: Dict[str, str], scores: Dict[str, Optional[float]]) -> List[str]:
    reasons = []
    labels = {
        "valuation": "估值分數強",
        "quality": "品質分數強",
        "growth": "成長分數強",
        "momentum_risk": "動能與風險分數強",
    }
    for engine, score in scores.items():
        if score is not None and score >= 75:
            reasons.append(labels.get(engine, f"{engine} 分數強"))
    pe = f(row, "pe")
    pb = f(row, "pb")
    roe = f(row, "roe")
    debt = f(row, "debt_to_equity")
    if pe is not None and pe <= 10:
        reasons.append("低 PE")
    if pb is not None and pb <= 1:
        reasons.append("低 PB")
    if roe is not None and roe >= 0.15:
        reasons.append("高 ROE")
    if debt is not None and debt >= 2:
        reasons.append("槓桿風險偏高")
    return reasons or ["需要人工檢查"]


def try_yfinance_snapshot(ticker: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        import yfinance as yf  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on local environment
        return None, f"yfinance 無法使用: {exc}"
    configure_yfinance_cache(yf)
    try:
        item = yf.Ticker(ticker)
        info = getattr(item, "info", {}) or {}
        return info, None
    except Exception as exc:  # pragma: no cover - network/provider dependent
        return None, f"yfinance 抓取失敗: {exc}"


def quote(args: argparse.Namespace) -> int:
    ticker = normalize_ticker(args.ticker, args.market)
    info, error = try_yfinance_snapshot(ticker)
    if error:
        print(json.dumps({"ticker": ticker, "error": error}, ensure_ascii=False, indent=2))
        return 1
    selected = {
        "ticker": ticker,
        "data_date": today_iso(),
        "name": info.get("longName") or info.get("shortName"),
        "currency": info.get("currency"),
        "exchange": info.get("exchange"),
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "previous_close": info.get("previousClose"),
        "market_cap": info.get("marketCap"),
        "trailing_pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "price_to_book": info.get("priceToBook"),
        "dividend_yield": info.get("dividendYield"),
        "beta": info.get("beta"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
    }
    print(json.dumps(selected, ensure_ascii=False, indent=2))
    return 0


def history(args: argparse.Namespace) -> int:
    try:
        import yfinance as yf  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on local environment
        print(json.dumps({"error": f"yfinance 無法使用: {exc}"}, ensure_ascii=False, indent=2))
        return 1
    configure_yfinance_cache(yf)
    ticker = normalize_ticker(args.ticker, args.market)
    try:
        frame = yf.Ticker(ticker).history(period=args.period, interval=args.interval)
    except Exception as exc:  # pragma: no cover - network/provider dependent
        print(json.dumps({"ticker": ticker, "error": f"歷史股價抓取失敗: {exc}"}, ensure_ascii=False, indent=2))
        return 1
    if frame is None or frame.empty:
        print(json.dumps({"ticker": ticker, "rows": []}, ensure_ascii=False, indent=2))
        return 0
    if args.format == "json":
        rows = []
        for index, row in frame.reset_index().iterrows():
            item = {}
            for key, value in row.items():
                if hasattr(value, "isoformat"):
                    item[key] = value.isoformat()
                elif value is None or (isinstance(value, float) and math.isnan(value)):
                    item[key] = None
                else:
                    item[key] = float(value) if isinstance(value, (int, float)) else str(value)
            rows.append(item)
        print(json.dumps({"ticker": ticker, "rows": rows}, ensure_ascii=False, indent=2))
        return 0
    frame.to_csv(sys.stdout, lineterminator="\n")
    return 0


def report(args: argparse.Namespace) -> int:
    ticker = normalize_ticker(args.ticker, args.market)
    info, error = try_yfinance_snapshot(ticker)
    lines = [
        f"# 個股報告: {ticker}",
        "",
        f"- 資料日期: {today_iso()}",
        "- 輸出類型: 投資分析，不是個人化投資建議",
    ]
    if error:
        lines.extend(["", f"- 資料狀態: {error}", "- 做出決策前必須查證即時資料。"])
    if info:
        fields = {
            "Name": info.get("longName") or info.get("shortName"),
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "Market cap": info.get("marketCap"),
            "Trailing PE": info.get("trailingPE"),
            "Forward PE": info.get("forwardPE"),
            "Price to book": info.get("priceToBook"),
            "Dividend yield": info.get("dividendYield"),
            "Beta": info.get("beta"),
        }
        lines.append("")
        lines.append("## Snapshot")
        for key, value in fields.items():
            if value is not None:
                lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## 投資論點",
            "- 基準論點:",
            "- 主要催化因素:",
            "- 主要風險:",
            "",
            "## 財務檢查",
            "- 營收趨勢:",
            "- 利潤率趨勢:",
            "- 現金流與資產負債表:",
            "",
            "## 估值分析",
            "- 同業比較:",
            "- 歷史區間:",
            "- 樂觀/基準/悲觀假設:",
            "",
            "## 追蹤觸發條件",
            "- 月營收:",
            "- 利潤率或財測變化:",
            "- 估值或價格觸發條件:",
        ]
    )
    print("\n".join(lines))
    return 0


def summarize_ledger(ledger_path: Path, prices_path: Optional[Path]) -> Dict[str, Any]:
    rows = read_csv(ledger_path)
    prices = read_prices(prices_path) if prices_path else {}
    positions: Dict[str, Dict[str, Any]] = {}
    realized = 0.0
    for row in rows:
        ticker = row.get("ticker", "").strip().upper()
        if not ticker:
            continue
        side = row.get("side", "").strip().lower()
        qty = f(row, "quantity", 0.0) or 0.0
        price = f(row, "price", 0.0) or 0.0
        fee = f(row, "fee", 0.0) or 0.0
        tax = f(row, "tax", 0.0) or 0.0
        sector = row.get("sector", "") or "Unknown"
        currency = row.get("currency", "") or "TWD"
        position = positions.setdefault(
            ticker,
            {
                "ticker": ticker,
                "quantity": 0.0,
                "cost": 0.0,
                "sector": sector,
                "currency": currency,
                "realized_pnl": 0.0,
            },
        )
        if side in {"buy", "b"}:
            position["quantity"] += qty
            position["cost"] += qty * price + fee + tax
        elif side in {"sell", "s"}:
            if position["quantity"] <= 0:
                realized += qty * price - fee - tax
                position["realized_pnl"] += qty * price - fee - tax
                continue
            avg_cost = position["cost"] / position["quantity"]
            realized_trade = qty * price - avg_cost * qty - fee - tax
            realized += realized_trade
            position["realized_pnl"] += realized_trade
            position["quantity"] -= qty
            position["cost"] -= avg_cost * qty
    holdings = []
    total_value = 0.0
    total_cost = 0.0
    for position in positions.values():
        if abs(position["quantity"]) < 1e-9:
            continue
        ticker = position["ticker"]
        mark = prices.get(ticker, {}).get("price")
        if mark is None:
            mark = position["cost"] / position["quantity"] if position["quantity"] else 0.0
        market_value = position["quantity"] * mark
        total_value += market_value
        total_cost += position["cost"]
        holdings.append(
            {
                **position,
                "price": mark,
                "market_value": market_value,
                "unrealized_pnl": market_value - position["cost"],
            }
        )
    for holding in holdings:
        holding["weight"] = holding["market_value"] / total_value if total_value else 0.0
    holdings.sort(key=lambda item: item["market_value"], reverse=True)
    return {
        "method": "average_cost",
        "total_market_value": total_value,
        "total_cost": total_cost,
        "realized_pnl": realized,
        "unrealized_pnl": total_value - total_cost,
        "holdings": holdings,
        "health": health_checks(holdings),
    }


def read_prices(path: Optional[Path]) -> Dict[str, Dict[str, Any]]:
    if not path:
        return {}
    output = {}
    for row in read_csv(path):
        ticker = row.get("ticker", "").strip().upper()
        if ticker:
            output[ticker] = {
                "price": f(row, "price"),
                "currency": row.get("currency", ""),
                "date": row.get("date", ""),
            }
    return output


def health_checks(holdings: List[Dict[str, Any]]) -> List[str]:
    checks = []
    if not holdings:
        return ["沒有有效持股"]
    top = holdings[0]
    if top["weight"] > 0.20:
        checks.append(f"最大持股 {top['ticker']} 權重為 {top['weight']:.1%}")
    sector_weights: Dict[str, float] = {}
    for item in holdings:
        sector_weights[item.get("sector", "Unknown")] = sector_weights.get(item.get("sector", "Unknown"), 0.0) + item[
            "weight"
        ]
    if sector_weights:
        sector, weight = max(sector_weights.items(), key=lambda pair: pair[1])
        if weight > 0.40:
            checks.append(f"最大產業 {sector} 權重為 {weight:.1%}")
    if not checks:
        checks.append("依現有欄位未發現重大集中度警訊")
    return checks


def portfolio_summary(args: argparse.Namespace) -> int:
    summary = summarize_ledger(Path(args.ledger), Path(args.prices) if args.prices else None)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def load_positions(args: argparse.Namespace) -> List[Dict[str, Any]]:
    if args.positions:
        rows = read_csv(Path(args.positions))
        output = []
        for row in rows:
            qty = f(row, "quantity", 0.0) or 0.0
            price = f(row, "price", 0.0) or 0.0
            output.append(
                {
                    "ticker": row.get("ticker", "").strip().upper(),
                    "quantity": qty,
                    "price": price,
                    "market_value": qty * price,
                    "sector": row.get("sector", "") or "Unknown",
                    "currency": row.get("currency", "") or "TWD",
                    "beta": f(row, "beta", 1.0) or 1.0,
                }
            )
        return output
    if args.ledger:
        summary = summarize_ledger(Path(args.ledger), Path(args.prices) if args.prices else None)
        return [
            {
                "ticker": item["ticker"],
                "quantity": item["quantity"],
                "price": item["price"],
                "market_value": item["market_value"],
                "sector": item.get("sector", "Unknown"),
                "currency": item.get("currency", "TWD"),
                "beta": 1.0,
            }
            for item in summary["holdings"]
        ]
    raise SystemExit("provide --positions or --ledger")


def stress_test(args: argparse.Namespace) -> int:
    scenario = SCENARIOS[args.scenario]
    positions = load_positions(args)
    total = sum(item["market_value"] for item in positions)
    rows = []
    for item in positions:
        sector = item.get("sector", "Unknown")
        market_shock = scenario["market"] * item.get("beta", 1.0)
        extra = scenario.get("sector", {}).get(sector, 0.0)
        shock = market_shock + extra
        if scenario.get("correlation_spike"):
            shock = min(shock, scenario["market"] * 1.2)
        loss = item["market_value"] * shock
        rows.append(
            {
                "ticker": item["ticker"],
                "sector": sector,
                "market_value": round(item["market_value"], 2),
                "shock": round(shock, 4),
                "loss": round(loss, 2),
                "new_value": round(item["market_value"] + loss, 2),
            }
        )
    rows.sort(key=lambda item: item["loss"])
    total_loss = sum(item["loss"] for item in rows)
    top_weight = max((item["market_value"] / total for item in positions), default=0.0) if total else 0.0
    sector_weights: Dict[str, float] = {}
    for item in positions:
        sector_weights[item["sector"]] = sector_weights.get(item["sector"], 0.0) + (
            item["market_value"] / total if total else 0.0
        )
    top_sector = max(sector_weights.items(), key=lambda pair: pair[1]) if sector_weights else ("None", 0.0)
    shocks = [abs(row["shock"]) for row in rows]
    var_proxy = total * (statistics.mean(shocks) if shocks else 0.0) * 1.65
    output = {
        "scenario": args.scenario,
        "portfolio_value": round(total, 2),
        "scenario_loss": round(total_loss, 2),
        "scenario_drawdown": round(total_loss / total, 4) if total else 0.0,
        "top_position_weight": round(top_weight, 4),
        "top_sector": top_sector[0],
        "top_sector_weight": round(top_sector[1], 4),
        "var_proxy_95": round(var_proxy, 2),
        "positions": rows,
        "notes": [
            "除非另外提供歷史報酬資料，VaR 為情境式 proxy。",
            "相關性風險以最大產業權重與情境共同變動作為 proxy。",
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def load_watchlist(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"items": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_watchlist(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def watchlist(args: argparse.Namespace) -> int:
    path = Path(args.file)
    data = load_watchlist(path)
    items = data.setdefault("items", [])
    if args.watch_action == "list":
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    ticker = normalize_ticker(args.ticker, args.market)
    if args.watch_action == "add":
        existing = next((item for item in items if item.get("ticker", "").upper() == ticker), None)
        payload = {
            "ticker": ticker,
            "reason": args.reason or "",
            "target_price": args.target_price,
            "stop_loss": args.stop_loss,
            "catalyst": args.catalyst or "",
            "status": args.status,
            "updated_at": today_iso(),
        }
        if existing:
            existing.update({key: value for key, value in payload.items() if value not in {None, ""}})
        else:
            items.append(payload)
        save_watchlist(path, data)
        print(f"已將 {ticker} 儲存到 {path}")
        return 0
    if args.watch_action == "remove":
        data["items"] = [item for item in items if item.get("ticker", "").upper() != ticker]
        save_watchlist(path, data)
        print(f"已從 {path} 移除 {ticker}")
        return 0
    raise SystemExit(f"unsupported watchlist action {args.watch_action}")


def build_parser() -> argparse.ArgumentParser:
    parser = ChineseArgumentParser(description="台股分析輔助工具")
    sub = parser.add_subparsers(dest="command", required=True, parser_class=ChineseArgumentParser)

    normalize_cmd = sub.add_parser("normalize", help="將股票代碼正規化為 yfinance 格式")
    normalize_cmd.add_argument("ticker")
    normalize_cmd.add_argument("--market")
    normalize_cmd.set_defaults(func=lambda args: print(normalize_ticker(args.ticker, args.market)) or 0)

    screen_cmd = sub.add_parser("screen", help="對基本面 CSV 進行篩選評分")
    screen_cmd.add_argument("--input", required=True)
    screen_cmd.add_argument("--preset", choices=sorted(PRESETS), default="deep-value")
    screen_cmd.add_argument("--limit", type=int)
    screen_cmd.set_defaults(func=screen)

    report_cmd = sub.add_parser("report", help="產生個股報告骨架，並可加入 yfinance 快照")
    report_cmd.add_argument("ticker")
    report_cmd.add_argument("--market")
    report_cmd.set_defaults(func=report)

    quote_cmd = sub.add_parser("quote", help="抓取 yfinance 報價快照並輸出 JSON")
    quote_cmd.add_argument("ticker")
    quote_cmd.add_argument("--market")
    quote_cmd.set_defaults(func=quote)

    history_cmd = sub.add_parser("history", help="抓取 yfinance 歷史股價")
    history_cmd.add_argument("ticker")
    history_cmd.add_argument("--market")
    history_cmd.add_argument("--period", default="1y")
    history_cmd.add_argument("--interval", default="1d")
    history_cmd.add_argument("--format", choices=["csv", "json"], default="csv")
    history_cmd.set_defaults(func=history)

    portfolio_cmd = sub.add_parser("portfolio-summary", help="彙總交易紀錄並分析投資組合")
    portfolio_cmd.add_argument("--ledger", required=True)
    portfolio_cmd.add_argument("--prices")
    portfolio_cmd.set_defaults(func=portfolio_summary)

    stress_cmd = sub.add_parser("stress-test", help="執行投資組合壓力測試情境")
    stress_cmd.add_argument("--positions")
    stress_cmd.add_argument("--ledger")
    stress_cmd.add_argument("--prices")
    stress_cmd.add_argument("--scenario", choices=sorted(SCENARIOS), default="taiex-correction")
    stress_cmd.set_defaults(func=stress_test)

    watch_cmd = sub.add_parser("watchlist", help="管理 JSON 觀察名單")
    watch_sub = watch_cmd.add_subparsers(dest="watch_action", required=True)
    watch_list = watch_sub.add_parser("list")
    watch_list.add_argument("--file", required=True)
    watch_list.set_defaults(func=watchlist)
    watch_add = watch_sub.add_parser("add")
    watch_add.add_argument("--file", required=True)
    watch_add.add_argument("--ticker", required=True)
    watch_add.add_argument("--market")
    watch_add.add_argument("--reason")
    watch_add.add_argument("--target-price", type=float)
    watch_add.add_argument("--stop-loss", type=float)
    watch_add.add_argument("--catalyst")
    watch_add.add_argument("--status", default="active")
    watch_add.set_defaults(func=watchlist)
    watch_remove = watch_sub.add_parser("remove")
    watch_remove.add_argument("--file", required=True)
    watch_remove.add_argument("--ticker", required=True)
    watch_remove.add_argument("--market")
    watch_remove.set_defaults(func=watchlist)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
