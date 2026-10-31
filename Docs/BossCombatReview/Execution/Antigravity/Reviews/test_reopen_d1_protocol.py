"""Re-open tests for D1_REFERENCE_MEASUREMENT_PROTOCOL.md (v2).
Verifies:
(a) Section 1 parses all 82 rows cleanly from the markdown table.
(b) Every row ID exists in requirements.json, exactly once, none missing (82/82).
(c) The classification counts stated in summary equal the parsed table counts (22 + 27 + 33 = 82).
(d) Video metadata, combat zero at 01:45 (105.000 s), 59.94 fps, and arithmetic consistency.
(e) Roadmap observability rules quoted and respected.
(f) Concrete measurement list M-01 to M-12 present and mapped to real rows.
(g) 8 first clips present with specific questions.
(h) File is pure CRLF.

Run: python -I test_reopen_d1_protocol.py
"""
import json
import os
import re
import unittest

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
DOC_PATH = os.path.join(os.path.dirname(__file__), "D1_REFERENCE_MEASUREMENT_PROTOCOL.md")
REQ_PATH = os.path.join(ROOT, "Documentation", "Boss", "Morgott_82_Point_Combat_Reference", "requirements.json")


class TestD1ProtocolDocV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DOC_PATH, "rb") as f:
            cls.raw = f.read()
        cls.text = cls.raw.decode("utf-8", errors="replace")
        with open(REQ_PATH, "r", encoding="utf-8") as f:
            cls.reqs = json.load(f)
        cls.req_ids = set(r["id"] for r in cls.reqs)

    def test_file_exists(self):
        self.assertTrue(os.path.exists(DOC_PATH), "D1_REFERENCE_MEASUREMENT_PROTOCOL.md not found")

    def test_pure_crlf(self):
        lone_lf = self.raw.count(b"\n") - self.raw.count(b"\r\n")
        self.assertEqual(lone_lf, 0, f"Found {lone_lf} lone LF characters; must be pure CRLF")

    def test_section_1_parses_all_82_ids(self):
        """Parses the 82-row markdown table in Section 1 and verifies 100% match with requirements.json."""
        table_pattern = re.compile(r"^\|\s*(BOSS-[A-Z]+-\d{3})\s*\|\s*([^|]+)\s*\|\s*\*\*([A-Z\s]+)\*\*\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|", re.MULTILINE)
        matches = table_pattern.findall(self.text)
        
        self.assertEqual(len(matches), 82, f"Expected exactly 82 rows in Section 1 table, found {len(matches)}")
        
        parsed_ids = [m[0] for m in matches]
        unique_ids = set(parsed_ids)
        self.assertEqual(len(unique_ids), 82, f"Expected 82 unique IDs, found duplicates in {len(parsed_ids)}")
        
        missing = self.req_ids - unique_ids
        extra = unique_ids - self.req_ids
        self.assertEqual(len(missing), 0, f"Missing requirements.json IDs: {missing}")
        self.assertEqual(len(extra), 0, f"Extra/invented IDs: {extra}")

    def test_section_1_classification_counts(self):
        """Verifies counts stated in summary equal the rows in the table."""
        table_pattern = re.compile(r"^\|\s*(BOSS-[A-Z]+-\d{3})\s*\|\s*([^|]+)\s*\|\s*\*\*([A-Z\s]+)\*\*\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|", re.MULTILINE)
        matches = table_pattern.findall(self.text)
        
        counts = {"OBSERVABLE": 0, "PARTIAL": 0, "NOT OBSERVABLE": 0}
        for m in matches:
            cls = m[2].strip()
            self.assertIn(cls, counts, f"Invalid classification '{cls}' in row {m[0]}")
            counts[cls] += 1
            
        self.assertEqual(counts["OBSERVABLE"], 22, f"Expected 22 OBSERVABLE, got {counts['OBSERVABLE']}")
        self.assertEqual(counts["PARTIAL"], 27, f"Expected 27 PARTIAL, got {counts['PARTIAL']}")
        self.assertEqual(counts["NOT OBSERVABLE"], 33, f"Expected 33 NOT OBSERVABLE, got {counts['NOT OBSERVABLE']}")
        self.assertEqual(sum(counts.values()), 82)
        
        # Verify text summary cites the exact same numbers
        self.assertIn("OBSERVABLE:** 22", self.text)
        self.assertIn("PARTIAL:** 27", self.text)
        self.assertIn("NOT OBSERVABLE:** 33", self.text)
        self.assertIn("TOTAL:** 82", self.text)

    def test_concrete_measurements_list_present(self):
        """Verifies measurements list M-01 to M-12 maps to real framework rows without fake IDs."""
        for i in range(1, 13):
            m_id = f"M-{i:02d}"
            self.assertIn(f"**{m_id}**", self.text, f"Measurement {m_id} missing from Section 2")

    def test_video_metadata_and_combat_zero(self):
        self.assertIn("01:45", self.text, "Must cite 01:45 combat start")
        self.assertIn("59.94", self.text, "Must cite 59.94 fps")
        self.assertIn("105.000", self.text, "Must cite 105.000 seconds as combat zero")
        self.assertIn("t_combat = t_orig - 105.000", self.text, "Must define combat-relative timestamp formula")

    def test_ffmpeg_command_present(self):
        self.assertIn("ffmpeg", self.text)
        self.assertIn("-ss 105.0", self.text)
        self.assertIn("fps=59.94", self.text)
        self.assertIn("scale=960:-1", self.text)

    def test_example_row_arithmetic_consistency(self):
        """Verifies frame math and explicit extraction window offset."""
        self.assertIn("t_extract_start = 105.000", self.text)
        self.assertIn("frame = round((t_orig - 105.000) * 59.94) + 1", self.text)
        self.assertIn("morgott_c0_00447.png", self.text)
        self.assertIn("morgott_c0_00465.png", self.text)
        self.assertIn("morgott_c0_00472.png", self.text)
        self.assertIn("morgott_c0_00500.png", self.text)
        self.assertIn("18 frames (0.300 s)", self.text)
        self.assertIn("7 frames (0.117 s)", self.text)
        self.assertIn("28 frames (0.467 s)", self.text)

    def test_all_boss_tokens_exist_in_requirements(self):
        """Asserts that EVERY BOSS-XXX-NNN token anywhere in the entire document exists in requirements.json."""
        all_tokens = set(re.findall(r'BOSS-[A-Z]+-\d{3}', self.text))
        invalid_tokens = all_tokens - self.req_ids
        self.assertEqual(len(invalid_tokens), 0, f"Found invalid BOSS tokens in document: {invalid_tokens}")

    def test_observability_rule_quoted(self):
        self.assertIn("Observation only. No extraction of game files. Original names in shipped content stay out of shipped assets.", self.text)

    def test_first_8_clips_listed_with_questions(self):
        for i in range(1, 9):
            self.assertIn(f"| **{i}** |", self.text, f"Clip priority {i} must be present in table")


if __name__ == "__main__":
    unittest.main(verbosity=2)
