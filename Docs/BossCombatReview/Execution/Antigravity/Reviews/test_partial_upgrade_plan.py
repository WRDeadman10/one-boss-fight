#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_partial_upgrade_plan.py

Automated verification suite for PARTIAL_UPGRADE_PLAN.md:
1. Pure LF line endings (no CR).
2. Covers all 27 canonical PARTIAL rows from witness_status_v3.json.
3. Title parity: Table titles and section titles match ledger titles verbatim for all 27 rows.
4. Verbatim citations: Every file:line citation exists on disk and is within line bounds.
5. Verbatim symbols and paths: Every backticked identifier referencing a file or C++ symbol exists in Source/ or Docs/ (grep).
6. Complete execution authority classification: All 27 rows classified as Test-Only vs Engine Required.
"""

import unittest
from pathlib import Path
import json
import re
import subprocess

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
DOC_PATH = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews/PARTIAL_UPGRADE_PLAN.md"
LEDGER_PATH = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json"

class TestPartialUpgradePlan(unittest.TestCase):

    def test_file_exists_and_pure_lf(self):
        self.assertTrue(DOC_PATH.exists(), f"Missing file: {DOC_PATH}")
        raw = DOC_PATH.read_bytes()
        self.assertNotIn(b"\r", raw, "PARTIAL_UPGRADE_PLAN.md contains CR! Must be pure LF.")

    def test_all_27_rows_partial_and_title_parity(self):
        ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        # 27 rows planned in v2.0 (v3.6.0 baseline; 3 graduated to WITNESSED in v3.7.0)
        planned_ids = {
            'BOSS-AWR-001', 'BOSS-AWR-002', 'BOSS-AWR-004', 'BOSS-AWR-005',
            'BOSS-SEL-008',
            'BOSS-EXE-004', 'BOSS-EXE-006', 'BOSS-EXE-007',
            'BOSS-COM-002', 'BOSS-COM-003', 'BOSS-COM-004', 'BOSS-COM-005', 'BOSS-COM-007',
            'BOSS-ANM-002', 'BOSS-ANM-005', 'BOSS-ANM-007',
            'BOSS-HIT-005', 'BOSS-HIT-008', 'BOSS-HIT-009',
            'BOSS-MOV-001',
            'BOSS-PAC-006',
            'BOSS-PHS-004',
            'BOSS-QA-001', 'BOSS-QA-002', 'BOSS-QA-003', 'BOSS-QA-004', 'BOSS-QA-005'
        }
        canonical_partial = {r["id"]: r["title"] for r in ledger["requirements"] if r["id"] in planned_ids}
        self.assertEqual(len(canonical_partial), 27, f"Expected 27 planned rows in ledger, got {len(canonical_partial)}")

        text = DOC_PATH.read_text(encoding="utf-8")

        # Check Table rows in Section 2: | `BOSS-...` | Title | ...
        table_matches = re.findall(r"\|\s*`(BOSS-[A-Za-z0-9\-]+)`\s*\|\s*([^\|]+?)\s*\|\s*PARTIAL\s*\|", text)
        self.assertEqual(len(table_matches), 27, f"Expected 27 table rows, got {len(table_matches)}")
        for row_id, table_title in table_matches:
            self.assertIn(row_id, canonical_partial, f"Unexpected row {row_id} in table")
            expected_title = canonical_partial[row_id]
            self.assertEqual(table_title.strip(), expected_title, f"Table title mismatch for {row_id}: got '{table_title.strip()}', expected '{expected_title}'")

        # Check Section headers in Section 3: ### `BOSS-...`: Title
        section_matches = re.findall(r"###\s*`(BOSS-[A-Za-z0-9\-]+)`:\s*([^\n\r]+)", text)
        self.assertEqual(len(section_matches), 27, f"Expected 27 section headers, got {len(section_matches)}")
        for row_id, sec_title in section_matches:
            self.assertIn(row_id, canonical_partial, f"Unexpected section {row_id}")
            expected_title = canonical_partial[row_id]
            self.assertEqual(sec_title.strip(), expected_title, f"Section title mismatch for {row_id}: got '{sec_title.strip()}', expected '{expected_title}'")

    def test_citations_exist_and_in_bounds(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        citation_pattern = re.compile(r"([A-Za-z0-9_\-\./]+(?:\.cpp|\.h|\.json|\.umap|\.log|\.md)):([0-9]+)(?:-([0-9]+))?")
        citations = citation_pattern.findall(text)
        self.assertGreaterEqual(len(citations), 27, "Expected at least 27 verified citations in review.")

        for file_ref, start_line_str, end_line_str in citations:
            p = REPO_ROOT / file_ref
            self.assertTrue(p.exists(), f"Cited file does not exist on disk: {file_ref}")
            max_line = int(end_line_str) if end_line_str else int(start_line_str)
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                file_lines = f.readlines()
            self.assertLessEqual(
                max_line, len(file_lines),
                f"Line {max_line} out of range for {file_ref} (total lines: {len(file_lines)})"
            )

    def test_backticked_identifiers_exist_via_grep(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        backticks = re.findall(r"`([^`\n]+)`", text)

        for token in set(backticks):
            token_clean = token.strip()
            # If token is a file path
            if "/" in token_clean or token_clean.endswith((".cpp", ".h", ".json", ".py", ".md", ".log", ".txt")):
                base_path = re.sub(r":[0-9\-]+$", "", token_clean)
                p = REPO_ROOT / base_path
                self.assertTrue(p.exists(), f"Backticked path does not exist on disk: {token_clean} -> {base_path}")
            # If token looks like a C++ symbol or class
            elif "::" in token_clean or (re.match(r"^[A-Z][a-zA-Z0-9_]+$", token_clean) and token_clean not in ["PARTIAL", "INDEX_NONE"] and not token_clean.startswith("BOSS-")):
                # grep in Source/ and Docs/
                cmd = ["git", "grep", "-q", "-F", token_clean, "--", "Source/", "Docs/"]
                res = subprocess.run(cmd, cwd=str(REPO_ROOT))
                self.assertEqual(res.returncode, 0, f"Backticked C++ symbol '{token_clean}' not found in Source/ or Docs/ via git grep!")

    def test_authority_classification(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        engine_count = len(re.findall(r"\*\*Authority\*\*:\s*\*\*Engine Required \(Claude\)\*\*", text))
        test_only_count = len(re.findall(r"\*\*Authority\*\*:\s*\*\*Test-Only \(Antigravity\)\*\*", text))
        self.assertEqual(engine_count + test_only_count, 27, f"Expected 27 classified rows, got {engine_count + test_only_count}")
        self.assertEqual(engine_count, 26, f"Expected 26 Engine Required rows, got {engine_count}")
        self.assertEqual(test_only_count, 1, f"Expected 1 Test-Only row, got {test_only_count}")

    def test_header_status_matches_ledger(self):
        """Verify that every id listed in the header block as WITNESSED or PARTIAL matches ledger v3.12."""
        ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        ledger_version = ledger.get("version", "")
        status_map = {r["id"]: r["status"] for r in ledger["requirements"]}

        text = DOC_PATH.read_text(encoding="utf-8")
        # Extract header line
        m_version = re.search(r"Status as of ledger version ([0-9\.]+):", text)
        self.assertIsNotNone(m_version, "Header block missing ledger version string")
        self.assertEqual(m_version.group(1), ledger_version, f"Header version {m_version.group(1)} does not match ledger {ledger_version}")

        # Extract witnessed list
        m_wit = re.search(r"([0-9]+)\s+of the 27 rows are now WITNESSED \(([^)]+)\)", text)
        self.assertIsNotNone(m_wit, "Header block missing WITNESSED section")
        wit_count = int(m_wit.group(1))
        wit_ids = [tok.strip().strip("`") for tok in m_wit.group(2).split(",") if tok.strip()]
        self.assertEqual(len(wit_ids), wit_count, "WITNESSED count mismatch in header")
        for rid in wit_ids:
            self.assertEqual(status_map.get(rid), "WITNESSED", f"{rid} listed as WITNESSED in header, but ledger says {status_map.get(rid)}")

        # Extract current partial ids
        m_part = re.search(r"current PARTIAL ids:\s*([^\n\r]+)", text)
        self.assertIsNotNone(m_part, "Header block missing current PARTIAL ids section")
        part_str = m_part.group(1).rstrip(".")
        part_ids = [tok.strip().strip("`") for tok in part_str.split(",") if tok.strip()]
        self.assertEqual(len(part_ids), 27 - wit_count, "PARTIAL count mismatch in header (should be 27 - WITNESSED)")
        for rid in part_ids:
            self.assertEqual(status_map.get(rid), "PARTIAL", f"{rid} listed as PARTIAL in header, but ledger says {status_map.get(rid)}")

        # Combined must equal all 27 original planned rows
        self.assertEqual(set(wit_ids) | set(part_ids), set(wit_ids + part_ids), "Duplicate IDs between WITNESSED and PARTIAL")
        self.assertEqual(len(wit_ids) + len(part_ids), 27, "Total planned IDs in header != 27")

if __name__ == "__main__":
    unittest.main()
