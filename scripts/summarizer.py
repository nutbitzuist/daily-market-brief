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

MODELS = [
    "google/gemini-2.5-flash-lite",
    "openai/gpt-oss-120b:free",
    "google/gemma-3-27b-it:free",
    "qwen/qwen3-coder:free",
]

REPO_URL = os.environ.get("REPO_URL", "https://github.com/USERNAME/REPO")

SYSTEM_PROMPT = (
    "You are a senior sell-side research analyst writing a personal morning brief "
    "for an investor. Return STRICT JSON array of exactly 10 objects, each with: "
    "rank (1-10 by market impact), title_th (Thai concise), summary_th "
    "(Thai 4-6 lines covering what happened, why it matters, likely market reaction), "
    "category (Macro/Fed | Earnings | M&A | Regulation | Geopolitics | Sector-specific | Commodity | Crypto), "
    "sentiment (bullish/bearish/neutral for US equities), impact (high/medium/low), "
    "time_horizon (immediate/short-term/long-term), sectors (array of GICS sectors), "
    "tickers (array of primary tickers, empty if pure macro), key_numbers (array of "
    "important figures with context like 'CPI 3.2% vs 3.1% est'), watch_next (1 line "
    "on what to monitor), source_name, url. Be direct and analytical — no hedging "
    "language, no disclaimers. Return ONLY the JSON array, no preamble."
)

VALID_CATEGORIES = {
    "Macro/Fed", "Earnings", "M&A", "Regulation",
    "Geopolitics", "Sector-specific", "Commodity", "Crypto",
}
VALID_SENTIMENT = {"bullish", "bearish", "neutral"}
VALID_IMPACT = {"high", "medium", "low"}
VALID_HORIZON = {"immediate", "short-term", "long-term"}

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
        if it["time_horizon"] not in VALID_HORIZON:
            raise ValueError(f"item {i} bad time_horizon {it['time_horizon']}")
        if not isinstance(it["sectors"], list):
            raise ValueError(f"item {i} sectors not list")
        if not isinstance(it["tickers"], list):
            raise ValueError(f"item {i} tickers not list")
        if not isinstance(it["key_numbers"], list):
            raise ValueError(f"item {i} key_numbers not list")
    return items


def _build_user_prompt(articles: list[dict]) -> str:
    lines = ["Here are 10 top financial news items from the past 24 hours. "
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
            return items, model
        except (ValueError, json.JSONDecodeError) as e:
            last_err = e
            log.warning("model %s failed validation: %s", model, e)
            continue
    raise RuntimeError(f"all models failed; last err: {last_err}")


EXEC_SYSTEM_PROMPT = (
    "You are a senior sell-side research analyst. Given a JSON array of 10 news items, "
    "write a 4–5 line Thai executive summary that synthesizes the day's big picture "
    "for a US equities investor. Be direct and analytical, no disclaimers, no hedging. "
    "Return ONLY the Thai text — no preamble, no bullet points, no JSON."
)


AI_NEWS_SYSTEM_PROMPT = (
    "You are a senior AI research analyst writing a personal daily AI news brief. "
    "Return STRICT JSON array of exactly 5 objects, each with: title_th (Thai concise "
    "title), summary_th (Thai 3-5 line summary), url, source, why_it_matters (1 line "
    "in Thai on why this matters for AI builders/investors). Be direct and analytical, "
    "no hedging, no disclaimers. Return ONLY the JSON array, no preamble."
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
    lines = ["Here are 5 top AI news items from the past 24 hours. "
             "Analyze and return the JSON array as specified.\n"]
    for i, a in enumerate(articles, 1):
        body = (a.get("content") or a.get("summary") or "")[:3000]
        lines.append(
            f"--- ARTICLE {i} ---\n"
            f"source: {a['source_name']}\n"
            f"url: {a['link']}\n"
            f"published: {a['published']}\n"
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
            return items, model
        except (ValueError, json.JSONDecodeError) as e:
            last_err = e
            log.warning("model %s failed AI validation: %s", model, e)
            continue
    raise RuntimeError(f"all models failed for ai_news; last err: {last_err}")


TH_NEWS_SYSTEM_PROMPT = (
    "You are a senior Thai equities and macro analyst writing a personal morning brief. "
    "Return STRICT JSON array of exactly 10 objects, each with: rank (1-10 by market "
    "impact for Thai investors), title_th (Thai concise), summary_th (Thai 4-6 lines "
    "covering what happened, why it matters, likely SET/THB reaction), category "
    "(นโยบายการเงิน | SET/หุ้นไทย | เศรษฐกิจมหภาค | บริษัท-M&A | ธนาคาร-การเงิน | "
    "สินค้าโภคภัณฑ์ | ค่าเงิน-FX | กฎระเบียบ | ต่างประเทศกระทบไทย), sentiment "
    "(bullish/bearish/neutral for Thai equities), impact (high/medium/low), "
    "time_horizon (immediate/short-term/long-term), sectors (array of Thai sector names "
    "in Thai e.g. ['ธนาคาร','พลังงาน','สื่อสาร','อสังหาริมทรัพย์','อาหาร']), tickers "
    "(array of SET tickers like PTT, AOT, KBANK, ADVANC — empty if pure macro), "
    "key_numbers (array with context like 'GDP Q1 +2.3% vs +2.5% est'), watch_next "
    "(1 line on what to monitor), source_name, url. Be direct and analytical — no "
    "hedging, no disclaimers. Return ONLY the JSON array, no preamble."
)

TH_REQUIRED_FIELDS = [
    "rank", "title_th", "summary_th", "category", "sentiment", "impact",
    "time_horizon", "sectors", "tickers", "key_numbers", "watch_next",
    "source_name", "url",
]
TH_VALID_SENTIMENT = {"bullish", "bearish", "neutral"}
TH_VALID_IMPACT = {"high", "medium", "low"}
TH_VALID_HORIZON = {"immediate", "short-term", "long-term"}


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
        if it["time_horizon"] not in TH_VALID_HORIZON:
            raise ValueError(f"item {i} bad time_horizon {it['time_horizon']}")
        for k in ("sectors", "tickers", "key_numbers"):
            if not isinstance(it[k], list):
                raise ValueError(f"item {i} {k} not list")
    return items


def summarize_th_news(articles: list[dict]) -> tuple[list[dict], str]:
    user_prompt = "Here are 10 top Thai business/economy news items from the past 24 hours. " \
                  "Analyze and return the JSON array as specified.\n\n"
    for i, a in enumerate(articles, 1):
        body = (a.get("content") or a.get("summary") or "")[:3000]
        user_prompt += (
            f"--- ARTICLE {i} ---\n"
            f"source_name: {a['source_name']}\n"
            f"url: {a['link']}\n"
            f"published: {a['published']}\n"
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
            return items, model
        except (ValueError, json.JSONDecodeError) as e:
            last_err = e
            log.warning("model %s failed TH validation: %s", model, e)
            continue
    raise RuntimeError(f"all models failed for th_news; last err: {last_err}")


TH_EXEC_SYSTEM_PROMPT = (
    "You are a senior Thai equities & macro analyst. Given a JSON array of 10 Thai "
    "business/economy news items, write a 4–5 line Thai executive summary that "
    "synthesizes the day's big picture for a Thai investor (SET, THB, BoT policy, "
    "key sectors). Be direct and analytical, no hedging, no disclaimers. "
    "Return ONLY the Thai text — no preamble, no bullet points, no JSON."
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
    raise RuntimeError("all models failed for th_executive_summary")


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
    raise RuntimeError("all models failed for executive_summary")
