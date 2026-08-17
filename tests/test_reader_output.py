from scripts import ai_news, market_brief, notify, sources, summarizer, th_news


FORBIDDEN = (
    "http://",
    "https://",
    "🔗",
    "Source Policy",
    "generated_at",
    "Published Time",
    "Markdown Content",
    "Fallback brief",
    "deterministic fallback",
    "ตัวเลขสำคัญ",
)


def market_item(rank: int = 1) -> dict:
    return {
        "rank": rank,
        "title_th": "ข่าวสำคัญ",
        "summary_th": "เกิดเหตุการณ์สำคัญและมีผลต่อตลาด",
        "category": "Macro/Fed",
        "sentiment": "neutral",
        "impact": "high",
        "time_horizon": "short-term",
        "sectors": ["Tech"],
        "tickers": ["TEST"],
        "key_numbers": ["GDP 2.0%"],
        "watch_next": "ข้อมูลรอบถัดไป",
        "source_name": "Reuters",
        "url": "https://example.com/story",
    }


def assert_reader_clean(text: str) -> None:
    for token in FORBIDDEN:
        assert token.lower() not in text.lower()


def test_all_reader_outputs_are_concise_and_link_free():
    us_items = [market_item(i) for i in range(1, 11)]
    ai_items = [
        {
            "title_th": f"ข่าว AI {i}",
            "summary_th": "รายละเอียดสำคัญ",
            "why_it_matters": "กระทบการแข่งขันด้าน AI",
            "source": "Reuters",
            "url": "https://example.com/ai",
        }
        for i in range(1, 6)
    ]
    outputs = [
        market_brief.render_markdown(
            "2026-08-17", "timestamp", "model", 5, us_items, {"sentiment_counts": {}}, "summary"
        ),
        notify.build_digest("2026-08-17", us_items, {}, "https://github.com/repo", "summary"),
        th_news.render_md("2026-08-17", "timestamp", "model", 5, us_items, "summary"),
        th_news.build_th_digest("2026-08-17", us_items, "summary", "https://github.com/repo"),
        ai_news.render_md("2026-08-17", "timestamp", "model", 5, ai_items),
        ai_news.build_ai_digest("2026-08-17", ai_items, "https://github.com/repo"),
    ]
    for output in outputs:
        assert_reader_clean(output)
        assert "ข่าวสำคัญ" in output or "ข่าว AI" in output


def test_jina_transport_metadata_is_removed():
    raw = (
        "Title: Example\n"
        "URL Source: https://example.com\n"
        "Published Time: yesterday\n\n"
        "Markdown Content:\n"
        "Actual article detail that matters.\n"
        "![image](https://example.com/image.jpg)"
    )
    cleaned = sources.clean_enriched_text(raw)
    assert cleaned == "Actual article detail that matters."


def test_reader_guard_removes_links_metadata_and_redundant_watch_prefix():
    dirty = (
        "Published Time: yesterday\n"
        "Key detail [Reuters](https://example.com/story) www.example.com\n"
        "Fallback brief"
    )
    assert notify.reader_text(dirty) == "Key detail Reuters"
    assert notify.reader_watch("ติดตาม ข้อมูลรอบถัดไป") == "ข้อมูลรอบถัดไป"


def test_deterministic_rows_do_not_expose_fallback_or_transport_language():
    articles = [
        {
            "title": f"Headline {i}",
            "summary": "Key detail only",
            "source_name": "Reuters",
            "link": f"https://example.com/{i}",
        }
        for i in range(10)
    ]
    items = summarizer._fallback_us_items(articles)
    reader = market_brief.render_markdown(
        "2026-08-17", "timestamp", "fallback-model", 1, items, {"sentiment_counts": {}}, ""
    )
    assert_reader_clean(reader)
