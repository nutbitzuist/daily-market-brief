from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from scripts import jev_screen


class JevScreenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.articles = [
            {"title": "Fed changes rates", "source_name": "Federal Reserve", "link": "https://a"},
            {"title": "Best beach snacks", "source_name": "Lifestyle", "link": "https://b"},
            {"title": "Possible tariff change", "source_name": "News", "link": "https://c"},
        ]

    def _result(self) -> dict:
        return {
            "model": "jev-test",
            "answers": {
                "candidate_000": {
                    "choice": "include", "confidence": 0.98,
                    "probabilities": {"include": 0.98, "review": 0.01, "exclude": 0.01},
                },
                "candidate_001": {
                    "choice": "exclude", "confidence": 0.99,
                    "probabilities": {"include": 0.0, "review": 0.01, "exclude": 0.99},
                },
                "candidate_002": {
                    "choice": "exclude", "confidence": 0.60,
                    "probabilities": {"include": 0.20, "review": 0.20, "exclude": 0.60},
                },
            },
            "usage": {"input_tokens": 100, "output_tokens": 30},
        }

    @patch.dict(os.environ, {"JEV_SCREEN_MODE": "active", "TYPESAFE_API_KEY": "test-key"}, clear=False)
    @patch("scripts.jev_screen._request")
    def test_active_only_drops_high_confidence_exclude(self, request) -> None:
        request.return_value = self._result()
        kept, report = jev_screen.screen_articles(self.articles, "us", min_keep=2)
        self.assertEqual([a["link"] for a in kept], ["https://a", "https://c"])
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["high_confidence_excluded"], 1)

    @patch.dict(os.environ, {"JEV_SCREEN_MODE": "shadow", "TYPESAFE_API_KEY": "test-key"}, clear=False)
    @patch("scripts.jev_screen._request")
    def test_shadow_records_without_filtering(self, request) -> None:
        request.return_value = self._result()
        kept, report = jev_screen.screen_articles(self.articles, "us", min_keep=2)
        self.assertEqual(kept, self.articles)
        self.assertEqual(report["high_confidence_excluded"], 1)

    @patch.dict(os.environ, {"JEV_SCREEN_MODE": "active", "TYPESAFE_API_KEY": "test-key"}, clear=False)
    @patch("scripts.jev_screen._request")
    def test_minimum_output_floor_restores_best_excluded(self, request) -> None:
        result = self._result()
        result["answers"]["candidate_002"] = {
            "choice": "exclude", "confidence": 0.95,
            "probabilities": {"include": 0.30, "review": 0.05, "exclude": 0.65},
        }
        request.return_value = result
        kept, _ = jev_screen.screen_articles(self.articles, "us", min_keep=2)
        self.assertEqual([a["link"] for a in kept], ["https://a", "https://c"])

    @patch.dict(os.environ, {"JEV_SCREEN_MODE": "active", "TYPESAFE_API_KEY": "test-key"}, clear=False)
    @patch("scripts.jev_screen._request", side_effect=RuntimeError("temporary outage"))
    def test_api_failure_fails_open(self, _request) -> None:
        kept, report = jev_screen.screen_articles(self.articles, "us", min_keep=2)
        self.assertEqual(kept, self.articles)
        self.assertEqual(report["status"], "fail_open_error")

    @patch.dict(os.environ, {"JEV_SCREEN_MODE": "off"}, clear=False)
    def test_off_does_not_call_api(self) -> None:
        kept, report = jev_screen.screen_articles(self.articles, "us", min_keep=2)
        self.assertEqual(kept, self.articles)
        self.assertEqual(report["status"], "disabled")


if __name__ == "__main__":
    unittest.main()
