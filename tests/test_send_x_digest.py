from __future__ import annotations

import base64
import unittest

from scripts.send_x_digest import chunk_plain_text, decode_digest


class SendXDigestTests(unittest.TestCase):
    def test_decode_digest_round_trip(self) -> None:
        original = "🐦 ข่าวจาก X\n\n🤖 AI\nหัวข้อ: รายละเอียด"
        encoded = base64.b64encode(original.encode("utf-8")).decode("ascii")
        self.assertEqual(decode_digest(encoded), original)

    def test_decode_digest_rejects_invalid_input(self) -> None:
        with self.assertRaises(ValueError):
            decode_digest("not valid base64!")

    def test_chunks_remain_under_limit_and_round_trip(self) -> None:
        paragraphs = [f"ข่าว {i}: " + ("รายละเอียด " * 35).strip() for i in range(30)]
        original = "\n\n".join(paragraphs)
        chunks = chunk_plain_text(original, limit=500)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 500 for chunk in chunks))
        self.assertEqual("\n\n".join(chunks), original)


if __name__ == "__main__":
    unittest.main()
