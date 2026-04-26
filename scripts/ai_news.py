"""Daily AI News brief — runs at 04:00 Asia/Bangkok = 21:00 UTC.

10 RSS sources + Hacker News Algolia API → top 5 by AI-keyword relevance + recency
→ 3-layer enrichment fallback (RSS / Jina Reader / Wayback)
→ Gemini-2.5-flash-lite (with free-model fallback chain)
→ articles/{YYYY-MM-DD}.md + articles/latest.md
→ Telegram digest.
"""
from __future__ import annotations

import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import requests  # noqa: E402

from scripts import notify, sources, summarizer  # noqa: E402

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("ai_news")

REPO_URL = os.environ.get("REPO_URL", "https://github.com/USERNAME/REPO")
ARTICLES_DIR = ROOT / "articles"

AI_FEEDS: list[tuple[str, str]] = [
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("Ars Technica AI", "https://arstechnica.com/ai/feed/"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("MIT Technology Review AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
    ("Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss"),
    ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
    ("Google AI Blog", "https://blog.google/technology/ai/rss/"),
    ("OpenAI Blog", "https://openai.com/news/rss.xml"),
]

AI_KEYWORDS = [
    "ai", "llm", "gpt", "claude", "gemini", "model", "agent",
    "anthropic", "openai", "deepmind", "neural", "transformer",
    "fine-tune", "rag", "diffusion", "multimodal",
]


# ---------- Hacker News Algolia ----------

def fetch_hn_ai(cutoff: datetime) -> list[sources.Article]:
    ts = int(cutoff.timestamp())
    url = (
        "https://hn.algolia.com/api/v1/search_by_date"
        f"?tags=story&query=AI&numericFilters=created_at_i>{ts}&hitsPerPage=30"
    )
    out: list[sources.Article] = []
    try:
        r = requests.get(url, timeout=15,
                         headers={"User-Agent": sources.USER_AGENT})
        if r.status_code != 200:
            log.warning("HN Algolia HTTP %s", r.status_code)
            return out
        for hit in r.json().get("hits", []):
            link = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            title = hit.get("title") or ""
            ts_i = hit.get("created_at_i")
            if not title or not link or not ts_i:
                continue
            pub = datetime.fromtimestamp(ts_i, tz=timezone.utc)
            if pub < cutoff:
                continue
            out.append(sources.Article(
                title=title,
                link=link,
                published=pub,
                summary=hit.get("story_text") or "",
                source_name="Hacker News (AI)",
            ))
    except requests.RequestException as e:
        log.warning("HN Algolia error: %s", e)
    log.info("fetched %d entries from Hacker News (AI)", len(out))
    return out


# ---------- fetch + score ----------

def fetch_all_ai(hours: int = 24) -> list[sources.Article]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    out: list[sources.Article] = []
    for name, url in AI_FEEDS:
        try:
            out.extend(sources.fetch_feed(name, url, cutoff))
        except Exception as e:  # pragma: no cover
            log.warning("feed %s failed: %s", name, e)
    out.extend(fetch_hn_ai(cutoff))
    return out


def score_ai(articles: list[sources.Article]) -> list[sources.Article]:
    now = datetime.now(timezone.utc)
    for a in articles:
        text = f"{a.title}\n{a.summary}".lower()
        score = sum(2 for kw in AI_KEYWORDS if kw in text)
        hours = (now - a.published).total_seconds() / 3600
        if hours <= 6:
            score += 3
        elif hours <= 12:
            score += 2
        elif hours <= 18:
            score += 1
        a.score = score
        a.recency_hours = hours
    return articles


def dedupe_by_url(articles: list[sources.Article]) -> list[sources.Article]:
    seen: set[str] = set()
    out: list[sources.Article] = []
    for a in sorted(articles, key=lambda x: x.score, reverse=True):
        if a.link in seen:
            continue
        seen.add(a.link)
        out.append(a)
    return out


# ---------- render ----------

def render_md(date_str: str, generated_at_utc: str, model_used: str,
              sources_count: int, items: list[dict]) -> str:
    lines: list[str] = []
    lines.append("---")
    lines.append(f"date: {date_str}")
    lines.append(f"generated_at: {generated_at_utc}")
    lines.append(f"model_used: {model_used}")
    lines.append(f"sources_count: {sources_count}")
    lines.append("---")
    lines.append("")
    lines.append(f"# 📰 AI News {date_str}")
    lines.append("")
    for i, it in enumerate(items, 1):
        lines.append(f"## {i}. {it.get('title_th','')}")
        lines.append("")
        lines.append((it.get("summary_th") or "").strip())
        lines.append("")
        lines.append(f"**Why it matters:** {it.get('why_it_matters','')}")
        lines.append("")
        lines.append(f"🔗 Source: [{it.get('source','')}]({it.get('url','')})")
        lines.append("")
    return "\n".join(lines)


# ---------- telegram ----------

def build_ai_digest(date_str: str, items: list[dict], repo_url: str) -> str:
    esc = notify.escape_mdv2
    lines: list[str] = []
    lines.append(f"📰 *AI News — {esc(date_str)}*")
    lines.append("")
    for i, it in enumerate(items, 1):
        title = esc(it.get("title_th", ""))
        summary = esc((it.get("summary_th", "") or "").strip())
        why = esc(it.get("why_it_matters", ""))
        src = esc(it.get("source", ""))
        lines.append(f"*{i}\\. {title}*")
        if summary:
            lines.append(summary)
        if why:
            lines.append(f"💡 {why}")
        lines.append(f"🔗 {src}")
        lines.append("")
    full_url = f"{repo_url}/blob/main/articles/{date_str}.md"
    lines.append(f"📂 Full: {esc(full_url)}")
    return "\n".join(lines)


def send_ai_digest(date_str: str, items: list[dict], repo_url: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log.warning("Telegram secrets missing; skipping notify")
        return
    text = build_ai_digest(date_str, items, repo_url)
    for chunk in notify._chunk(text):
        notify._send(token, chat_id, chunk)


# ---------- main ----------

def run() -> int:
    dry_run = os.environ.get("DRY_RUN") == "1"
    limit = int(os.environ.get("LIMIT", "5"))

    now_utc = datetime.now(timezone.utc)
    date_str = now_utc.strftime("%Y-%m-%d")
    generated_at_utc = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    articles = fetch_all_ai(hours=24)
    log.info("total fetched: %d", len(articles))
    if not articles:
        log.error("no AI news fetched")
        return 1

    articles = score_ai(articles)
    articles = dedupe_by_url(articles)
    top = articles[:limit]
    log.info("selected top %d", len(top))

    top = sources.enrich_all(top)

    while len(top) < 5:
        top.append(top[-1])
    top_dicts = [a.to_dict() for a in top[:5]]

    items, model_used = summarizer.summarize_ai_news(top_dicts)

    md = render_md(
        date_str=date_str,
        generated_at_utc=generated_at_utc,
        model_used=model_used,
        sources_count=len({a.source_name for a in top}),
        items=items,
    )

    ARTICLES_DIR.mkdir(exist_ok=True)
    out_path = ARTICLES_DIR / f"{date_str}.md"
    latest = ARTICLES_DIR / "latest.md"

    if dry_run:
        print("=== DRY RUN — would write to", out_path, "===")
        print(md[:3000])
        print("\n=== Telegram preview ===")
        print(build_ai_digest(date_str, items, REPO_URL))
        return 0

    out_path.write_text(md, encoding="utf-8")
    latest.write_text(md, encoding="utf-8")
    log.info("wrote %s and %s", out_path, latest)

    send_ai_digest(date_str, items, REPO_URL)
    return 0


if __name__ == "__main__":
    sys.exit(run())
