"""Fail-closed QA for the four-times-daily X investment brief.

The LLM still makes the editorial decision. This validator enforces the parts
that should be deterministic: item limits, evidence completeness, event-key
reuse, obvious cross-slot duplication, and common Thai AI-writing tells.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

MAX_ITEMS = 10
MIN_ITEM_CHARS = 120
MAX_ITEM_CHARS = 900
DUPLICATE_SIMILARITY = 0.68
NO_EVENT_TEXT = "รอบนี้ยังไม่มีเหตุการณ์ใหม่ที่เปลี่ยนมุมมองการลงทุนจาก Brief ก่อนหน้า จึงไม่หยิบข่าวเดิมมาเล่าซ้ำ"

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")
URL_RE = re.compile(r"https?://", re.I)
EVENT_KEY_RE = re.compile(r"(?im)^\s*-?\s*event_key\s*:\s*([^\n#]+)")
STATUS_RE = re.compile(r"(?im)^\s*-?\s*status\s*:\s*(NEW|UPDATE)\s*$")
MATERIAL_RE = re.compile(r"(?im)^\s*-?\s*material_update\s*:\s*(.+)$")
X_URL_RE = re.compile(r"https?://(?:www\.)?x\.com/[^\s)]+", re.I)

BANNED_THAI_PHRASES = (
    "สะท้อนให้เห็นว่า",
    "ท่ามกลางภูมิทัศน์",
    "ถือเป็นจุดเปลี่ยนสำคัญ",
    "นักลงทุนควรจับตาอย่างใกล้ชิด",
    "สร้างแรงกดดันอย่างมีนัยสำคัญ",
)


@dataclass(frozen=True)
class EvidenceItem:
    event_key: str
    status: str
    material_update: str
    urls: tuple[str, ...]


def split_body_items(text: str) -> tuple[str, list[str]]:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text.strip()) if block.strip()]
    if not blocks:
        return "", []
    return blocks[0], blocks[1:]


def split_evidence_items(text: str) -> list[str]:
    return [
        block.strip()
        for block in re.split(r"(?m)^###\s+\d+\D.*$", text)
        if EVENT_KEY_RE.search(block)
    ]


def parse_evidence(text: str) -> list[EvidenceItem]:
    items: list[EvidenceItem] = []
    for block in split_evidence_items(text):
        event = EVENT_KEY_RE.search(block)
        status = STATUS_RE.search(block)
        material = MATERIAL_RE.search(block)
        if not event or not status:
            continue
        items.append(
            EvidenceItem(
                event_key=event.group(1).strip().lower(),
                status=status.group(1).upper(),
                material_update=(material.group(1).strip() if material else ""),
                urls=tuple(X_URL_RE.findall(block)),
            )
        )
    return items


def normalize_for_similarity(text: str) -> str:
    text = URL_RE.sub(" ", text.lower())
    text = re.sub(r"[^0-9a-zก-๙]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def similarity(left: str, right: str) -> float:
    a, b = normalize_for_similarity(left), normalize_for_similarity(right)
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def recent_files(directory: Path, current: Path, limit: int = 12) -> list[Path]:
    if not directory.exists():
        return []
    files = [p for p in directory.glob("*.md") if p.resolve() != current.resolve()]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def validate(body_path: Path, evidence_path: Path, archive_dir: Path, evidence_dir: Path) -> list[str]:
    errors: list[str] = []
    body = body_path.read_text(encoding="utf-8")
    evidence = evidence_path.read_text(encoding="utf-8")
    header, raw_items = split_body_items(body)
    no_event = raw_items == [NO_EVENT_TEXT]
    items = [] if no_event else raw_items
    evidence_items = parse_evidence(evidence)

    if not header.startswith("🐦 X Investment Update — รอบ"):
        errors.append("invalid or missing brief header")
    if not items and not no_event:
        errors.append("brief has no event items")
    if no_event and not re.search(r"(?im)^\s*-?\s*result\s*:\s*NO_MATERIAL_EVENT\s*$", evidence):
        errors.append("no-event brief requires `result: NO_MATERIAL_EVENT` in evidence")
    if len(items) > MAX_ITEMS:
        errors.append(f"too many items: {len(items)} > {MAX_ITEMS}")
    if len(evidence_items) != len(items):
        errors.append(f"evidence count {len(evidence_items)} does not match body count {len(items)}")

    if URL_RE.search(body):
        errors.append("Telegram body contains a URL")
    if "#" in body:
        errors.append("Telegram body contains a hashtag or markdown heading")
    if CJK_RE.search(body):
        errors.append("Telegram body contains CJK characters")

    for phrase in BANNED_THAI_PHRASES:
        if phrase in body:
            errors.append(f"banned AI-writing phrase: {phrase}")
    if body.count("แปลว่า") > 2:
        errors.append("repetitive translated phrasing: 'แปลว่า' appears more than twice")

    for index, item in enumerate(items, 1):
        if not (MIN_ITEM_CHARS <= len(item) <= MAX_ITEM_CHARS):
            errors.append(f"item {index} length {len(item)} outside {MIN_ITEM_CHARS}-{MAX_ITEM_CHARS}")
        if item.count("\n") < 1:
            errors.append(f"item {index} must use a headline line plus a separate explanation line")

    keys = [item.event_key for item in evidence_items]
    if len(keys) != len(set(keys)):
        errors.append("duplicate event_key inside current evidence")
    for index, item in enumerate(evidence_items, 1):
        if not item.urls:
            errors.append(f"evidence item {index} has no exact x.com URL")
        if item.status == "UPDATE" and (
            len(item.material_update) < 20 or item.material_update.lower() in {"n/a", "none", "-"}
        ):
            errors.append(f"UPDATE item {index} lacks a specific material_update")

    prior_event_keys: set[str] = set()
    for path in recent_files(evidence_dir, evidence_path):
        try:
            prior_event_keys.update(item.event_key for item in parse_evidence(path.read_text(encoding="utf-8")))
        except OSError:
            continue
    for index, item in enumerate(evidence_items, 1):
        if item.event_key in prior_event_keys and item.status != "UPDATE":
            errors.append(f"item {index} reuses prior event_key as NEW: {item.event_key}")

    prior_items: list[tuple[Path, str]] = []
    for path in recent_files(archive_dir, body_path):
        try:
            _, archived = split_body_items(path.read_text(encoding="utf-8"))
            prior_items.extend((path, text) for text in archived)
        except OSError:
            continue
    for index, item in enumerate(items, 1):
        status = evidence_items[index - 1].status if index <= len(evidence_items) else "NEW"
        if status == "UPDATE":
            continue
        best = max(((similarity(item, old), path) for path, old in prior_items), default=(0.0, None))
        if best[0] >= DUPLICATE_SIMILARITY:
            errors.append(
                f"item {index} resembles prior brief ({best[0]:.2f}) in {best[1].name if best[1] else 'archive'}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--body", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--archive-dir", type=Path, default=Path("x-digests"))
    parser.add_argument("--evidence-dir", type=Path, default=Path("x-digests/sources"))
    args = parser.parse_args()

    try:
        errors = validate(args.body, args.evidence, args.archive_dir, args.evidence_dir)
    except (OSError, UnicodeError) as exc:
        print(f"FAILED: cannot read QA input: {exc}", file=sys.stderr)
        return 2

    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    _, raw_items = split_body_items(args.body.read_text(encoding="utf-8"))
    count = 0 if raw_items == [NO_EVENT_TEXT] else len(raw_items)
    print(f"PASS: {count} unique event items; evidence and Thai QA complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
