"""Common helpers for SET/TFEX/SETSmart trackers.

SET and TFEX sit behind Imperva/Incapsula WAF which blocks plain `requests`.
We use `curl_cffi` with Chrome TLS fingerprint impersonation and warm up
the session with a homepage GET so the Imperva cookies are set, then call
the real JSON APIs discovered from SET's Nuxt bundles.

Provides:
- get_set_session() / get_tfex_session() — cached warm sessions
- fetch_json() — one call with proper referer + JSON parsing
- SETSmartClient — minimal client using user-provided API key
- history file management in pulse/data/
- TrackerResult dataclass
"""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from curl_cffi import requests as cr

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "pulse" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class TrackerResult:
    """Standard tracker output."""
    name: str
    ok: bool
    summary: str  # short Thai/English string for the digest
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


# ---------- Imperva-bypass sessions ----------

_SET_SESSION: cr.Session | None = None
_TFEX_SESSION: cr.Session | None = None


def get_set_session() -> cr.Session:
    """Return a warmed curl_cffi session for www.set.or.th.

    Imperva requires a browser-like TLS fingerprint + a prior GET to the
    homepage so the incap_ses_* cookies are set before any /api/ call."""
    global _SET_SESSION
    if _SET_SESSION is not None:
        return _SET_SESSION
    s = cr.Session(impersonate="chrome120")
    try:
        r = s.get("https://www.set.or.th/en/home", timeout=20)
        log.info("SET session warmup: HTTP %s (cookies: %s)",
                 r.status_code, len(list(s.cookies.keys())))
    except Exception as e:
        log.warning("SET session warmup failed: %s", e)
    _SET_SESSION = s
    return s


def get_tfex_session() -> cr.Session:
    """Return a warmed curl_cffi session for www.tfex.co.th."""
    global _TFEX_SESSION
    if _TFEX_SESSION is not None:
        return _TFEX_SESSION
    s = cr.Session(impersonate="chrome120")
    try:
        r = s.get("https://www.tfex.co.th/en/home", timeout=20)
        log.info("TFEX session warmup: HTTP %s (cookies: %s)",
                 r.status_code, len(list(s.cookies.keys())))
    except Exception as e:
        log.warning("TFEX session warmup failed: %s", e)
    _TFEX_SESSION = s
    return s


def fetch_json(session: cr.Session, url: str, *,
               referer: str = "https://www.set.or.th/",
               params: dict | None = None,
               timeout: int = 15,
               retries: int = 2) -> Any | None:
    """GET `url` with proper Referer and parse JSON. Returns parsed obj or None."""
    headers = {"Referer": referer, "Accept": "application/json,text/plain,*/*"}
    last_err: str | None = None
    for attempt in range(retries + 1):
        try:
            r = session.get(url, headers=headers, params=params,
                            timeout=timeout)
            if r.status_code == 200:
                ct = r.headers.get("content-type", "")
                if "json" in ct.lower():
                    try:
                        return r.json()
                    except Exception as e:
                        last_err = f"json parse: {e}"
                else:
                    last_err = f"non-json content-type: {ct[:40]}"
            else:
                last_err = f"HTTP {r.status_code} (size {len(r.content)})"
            log.warning("fetch_json %s → %s", url, last_err)
        except Exception as e:
            last_err = str(e)
            log.warning("fetch_json %s → %s", url, e)
        if attempt < retries:
            time.sleep(2 ** attempt)
    return None


# ---------- SETSmart client ----------

class SETSmartClient:
    """Minimal SETSmart API client.

    Auth: `Authorization: <api_key>` header (raw key, no 'Bearer' prefix).
    The key's tier determines which endpoints return 200 vs 403.

    Known endpoints available on the basic tier (listed-company-controller):
      - /api/listed-company-api/eod-price-by-security-type
      - /api/listed-company-api/eod-price-by-symbol
      - /api/listed-company-api/financial-data-and-ratio
      - /api/listed-company-api/financial-data-and-ratio-by-symbol
    """
    BASE = "https://api.setsmart.com/api"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("SETSMART_API_KEY") or ""
        self.session = cr.Session(impersonate="chrome120")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def get(self, path: str, params: dict | None = None) -> Any | None:
        if not self.enabled:
            return None
        url = self.BASE + path
        headers = {"Authorization": self.api_key,
                   "Accept": "application/json"}
        try:
            r = self.session.get(url, headers=headers, params=params, timeout=20)
            if r.status_code == 200:
                return r.json()
            log.warning("SETSmart %s → HTTP %s %s",
                        path, r.status_code, r.text[:150])
        except Exception as e:
            log.warning("SETSmart %s → %s", path, e)
        return None

    # Convenience wrappers ----
    def eod_price_by_security_type(self, date: str,
                                    security_type: str = "S") -> Any | None:
        return self.get("/listed-company-api/eod-price-by-security-type",
                        {"date": date, "securityType": security_type})

    def eod_price_by_symbol(self, symbol: str, date: str) -> Any | None:
        return self.get("/listed-company-api/eod-price-by-symbol",
                        {"symbol": symbol, "date": date})

    def financials(self, symbol: str, period: str = "Q",
                   year: int | None = None) -> Any | None:
        params = {"symbol": symbol, "accountType": period}
        if year:
            params["year"] = year
        return self.get("/listed-company-api/financial-data-and-ratio-by-symbol",
                        params)


def load_history(name: str) -> list[dict]:
    """Load tracker history list (newest first)."""
    p = DATA_DIR / f"{name}.json"
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        log.warning("history %s corrupt: %s", name, e)
        return []


def save_history(name: str, history: list[dict], keep: int = 30) -> None:
    p = DATA_DIR / f"{name}.json"
    history = history[:keep]
    p.write_text(json.dumps(history, ensure_ascii=False, indent=2),
                 encoding="utf-8")


def append_today(name: str, today_record: dict, keep: int = 30) -> list[dict]:
    """Insert today's record at the front (replacing if same date) and persist."""
    h = load_history(name)
    today_date = today_record.get("date")
    h = [r for r in h if r.get("date") != today_date]
    h.insert(0, today_record)
    save_history(name, h, keep=keep)
    return h
