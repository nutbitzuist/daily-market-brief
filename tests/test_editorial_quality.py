from datetime import datetime, timezone

import pytest

from scripts import classifier, summarizer
from scripts.sources import Article


def article(title: str, source: str, url: str) -> Article:
    return Article(
        title=title,
        link=url,
        published=datetime.now(timezone.utc),
        summary=title,
        source_name=source,
    )


def test_default_model_chain_is_current_and_synchronous():
    assert summarizer.DEFAULT_MODELS == [
        "google/gemini-3.7-flash",
        "deepseek/deepseek-v4-flash-0731",
        "x-ai/grok-4.3",
    ]
    assert all(":batch" not in model for model in summarizer.DEFAULT_MODELS)


def test_us_scope_penalizes_unrelated_foreign_domestic_story():
    foreign = article(
        "UK government considers a domestic bank tax",
        "Financial Times",
        "https://example.com/uk",
    )
    us = article(
        "Federal Reserve signals rate decision after US inflation data",
        "Reuters",
        "https://example.com/us",
    )
    scored = classifier.score_articles([foreign, us])
    assert us.score > foreign.score


def test_dedupe_preserves_independent_corroborating_source():
    first = article(
        "Federal Reserve signals rate cut after inflation report",
        "Reuters",
        "https://example.com/1",
    )
    second = article(
        "Federal Reserve signals rate cut after inflation report",
        "CNBC",
        "https://example.com/2",
    )
    kept = classifier.dedupe(classifier.score_articles([first, second]))
    assert len(kept) == 1
    assert len(kept[0].corroborating_sources) == 1


def test_validator_rejects_invented_and_duplicate_urls():
    candidates = [
        {"link": "https://example.com/1"},
        {"link": "https://example.com/2"},
    ]
    with pytest.raises(ValueError, match="outside candidate"):
        summarizer._validate_selected_urls(
            [{"url": "https://invented.example/"}], candidates
        )
    with pytest.raises(ValueError, match="duplicated"):
        summarizer._validate_selected_urls(
            [
                {"url": "https://example.com/1"},
                {"url": "https://example.com/1"},
            ],
            candidates,
        )


def test_common_horizon_alias_is_normalized_instead_of_rejecting_brief():
    item = {
        "title_th": "ข่าว",
        "summary_th": "สรุป",
        "category": "Macro/Fed",
        "sentiment": "neutral",
        "impact": "medium",
        "time_horizon": "medium-term",
        "sectors": [],
        "tickers": [],
        "key_numbers": [],
        "watch_next": "ติดตาม",
        "source_name": "Reuters",
        "url": "https://example.com/1",
    }
    items = summarizer._validate(
        [dict(item, rank=rank) for rank in range(1, 11)]
    )
    assert all(row["time_horizon"] == "short-term" for row in items)


def test_repair_keeps_model_rows_and_backfills_one_bad_selection():
    model_rows = [
        {"rank": rank, "url": f"https://example.com/{rank}", "title_th": f"ข่าว {rank}"}
        for rank in range(1, 11)
    ]
    model_rows[2]["url"] = model_rows[1]["url"]
    candidates = [
        {"link": f"https://example.com/{rank}"} for rank in range(1, 12)
    ]
    fallback = [
        {"rank": rank, "url": f"https://example.com/{rank}", "title_th": f"สำรอง {rank}"}
        for rank in range(1, 12)
    ]
    repaired, replacements = summarizer._repair_selected_items(
        model_rows, candidates, fallback
    )
    assert replacements == 1
    assert len(repaired) == 10
    assert len({row["url"] for row in repaired}) == 10
