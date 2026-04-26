"""RSS feed list and fetchers for the Daily US Market & Economy Brief."""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Iterable

import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dtparser

log = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (compatible; MarketBriefBot/1.0; "
    "+https://github.com/nutbitzuist/daily-market-brief)"
)
HTTP_TIMEOUT = 15
HTTP_RETRIES = 2

FEEDS: list[tuple[str, str]] = [
    ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews"),
    ("Reuters US Markets", "https://feeds.reuters.com/reuters/USMarketsNews"),
    ("CNBC Top News", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"),
    ("CNBC Markets", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839135"),
    ("CNBC Economy", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258"),
    ("MarketWatch Top Stories", "https://feeds.content.dowjones.io/public/rss/mw_topstories"),
    ("MarketWatch Real-time Headlines", "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines"),
    ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
    ("Seeking Alpha Market News", "https://seekingalpha.com/market_currents.xml"),
    ("Financial Times Companies", "https://www.ft.com/companies?format=rss"),
    ("Bloomberg Markets (Google News)", "https://news.google.com/rss/search?q=site:bloomberg.com+markets&hl=en-US"),
    ("WSJ Markets (Google News)", "https://news.google.com/rss/search?q=site:wsj.com+markets&hl=en-US"),
    ("Federal Reserve Press Releases", "https://www.federalreserve.gov/feeds/press_all.xml"),
    ("US Treasury News", "https://home.treasury.gov/news/press-releases/feed"),
    ("BLS Latest", "https://www.bls.gov/feed/bls_latest.rss"),
    ("SEC Press Releases", "https://www.sec.gov/news/pressreleases.rss"),
]


@dataclass
class Article:
    title: str
    link: str
    published: datetime
    summary: str
    source_name: str
    content: str = ""
    paywalled: bool = False
    score: float = 0.0
    candidate_tickers: list[str] = field(default_factory=list)
    sector_hints: list[str] = field(default_factory=list)
    recency_hours: float = 0.0

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "link": self.link,
            "published": self.published.isoformat(),
            "summary": self.summary,
            "source_name": self.source_name,
            "content": self.content,
            "paywalled": self.paywalled,
            "score": self.score,
            "candidate_tickers": self.candidate_tickers,
            "sector_hints": self.sector_hints,
        }


def _http_get(url: str, **kwargs) -> requests.Response | None:
    headers = {"User-Agent": USER_AGENT, **kwargs.pop("headers", {})}
    last_exc = None
    for attempt in range(HTTP_RETRIES + 1):
        try:
            r = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT, **kwargs)
            if r.status_code == 200:
                return r
            log.debug("GET %s → %s", url, r.status_code)
        except requests.RequestException as e:
            last_exc = e
            log.debug("GET %s failed: %s", url, e)
        time.sleep(2 ** attempt)
    if last_exc:
        log.debug("giving up on %s: %s", url, last_exc)
    return None


def _parse_date(entry) -> datetime | None:
    for key in ("published", "updated", "created"):
        val = entry.get(key)
        if not val:
            continue
        try:
            dt = dtparser.parse(val)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except (ValueError, TypeError):
            continue
    if entry.get("published_parsed"):
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except Exception:  # pragma: no cover
            pass
    return None


def _extract_rss_content(entry) -> str:
    # Try content:encoded first, then summary/description
    parts: list[str] = []
    content_list = entry.get("content") or []
    for c in content_list:
        if isinstance(c, dict) and c.get("value"):
            parts.append(c["value"])
    if entry.get("summary"):
        parts.append(entry["summary"])
    if entry.get("description"):
        parts.append(entry["description"])
    raw = "\n".join(parts)
    if not raw:
        return ""
    # strip HTML
    soup = BeautifulSoup(raw, "html.parser")
    return soup.get_text(" ", strip=True)


def fetch_feed(source_name: str, url: str, cutoff: datetime) -> list[Article]:
    resp = _http_get(url)
    data = resp.content if resp else None
    parsed = feedparser.parse(data if data else url)
    out: list[Article] = []
    for entry in parsed.entries:
        pub = _parse_date(entry)
        if not pub or pub < cutoff:
            continue
        link = entry.get("link") or ""
        title = (entry.get("title") or "").strip()
        if not link or not title:
            continue
        summary = _extract_rss_content(entry)
        out.append(
            Article(
                title=title,
                link=link,
                published=pub,
                summary=summary,
                source_name=source_name,
            )
        )
    log.info("fetched %d entries from %s", len(out), source_name)
    return out


def fetch_all(hours: int = 24) -> list[Article]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    all_articles: list[Article] = []
    for name, url in FEEDS:
        try:
            all_articles.extend(fetch_feed(name, url, cutoff))
        except Exception as e:  # pragma: no cover
            log.warning("feed %s failed: %s", name, e)
    return all_articles


# ---------- enrichment fallback chain ----------

def _jina_reader(url: str) -> str:
    r = _http_get(f"https://r.jina.ai/{url}")
    if r and r.text and len(r.text) > 200:
        return r.text
    return ""


def _wayback(url: str) -> str:
    meta = _http_get(f"https://archive.org/wayback/available?url={url}")
    if not meta:
        return ""
    try:
        js = meta.json()
        snap = js.get("archived_snapshots", {}).get("closest", {})
        snap_url = snap.get("url")
        if not snap_url:
            return ""
    except Exception:
        return ""
    page = _http_get(snap_url)
    if not page:
        return ""
    soup = BeautifulSoup(page.content, "html.parser")
    for t in soup(["script", "style", "nav", "footer", "header"]):
        t.decompose()
    return soup.get_text(" ", strip=True)


PAYWALL_HOSTS = ("wsj.com", "bloomberg.com", "ft.com")


def enrich(article: Article, min_rss_chars: int = 500) -> Article:
    """Three-layer fallback: RSS → Jina → Wayback."""
    if len(article.summary) >= min_rss_chars:
        article.content = article.summary
        return article
    text = _jina_reader(article.link)
    if text and len(text) >= min_rss_chars:
        article.content = text
        return article
    text = _wayback(article.link)
    if text and len(text) >= min_rss_chars:
        article.content = text
        return article
    # hard paywall fallback — teaser only
    article.content = article.summary or article.title
    if any(h in article.link for h in PAYWALL_HOSTS):
        article.paywalled = True
    return article


def enrich_all(articles: Iterable[Article]) -> list[Article]:
    out = []
    for a in articles:
        try:
            out.append(enrich(a))
        except Exception as e:  # pragma: no cover
            log.warning("enrich failed for %s: %s", a.link, e)
            a.content = a.summary or a.title
            out.append(a)
    return out
