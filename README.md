# 📈 Daily US Market & Economy Brief

ระบบสรุปข่าวตลาดหุ้นสหรัฐและเศรษฐกิจรายวันแบบอัตโนมัติเต็มรูปแบบ — รันบน GitHub Actions ฟรี 100% (ไม่มีบริการเสียเงินแอบแฝง) ส่งไฟล์ Markdown เข้า repo และ Telegram digest ทุกเช้า 06:00 น. (Asia/Bangkok)

## Setup

1. **Fork / clone** repo นี้ (เก็บเป็น public เพื่อใช้ Actions ฟรีไม่จำกัดนาที — ถ้า private ให้ตั้ง spending limit = $0 ที่ Settings → Billing)
2. ตั้งค่า **GitHub Secrets** 3 ตัวที่ Settings → Secrets and variables → Actions:
   - `OPENROUTER_API_KEY` — สมัครฟรีที่ https://openrouter.ai (ไม่ต้องใช้บัตร)
   - `TELEGRAM_BOT_TOKEN` — ขอจาก @BotFather บน Telegram
   - `TELEGRAM_CHAT_ID` — ส่งข้อความใด ๆ ให้บอท แล้วเรียก `https://api.telegram.org/bot<TOKEN>/getUpdates` ดู `chat.id`
3. ไปที่แท็บ **Actions** ของ repo แล้วกด **Enable workflows**

## Schedule rationale

- Cron `0 23 * * *` (UTC) = **06:00 น. ตามเวลาไทย** ทุกวัน
- รันทุกวัน (Mon–Sun) เพราะต้องครอบคลุม:
  - ข่าวหลัง US close (16:00 ET) + after-hours earnings — มี buffer ~2 ชม. ให้ตลาดนิ่งและ feed อัปเดตครบ
  - ข่าว geopolitics / commodity ที่เกิดวันเสาร์–อาทิตย์
  - ข่าวที่ส่งผลต่อ Asia open วันถัดไป

## Manual run

```bash
gh workflow run market-brief.yml
```

หรือกดปุ่ม **Run workflow** ในหน้า Actions UI

## Local test

```bash
pip install -r requirements.txt

# Dry run (ไม่ commit, ไม่ส่ง Telegram), ประมวลผลแค่ 3 ข่าว
DRY_RUN=1 LIMIT=3 python scripts/market_brief.py

# ใช้ fixtures offline (วาง RSS XML ไว้ที่ tests/fixtures/*.xml)
USE_FIXTURES=1 DRY_RUN=1 LIMIT=3 python scripts/market_brief.py

# helper script เซตค่า default ให้
python scripts/test_local.py
```

ต้องตั้ง `OPENROUTER_API_KEY` ใน env ก่อน (จะ skip Telegram ถ้าไม่มี secrets ของมัน)

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│ GitHub Actions cron: 0 23 * * *  (06:00 Asia/Bangkok)          │
└──────────────────────┬─────────────────────────────────────────┘
                       │
              ubuntu-latest runner
                       │
   ┌───────────────────▼────────────────────┐
   │ 15 RSS feeds (Reuters, CNBC, MW, FT,   │
   │ Yahoo, SeekingAlpha, Bloomberg via GN, │
   │ Fed, Treasury, BLS, SEC, …)            │
   └───────────────────┬────────────────────┘
                       │  feedparser, last 24h
   ┌───────────────────▼────────────────────┐
   │ dedupe (URL + difflib > 0.8)           │
   │ score (tier1×3 + tier2×2 + tier3×1     │
   │        + recency bonus +2/+1)          │
   │ pick top 10, max 2/source              │
   └───────────────────┬────────────────────┘
                       │
   ┌───────────────────▼────────────────────┐
   │ Enrich fallback chain:                 │
   │ 1) RSS ≥500 chars                      │
   │ 2) https://r.jina.ai/{url}             │
   │ 3) Wayback snapshot + BeautifulSoup    │
   └───────────────────┬────────────────────┘
                       │
   ┌───────────────────▼────────────────────┐
   │ Pre-extract: $TICKER regex,            │
   │ sector keyword hints                   │
   └───────────────────┬────────────────────┘
                       │
   ┌───────────────────▼────────────────────┐
   │ OpenRouter chat/completions            │
   │ DeepSeek-V4-Flash → GPT-OSS-120B       │
   │   → Gemma-3-27B → Qwen3-Coder          │
   │ STRICT JSON × 10 items, validated      │
   └───────────────────┬────────────────────┘
                       │
   ┌───────────────────▼────────────────────┐
   │ Executive Summary (2nd LLM call,       │
   │ same fallback chain)                   │
   └───────────────────┬────────────────────┘
                       │
   ┌───────────────────▼────────────────────┐
   │ Render briefs/YYYY-MM-DD.md            │
   │ + briefs/latest.md  (YAML front-matter │
   │ + H1 + Exec + 🚨 Alerts + 10 sections) │
   └───────────────────┬────────────────────┘
                       │
              git add / commit / push
                       │
              Telegram digest (MarkdownV2)
```

## Folder layout

```
.github/workflows/market-brief.yml   # cron + workflow_dispatch
scripts/
  market_brief.py     # main orchestrator
  sources.py          # 15 RSS feeds + 3-layer fetch fallback
  classifier.py       # dedupe, score, ticker/sector tagging
  summarizer.py       # OpenRouter call + model fallback chain
  notify.py           # Telegram MarkdownV2 digest
  test_local.py       # DRY_RUN / LIMIT / USE_FIXTURES helper
briefs/               # daily output Markdown files
requirements.txt
README.md
```

## Troubleshooting

- **HTTP 429 from OpenRouter** → fallback chain (DeepSeek-V4-Flash → GPT-OSS-120B → Gemma-3-27B → Qwen3-Coder) จะลองรุ่นถัดไปอัตโนมัติ; DeepSeek-V4-Flash เป็นรุ่น paid (ราคาถูกมาก ~$0.0002/brief) ที่ไม่มี rate limit กวนใจ — รุ่น `:free` เหลือไว้เป็น safety net
- **RSS feed ว่างเปล่า** → เทสต์เดี่ยวด้วย `python -c "import feedparser; print(len(feedparser.parse('URL').entries))"`; บางฟีดอาจย้าย URL — แก้ใน `scripts/sources.py` ตัวแปร `FEEDS`
- **Tickers ผิด / ขาด** → ตรวจ regex `\$[A-Z]{1,5}\b` ใน `scripts/classifier.py:TICKER_RE`; เพิ่ม keyword sector ใน `SECTOR_KEYWORDS`
- **Telegram MarkdownV2 error (`can't parse entities`)** → ตรวจ `escape_mdv2()` ใน `scripts/notify.py` — ทุกตัวอักษรในเซต `_*[]()~\`>#+-=|{}.!\\` ต้องถูก escape
- **Workflow ถูก auto-disable** → GitHub disable scheduled workflow หลัง 60 วันที่ไม่มี commit; การ commit `briefs/` ทุกวันช่วยกัน auto-disable
- **Runner ใช้นาทีเกิน** → ใช้เฉพาะ `ubuntu-latest` (อย่าเปลี่ยนเป็น macOS/Windows/larger ซึ่งกินโควต้าหลายเท่า)

## Cost guarantees

- Repo public → unlimited free Actions minutes
- ใช้แต่ `ubuntu-latest`
- OpenRouter ใช้เฉพาะรุ่น `:free`
- Jina Reader API (`r.jina.ai`) และ Wayback ใช้ฟรีไม่ต้องมี key
- Telegram Bot API ฟรี
