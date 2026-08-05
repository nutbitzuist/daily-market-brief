#!/usr/bin/env python3
"""Silent watchdog for the daily X morning Telegram delivery.

Empty stdout means healthy. A concise stdout alert is delivered to Nut by Hermes cron.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

REPO = "nutbitzuist/daily-market-brief"
WORKFLOW = "x-morning-news.yml"
BANGKOK = ZoneInfo("Asia/Bangkok")


def gh(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args],
        text=True,
        capture_output=True,
        timeout=45,
    )


def alert(message: str) -> int:
    print(f"⚠️ X morning news: {message}")
    return 0


def main() -> int:
    date_bkk = os.environ.get("CHECK_DATE_BKK") or datetime.now(BANGKOK).date().isoformat()
    result = gh(
        "run", "list", "-R", REPO,
        "--workflow", WORKFLOW,
        "--event", "workflow_dispatch",
        "--limit", "5",
        "--json", "status,conclusion,createdAt",
    )
    if result.returncode != 0:
        return alert("ตรวจสอบ GitHub ไม่สำเร็จ — เช็กการเชื่อมต่อหรือ GitHub auth")

    try:
        runs = json.loads(result.stdout)
    except json.JSONDecodeError:
        return alert("GitHub ส่งสถานะที่อ่านไม่ได้")

    todays_runs = []
    for run in runs:
        try:
            created = datetime.fromisoformat(run["createdAt"].replace("Z", "+00:00"))
        except (KeyError, ValueError):
            continue
        if created.astimezone(BANGKOK).date().isoformat() == date_bkk:
            todays_runs.append(run)

    if not todays_runs:
        return alert(f"ยังไม่พบงานส่งข่าววันที่ {date_bkk}")

    latest = todays_runs[0]
    if latest.get("status") != "completed":
        return alert(f"งานวันที่ {date_bkk} ยังทำไม่เสร็จหลังเวลาเป้าหมาย")
    if latest.get("conclusion") != "success":
        return alert(f"ส่งข่าววันที่ {date_bkk} ไม่สำเร็จ — Jax ต้องซ่อมและรันใหม่")

    artifact = gh("api", f"repos/{REPO}/contents/x-digests/{date_bkk}.md")
    if artifact.returncode != 0:
        return alert(f"ส่งสำเร็จแต่ไม่พบไฟล์ยืนยันวันที่ {date_bkk}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (subprocess.TimeoutExpired, OSError):
        sys.exit(alert("ตัวตรวจสอบทำงานไม่สำเร็จ"))
