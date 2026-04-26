"""Daily US Market & Economy Brief — main orchestrator."""
from __future__ import annotations

import json
import logging
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# Allow `python scripts/market_brief.py` from repo root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import classifier, notify, sources, summarizer  # noqa: E402

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("market_brief")

REPO_URL = os.environ.get("REPO_URL", "https://github.com/USERNAME/REPO")
BRIEFS_DIR = ROOT / "briefs"


# ------------------------ aggregate ------------------------

def compute_aggregate(items: list[dict]) -> dict:
    sentiment_counts: Counter = Counter(it.get("sentiment", "neutral") for it in items)
    sector_counter: Counter = Counter()
    ticker_counter: Counter = Counter()
    for it in items:
        for s in it.get("sectors", []) or []:
            sector_counter[s] += 1
        for t in it.get("tickers", []) or []:
            ticker_counter[t.upper()] += 1
    return {
        "sentiment_counts": dict(sentiment_counts),
        "top_sectors": [s for s, _ in sector_counter.most_common(3)],
        "top_tickers": [t for t, _ in ticker_counter.most_common(5)],
    }


# ------------------------ markdown render ------------------------

def _yaml_list(vals: list[str]) -> str:
    if not vals:
        return "[]"
    return "[" + ", ".join(json.dumps(v, ensure_ascii=False) for v in vals) + "]"


def render_markdown(date_str: str, generated_at_utc: str, model_used: str,
                    sources_count: int, items: list[dict], aggregate: dict,
                    exec_summary: str) -> str:
    agg_sent = aggregate["sentiment_counts"]
    yaml_fm = (
        "---\n"
        f"date: {date_str}\n"
        f"generated_at_utc: {generated_at_utc}\n"
        f"model_used: {model_used}\n"
        f"sources_count: {sources_count}\n"
        f"aggregate_sentiment: "
        f"{{bullish: {agg_sent.get('bullish', 0)}, "
        f"bearish: {agg_sent.get('bearish', 0)}, "
        f"neutral: {agg_sent.get('neutral', 0)}}}\n"
        f"top_sectors: {_yaml_list(aggregate['top_sectors'])}\n"
        f"top_tickers: {_yaml_list(aggregate['top_tickers'])}\n"
        "---\n"
    )

    md = [yaml_fm]
    md.append(f"# 📈 US Market Brief — {date_str}\n")
    md.append("## Executive Summary\n")
    md.append(exec_summary.strip() + "\n")

    alerts = [
        it for it in items
        if it.get("impact") == "high" and it.get("time_horizon") == "immediate"
    ]
    md.append("## 🚨 High-Impact Alerts\n")
    if alerts:
        for it in alerts:
            md.append(f"- **{it.get('title_th', '')}** — {it.get('source_name', '')}")
        md.append("")
    else:
        md.append("_ไม่มีรายการ impact=high + immediate ในวันนี้_\n")

    for it in sorted(items, key=lambda x: x.get("rank", 99)):
        rank = it.get("rank", "?")
        md.append(f"## {rank}. {it.get('title_th', '')}\n")
        md.append("| Category | Sentiment | Impact | Horizon | Sectors | Tickers |")
        md.append("|---|---|---|---|---|---|")
        md.append(
            f"| {it.get('category','')} | {it.get('sentiment','')} | "
            f"{it.get('impact','')} | {it.get('time_horizon','')} | "
            f"{', '.join(it.get('sectors', []) or []) or '—'} | "
            f"{', '.join(it.get('tickers', []) or []) or '—'} |"
        )
        md.append("")
        md.append(it.get("summary_th", "").strip() + "\n")
        md.append("**📊 Key Numbers**")
        kn = it.get("key_numbers") or []
        if kn:
            for n in kn:
                md.append(f"- {n}")
        else:
            md.append("- —")
        md.append("")
        md.append(f"**👀 Watch Next:** {it.get('watch_next','—')}")
        md.append("")
        md.append(f"🔗 Source: [{it.get('source_name','')}]({it.get('url','')})")
        md.append("")

    return "\n".join(md)


# ------------------------ pipeline ------------------------

def run() -> int:
    dry_run = os.environ.get("DRY_RUN") == "1"
    limit = int(os.environ.get("LIMIT", "10"))
    use_fixtures = os.environ.get("USE_FIXTURES") == "1"

    now_utc = datetime.now(timezone.utc)
    date_str = now_utc.strftime("%Y-%m-%d")
    generated_at_utc = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. fetch
    if use_fixtures:
        articles = _load_fixtures()
    else:
        articles = sources.fetch_all(hours=24)
    log.info("fetched %d articles total", len(articles))
    if not articles:
        log.error("no articles fetched")
        return 1

    # 2. score + dedupe + top-N
    articles = classifier.score_articles(articles)
    articles = classifier.dedupe(articles)
    top = classifier.top_n_with_diversity(articles, n=limit, max_per_source=2)
    log.info("selected top %d articles", len(top))
    if len(top) < limit:
        log.warning("only %d articles after filtering (wanted %d)", len(top), limit)

    # 3. enrich
    top = sources.enrich_all(top)

    # pad to 10 if needed (for LLM validation) — duplicate last
    while len(top) < 10:
        top.append(top[-1])

    top_dicts = [a.to_dict() for a in top[:10]]

    # 4. LLM summarize
    items, model_used = summarizer.summarize_articles(top_dicts)

    # 5. executive summary
    exec_summary, _ = summarizer.executive_summary(items)

    # 6. aggregate
    aggregate = compute_aggregate(items)

    # 7. render markdown
    md = render_markdown(
        date_str=date_str,
        generated_at_utc=generated_at_utc,
        model_used=model_used,
        sources_count=len({a.source_name for a in top}),
        items=items,
        aggregate=aggregate,
        exec_summary=exec_summary,
    )

    BRIEFS_DIR.mkdir(exist_ok=True)
    out_path = BRIEFS_DIR / f"{date_str}.md"
    latest_path = BRIEFS_DIR / "latest.md"

    if dry_run:
        print("=== DRY RUN — would write to", out_path, "===")
        print(md[:3000])
        print("...\n=== Telegram digest preview ===")
        print(notify.build_digest(date_str, items, aggregate, REPO_URL))
        return 0

    out_path.write_text(md, encoding="utf-8")
    latest_path.write_text(md, encoding="utf-8")
    log.info("wrote %s and %s", out_path, latest_path)

    # 8. telegram
    notify.send_digest(date_str, items, aggregate, REPO_URL)
    return 0


def _load_fixtures() -> list[sources.Article]:
    """Load RSS fixtures from tests/fixtures/ for offline iteration."""
    import feedparser
    from datetime import timedelta

    fx_dir = ROOT / "tests" / "fixtures"
    if not fx_dir.exists():
        log.error("no fixtures dir at %s", fx_dir)
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=365)  # don't filter by time for fixtures
    out: list[sources.Article] = []
    for f in fx_dir.glob("*.xml"):
        parsed = feedparser.parse(f.read_bytes())
        for entry in parsed.entries:
            pub = sources._parse_date(entry) or datetime.now(timezone.utc)
            if pub < cutoff:
                continue
            out.append(sources.Article(
                title=entry.get("title", ""),
                link=entry.get("link", ""),
                published=pub,
                summary=sources._extract_rss_content(entry),
                source_name=f.stem,
            ))
    return out


if __name__ == "__main__":
    sys.exit(run())
