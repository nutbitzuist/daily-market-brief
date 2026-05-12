"""#1 — official SET investor-type flow tracker.

Pulls SET's official investor-type table for SET market:
- Local institutions
- Proprietary trading
- Foreign investors
- Local individuals
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from scripts.trackers._base import (
    TrackerResult, append_today, fetch_json, get_set_session, load_history,
)

log = logging.getLogger(__name__)

NAME = "set_investor_type"

INVESTOR_TYPE_URL = "https://www.set.or.th/api/set/market/SET/investor-type"
SET_REFERER = "https://www.set.or.th/en/market/statistics/investor-type"


def _fmt_mb(value: float | None) -> str:
    if value is None:
        return "n/a"
    mb = value / 1e6
    sign = "+" if mb >= 0 else ""
    return f"{sign}฿{mb:,.0f}M"


def _parse(payload: dict) -> tuple[str, float, dict[str, dict]]:
    if not isinstance(payload, dict):
        raise ValueError("payload is not dict")
    investors = payload.get("investors")
    if not isinstance(investors, list):
        raise ValueError("missing investors list")
    by_type: dict[str, dict] = {}
    for row in investors:
        if not isinstance(row, dict):
            continue
        typ = str(row.get("type") or "").strip().lower()
        if not typ:
            continue
        by_type[typ] = {
            "buy_value_thb": float(row.get("buyValue") or 0),
            "sell_value_thb": float(row.get("sellValue") or 0),
            "net_value_thb": float(row.get("netValue") or 0),
            "percent_buy_value": row.get("percentBuyValue"),
            "percent_sell_value": row.get("percentSellValue"),
        }
    required = {"institution", "proprietary", "foreign", "individual"}
    missing = required - set(by_type)
    if missing:
        raise ValueError(f"missing investor types: {sorted(missing)}")
    return (
        str(payload.get("asOfDate") or payload.get("endDate") or ""),
        float(payload.get("totalValue") or 0),
        by_type,
    )


def run() -> TrackerResult:
    log.info("[%s] starting", NAME)
    s = get_set_session()
    payload = fetch_json(s, INVESTOR_TYPE_URL, referer=SET_REFERER)
    if payload is None:
        return TrackerResult(name=NAME, ok=False,
                             summary="(SET investor-type unreachable)",
                             error="endpoint failed")
    try:
        today_date, total_value, by_type = _parse(payload)
    except Exception as e:
        return TrackerResult(name=NAME, ok=False,
                             summary="(SET investor-type schema not recognized)",
                             error=str(e),
                             data={"sample": str(payload)[:500]})

    record = {
        "date": today_date,
        "total_value_thb": total_value,
        "investors": by_type,
    }
    history = append_today(NAME, record)
    rolling_5d: dict[str, float] = {}
    for investor_type in ("foreign", "individual", "institution", "proprietary"):
        rolling_5d[investor_type] = sum(
            ((r.get("investors") or {}).get(investor_type) or {})
            .get("net_value_thb", 0) or 0
            for r in history[:5]
        )

    summary = (
        f"Official SET investor type: Foreign "
        f"{_fmt_mb(by_type['foreign']['net_value_thb'])}, "
        f"Individual {_fmt_mb(by_type['individual']['net_value_thb'])}, "
        f"Institution {_fmt_mb(by_type['institution']['net_value_thb'])}, "
        f"Proprietary {_fmt_mb(by_type['proprietary']['net_value_thb'])}"
    )

    return TrackerResult(
        name=NAME, ok=True, summary=summary,
        data={
            "date": today_date,
            "source": INVESTOR_TYPE_URL,
            "total_value_thb": total_value,
            "investors": by_type,
            "rolling_5d_net_mb": {
                k: v / 1e6 for k, v in rolling_5d.items()
            },
            "history_size": len(history),
        },
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    r = run()
    print(r)
