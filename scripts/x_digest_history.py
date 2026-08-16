"""Print a compact 72-hour event index for X brief research."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from scripts.validate_x_digest import parse_evidence, split_body_items
except ModuleNotFoundError:  # Direct execution: python3 scripts/x_digest_history.py
    from validate_x_digest import parse_evidence, split_body_items


def recent_markdown(directory: Path, hours: int, max_files: int = 4) -> list[Path]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    files: list[Path] = []
    for path in directory.glob("*.md") if directory.exists() else []:
        modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        if modified >= cutoff:
            files.append(path)
    return sorted(files, key=lambda path: path.stat().st_mtime)[-max_files:]


def compact_headline(item: str, limit: int = 180) -> str:
    first_line = item.splitlines()[0].strip()
    headline = first_line.split(" : ", 1)[0].strip()
    return headline if len(headline) <= limit else headline[: limit - 1].rstrip() + "…"


def build_history(archive_dir: Path, evidence_dir: Path, hours: int = 48) -> str:
    lines = [f"X brief event history — last {hours}h"]
    for path in recent_markdown(archive_dir, hours):
        _, items = split_body_items(path.read_text(encoding="utf-8"))
        if not items:
            continue
        lines.append(f"\n[{path.name}]")
        source = evidence_dir / path.name
        evidence = parse_evidence(source.read_text(encoding="utf-8")) if source.exists() else []
        for index, item in enumerate(items, 1):
            headline = compact_headline(item)
            if index <= len(evidence):
                meta = evidence[index - 1]
                lines.append(f"- {meta.event_key} | {meta.status} | {headline}")
            else:
                lines.append(f"- legacy-no-key | {headline}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-dir", type=Path, default=Path("x-digests"))
    parser.add_argument("--evidence-dir", type=Path, default=Path("x-digests/sources"))
    parser.add_argument("--hours", type=int, default=48)
    args = parser.parse_args()
    print(build_history(args.archive_dir, args.evidence_dir, args.hours), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
