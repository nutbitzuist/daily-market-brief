"""#2 — SET short-sale daily ranking.

Pulls the short-sale value/volume by stock and computes:
- top-20 by short value today
- biggest day-over-day percentage spikes vs. yesterday's history
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from scripts.trackers._base import (
    TrackerResult, append_today, fetch_json, get_set_session, load_history,
)

log = logging.getLogger(__name__)

NAME = "set_short"

URL = "https://www.set.or.th/api/set/shortsales/statistics/list"


def _parse(payload: Any) -> tuple[str | None, list[dict]]:
    """SET short-sales response shape:
        {"tradingBeginDate": "...", "tradingEndDate": "...",
         "shortPositionDate": "...",
         "shortSales": [{"symbol": "...", "value": ..., "volume": ..., ...}, ...]}
    Returns (date, [{symbol, short_value, short_volume}])
    """
    if not isinstance(payload, dict):
        return None, []
    date = payload.get("tradingEndDate") or payload.get("shortPositionDate")
    rows = payload.get("shortSales") or []
    out: list[dict] = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        sym = r.get("symbol") or r.get("name")
        val = r.get("value") or r.get("shortValue") or r.get("totalValue")
        vol = r.get("volume") or r.get("shortVolume")
        if not sym or val is None:
            continue
        try:
            out.append({
                "symbol": str(sym).strip(),
                "short_value": float(val),
                "short_volume": float(vol) if vol is not None else None,
            })
        except (TypeError, ValueError):
            continue
    return date, out


def run() -> TrackerResult:
    log.info("[%s] starting", NAME)
    s = get_set_session()
    payload = fetch_json(s, URL)
    if payload is None:
        return TrackerResult(name=NAME, ok=False,
                             summary="(SET short-sales unreachable)",
                             error="endpoint failed")
    date, parsed = _parse(payload)
    if not parsed:
        return TrackerResult(
            name=NAME, ok=False,
            summary="(SET short-sales schema not recognized)",
            error="parse failed",
            data={"sample": str(payload)[:300]},
        )

    parsed.sort(key=lambda r: r["short_value"], reverse=True)
    top20 = parsed[:20]

    # diff vs yesterday
    history = load_history(NAME)
    prev = None
    if history:
        prev_rows = history[0].get("rows") or []
        prev = {r["symbol"]: r["short_value"] for r in prev_rows}

    movers: list[dict] = []
    if prev:
        for r in parsed[:50]:  # check top-50 for big movers
            p = prev.get(r["symbol"])
            if p and p > 0:
                pct = (r["short_value"] - p) / p * 100
                if pct >= 50 or pct <= -50:
                    movers.append({"symbol": r["symbol"],
                                   "short_value": r["short_value"],
                                   "pct_dod": round(pct, 1)})
        movers.sort(key=lambda x: abs(x["pct_dod"]), reverse=True)
        movers = movers[:10]

    today_date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    append_today(NAME, {"date": today_date, "rows": top20})

    top5_str = ", ".join(
        f"{r['symbol']} ฿{r['short_value']/1e6:.0f}M" for r in top20[:5]
    )
    if movers:
        mover_str = ", ".join(
            f"{m['symbol']} {'+'  if m['pct_dod']>=0 else ''}{m['pct_dod']}%"
            for m in movers[:5]
        )
        summary = f"Top short value: {top5_str}. Biggest DoD movers: {mover_str}"
    else:
        summary = f"Top short value: {top5_str}"

    return TrackerResult(
        name=NAME, ok=True, summary=summary,
        data={
            "date": today_date,
            "top20": top20,
            "biggest_movers_dod": movers,
        },
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    r = run()
    print(r)
