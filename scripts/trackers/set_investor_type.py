"""#1 proxy — SET foreign-flow tracker via NVDR comparative data.

The true institutional investor-type breakdown is not exposed in SET's
public web API (gated behind SETSmart Premium tier). As the closest free
proxy we use NVDR's `comparative-data` endpoint which shows what % of
total SET trading value/volume was foreign plus NVDR's own aggregate
buy/sell flows — the single most-watched Thai foreign-flow indicator.

Combined signal:
- percent of market value/volume that was foreign today
- total NVDR net buy/sell (= net foreign flow proxy, in THB millions)
- 5-day rolling cumulative NVDR net
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from scripts.trackers._base import (
    TrackerResult, append_today, fetch_json, get_set_session, load_history,
)

log = logging.getLogger(__name__)

NAME = "set_investor_type"

COMPARATIVE_URL = "https://www.set.or.th/api/set/nvdr-trade/comparative-data"
OVERVIEW_URL = "https://www.set.or.th/api/set/nvdr-trade/overview"


def _pick_market(rows: list[dict], market: str = "SET") -> dict | None:
    """Pick the row for a given market (SET or mai) from the response."""
    if not isinstance(rows, list):
        return None
    for r in rows:
        if isinstance(r, dict) and str(r.get("market", "")).upper() == market.upper():
            return r
    return rows[0] if rows and isinstance(rows[0], dict) else None


def run() -> TrackerResult:
    log.info("[%s] starting", NAME)
    s = get_set_session()
    comp = fetch_json(s, COMPARATIVE_URL)
    overview = fetch_json(s, OVERVIEW_URL)
    if comp is None and overview is None:
        return TrackerResult(name=NAME, ok=False,
                             summary="(NVDR foreign-flow proxy unreachable)",
                             error="both endpoints failed")

    set_comp = _pick_market(comp or [], "SET") or {}
    set_ov = _pick_market(overview or [], "SET") or {}

    today_date = (set_comp.get("date") or set_ov.get("date")
                  or datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    buy_value = float(set_ov.get("buyValue") or 0)
    sell_value = float(set_ov.get("sellValue") or 0)
    net_value = buy_value - sell_value
    pct_foreign_vol = set_comp.get("percentForeignVolume")
    pct_foreign_val = set_comp.get("percentForeignValue")
    pct_market_val = set_comp.get("percentMarketValue")

    record = {
        "date": today_date,
        "nvdr_buy_value": buy_value,
        "nvdr_sell_value": sell_value,
        "nvdr_net_value": net_value,
        "percent_foreign_volume": pct_foreign_vol,
        "percent_foreign_value": pct_foreign_val,
        "percent_market_value": pct_market_val,
    }
    history = append_today(NAME, record)
    net_5d = sum(r.get("nvdr_net_value", 0) or 0 for r in history[:5])

    def fmt(v: float | None, scale: float = 1e6) -> str:
        if v is None:
            return "n/a"
        val = v / scale
        sign = "+" if val >= 0 else ""
        return f"{sign}฿{val:,.0f}M"

    def pct(v: Any) -> str:
        try:
            return f"{float(v):.1f}%"
        except (TypeError, ValueError):
            return "n/a"

    summary = (
        f"NVDR net flow: {fmt(net_value)} (5d: {fmt(net_5d)}); "
        f"Foreign % of market value: {pct(pct_foreign_val)}, "
        f"% of market volume: {pct(pct_foreign_vol)}"
    )

    return TrackerResult(
        name=NAME, ok=True, summary=summary,
        data={
            "date": today_date,
            "nvdr_today": {
                "buy_value_thb": buy_value,
                "sell_value_thb": sell_value,
                "net_value_thb": net_value,
                "net_value_mb": net_value / 1e6,
            },
            "rolling_5d_net_mb": net_5d / 1e6,
            "foreign_share": {
                "percent_volume": pct_foreign_vol,
                "percent_value": pct_foreign_val,
                "percent_market_value": pct_market_val,
            },
            "history_size": len(history),
        },
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    r = run()
    print(r)
