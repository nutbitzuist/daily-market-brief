"""Local test harness.

Modes (set via env vars):
  DRY_RUN=1      → run full pipeline but skip git push & Telegram, print preview
  LIMIT=N        → cap top items to N (default 10) for fast iteration
  USE_FIXTURES=1 → load RSS from tests/fixtures/*.xml offline (no network)

Examples:
  DRY_RUN=1 LIMIT=3 python scripts/test_local.py
  USE_FIXTURES=1 DRY_RUN=1 LIMIT=3 python scripts/test_local.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# default to safe values
os.environ.setdefault("DRY_RUN", "1")
os.environ.setdefault("LIMIT", "3")

from scripts import market_brief  # noqa: E402


if __name__ == "__main__":
    sys.exit(market_brief.run())
