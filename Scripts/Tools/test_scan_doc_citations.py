"""test_scan_doc_citations.py - Unit tests for Lane A Citation Scanner (Evidence Rule C-932)."""

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from scan_doc_citations import line_has_citation, scan_file


class TestScanDocCitations(unittest.TestCase):
    def test_line_has_citation_detects_proposals_and_files(self):
        self.assertTrue(line_has_citation(["This is a 95% alignment [PROPOSAL]."]))
        self.assertTrue(line_has_citation(["Source/OneBossFight/Boss.cpp:20", "Value is 50 ms"]))
        self.assertTrue(line_has_citation(["See evidence/B_C928 for 60 FPS profile."]))
        self.assertTrue(line_has_citation(["Dilation clamped via CVar rpg.Parry."]))
        self.assertFalse(line_has_citation(["This hits for 50 ms and 95% with no source."]))

    def test_scan_file_flags_uncited_claims(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".md", delete=False) as f:
            f.write("# Test Doc\n\nThe attack has 80 ms latency and 95% alignment without proof.\n")
            temp_path = Path(f.name)

        try:
            findings = scan_file(temp_path)
            self.assertEqual(len(findings), 1)
            line_num, match_str, text = findings[0]
            self.assertEqual(line_num, 3)
            self.assertIn("80 ms", match_str)
            self.assertIn("95%", match_str)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_scan_file_cleans_cited_claims(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".md", delete=False) as f:
            f.write(
                "# Test Doc\n**Sources:** Source/OneBossFight/Test.cpp\n\nThe attack has 80 ms latency and 95% alignment.\n"
            )
            temp_path = Path(f.name)

        try:
            findings = scan_file(temp_path)
            self.assertEqual(len(findings), 0)
        finally:
            if temp_path.exists():
                temp_path.unlink()


if __name__ == "__main__":
    unittest.main()
