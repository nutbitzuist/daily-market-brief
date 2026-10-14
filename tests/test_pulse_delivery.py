"""Delivery acceptance: stale data, false green, and duplicate controls."""
import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, Mock
from zoneinfo import ZoneInfo
from scripts import th_market_pulse as pulse
from scripts.trackers._base import TrackerResult


class DeliveryTests(unittest.TestCase):
    def test_rejected_telegram_is_not_success(self):
        response = Mock(status_code=403)
        response.json.return_value = {"ok": False}
        with patch.dict(os.environ, TELEGRAM_BOT_TOKEN="test", TELEGRAM_CHAT_ID="1"), patch.object(pulse.requests, "post", return_value=response):
            with self.assertRaises(RuntimeError):
                pulse.send_pulse_digest("2026-10-14", {}, "test", "test")

    def test_missing_credentials_fail(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                pulse.send_pulse_digest("2026-10-14", {}, "test", "test")

    def test_confirmed_delivery_receipt(self):
        response = Mock(status_code=200)
        response.json.return_value = {"ok": True, "result": {"chat": {"id": 1}, "message_id": 123}}
        with tempfile.TemporaryDirectory() as folder, patch.object(pulse, "PULSE_DIR", Path(folder)), patch.dict(os.environ, TELEGRAM_BOT_TOKEN="test", TELEGRAM_CHAT_ID="1"), patch.object(pulse.requests, "post", return_value=response):
            pulse.send_pulse_digest("2026-10-14", {}, "test", "test")
            receipt = json.loads((Path(folder) / "2026-10-14.delivery.json").read_text())
            self.assertEqual(receipt["message_ids"], [123])

    def test_duplicate_never_collects_or_sends(self):
        today = datetime.now(ZoneInfo("Asia/Bangkok")).date().isoformat()
        with tempfile.TemporaryDirectory() as folder, patch.object(pulse, "PULSE_DIR", Path(folder)), patch.dict(os.environ, DRY_RUN="0"), patch.object(pulse, "run_all") as collect:
            (Path(folder) / f"{today}.delivery.json").write_text('{"delivered": true, "complete": true}')
            self.assertEqual(pulse.run(), 0)
            collect.assert_not_called()

    def test_stale_source_never_sends(self):
        data = {name: TrackerResult(name=name, ok=True, summary="stale", data={"date": "2000-01-01"}) for name, _ in pulse.TRACKERS}
        with tempfile.TemporaryDirectory() as folder, patch.object(pulse, "PULSE_DIR", Path(folder)), patch.object(pulse, "run_all", return_value=data), patch.object(pulse, "send_pulse_digest") as send:
            self.assertEqual(pulse.run(), 0)
            send.assert_not_called()

    def test_next_morning_keeps_trading_session_date(self):
        from datetime import timezone
        source_date = "2026-10-14"
        next_morning = datetime(2026, 10, 15, 0, 30, tzinfo=timezone.utc)
        data = {name: TrackerResult(name=name, ok=True, summary="verified", data={"date": source_date}) for name, _ in pulse.TRACKERS}
        with tempfile.TemporaryDirectory() as folder, patch.object(pulse, "PULSE_DIR", Path(folder)), patch.dict(os.environ, PULSE_SESSION_DATE=source_date, DRY_RUN="0"), patch.object(pulse, "datetime") as clock, patch.object(pulse, "run_all", return_value=data), patch.object(pulse.summarizer, "th_market_pulse_commentary", return_value=("Verified commentary", "test")), patch.object(pulse, "send_pulse_digest") as send:
            clock.now.return_value = next_morning
            self.assertEqual(pulse.run(), 0)
            self.assertEqual(send.call_args.args[0], source_date)
            self.assertTrue((Path(folder) / "2026-10-14.md").exists())

if __name__ == "__main__":
    unittest.main()
