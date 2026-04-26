"""Dedupe, score, ticker/sector tagging."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Iterable

from scripts.sources import Article

TIER1 = [
    "fed", "fomc", "rate cut", "rate hike", "powell", "cpi", "pce", "nfp",
    "jobs report", "gdp", "recession", "earnings", "guidance", "s&p 500",
    "nasdaq", "dow", "tariff", "treasury yield",
]
TIER2 = [
    "inflation", "unemployment", "retail sales", "pmi", "ism",
    "consumer confidence", "ipo", "merger", "acquisition", "sec",
    "antitrust", "buyback", "dividend",
]
TIER3 = [
    "opec", "oil", "gold", "bond", "tech", "financials", "energy",
    "healthcare", "consumer", "industrials", "utilities", "materials",
    "real estate", "communication services",
]

TICKER_RE = re.compile(r"\$([A-Z]{1,5})\b")

SECTOR_KEYWORDS = {
    "Tech": ["chip", "semiconductor", "software", "cloud", "ai", "artificial intelligence", "data center"],
    "Financials": ["bank", "insurance", "fintech", "lending", "hedge fund", "private equity"],
    "Energy": ["oil", "gas", "opec", "crude", "refinery", "lng", "pipeline"],
    "Healthcare": ["fda", "drug", "pharma", "biotech", "clinical trial", "medicare"],
    "Consumer": ["retail", "e-commerce", "restaurant", "apparel", "consumer spending"],
    "Industrials": ["airline", "defense", "machinery", "logistics", "aerospace", "shipping"],
    "Utilities": ["utility", "electric grid", "power plant"],
    "Materials": ["mining", "steel", "copper", "lithium", "chemicals"],
    "Real Estate": ["reit", "housing", "mortgage", "home sales", "commercial real estate"],
    "Communication Services": ["telecom", "streaming", "media", "advertising"],
}


def extract_tickers(text: str) -> list[str]:
    found = TICKER_RE.findall(text or "")
    out: list[str] = []
    seen = set()
    for t in found:
        tu = t.upper()
        if tu not in seen:
            seen.add(tu)
            out.append(tu)
    return out


def detect_sectors(text: str) -> list[str]:
    low = (text or "").lower()
    hits: list[str] = []
    for sector, kws in SECTOR_KEYWORDS.items():
        if any(kw in low for kw in kws):
            hits.append(sector)
    return hits


def _keyword_score(text: str) -> float:
    low = text.lower()
    score = 0.0
    for kw in TIER1:
        if kw in low:
            score += 3
    for kw in TIER2:
        if kw in low:
            score += 2
    for kw in TIER3:
        if kw in low:
            score += 1
    if TICKER_RE.search(text):
        score += 1
    return score


def _recency_bonus(pub: datetime, now: datetime) -> float:
    hours = (now - pub).total_seconds() / 3600
    if hours <= 6:
        return 2
    if hours <= 12:
        return 1
    return 0


def score_articles(articles: Iterable[Article]) -> list[Article]:
    now = datetime.now(timezone.utc)
    out = []
    for a in articles:
        text = f"{a.title}\n{a.summary}"
        a.score = _keyword_score(text) + _recency_bonus(a.published, now)
        a.recency_hours = (now - a.published).total_seconds() / 3600
        a.candidate_tickers = extract_tickers(text)
        a.sector_hints = detect_sectors(text)
        out.append(a)
    return out


def _normalize_title(t: str) -> str:
    return re.sub(r"\s+", " ", t.lower().strip())


def dedupe(articles: list[Article], ratio_threshold: float = 0.8) -> list[Article]:
    seen_urls: set[str] = set()
    kept: list[Article] = []
    for a in sorted(articles, key=lambda x: x.score, reverse=True):
        if a.link in seen_urls:
            continue
        norm = _normalize_title(a.title)
        is_dup = False
        for k in kept:
            if SequenceMatcher(None, norm, _normalize_title(k.title)).ratio() > ratio_threshold:
                is_dup = True
                break
        if is_dup:
            continue
        seen_urls.add(a.link)
        kept.append(a)
    return kept


def top_n_with_diversity(articles: list[Article], n: int = 10, max_per_source: int = 2) -> list[Article]:
    picked: list[Article] = []
    counts: dict[str, int] = {}
    for a in sorted(articles, key=lambda x: x.score, reverse=True):
        if counts.get(a.source_name, 0) >= max_per_source:
            continue
        picked.append(a)
        counts[a.source_name] = counts.get(a.source_name, 0) + 1
        if len(picked) >= n:
            break
    # if we somehow didn't reach n because of diversity cap, relax
    if len(picked) < n:
        for a in sorted(articles, key=lambda x: x.score, reverse=True):
            if a in picked:
                continue
            picked.append(a)
            if len(picked) >= n:
                break
    return picked
