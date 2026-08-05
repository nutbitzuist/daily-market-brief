#!/usr/bin/env python3
"""Silent watchdog for the four-times-daily X investment delivery.

Empty stdout means healthy. A concise stdout alert is delivered to Nut by Hermes cron.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, time
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
    print(f"⚠️ X Intelligence Brief: {message}")
    return 0


def main() -> int:
    now_bkk = datetime.now(BANGKOK)
    date_bkk = os.environ.get("CHECK_DATE_BKK") or now_bkk.date().isoformat()
    forced_slot = os.environ.get("CHECK_SLOT")
    slot_starts = {
        "open-0500": time(4, 45),
        "thai-am-1030": time(10, 15),
        "thai-close-1500": time(14, 45),
        "us-open-1930": time(19, 15),
    }
    if forced_slot:
        if forced_slot not in slot_starts:
            return alert(f"invalid CHECK_SLOT {forced_slot!r}")
        slot = forced_slot
    elif now_bkk.hour < 8:
        slot = "open-0500"
    elif now_bkk.hour < 13:
        slot = "thai-am-1030"
    elif now_bkk.hour < 17:
        slot = "thai-close-1500"
    else:
        slot = "us-open-1930"
    start_time = slot_starts[slot]
    slot_date = datetime.strptime(date_bkk, "%Y-%m-%d").date()
    slot_start = datetime.combine(slot_date, start_time, BANGKOK)
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
        created_bkk = created.astimezone(BANGKOK)
        if created_bkk.date().isoformat() == date_bkk and created_bkk >= slot_start:
            todays_runs.append(run)

    if not todays_runs:
        return alert(f"ยังไม่พบงานรอบ {slot} วันที่ {date_bkk}")

    latest = todays_runs[0]
    if latest.get("status") != "completed":
        return alert(f"งานรอบ {slot} วันที่ {date_bkk} ยังทำไม่เสร็จ")
    if latest.get("conclusion") != "success":
        return alert(f"ส่งข่าวรอบ {slot} วันที่ {date_bkk} ไม่สำเร็จ — Jax ต้องซ่อมและรันใหม่")

    artifact = gh("api", f"repos/{REPO}/contents/x-digests/{date_bkk}-{slot}.md")
    if artifact.returncode != 0:
        return alert(f"ส่งสำเร็จแต่ไม่พบไฟล์ยืนยันวันที่ {date_bkk}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (subprocess.TimeoutExpired, OSError):
        sys.exit(alert("ตัวตรวจสอบทำงานไม่สำเร็จ"))
