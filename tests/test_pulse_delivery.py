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

if __name__ == "__main__":
    unittest.main()
