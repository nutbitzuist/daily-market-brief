"""Telegram digest notifier (MarkdownV2)."""
from __future__ import annotations

import logging
import os
import re
import time
from typing import Iterable

import requests

log = logging.getLogger(__name__)

TG_API = "https://api.telegram.org/bot{token}/sendMessage"
MAX_LEN = 4000

SENTIMENT_EMOJI = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}

_MDV2_SPECIAL = r"_*[]()~`>#+-=|{}.!\\"


def escape_mdv2(text: str) -> str:
    if text is None:
        return ""
    out = []
    for ch in str(text):
        if ch in _MDV2_SPECIAL:
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)


def _chunk(text: str, limit: int = MAX_LEN) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    buf: list[str] = []
    cur = 0
    for line in text.split("\n"):
        add = len(line) + 1
        if cur + add > limit and buf:
            chunks.append("\n".join(buf))
            buf = [line]
            cur = add
        else:
            buf.append(line)
            cur += add
    if buf:
        chunks.append("\n".join(buf))
    return chunks


def _send(token: str, chat_id: str, text: str) -> None:
    url = TG_API.format(token=token)
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True,
    }
    for attempt in range(3):
        try:
            r = requests.post(url, json=payload, timeout=15)
            if r.status_code == 200:
                return
            log.warning("telegram → HTTP %s: %s", r.status_code, r.text[:300])
            if r.status_code in (429, 500, 502, 503):
                time.sleep(2 ** attempt)
                continue
            return
        except requests.RequestException as e:
            log.warning("telegram error: %s", e)
            time.sleep(2 ** attempt)


def build_digest(date_str: str, items: list[dict], aggregate: dict,
                 repo_url: str, exec_summary: str = "") -> str:
    lines: list[str] = []
    lines.append(f"📈 *US Market Brief — {escape_mdv2(date_str)}*")
    lines.append("")

    if exec_summary.strip():
        lines.append(escape_mdv2(exec_summary.strip()))
        lines.append("")

    lines.append("*Top 10 Headlines:*")
    lines.append("")
    for it in sorted(items, key=lambda x: x.get("rank", 99)):
        emoji = SENTIMENT_EMOJI.get(it.get("sentiment", "neutral"), "⚪")
        rank = it.get("rank", "?")
        title = escape_mdv2(it.get("title_th", ""))
        summary = escape_mdv2((it.get("summary_th", "") or "").strip())
        lines.append(f"*{rank}\\. {emoji} {title}*")
        if summary:
            lines.append(summary)
        lines.append("")

    full_url = f"{repo_url}/blob/main/briefs/{date_str}.md"
    lines.append(f"🔗 Full: {escape_mdv2(full_url)}")
    return "\n".join(lines)


def send_digest(date_str: str, items: list[dict], aggregate: dict,
                repo_url: str = "https://github.com/USERNAME/REPO",
                exec_summary: str = "") -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log.warning("Telegram secrets missing; skipping notify")
        return
    text = build_digest(date_str, items, aggregate, repo_url, exec_summary)
    for chunk in _chunk(text):
        _send(token, chat_id, chunk)
