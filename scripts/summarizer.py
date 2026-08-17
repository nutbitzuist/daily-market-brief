"""OpenRouter LLM calls with fallback model chain + JSON validation."""
from __future__ import annotations

import json
import logging
import os
import re
import time
from typing import Any

import requests

log = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

DEFAULT_MODELS = [
    "google/gemini-3.7-flash",
    "deepseek/deepseek-v4-flash-0731",
    "x-ai/grok-4.3",
]
MODELS = [
    model.strip()
    for model in os.environ.get("OPENROUTER_MODELS", ",".join(DEFAULT_MODELS)).split(",")
    if model.strip()
]

REPO_URL = os.environ.get("REPO_URL", "https://github.com/USERNAME/REPO")

SYSTEM_PROMPT = (
    "You are the editor of a morning US news brief for Nut and her family group. "
    "Goal: select the 10 most important US stories from the candidate articles and "
    "explain them in Thai so a smart reader can digest the news quickly. This is a "
    "NEWS digest, not an investment-signal service. "
    "Prioritize: (1) Fed/inflation/jobs/yields/dollar; (2) market-moving earnings or "
    "mega-cap/AI-capex news; (3) White House/Congress/regulation/courts with national "
    "or market impact; (4) geopolitics involving the US, oil, defense, shipping, or "
    "supply chains; (5) consumer/housing/credit data; (6) major corporate/M&A stories. "
    "Do not over-rank small single-stock stories unless they reveal a broader theme. "
    "US SCOPE: reject domestic stories from other countries unless they materially affect "
    "US markets, companies, policy, supply chains, energy, or geopolitics. "
    "SOURCE DISCIPLINE: consequential factual claims need an official/primary source or "
    "corroboration shown in corroborating_sources. If only one secondary source supports a "
    "claim, state it cautiously and do not turn commentary into fact. "
    "EXCLUDE: crypto price chatter, minor management changes, lifestyle/fluff, local "
    "crime/weather unless national economic impact, and duplicated versions of the same story. "
    "STRICT SAFETY: never write direct trade instructions such as 'buy', 'sell', "
    "'short', 'avoid below X', 'overweight', or price-entry calls. Use 'watch' / "
    "'market implication' language only. Do not invent numbers, consensus, prices, "
    "flows, or positioning. If a number is not in the source, omit it. "
    "Return STRICT JSON array of exactly 10 objects, each with: rank (1-10 by real-world "
    "importance), title_th (Thai concise), summary_th (Thai 3-5 short lines: what "
    "happened, why it matters, likely market/economic implication if any, what to watch next), "
    "category (Macro/Fed | Earnings | M&A | Regulation | Geopolitics | Sector-specific | Commodity | Crypto), "
    "sentiment (bullish/bearish/neutral for US equities), impact (high/medium/low), "
    "time_horizon (immediate/short-term/long-term), sectors (array), tickers (array), "
    "key_numbers (array of sourced figures only), watch_next (1 line), source_name, url. "
    "Return ONLY the JSON array, no preamble."
)

VALID_CATEGORIES = {
    "Macro/Fed", "Earnings", "M&A", "Regulation",
    "Geopolitics", "Sector-specific", "Commodity", "Crypto",
}
VALID_SENTIMENT = {"bullish", "bearish", "neutral"}
VALID_IMPACT = {"high", "medium", "low"}
VALID_HORIZON = {"immediate", "short-term", "long-term"}
HORIZON_ALIASES = {
    "near-term": "short-term",
    "medium-term": "short-term",
    "mid-term": "short-term",
}

REQUIRED_FIELDS = [
    "rank", "title_th", "summary_th", "category", "sentiment", "impact",
    "time_horizon", "sectors", "tickers", "key_numbers", "watch_next",
    "source_name", "url",
]


def _headers() -> dict[str, str]:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    return {
        "Authorization": f"Bearer {key}",
        "HTTP-Referer": REPO_URL,
        "X-Title": "Daily Market Brief",
        "Content-Type": "application/json",
    }


def _call_model(model: str, messages: list[dict], max_tokens: int = 8000,
                temperature: float = 0.3) -> str | None:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    for attempt in range(3):
        try:
            r = requests.post(OPENROUTER_URL, headers=_headers(),
                              data=json.dumps(payload), timeout=120)
            if r.status_code == 200:
                data = r.json()
                return data["choices"][0]["message"]["content"]
            log.warning("OpenRouter %s → HTTP %s: %s", model, r.status_code, r.text[:300])
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt * 2)
                continue
            return None
        except requests.RequestException as e:
            log.warning("OpenRouter request error (%s): %s", model, e)
            time.sleep(2 ** attempt)
    return None


def _extract_json_array(text: str) -> Any:
    # strip code fences / preamble
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    # find first [ and last ]
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("no JSON array found")
    return json.loads(text[start:end + 1])


def _validate(items: Any) -> list[dict]:
    if not isinstance(items, list) or len(items) != 10:
        raise ValueError(f"expected list of 10, got {type(items).__name__} len={len(items) if isinstance(items, list) else 'n/a'}")
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            raise ValueError(f"item {i} not dict")
        for f in REQUIRED_FIELDS:
            if f not in it:
                raise ValueError(f"item {i} missing field {f}")
        if it["category"] not in VALID_CATEGORIES:
            raise ValueError(f"item {i} bad category {it['category']}")
        if it["sentiment"] not in VALID_SENTIMENT:
            raise ValueError(f"item {i} bad sentiment {it['sentiment']}")
        if it["impact"] not in VALID_IMPACT:
            raise ValueError(f"item {i} bad impact {it['impact']}")
        it["time_horizon"] = HORIZON_ALIASES.get(it["time_horizon"], it["time_horizon"])
        if it["time_horizon"] not in VALID_HORIZON:
            raise ValueError(f"item {i} bad time_horizon {it['time_horizon']}")
        for k in ("sectors", "tickers", "key_numbers"):
            it[k] = _coerce_str_list(it.get(k))
    return items


def _validate_selected_urls(items: list[dict], articles: list[dict]) -> list[dict]:
    """Reject invented URLs and duplicate story selections."""
    allowed = {str(a.get("link", "")).strip() for a in articles}
    selected: set[str] = set()
    for i, item in enumerate(items):
        url = str(item.get("url", "")).strip()
        if url not in allowed:
            raise ValueError(f"item {i} returned URL outside candidate set")
        if url in selected:
            raise ValueError(f"item {i} duplicated a selected story URL")
        selected.add(url)
    return items


def _build_user_prompt(articles: list[dict]) -> str:
    lines = [f"Here are {len(articles)} candidate financial news items from the past 24 hours. "
             "Analyze them and return the JSON array as specified.\n"]
    for i, a in enumerate(articles, 1):
        body = (a.get("content") or a.get("summary") or "")[:3000]
        lines.append(
            f"--- ARTICLE {i} ---\n"
            f"source_name: {a['source_name']}\n"
            f"url: {a['link']}\n"
            f"published: {a['published']}\n"
            f"paywalled: {a.get('paywalled', False)}\n"
            f"candidate_tickers: {a.get('candidate_tickers', [])}\n"
            f"sector_hints: {a.get('sector_hints', [])}\n"
            f"corroborating_sources: {a.get('corroborating_sources', [])}\n"
            f"title: {a['title']}\n"
            f"content:\n{body}\n"
        )
    return "\n".join(lines)


def summarize_articles(articles: list[dict]) -> tuple[list[dict], str]:
    """Returns (items, model_used). Tries models in order until valid JSON."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(articles)},
    ]
    last_err = None
    for model in MODELS:
        log.info("summarize_articles: trying model %s", model)
        out = _call_model(model, messages)
        if not out:
            continue
        try:
            items = _validate(_extract_json_array(out))
            items = _validate_selected_urls(items, articles)
            return items, model
        except (ValueError, json.JSONDecodeError) as e:
            last_err = e
            log.warning("model %s failed validation: %s", model, e)
            continue
    log.error("all OpenRouter models failed for US brief; using deterministic fallback; last err: %s", last_err)
    return _fallback_us_items(articles), "deterministic-fallback/openrouter-unavailable"


EXEC_SYSTEM_PROMPT = (
    "You are writing the top paragraph for a morning US news digest in Thai. Given "
    "10 selected news items, write 3–4 concise lines: the biggest overnight driver, "
    "the key number/event if sourced, why it matters for markets/economy/geopolitics, "
    "and what readers should watch today. No direct investment advice, no buy/sell/short, "
    "no invented numbers, no heading, no preamble. Return ONLY Thai text."
)


AI_NEWS_SYSTEM_PROMPT = (
    "You are the editor of a morning AI news digest for Nut and her family group. "
    "Select the 5 most important AI developments from the candidate list and explain "
    "them in Thai. Optimize for breadth and real significance, not one company's changelog. "
    "Required coverage preference: include different buckets when available — frontier "
    "labs/models (OpenAI, Anthropic, Google, Meta, xAI, Mistral, DeepSeek/Qwen), AI "
    "infrastructure/chips (NVIDIA, AMD, TSMC, Broadcom, data centers/power), enterprise "
    "AI/hyperscalers, agents/tools, regulation/legal, open-source models, funding/M&A. "
    "DIVERSITY RULE: no more than 2 items about the same company, and never include "
    "multiple minor platform/admin feature updates from the same company unless each is "
    "clearly a top-5 industry story. Prefer one synthesis item over duplicates. "
    "EXCLUDE: small startup funding <$50M, indie tools, routine developer docs, generic "
    "opinion pieces, crypto, recycled announcements, and posts with no concrete new fact. "
    "Do not invent revenue, growth, users, benchmarks, or competitive effects not present "
    "in the source. If a number is not sourced, omit it. "
    "Prefer official announcements and independently corroborated reports. Treat a single "
    "secondary-source interpretation cautiously. "
    "Return STRICT JSON array of exactly 5 objects, each with: title_th, summary_th "
    "(Thai 3-4 short lines: what happened, why it matters, who/what is affected), url, "
    "source, why_it_matters (1 sharp Thai line). Return ONLY the JSON array, no preamble."
)

AI_REQUIRED_FIELDS = ["title_th", "summary_th", "url", "source", "why_it_matters"]


def _validate_ai(items: Any) -> list[dict]:
    if not isinstance(items, list) or len(items) != 5:
        raise ValueError(
            f"expected list of 5, got {type(items).__name__} "
            f"len={len(items) if isinstance(items, list) else 'n/a'}"
        )
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            raise ValueError(f"item {i} not dict")
        for f in AI_REQUIRED_FIELDS:
            if f not in it or not isinstance(it[f], str):
                raise ValueError(f"item {i} missing/invalid field {f}")
    return items


def _build_ai_user_prompt(articles: list[dict]) -> str:
    lines = [f"Here are {len(articles)} candidate AI news items from the past 24 hours. "
             "Select ONLY the 5 most important, diverse, non-duplicate AI stories. "
             "Analyze and return the JSON array as specified.\n"]
    for i, a in enumerate(articles, 1):
        body = (a.get("content") or a.get("summary") or "")[:3000]
        lines.append(
            f"--- ARTICLE {i} ---\n"
            f"source: {a['source_name']}\n"
            f"url: {a['link']}\n"
            f"published: {a['published']}\n"
            f"corroborating_sources: {a.get('corroborating_sources', [])}\n"
            f"title: {a['title']}\n"
            f"content:\n{body}\n"
        )
    return "\n".join(lines)


def summarize_ai_news(articles: list[dict]) -> tuple[list[dict], str]:
    messages = [
        {"role": "system", "content": AI_NEWS_SYSTEM_PROMPT},
        {"role": "user", "content": _build_ai_user_prompt(articles)},
    ]
    last_err = None
    for model in MODELS:
        log.info("summarize_ai_news: trying model %s", model)
        out = _call_model(model, messages, max_tokens=4000, temperature=0.3)
        if not out:
            continue
        try:
            items = _validate_ai(_extract_json_array(out))
            items = _validate_selected_urls(items, articles)
            return items, model
        except (ValueError, json.JSONDecodeError) as e:
            last_err = e
            log.warning("model %s failed AI validation: %s", model, e)
            continue
    log.error("all OpenRouter models failed for AI news; using deterministic fallback; last err: %s", last_err)
    return _fallback_ai_items(articles), "deterministic-fallback/openrouter-unavailable"


TH_NEWS_SYSTEM_PROMPT = (
    "You are the editor of a morning Thailand news digest for Nut and her family group. "
    "Select the 10 most important Thailand stories and explain them in Thai with a "
    "business/markets lens. This is a NEWS digest, not a trading instruction note. "
    "SOURCE DISCIPLINE: prioritize BoT/SET/MoF/SEC and other primary sources for official "
    "figures. Consequential claims from secondary media need corroboration shown in "
    "corroborating_sources; otherwise use cautious attribution. "
    "Prioritize: (1) government/cabinet/fiscal policy; (2) Bank of Thailand/กนง./THB/rates; "
    "(3) SET/SEC/capital-market rules, flows, short selling, NVDR; (4) material SET-listed "
    "company news; (5) GDP/CPI/exports/tourism/consumption; (6) politics/geopolitics that "
    "affects Thai economy or markets; (7) major social/economic policy affecting households. "
    "Keep breadth: do not fill the brief with repetitive broker index calls or generic SET "
    "sentiment pieces if there are concrete policy/company/macro stories available. "
    "EXCLUDE: crypto/Bitcoin retail stories, lottery/celebrity/lifestyle fluff, routine filings, "
    "generic event-calendar notices, minor management changes, agriculture/weather unless "
    "national economic impact is explicit. "
    "STRICT SAFETY: never write direct trade instructions such as 'ซื้อ', 'ขาย', 'short', "
    "'overweight', 'underweight', or target entry levels. Use 'จับตา', 'ผลกระทบ', and "
    "'ประเด็นที่ต้องดูต่อ' language. Do not invent numbers, fund flows, prices, or affected "
    "tickers. If not sourced, omit. "
    "Return STRICT JSON array of exactly 10 objects, each with: rank (1-10 by importance), "
    "title_th, summary_th (Thai 3-5 short lines: what happened, why it matters, business/SET/THB "
    "impact if any, what to watch next), category (นโยบายรัฐ-การคลัง | นโยบายการเงิน-ธปท. "
    "| SET/หุ้นไทย | เศรษฐกิจมหภาค | บริษัท-M&A | ธนาคาร-การเงิน | ค่าเงิน-FX | "
    "กฎระเบียบ | ต่างประเทศกระทบไทย), sentiment (bullish/bearish/neutral for SET), "
    "impact (high/medium/low), time_horizon (immediate/short-term/long-term), sectors, "
    "tickers, key_numbers (sourced figures only), watch_next (1 line), source_name, url. "
    "Return ONLY the JSON array, no preamble."
)

TH_REQUIRED_FIELDS = [
    "rank", "title_th", "summary_th", "category", "sentiment", "impact",
    "time_horizon", "sectors", "tickers", "key_numbers", "watch_next",
    "source_name", "url",
]
TH_VALID_SENTIMENT = {"bullish", "bearish", "neutral"}
TH_VALID_IMPACT = {"high", "medium", "low"}
TH_VALID_HORIZON = {"immediate", "short-term", "long-term"}
TH_BLOCK_TERMS = (
    "bitcoin", "btc", "crypto", "cryptocurrency", "digital asset",
    "บิตคอยน์", "คริปโต", "สินทรัพย์ดิจิทัล",
    "oppday", "opportunity day", "treasury stock", "หุ้นซื้อคืน",
    "จำหน่ายหุ้นซื้อคืน",
)


def _coerce_str_list(v: Any) -> list[str]:
    """Coerce LLM output for list fields into list[str].
    Accepts None, str, dict, or list of mixed types — never raises."""
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v if x not in (None, "")]
    if isinstance(v, str):
        s = v.strip()
        return [s] if s else []
    if isinstance(v, dict):
        return [f"{k}: {val}" for k, val in v.items()]
    return [str(v)]

def _clean_text(v: Any, limit: int = 600) -> str:
    text = re.sub(r"\s+", " ", str(v or "")).strip()
    return text[:limit].rstrip()


def _article_url(a: dict) -> str:
    return str(a.get("link") or a.get("url") or "")


def _article_source(a: dict) -> str:
    return str(a.get("source_name") or a.get("source") or "Unknown")


def _article_title(a: dict) -> str:
    return _clean_text(a.get("title") or a.get("title_th") or "Untitled", 180)


def _article_body(a: dict) -> str:
    body = a.get("content") or a.get("summary") or a.get("description") or ""
    return _clean_text(body, 420)


def _pad_articles(articles: list[dict], n: int) -> list[dict]:
    usable = [a for a in articles if isinstance(a, dict)]
    if not usable:
        usable = [{
            "title": "Market data feed returned no usable article",
            "summary": "The scheduled job could not fetch or summarize enough inputs. Check RSS/API sources and OpenRouter credentials.",
            "source_name": "Daily Market Brief fallback",
            "link": REPO_URL,
        }]
    out = usable[:n]
    while len(out) < n:
        out.append(out[-1])
    return out


def _fallback_us_items(articles: list[dict]) -> list[dict]:
    """Last-resort brief: valid schema from fetched articles, no LLM dependency."""
    items: list[dict] = []
    for rank, a in enumerate(_pad_articles(articles, 10), 1):
        title = _article_title(a)
        body = _article_body(a)
        tickers = _coerce_str_list(a.get("candidate_tickers"))[:5]
        sectors = _coerce_str_list(a.get("sector_hints"))[:3]
        source = _article_source(a)
        items.append({
            "rank": rank,
            "title_th": title,
            "summary_th": (
                f"Fallback brief จาก {source}: {title}\n"
                f"ประเด็นจากแหล่งข่าว: {body or 'ไม่มีเนื้อหาเพิ่มเติมจาก RSS'}\n"
                "อ่านเป็น market-monitor item ก่อนเปิดพอร์ต: ใช้ headline/source เป็น trigger แล้วรอ desk review เพื่อสรุปผลต่อ sector และ risk."
            ),
            "category": "Sector-specific" if tickers or sectors else "Macro/Fed",
            "sentiment": "neutral",
            "impact": "medium" if rank <= 3 else "low",
            "time_horizon": "immediate",
            "sectors": sectors,
            "tickers": tickers,
            "key_numbers": _coerce_str_list(a.get("key_numbers"))[:5] or ["OpenRouter unavailable; deterministic fallback used"],
            "watch_next": "ตรวจสอบต้นทางและอัปเดต OpenRouter secret; fallback นี้ป้องกัน workflow ล้มเหลวแต่ไม่แทน desk analysis เต็มรูปแบบ",
            "source_name": source,
            "url": _article_url(a),
        })
    return _validate(items)


def _fallback_ai_items(articles: list[dict]) -> list[dict]:
    items: list[dict] = []
    for rank, a in enumerate(_pad_articles(articles, 5), 1):
        title = _article_title(a)
        body = _article_body(a)
        source = _article_source(a)
        items.append({
            "title_th": title,
            "summary_th": f"Fallback AI brief #{rank}: {body or title}",
            "url": _article_url(a),
            "source": source,
            "why_it_matters": "OpenRouter unavailable; surfaced source headline so the scheduled alert still ships.",
        })
    return _validate_ai(items)


def _fallback_th_items(articles: list[dict]) -> list[dict]:
    """Last-resort Thailand brief: valid schema from fetched articles, no LLM dependency."""
    items: list[dict] = []
    for rank, a in enumerate(_pad_articles(articles, 10), 1):
        title = _article_title(a)
        body = _article_body(a)
        source = _article_source(a)
        text = f"{title} {body}".upper()
        tickers = sorted(set(re.findall(r"\b[A-Z]{2,6}\b", text)))[:5]
        items.append({
            "rank": rank,
            "title_th": title,
            "summary_th": (
                f"Fallback brief จาก {source}: {title}\n"
                f"ประเด็นจากแหล่งข่าว: {body or 'ไม่มีเนื้อหาเพิ่มเติมจาก RSS'}\n"
                "ใช้เป็น early-warning สำหรับ SET/THB/sector watch; ต้องตามด้วย desk review เมื่อโมเดลกลับมาใช้งานได้."
            ),
            "category": "SET/หุ้นไทย" if tickers else "เศรษฐกิจมหภาค",
            "sentiment": "neutral",
            "impact": "medium" if rank <= 3 else "low",
            "time_horizon": "immediate",
            "sectors": [],
            "tickers": tickers,
            "key_numbers": ["OpenRouter unavailable; deterministic fallback used"],
            "watch_next": "ตรวจสอบ OpenRouter secret และต้นทางข่าว; fallback นี้ทำให้ workflow ส่ง brief ได้แม้ LLM ล่ม",
            "source_name": source,
            "url": _article_url(a),
        })
    return _validate_th(items)


def _validate_th(items: Any) -> list[dict]:
    if not isinstance(items, list) or len(items) != 10:
        raise ValueError(
            f"expected list of 10, got {type(items).__name__} "
            f"len={len(items) if isinstance(items, list) else 'n/a'}"
        )
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            raise ValueError(f"item {i} not dict")
        for f in TH_REQUIRED_FIELDS:
            if f not in it:
                raise ValueError(f"item {i} missing field {f}")
        if it["sentiment"] not in TH_VALID_SENTIMENT:
            raise ValueError(f"item {i} bad sentiment {it['sentiment']}")
        if it["impact"] not in TH_VALID_IMPACT:
            raise ValueError(f"item {i} bad impact {it['impact']}")
        it["time_horizon"] = HORIZON_ALIASES.get(it["time_horizon"], it["time_horizon"])
        if it["time_horizon"] not in TH_VALID_HORIZON:
            raise ValueError(f"item {i} bad time_horizon {it['time_horizon']}")
        searchable = (
            f"{it.get('title_th', '')}\n{it.get('summary_th', '')}\n"
            f"{it.get('source_name', '')}"
        ).lower()
        if any(term in searchable for term in TH_BLOCK_TERMS):
            raise ValueError(f"item {i} contains blocked Thailand Brief topic")
        for k in ("sectors", "tickers", "key_numbers"):
            it[k] = _coerce_str_list(it.get(k))
    return items


def summarize_th_news(articles: list[dict]) -> tuple[list[dict], str]:
    user_prompt = (
        f"Here are {len(articles)} candidate Thailand news items "
        "from the past 24 hours. Select ONLY the 10 most important, diverse, "
        "non-duplicate stories for a morning Thailand digest with business/market context. "
        "Reject BTC/crypto, generic SET calendar notices, routine filings, and repetitive "
        "broker index calls when better concrete news exists. Analyze and return the JSON "
        "array as specified.\n\n"
    )
    for i, a in enumerate(articles, 1):
        body = (a.get("content") or a.get("summary") or "")[:3000]
        user_prompt += (
            f"--- ARTICLE {i} ---\n"
            f"source_name: {a['source_name']}\n"
            f"url: {a['link']}\n"
            f"published: {a['published']}\n"
            f"corroborating_sources: {a.get('corroborating_sources', [])}\n"
            f"title: {a['title']}\n"
            f"content:\n{body}\n\n"
        )
    messages = [
        {"role": "system", "content": TH_NEWS_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    last_err = None
    for model in MODELS:
        log.info("summarize_th_news: trying model %s", model)
        out = _call_model(model, messages, max_tokens=8000, temperature=0.3)
        if not out:
            continue
        try:
            items = _validate_th(_extract_json_array(out))
            items = _validate_selected_urls(items, articles)
            return items, model
        except (ValueError, json.JSONDecodeError) as e:
            last_err = e
            log.warning("model %s failed TH validation: %s", model, e)
            continue
    log.error("all OpenRouter models failed for Thailand brief; using deterministic fallback; last err: %s", last_err)
    return _fallback_th_items(articles), "deterministic-fallback/openrouter-unavailable"


TH_EXEC_SYSTEM_PROMPT = (
    "You are writing the top paragraph for a morning Thailand news digest in Thai. "
    "Given 10 selected news items, write 3–4 concise lines: the biggest Thailand driver, "
    "the key number/event if sourced, why it matters for the economy/SET/THB/households, "
    "and what readers should watch today. No buy/sell/overweight/underweight calls, no "
    "invented numbers, no heading, no preamble. Return ONLY Thai text."
)


PULSE_SYSTEM_PROMPT = (
    "You are a top-1% Thai equities sales-trading analyst (CLSA / JPMorgan / "
    "Maybank Bangkok desk voice) writing the 6pm post-close positioning note "
    "for buy-side PMs. You are given today's structured Thai market data: "
    "(1) official SET investor-type net flows, "
    "(2) SET short-sale rankings & DoD movers, "
    "(3) NVDR top net buy/sell names. "
    "Write a Thai commentary, 6–9 lines, in this exact order: "
    "(a) one-line headline read on today's flow regime "
    "(foreign buying/selling, retail behaviour, short-side conviction); "
    "(b) the single most actionable observation across the 3 datasets — "
    "name the specific tickers and the trade implication; "
    "(c) sector rotation read-through (which sectors saw real institutional "
    "money, which had only short/retail/NVDR); "
    "(d) one explicit positioning view for tomorrow's open (overweight/underweight/"
    "fade/chase + named tickers); "
    "(e) one risk to the view. "
    "Numbers-first. Reference exact ฿M figures and DoD%. No hedging, no "
    "'may/could/might', no disclaimers, no boilerplate, no headings. "
    "If a dataset is missing/unavailable, note it briefly and work with what's "
    "available. Return ONLY the Thai commentary text."
)


def th_market_pulse_commentary(pulse_data: dict) -> tuple[str, str]:
    """Generate the institutional commentary for the daily Thai market pulse.

    pulse_data is a dict like:
        {"set_investor_type": {...}, "set_short": {...},
         "set_nvdr": {...}}
    """
    user_prompt = (
        "Today's Thai market data (post-close):\n\n"
        + json.dumps(pulse_data, ensure_ascii=False, indent=2)
        + "\n\nWrite the 6–9 line institutional commentary now."
    )
    messages = [
        {"role": "system", "content": PULSE_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    for model in MODELS:
        log.info("th_market_pulse_commentary: trying %s", model)
        out = _call_model(model, messages, max_tokens=1200, temperature=0.4)
        if out and out.strip():
            txt = out.strip()
            txt = re.sub(r"^```.*?\n", "", txt)
            txt = re.sub(r"\n```$", "", txt)
            return txt.strip(), model
    log.error("all OpenRouter models failed for Thai market pulse; using deterministic fallback")
    return (
        "OpenRouter unavailable; ส่ง fallback pulse จากข้อมูลดิบแทนเพื่อไม่ให้ workflow ล้มเหลว. "
        "ตรวจ SET investor type, short-sale และ NVDR blocks ในไฟล์เต็มก่อนตัดสินใจ.",
        "deterministic-fallback/openrouter-unavailable",
    )


def th_executive_summary(items: list[dict]) -> tuple[str, str]:
    messages = [
        {"role": "system", "content": TH_EXEC_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(items, ensure_ascii=False)},
    ]
    for model in MODELS:
        log.info("th_executive_summary: trying %s", model)
        out = _call_model(model, messages, max_tokens=800, temperature=0.4)
        if out and out.strip():
            txt = out.strip()
            txt = re.sub(r"^```.*?\n", "", txt)
            txt = re.sub(r"\n```$", "", txt)
            return txt.strip(), model
    log.error("all OpenRouter models failed for Thailand executive summary; using deterministic fallback")
    lead = items[0].get("title_th", "Thailand market monitor") if items else "Thailand market monitor"
    return f"Fallback summary: {lead}. OpenRouter unavailable; top headlines are still shipped from source data for monitoring.", "deterministic-fallback/openrouter-unavailable"


def executive_summary(items: list[dict]) -> tuple[str, str]:
    messages = [
        {"role": "system", "content": EXEC_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(items, ensure_ascii=False)},
    ]
    for model in MODELS:
        log.info("executive_summary: trying %s", model)
        out = _call_model(model, messages, max_tokens=800, temperature=0.4)
        if out and out.strip():
            txt = out.strip()
            txt = re.sub(r"^```.*?\n", "", txt)
            txt = re.sub(r"\n```$", "", txt)
            return txt.strip(), model
    log.error("all OpenRouter models failed for US executive summary; using deterministic fallback")
    lead = items[0].get("title_th", "US market monitor") if items else "US market monitor"
    return f"Fallback summary: {lead}. OpenRouter unavailable; top headlines are still shipped from source data for monitoring.", "deterministic-fallback/openrouter-unavailable"
