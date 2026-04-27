"""Daily Thai Market Pulse — runs 18:00 Asia/Bangkok = 11:00 UTC, Mon-Fri.

Bundles 3 Thai-specific institutional positioning signals into one
post-close digest:
  1. SET investor-type net flow proxy (NVDR-based foreign flow)
  2. SET short-sale daily rank + DoD movers
  3. NVDR top net buy / top net sell

Runs each tracker independently (graceful degradation if any single
endpoint breaks), feeds combined data to a top-1% institutional sales
prompt, and pushes the commentary + raw highlights to Telegram.
"""
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import notify, summarizer  # noqa: E402
from scripts.trackers import (  # noqa: E402
    set_investor_type, set_nvdr, set_short,
)
from scripts.trackers._base import TrackerResult  # noqa: E402

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("th_market_pulse")

REPO_URL = os.environ.get("REPO_URL", "https://github.com/USERNAME/REPO")
PULSE_DIR = ROOT / "pulse"

TRACKERS = [
    ("set_investor_type", set_investor_type.run),
    ("set_short", set_short.run),
    ("set_nvdr", set_nvdr.run),
]


def run_all() -> dict[str, TrackerResult]:
    results: dict[str, TrackerResult] = {}
    for name, fn in TRACKERS:
        try:
            log.info("running tracker %s", name)
            results[name] = fn()
            log.info("[%s] ok=%s summary=%s",
                     name, results[name].ok, results[name].summary)
        except Exception as e:  # pragma: no cover - defensive
            log.exception("tracker %s crashed", name)
            results[name] = TrackerResult(
                name=name, ok=False,
                summary=f"({name} crashed)", error=str(e),
            )
    return results


# ---------- render markdown ----------

def _section_md(title: str, r: TrackerResult) -> list[str]:
    out = [f"## {title}"]
    if not r.ok:
        out.append(f"_⚠️ {r.summary}_")
        if r.error:
            out.append(f"_error: {r.error}_")
        return out
    out.append(r.summary)
    out.append("")
    out.append("```json")
    out.append(json.dumps(r.data, ensure_ascii=False, indent=2)[:2500])
    out.append("```")
    return out


def render_md(date_str: str, generated_at: str, model_used: str,
              results: dict[str, TrackerResult], commentary: str) -> str:
    lines: list[str] = []
    lines.append("---")
    lines.append(f"date: {date_str}")
    lines.append(f"generated_at_utc: {generated_at}")
    lines.append(f"model_used: {model_used}")
    n_ok = sum(1 for r in results.values() if r.ok)
    lines.append(f"trackers_ok: {n_ok}/{len(results)}")
    lines.append("---")
    lines.append("")
    lines.append(f"# 🇹🇭 Thai Market Pulse — {date_str}")
    lines.append("")
    lines.append(commentary.strip())
    lines.append("")
    lines += _section_md("1. SET Investor-Type Flow",
                         results["set_investor_type"])
    lines.append("")
    lines += _section_md("2. SET Short-Sale Ranking", results["set_short"])
    lines.append("")
    lines += _section_md("3. NVDR Daily Flow", results["set_nvdr"])
    lines.append("")
    return "\n".join(lines)


# ---------- telegram digest ----------

def build_pulse_digest(date_str: str, results: dict[str, TrackerResult],
                       commentary: str, repo_url: str) -> str:
    esc = notify.escape_mdv2
    lines: list[str] = []
    lines.append(f"🇹🇭 *Thai Market Pulse — {esc(date_str)}*")
    lines.append("")
    if commentary.strip():
        lines.append(esc(commentary.strip()))
        lines.append("")

    section_titles = {
        "set_investor_type": "Investor\\-Type Flow",
        "set_short": "Top Short Interest",
        "set_nvdr": "NVDR Flow",
    }
    for key, title in section_titles.items():
        r = results.get(key)
        if not r:
            continue
        emoji = "✅" if r.ok else "⚠️"
        lines.append(f"{emoji} *{title}*")
        lines.append(esc(r.summary))
        lines.append("")

    full_url = f"{repo_url}/blob/main/pulse/{date_str}.md"
    lines.append(f"📎 Detail: {esc(full_url)}")
    return "\n".join(lines)


def send_pulse_digest(date_str: str, results: dict[str, TrackerResult],
                      commentary: str, repo_url: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log.warning("Telegram secrets missing; skipping notify")
        return
    text = build_pulse_digest(date_str, results, commentary, repo_url)
    for chunk in notify._chunk(text):
        notify._send(token, chat_id, chunk)


# ---------- main ----------

def run() -> int:
    dry_run = os.environ.get("DRY_RUN") == "1"
    now_utc = datetime.now(timezone.utc)
    date_str = now_utc.strftime("%Y-%m-%d")
    generated_at = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    results = run_all()
    n_ok = sum(1 for r in results.values() if r.ok)
    log.info("trackers ok: %d/%d", n_ok, len(results))

    # Build LLM input
    pulse_data = {k: (r.data if r.ok else {"unavailable": r.summary,
                                            "error": r.error})
                  for k, r in results.items()}

    if n_ok == 0:
        commentary = "ระบบดึงข้อมูล SET ไม่สำเร็จทุกแหล่งวันนี้ — ข้ามการวิเคราะห์"
        model_used = "none"
    else:
        try:
            commentary, model_used = summarizer.th_market_pulse_commentary(
                pulse_data)
        except Exception as e:  # noqa: BLE001 - LLM fallback
            log.error("LLM commentary failed (all models): %s", e)
            commentary = (
                "⚠️ LLM commentary unavailable today "
                "(all models failed — check OPENROUTER_API_KEY). "
                "Raw tracker data below."
            )
            model_used = "none"

    PULSE_DIR.mkdir(exist_ok=True)
    out_path = PULSE_DIR / f"{date_str}.md"
    latest = PULSE_DIR / "latest.md"

    md = render_md(date_str, generated_at, model_used, results, commentary)

    if dry_run:
        print("=== DRY RUN — would write", out_path, "===")
        print(md[:3500])
        print("\n=== Telegram preview ===")
        print(build_pulse_digest(date_str, results, commentary, REPO_URL))
        return 0

    out_path.write_text(md, encoding="utf-8")
    latest.write_text(md, encoding="utf-8")
    log.info("wrote %s and %s", out_path, latest)

    send_pulse_digest(date_str, results, commentary, REPO_URL)
    # Always exit 0 even if some trackers failed — partial data is still useful
    return 0


if __name__ == "__main__":
    sys.exit(run())
