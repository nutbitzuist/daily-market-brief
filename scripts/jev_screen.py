"""TypeSafe Jev candidate screening for the group news briefs.

Jev is a cheap typed gate before the substantive summarizer. It may remove only
high-confidence noise; ambiguous and potentially useful stories remain for the
editor model. Any API/schema failure fails open so a Jev outage cannot suppress
the brief.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests

log = logging.getLogger(__name__)

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = os.environ.get("JEV_MODEL", "jev-latest")
EXCLUDE_CONFIDENCE = float(os.environ.get("JEV_EXCLUDE_CONFIDENCE", "0.85"))

BRIEF_CONTEXT = {
    "us": (
        "US family-office news brief. Prioritize material macro, Fed, policy, "
        "geopolitics, market-moving company, earnings, energy and supply-chain events."
    ),
    "ai": (
        "AI industry news brief. Prioritize concrete model/lab, chips, infrastructure, "
        "enterprise adoption, regulation, legal, funding and M&A developments."
    ),
    "th": (
        "Thailand business and market news brief. Prioritize government and monetary "
        "policy, SET/SEC, listed companies, macro data, trade, tourism and material social policy."
    ),
}

CRITERIA = {
    "include": (
        "Concrete, current, materially relevant to this brief, and contains a real new event, "
        "official decision, data point, earnings/guidance change, or important market implication."
    ),
    "review": (
        "Potentially useful, but significance, freshness, scope, or evidence is unclear; "
        "a substantive editor should inspect it rather than discard it."
    ),
    "exclude": (
        "Lifestyle, promotional, trivial, irrelevant, stale, routine, clickbait, pure opinion, "
        "or lacks a concrete new fact for this brief."
    ),
}


def _mode() -> str:
    return os.environ.get("JEV_SCREEN_MODE", "off").strip().lower()


def _candidate_instruction(candidate_id: str, article: dict[str, Any]) -> str:
    title = str(article.get("title", ""))[:500]
    source = str(article.get("source_name", article.get("source", "")))[:150]
    summary = str(article.get("summary") or article.get("content") or "")[:900]
    published = str(article.get("published", ""))[:100]
    return (
        f"Evaluate ONLY candidate {candidate_id} for the stated brief. "
        f"Title: {title!r}. Source: {source!r}. Published: {published!r}. "
        f"Summary: {summary!r}. Which screening decision applies?"
    )


def _request(payload: dict[str, Any], api_key: str, attempts: int = 3) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Daily-Market-Brief-Jev/1.0",
    }
    for attempt in range(attempts):
        try:
            response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=45)
        except requests.RequestException:
            if attempt + 1 >= attempts:
                raise
            time.sleep(2**attempt)
            continue
        if response.status_code == 200:
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError("Jev response must be an object")
            return data
        if response.status_code in (429, 529) and attempt + 1 < attempts:
            time.sleep(2**attempt)
            continue
        raise RuntimeError(f"TypeSafe Jev HTTP {response.status_code}: {response.text[:300]}")
    raise RuntimeError("TypeSafe Jev request exhausted retries")


def screen_articles(
    articles: list[dict[str, Any]],
    brief_kind: str,
    min_keep: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return screened candidates and a compact audit report.

    Modes: off (no API), shadow (record decisions, do not filter), active (drop only
    high-confidence excludes). Missing credentials and all errors fail open.
    """
    mode = _mode()
    base_report: dict[str, Any] = {
        "mode": mode,
        "brief_kind": brief_kind,
        "input_count": len(articles),
    }
    if mode not in {"shadow", "active"}:
        return articles, {**base_report, "status": "disabled", "output_count": len(articles)}
    api_key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if not api_key:
        log.warning("Jev screening skipped: TYPESAFE_API_KEY missing")
        return articles, {**base_report, "status": "fail_open_missing_key", "output_count": len(articles)}
    if brief_kind not in BRIEF_CONTEXT:
        raise ValueError(f"unsupported Jev brief kind: {brief_kind}")
    if not articles:
        return articles, {**base_report, "status": "empty", "output_count": 0, "decisions": []}

    questions: dict[str, Any] = {}
    ids: list[str] = []
    for index, article in enumerate(articles):
        candidate_id = f"candidate_{index:03d}"
        ids.append(candidate_id)
        questions[candidate_id] = {
            "type": "choice",
            "instructions": _candidate_instruction(candidate_id, article),
            "criteria": CRITERIA,
        }
    payload = {
        "model": MODEL,
        "state": {
            "task": "news_candidate_screening",
            "brief": BRIEF_CONTEXT[brief_kind],
            "rule": "Judge each named candidate independently. Do not let another candidate affect its label.",
        },
        "questions": questions,
    }

    try:
        result = _request(payload, api_key)
        answers = result.get("answers")
        if not isinstance(answers, dict):
            raise ValueError("Jev response missing answers object")

        decisions: list[dict[str, Any]] = []
        accepted: list[tuple[dict[str, Any], float]] = []
        excluded: list[tuple[dict[str, Any], float]] = []
        for candidate_id, article in zip(ids, articles):
            answer = answers.get(candidate_id)
            if not isinstance(answer, dict):
                raise ValueError(f"Jev response missing {candidate_id}")
            choice = str(answer.get("choice", ""))
            confidence = float(answer.get("confidence", 0.0))
            probabilities = answer.get("probabilities") or {}
            include_probability = float(probabilities.get("include", 0.0))
            should_exclude = choice == "exclude" and confidence >= EXCLUDE_CONFIDENCE
            record = {
                "candidate_id": candidate_id,
                "title": str(article.get("title", "")),
                "source": str(article.get("source_name", article.get("source", ""))),
                "url": str(article.get("link", article.get("url", ""))),
                "choice": choice,
                "confidence": confidence,
                "probabilities": probabilities,
                "high_confidence_exclude": should_exclude,
            }
            decisions.append(record)
            (excluded if should_exclude else accepted).append((article, include_probability))

        if mode == "shadow":
            screened = list(articles)
        else:
            screened = [article for article, _ in accepted]
            if len(screened) < min_keep:
                for article, _ in sorted(excluded, key=lambda row: row[1], reverse=True):
                    screened.append(article)
                    if len(screened) >= min_keep:
                        break

        report = {
            **base_report,
            "status": "ok",
            "model": result.get("model", MODEL),
            "output_count": len(screened),
            "high_confidence_excluded": sum(1 for row in decisions if row["high_confidence_exclude"]),
            "usage": result.get("usage", {}),
            "decisions": decisions,
        }
        log.info(
            "Jev %s screening: %d candidates -> %d kept; %d high-confidence excludes",
            mode,
            len(articles),
            len(screened),
            report["high_confidence_excluded"],
        )
        return screened, report
    except Exception as exc:
        log.warning("Jev screening failed open: %s", exc)
        return articles, {
            **base_report,
            "status": "fail_open_error",
            "error_type": type(exc).__name__,
            "output_count": len(articles),
        }
