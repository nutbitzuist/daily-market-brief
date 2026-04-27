"""Daily Thailand News brief — runs at 06:30 Asia/Bangkok = 23:30 UTC.

15 Thai/Thai-English business & economy RSS feeds → top 10 by recency + source tier
→ 3-layer enrichment → Gemini-2.5-flash-lite (with free-model fallback)
→ thailand/{YYYY-MM-DD}.md + thailand/latest.md → Telegram digest.
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import classifier, notify, sources, summarizer  # noqa: E402

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("th_news")

REPO_URL = os.environ.get("REPO_URL", "https://github.com/USERNAME/REPO")
TH_DIR = ROOT / "thailand"

TH_FEEDS: list[tuple[str, str]] = [
    # Thai-language business
    ("ประชาชาติธุรกิจ Finance", "https://www.prachachat.net/finance/feed"),
    ("ประชาชาติธุรกิจ Economy", "https://www.prachachat.net/economy/feed"),
    ("กรุงเทพธุรกิจ Business", "https://www.bangkokbiznews.com/rss/feed/business.xml"),
    ("กรุงเทพธุรกิจ Finance", "https://www.bangkokbiznews.com/rss/feed/finance.xml"),
    ("ฐานเศรษฐกิจ Finance", "https://www.thansettakij.com/rss/finance"),
    ("ฐานเศรษฐกิจ Economy", "https://www.thansettakij.com/rss/economy"),
    ("PostToday Market", "https://www.posttoday.com/rss/market.xml"),
    ("MoneyChannel TH (Google News)",
     "https://news.google.com/rss/search?q=%E0%B8%95%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B8%AB%E0%B8%B8%E0%B9%89%E0%B8%99%E0%B9%84%E0%B8%97%E0%B8%A2+SET&hl=th&gl=TH&ceid=TH:th"),
    # English Thailand business
    ("Bangkok Post Business", "https://www.bangkokpost.com/rss/data/business.xml"),
    ("The Nation Thailand Business", "https://www.nationthailand.com/rss/business"),
    ("Reuters Thailand (Google News)",
     "https://news.google.com/rss/search?q=site:reuters.com+Thailand+economy&hl=en"),
    ("Nikkei Asia Thailand", "https://asia.nikkei.com/rss/feed/nar?tag=Thailand"),
    # Primary sources
    ("ธปท. ข่าว", "https://www.bot.or.th/th/news-and-media/news/news-rss.xml"),
    ("SET News (Google News)",
     "https://news.google.com/rss/search?q=site:set.or.th+OR+%22%E0%B8%95%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B8%AB%E0%B8%A5%E0%B8%B1%E0%B8%81%E0%B8%97%E0%B8%A3%E0%B8%B1%E0%B8%9E%E0%B8%A2%E0%B9%8C%22&hl=th&gl=TH&ceid=TH:th"),
    ("กระทรวงการคลัง (Google News)",
     "https://news.google.com/rss/search?q=site:mof.go.th+OR+%22%E0%B8%81%E0%B8%A3%E0%B8%B0%E0%B8%97%E0%B8%A3%E0%B8%A7%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B8%84%E0%B8%A5%E0%B8%B1%E0%B8%87%22&hl=th"),
]

# Source tier scoring — primary sources (BoT, SET, MoF) get the biggest boost.
TIER1 = ("ธปท.", "SET News", "กระทรวงการคลัง")
TIER2 = ("Reuters", "Nikkei", "Bangkok Post", "The Nation",
         "ประชาชาติ", "กรุงเทพธุรกิจ", "ฐานเศรษฐกิจ")
TIER3 = ("PostToday", "MoneyChannel")


def _source_score(name: str) -> float:
    if any(t in name for t in TIER1):
        return 5.0
    if any(t in name for t in TIER2):
        return 3.0
    if any(t in name for t in TIER3):
        return 1.0
    return 0.0


def score_th(articles: list[sources.Article]) -> list[sources.Article]:
    now = datetime.now(timezone.utc)
    for a in articles:
        score = _source_score(a.source_name)
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


# ---------- render ----------

def _yaml_list(vals: list[str]) -> str:
    if not vals:
        return "[]"
    return "[" + ", ".join(json.dumps(v, ensure_ascii=False) for v in vals) + "]"


def render_md(date_str: str, generated_at_utc: str, model_used: str,
              sources_count: int, items: list[dict], exec_summary: str) -> str:
    lines: list[str] = []
    lines.append("---")
    lines.append(f"date: {date_str}")
    lines.append(f"generated_at_utc: {generated_at_utc}")
    lines.append(f"model_used: {model_used}")
    lines.append(f"sources_count: {sources_count}")
    lines.append("---")
    lines.append("")
    lines.append(f"# 🇹🇭 Thailand Brief — {date_str}")
    lines.append("")
    lines.append(exec_summary.strip())
    lines.append("")

    for it in sorted(items, key=lambda x: x.get("rank", 99)):
        rank = it.get("rank", "?")
        lines.append(f"## {rank}. {it.get('title_th', '')}")
        lines.append("")
        lines.append("| Category | Sentiment | Impact | Horizon | Sectors | Tickers |")
        lines.append("|---|---|---|---|---|---|")
        lines.append(
            f"| {it.get('category','')} | {it.get('sentiment','')} | "
            f"{it.get('impact','')} | {it.get('time_horizon','')} | "
            f"{', '.join(it.get('sectors', []) or []) or '—'} | "
            f"{', '.join(it.get('tickers', []) or []) or '—'} |"
        )
        lines.append("")
        lines.append((it.get("summary_th", "") or "").strip())
        lines.append("")
        kn = it.get("key_numbers") or []
        lines.append("**📊 Key Numbers**")
        if kn:
            for n in kn:
                lines.append(f"- {n}")
        else:
            lines.append("- —")
        lines.append("")
        lines.append(f"**👀 Watch Next:** {it.get('watch_next','—')}")
        lines.append("")
        lines.append(f"🔗 Source: [{it.get('source_name','')}]({it.get('url','')})")
        lines.append("")
    return "\n".join(lines)


# ---------- telegram ----------

SENT_EMOJI = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}


def build_th_digest(date_str: str, items: list[dict], exec_summary: str,
                    repo_url: str) -> str:
    esc = notify.escape_mdv2
    lines: list[str] = []
    lines.append(f"🇹🇭 *Thailand Brief — {esc(date_str)}*")
    lines.append("")
    if exec_summary.strip():
        lines.append(esc(exec_summary.strip()))
        lines.append("")

    lines.append("*Top 10 Headlines:*")
    lines.append("")
    for it in sorted(items, key=lambda x: x.get("rank", 99)):
        emo = SENT_EMOJI.get(it.get("sentiment", "neutral"), "⚪")
        rank = it.get("rank", "?")
        title = esc(it.get("title_th", ""))
        summary = esc((it.get("summary_th", "") or "").strip())
        lines.append(f"*{rank}\\. {emo} {title}*")
        if summary:
            lines.append(summary)
        lines.append("")

    full_url = f"{repo_url}/blob/main/thailand/{date_str}.md"
    lines.append(f"🔗 Full: {esc(full_url)}")
    return "\n".join(lines)


def send_th_digest(date_str: str, items: list[dict], exec_summary: str,
                   repo_url: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log.warning("Telegram secrets missing; skipping notify")
        return
    text = build_th_digest(date_str, items, exec_summary, repo_url)
    for chunk in notify._chunk(text):
        notify._send(token, chat_id, chunk)


# ---------- main ----------

def run() -> int:
    dry_run = os.environ.get("DRY_RUN") == "1"
    limit = int(os.environ.get("LIMIT", "10"))

    now_utc = datetime.now(timezone.utc)
    date_str = now_utc.strftime("%Y-%m-%d")
    generated_at_utc = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. fetch
    cutoff = now_utc - __import__("datetime").timedelta(hours=24)
    articles: list[sources.Article] = []
    for name, url in TH_FEEDS:
        try:
            articles.extend(sources.fetch_feed(name, url, cutoff))
        except Exception as e:  # pragma: no cover
            log.warning("feed %s failed: %s", name, e)
    log.info("fetched %d articles", len(articles))
    if not articles:
        log.error("no Thai news fetched")
        return 1

    # 2. score + dedupe + diversity-aware top-N
    articles = score_th(articles)
    articles = classifier.dedupe(articles)
    top = classifier.top_n_with_diversity(articles, n=limit, max_per_source=2)
    log.info("selected top %d articles", len(top))

    # 3. enrich
    top = sources.enrich_all(top)

    while len(top) < 10:
        top.append(top[-1])
    top_dicts = [a.to_dict() for a in top[:10]]

    # 4. summarize
    items, model_used = summarizer.summarize_th_news(top_dicts)

    # 5. exec summary
    exec_summary, _ = summarizer.th_executive_summary(items)

    # 6. render
    md = render_md(
        date_str=date_str,
        generated_at_utc=generated_at_utc,
        model_used=model_used,
        sources_count=len({a.source_name for a in top}),
        items=items,
        exec_summary=exec_summary,
    )

    TH_DIR.mkdir(exist_ok=True)
    out_path = TH_DIR / f"{date_str}.md"
    latest = TH_DIR / "latest.md"

    if dry_run:
        print("=== DRY RUN — would write to", out_path, "===")
        print(md[:3000])
        print("\n=== Telegram preview ===")
        print(build_th_digest(date_str, items, exec_summary, REPO_URL))
        return 0

    out_path.write_text(md, encoding="utf-8")
    latest.write_text(md, encoding="utf-8")
    log.info("wrote %s and %s", out_path, latest)

    send_th_digest(date_str, items, exec_summary, REPO_URL)
    return 0


if __name__ == "__main__":
    sys.exit(run())
