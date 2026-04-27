"""#3 — NVDR daily flow tracker.

Pulls NVDR (Non-Voting Depository Receipts) buy/sell by stock — the
canonical proxy for foreign flows in Thai equities.

Endpoint: /api/set/nvdr-trade/stock-trading?sortBy=netBuyValue
  Returns {date, nvdrTradings:[{symbol, buyValue, sellValue, netValue,
  totalValue, percentValue, ...}]} for ~all liquid SET names.

Returns top-10 net buy and top-10 net sell by THB value.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from scripts.trackers._base import (
    TrackerResult, append_today, fetch_json, get_set_session,
)

log = logging.getLogger(__name__)

NAME = "set_nvdr"

# NVDR per-symbol trade endpoint. sortBy is REQUIRED (server returns
# 400 "Bad Request" / "Invalid Sort" otherwise). Valid values discovered
# from www.set.or.th Nuxt bundle: netBuyValue, netSellValue.
STOCK_URL = "https://www.set.or.th/api/set/nvdr-trade/stock-trading"
NVDR_REFERER = "https://www.set.or.th/en/market/get-quote/nvdr"


def _parse_stock(payload: Any) -> list[dict]:
    """Parse stock-trading endpoint into [{symbol, buy, sell, net, ...}]."""
    if not isinstance(payload, dict):
        return []
    rows = payload.get("nvdrTradings")
    if not isinstance(rows, list):
        # tolerate older / alternate shapes
        for key in ("stockTrading", "data", "items", "result"):
            v = payload.get(key)
            if isinstance(v, list):
                rows = v
                break
    if not rows:
        return []
    out: list[dict] = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        sym = r.get("symbol") or r.get("name")
        if not sym:
            continue
        try:
            b = float(r.get("buyValue") or 0)
            sv = float(r.get("sellValue") or 0)
            n = (float(r["netValue"]) if r.get("netValue") is not None
                 else b - sv)
            tot = float(r.get("totalValue") or (b + sv))
            pct = (float(r["percentValue"])
                   if r.get("percentValue") is not None else None)
        except (TypeError, ValueError):
            continue
        out.append({
            "symbol": str(sym).strip(),
            "buy_value": b,
            "sell_value": sv,
            "net_value": n,
            "total_value": tot,
            "percent_of_underlying": pct,
        })
    return out


def run() -> TrackerResult:
    log.info("[%s] starting", NAME)
    s = get_set_session()
    # The API returns ONE side at a time depending on sortBy:
    #   sortBy=netBuyValue  → only net-buy names (descending net)
    #   sortBy=netSellValue → only net-sell names (descending sell)
    # We need both to build top buy + top sell. Merge by symbol.
    merged: dict[str, dict] = {}
    for sort_key in ("netBuyValue", "netSellValue"):
        payload = fetch_json(s, STOCK_URL,
                            params={"sortBy": sort_key},
                            referer=NVDR_REFERER)
        rows = _parse_stock(payload) if payload is not None else []
        log.info("[%s] sortBy=%s → %d rows", NAME, sort_key, len(rows))
        for r in rows:
            merged.setdefault(r["symbol"], r)

    if not merged:
        return TrackerResult(name=NAME, ok=False,
                             summary="(NVDR stock-trading unreachable)",
                             error="no rows parsed")

    parsed = list(merged.values())
    log.info("[%s] merged %d unique symbols", NAME, len(parsed))
    top_buy = sorted(parsed, key=lambda r: r["net_value"], reverse=True)[:10]
    top_sell = sorted(parsed, key=lambda r: r["net_value"])[:10]

    today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    append_today(NAME, {
        "date": today_date,
        "top_buy": top_buy,
        "top_sell": top_sell,
    })

    def fmt_row(r: dict) -> str:
        v_mb = r["net_value"] / 1e6
        sign = "+" if v_mb >= 0 else ""
        return f"{r['symbol']} {sign}฿{v_mb:.0f}M"

    buy_str = ", ".join(fmt_row(r) for r in top_buy[:5])
    sell_str = ", ".join(fmt_row(r) for r in top_sell[:5])
    summary = f"NVDR net BUY top: {buy_str}. NVDR net SELL top: {sell_str}"

    return TrackerResult(
        name=NAME, ok=True, summary=summary,
        data={
            "date": today_date,
            "top_buy": top_buy,
            "top_sell": top_sell,
        },
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    r = run()
    print(r)
