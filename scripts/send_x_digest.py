"""Send a pre-built plain-text X news digest to the configured Telegram group.

The workflow passes UTF-8 content as base64 so Telegram credentials remain in
GitHub Secrets and multiline dispatch inputs do not get mangled.
"""
from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path

import requests

MAX_TELEGRAM_TEXT = 4096
SAFE_CHUNK_SIZE = 3900


def decode_digest(value: str) -> str:
    try:
        text = base64.b64decode(value, validate=True).decode("utf-8")
    except Exception as exc:
        raise ValueError("DIGEST_B64 is not valid base64-encoded UTF-8") from exc
    text = text.replace("\r\n", "\n").strip()
    if not text:
        raise ValueError("digest is empty")
    return text


def chunk_plain_text(text: str, limit: int = SAFE_CHUNK_SIZE) -> list[str]:
    if not text:
        return []
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        split_at = remaining.rfind("\n\n", 0, limit + 1)
        if split_at < limit // 2:
            split_at = remaining.rfind("\n", 0, limit + 1)
        if split_at < limit // 2:
            split_at = remaining.rfind(" ", 0, limit + 1)
        if split_at <= 0:
            split_at = limit
        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()
    if remaining:
        chunks.append(remaining)
    return chunks


def telegram_call(token: str, method: str, payload: dict) -> dict:
    response = requests.post(
        f"https://api.telegram.org/bot{token}/{method}",
        json=payload,
        timeout=30,
    )
    try:
        body = response.json()
    except ValueError as exc:
        raise RuntimeError(f"Telegram {method} returned non-JSON HTTP {response.status_code}") from exc
    if response.status_code != 200 or not body.get("ok"):
        description = body.get("description", f"HTTP {response.status_code}")
        raise RuntimeError(f"Telegram {method} failed: {description}")
    return body


def send_digest(text: str, token: str, chat_id: str, expected_title: str) -> list[int]:
    chat = telegram_call(token, "getChat", {"chat_id": chat_id})["result"]
    actual_title = (chat.get("title") or "").strip()
    if expected_title and actual_title != expected_title:
        raise RuntimeError(
            f"Telegram target mismatch: expected {expected_title!r}, got {actual_title!r}"
        )

    message_ids: list[int] = []
    for chunk in chunk_plain_text(text):
        result = telegram_call(
            token,
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": True,
            },
        )["result"]
        message_ids.append(int(result["message_id"]))
    print(json.dumps({"chat_title": actual_title, "chunks_sent": len(message_ids)}))
    return message_ids


def main() -> int:
    digest_b64 = os.environ.get("DIGEST_B64", "")
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    expected_title = os.environ.get("EXPECTED_CHAT_TITLE", "Daily News Update")
    archive_path = os.environ.get("ARCHIVE_PATH", "")

    text = decode_digest(digest_b64)
    if archive_path:
        path = Path(archive_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")

    if os.environ.get("DRY_RUN") == "1":
        print(json.dumps({"dry_run": True, "chars": len(text), "chunks": len(chunk_plain_text(text))}))
        return 0
    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required")

    send_digest(text, token, chat_id, expected_title)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
