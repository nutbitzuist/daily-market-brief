"""Durable internal source evidence for reader-facing briefs."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _article_record(article: Any) -> dict:
    if isinstance(article, dict):
        get = article.get
    else:
        get = lambda key, default="": getattr(article, key, default)
    published = get("published", "")
    if isinstance(published, datetime):
        published = published.isoformat()
    return {
        "title": str(get("title", "")),
        "source": str(get("source_name", get("source", ""))),
        "publisher": str(get("publisher", "")),
        "url": str(get("link", get("url", ""))),
        "published": str(published),
    }


def write_evidence(
    output_dir: Path,
    date_str: str,
    generated_at_utc: str,
    model_used: str,
    articles: list[Any],
    items: list[dict],
) -> Path:
    """Write provenance separately from clean reader Markdown."""
    evidence_dir = Path(output_dir) / "_internal"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / f"{date_str}.json"
    payload = {
        "date": date_str,
        "generated_at_utc": generated_at_utc,
        "model_used": model_used,
        "articles": [_article_record(article) for article in articles],
        "items": items,
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path
