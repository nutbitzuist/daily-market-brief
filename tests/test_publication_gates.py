import json
from datetime import datetime, timezone

from scripts import ai_news, market_brief, notify, provenance, sources, th_news


def test_publication_gate_rejects_missing_insufficient_and_deterministic_output():
    assert notify.publication_block_reason(0, 10, "google/gemini") == "no verified source articles"
    assert notify.publication_block_reason(9, 10, "google/gemini") == "only 9 unique source articles; need 10"
    assert notify.publication_block_reason(10, 10, "deterministic-fallback/openrouter-unavailable") == "summary models unavailable"
    assert notify.publication_block_reason(10, 10, "google/gemini") == ""
    assert notify.reader_output_issues("Key detail only") == []
    assert notify.reader_output_issues("OpenRouter unavailable https://example.com") == [
        "link",
        "fallback diagnostics",
    ]


def test_us_no_source_does_not_write_or_send(monkeypatch, tmp_path):
    monkeypatch.delenv("USE_FIXTURES", raising=False)
    monkeypatch.delenv("DRY_RUN", raising=False)
    monkeypatch.setattr(market_brief.sources, "fetch_all", lambda hours: [])
    monkeypatch.setattr(market_brief, "BRIEFS_DIR", tmp_path)
    sent = []
    monkeypatch.setattr(market_brief.notify, "send_digest", lambda *a, **k: sent.append(True))
    assert market_brief.run() == 1
    assert not sent
    assert list(tmp_path.iterdir()) == []


def _articles(count):
    return [
        sources.Article(
            title=f"Verified market event {i}",
            link=f"https://example.com/{i}",
            published=datetime(2026, 8, 17, tzinfo=timezone.utc),
            summary="Verified detail",
            source_name=f"Publisher {i}",
        )
        for i in range(count)
    ]


def _stub_us_selection(monkeypatch, articles):
    monkeypatch.setattr(market_brief.sources, "fetch_all", lambda hours: articles)
    monkeypatch.setattr(market_brief.classifier, "score_articles", lambda rows: rows)
    monkeypatch.setattr(market_brief.classifier, "dedupe", lambda rows: rows)
    monkeypatch.setattr(
        market_brief.classifier,
        "top_n_with_diversity",
        lambda rows, n, max_per_source: rows[:n],
    )


def test_us_insufficient_unique_sources_does_not_publish(monkeypatch, tmp_path):
    monkeypatch.delenv("USE_FIXTURES", raising=False)
    monkeypatch.delenv("DRY_RUN", raising=False)
    _stub_us_selection(monkeypatch, _articles(9))
    monkeypatch.setattr(market_brief, "BRIEFS_DIR", tmp_path)
    sent = []
    monkeypatch.setattr(market_brief.notify, "send_digest", lambda *a, **k: sent.append(True))
    assert market_brief.run() == 1
    assert not sent
    assert list(tmp_path.iterdir()) == []


def test_us_model_outage_does_not_publish(monkeypatch, tmp_path):
    monkeypatch.delenv("USE_FIXTURES", raising=False)
    monkeypatch.delenv("DRY_RUN", raising=False)
    articles = _articles(10)
    _stub_us_selection(monkeypatch, articles)
    monkeypatch.setattr(market_brief.sources, "enrich_all", lambda rows: rows)
    monkeypatch.setattr(
        market_brief.summarizer,
        "summarize_articles",
        lambda rows: ([], "deterministic-fallback/openrouter-unavailable"),
    )
    monkeypatch.setattr(market_brief, "BRIEFS_DIR", tmp_path)
    sent = []
    monkeypatch.setattr(market_brief.notify, "send_digest", lambda *a, **k: sent.append(True))
    assert market_brief.run() == 1
    assert not sent
    assert list(tmp_path.iterdir()) == []


def test_ai_no_source_does_not_write_or_send(monkeypatch, tmp_path):
    monkeypatch.delenv("DRY_RUN", raising=False)
    monkeypatch.setattr(ai_news, "fetch_all_ai", lambda hours: [])
    monkeypatch.setattr(ai_news, "ARTICLES_DIR", tmp_path)
    sent = []
    monkeypatch.setattr(ai_news, "send_ai_digest", lambda *a, **k: sent.append(True))
    assert ai_news.run() == 1
    assert not sent
    assert list(tmp_path.iterdir()) == []


def test_th_no_source_does_not_write_or_send(monkeypatch, tmp_path):
    monkeypatch.delenv("DRY_RUN", raising=False)
    monkeypatch.setattr(th_news.sources, "fetch_feed", lambda *a, **k: [])
    monkeypatch.setattr(th_news, "TH_DIR", tmp_path)
    sent = []
    monkeypatch.setattr(th_news, "send_th_digest", lambda *a, **k: sent.append(True))
    assert th_news.run() == 1
    assert not sent
    assert list(tmp_path.iterdir()) == []


def test_provenance_is_durable_but_not_in_reader_output(tmp_path):
    article = sources.Article(
        title="Verified event",
        link="https://example.com/source",
        published=datetime(2026, 8, 17, tzinfo=timezone.utc),
        summary="Key detail",
        source_name="Reuters",
        publisher="Reuters",
    )
    items = [{"title_th": "หัวข้อ", "summary_th": "รายละเอียดสำคัญ", "url": article.link}]
    path = provenance.write_evidence(
        output_dir=tmp_path,
        date_str="2026-08-17",
        generated_at_utc="2026-08-17T04:00:00Z",
        model_used="google/gemini",
        articles=[article],
        items=items,
    )
    data = json.loads(path.read_text())
    assert data["articles"][0]["url"] == article.link
    assert data["items"][0]["url"] == article.link
    reader = ai_news.render_md("2026-08-17", "hidden", "model", 1, items)
    assert article.link not in reader
    assert "Reuters" not in reader
