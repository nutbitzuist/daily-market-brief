from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_x_digest import NO_EVENT_TEXT, parse_evidence, similarity, validate
from scripts.x_digest_history import build_history


HEADER = "🐦 X Investment Update — รอบ 10:30 — 16 สิงหาคม 2569"


def body_item(headline: str, detail: str) -> str:
    return f"📊 {headline}\n{detail}"


def evidence_item(index: int, key: str, status: str = "NEW", material: str = "n/a") -> str:
    return (
        f"### {index}. Item\n"
        f"- event_key: {key}\n"
        f"- status: {status}\n"
        f"- material_update: {material}\n"
        f"- x_urls:\n  - https://x.com/example/status/{index}\n"
    )


class ValidateXDigestTests(unittest.TestCase):
    def make_workspace(self) -> tuple[Path, Path, Path, Path, tempfile.TemporaryDirectory[str]]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        archive = root / "x-digests"
        sources = archive / "sources"
        archive.mkdir()
        sources.mkdir()
        return root / "body.md", root / "evidence.md", archive, sources, tmp

    def test_valid_new_event_passes(self) -> None:
        body, evidence, archive, sources, tmp = self.make_workspace()
        self.addCleanup(tmp.cleanup)
        detail = "บริษัทปรับ guidance รายได้ไตรมาสหน้าต่ำกว่าที่ตลาดคาด 4% ตลาดจึงลดประมาณการกำไรระยะสั้น จุดต่อไปคือยอดส่งมอบผลิตภัณฑ์ใหม่ในเดือนหน้า"
        body.write_text(HEADER + "\n\n" + body_item("บริษัทลด guidance", detail), encoding="utf-8")
        evidence.write_text(evidence_item(1, "company|guidance-cut|2026-08-16"), encoding="utf-8")
        self.assertEqual(validate(body, evidence, archive, sources), [])

    def test_prior_event_key_must_be_update(self) -> None:
        body, evidence, archive, sources, tmp = self.make_workspace()
        self.addCleanup(tmp.cleanup)
        detail = "บริษัทแจ้งตัวเลขใหม่จากการประชุมนักวิเคราะห์ ตลาดปรับประมาณการกำไรลงและรอดูยอดส่งมอบเดือนหน้าเพื่อยืนยันผลกระทบต่อรายได้"
        body.write_text(HEADER + "\n\n" + body_item("บริษัทชี้แจง guidance เพิ่ม", detail), encoding="utf-8")
        evidence.write_text(evidence_item(1, "company|guidance-cut|2026-08-16"), encoding="utf-8")
        (sources / "prior.md").write_text(evidence_item(1, "company|guidance-cut|2026-08-16"), encoding="utf-8")
        errors = validate(body, evidence, archive, sources)
        self.assertTrue(any("reuses prior event_key as NEW" in error for error in errors))

    def test_material_update_can_reuse_event_key(self) -> None:
        body, evidence, archive, sources, tmp = self.make_workspace()
        self.addCleanup(tmp.cleanup)
        detail = "บริษัทออกประกาศอย่างเป็นทางการและเพิ่มตัวเลขยอดส่งมอบใหม่ ทำให้ประมาณการรายได้เปลี่ยนจากรอบก่อน ตลาดจึงต้องประเมิน margin ใหม่อีกครั้ง"
        body.write_text(HEADER + "\n\n" + body_item("บริษัทเพิ่มข้อมูลใหม่", detail), encoding="utf-8")
        evidence.write_text(
            evidence_item(1, "company|guidance-cut|2026-08-16", "UPDATE", "official shipment figure changed the revenue estimate"),
            encoding="utf-8",
        )
        (sources / "prior.md").write_text(evidence_item(1, "company|guidance-cut|2026-08-16"), encoding="utf-8")
        self.assertEqual(validate(body, evidence, archive, sources), [])

    def test_obvious_cross_slot_duplicate_fails(self) -> None:
        body, evidence, archive, sources, tmp = self.make_workspace()
        self.addCleanup(tmp.cleanup)
        detail = "บริษัทปรับ guidance รายได้ไตรมาสหน้าต่ำกว่าที่ตลาดคาด 4% ตลาดจึงลดประมาณการกำไรระยะสั้น จุดต่อไปคือยอดส่งมอบผลิตภัณฑ์ใหม่ในเดือนหน้า"
        item = body_item("บริษัทลด guidance", detail)
        body.write_text(HEADER + "\n\n" + item, encoding="utf-8")
        evidence.write_text(evidence_item(1, "company|guidance-new|2026-08-16"), encoding="utf-8")
        (archive / "prior.md").write_text(HEADER + "\n\n" + item, encoding="utf-8")
        errors = validate(body, evidence, archive, sources)
        self.assertTrue(any("resembles prior brief" in error for error in errors))

    def test_ai_phrase_and_repetitive_translation_fail(self) -> None:
        body, evidence, archive, sources, tmp = self.make_workspace()
        self.addCleanup(tmp.cleanup)
        detail = "สะท้อนให้เห็นว่าตลาดกังวล แปลว่ากำไรอาจลด แปลว่าราคายังเสี่ยง แปลว่าต้องรอตัวเลขใหม่ในเดือนหน้าเพื่อยืนยันแนวโน้มรายได้และ margin"
        body.write_text(HEADER + "\n\n" + body_item("ตลาดกังวล", detail), encoding="utf-8")
        evidence.write_text(evidence_item(1, "market|concern|2026-08-16"), encoding="utf-8")
        errors = validate(body, evidence, archive, sources)
        self.assertTrue(any("banned AI-writing phrase" in error for error in errors))
        self.assertTrue(any("แปลว่า" in error for error in errors))

    def test_no_material_event_receipt_passes(self) -> None:
        body, evidence, archive, sources, tmp = self.make_workspace()
        self.addCleanup(tmp.cleanup)
        body.write_text(HEADER + "\n\n" + NO_EVENT_TEXT, encoding="utf-8")
        evidence.write_text("# Evidence\n- result: NO_MATERIAL_EVENT\n", encoding="utf-8")
        self.assertEqual(validate(body, evidence, archive, sources), [])

    def test_history_lists_legacy_and_keyed_events(self) -> None:
        body, evidence, archive, sources, tmp = self.make_workspace()
        self.addCleanup(tmp.cleanup)
        detail = "บริษัทออกประกาศตัวเลขใหม่และตลาดปรับประมาณการกำไรลง จุดที่ต้องติดตามคือยอดส่งมอบเดือนหน้าและผลต่อ margin ของธุรกิจหลัก"
        archived = archive / "2026-08-16-slot.md"
        archived.write_text(HEADER + "\n\n" + body_item("บริษัทลด guidance", detail), encoding="utf-8")
        (sources / archived.name).write_text(evidence_item(1, "company|guidance-cut|2026-08-16"), encoding="utf-8")
        history = build_history(archive, sources)
        self.assertIn("company|guidance-cut|2026-08-16 | NEW", history)
        self.assertIn("บริษัทลด guidance", history)

    def test_parser_and_similarity(self) -> None:
        parsed = parse_evidence(evidence_item(1, "NVDA|guidance|2026-08-16"))
        self.assertEqual(parsed[0].event_key, "nvda|guidance|2026-08-16")
        self.assertGreater(similarity("Nvidia ลด guidance 4%", "Nvidia ลด guidance 4%"), 0.99)


if __name__ == "__main__":
    unittest.main()
