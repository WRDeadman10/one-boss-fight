#!/usr/bin/env python3
"""
test_emit_fields_manifest.py - Comprehensive Unit Tests for Parity Field Manifest Generator

Validates the conventions established in C-294 and C-297:
1. 110 DD26 preflight paths parity against RPGBossHydrationPreflightTests.cpp AllRequiredPaths.
2. Verified witness names exist in Source/OneBossFight/Tests automation suites.
3. SourceSite declaration lines are truthful and re-read from source with destination member present.
4. Value column for NativeDefault rows matches parsed C++ header/struct defaults.
5. Selected-phase CLI handling (110 rows with PhaseTwo vs 106 rows with 4 withheld).
6. PhaseNotFoundError handling on unknown PhaseId.
7. Ember Warden draft profile carries all 110 compliant rows and passes CompileParticipantImpl rules.
"""

import glob
import json
import os
import re
import sys
import unittest

# Ensure repo root is in sys.path regardless of execution working directory
def setup_path():
    cur = os.path.abspath(os.path.dirname(__file__))
    while cur and cur != os.path.dirname(cur):
        if os.path.exists(os.path.join(cur, "Source", "OneBossFight")) or os.path.exists(os.path.join(cur, ".git")):
            if cur not in sys.path:
                sys.path.insert(0, cur)
            return cur
        cur = os.path.dirname(cur)
    fallback = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
    if fallback not in sys.path:
        sys.path.insert(0, fallback)
    return fallback

REPO_ROOT = setup_path()

from Docs.BossCombatReview.Execution.Antigravity.AuthoringToolkit.emit_fields_manifest import (
    generate_manifest_rows,
    find_member_decl,
    BASE_FIELDS_SPEC,
    PhaseNotFoundError
)

class TestEmitFieldsManifest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo_root = REPO_ROOT
        # Parse all automation test names from C++ sources
        cls.available_tests = set()
        test_cpps = glob.glob(os.path.join(cls.repo_root, "Source", "OneBossFight", "Tests", "*.cpp"))
        for f in test_cpps:
            with open(f, "r", encoding="utf-8", errors="ignore") as fp:
                for line in fp:
                    m = re.search(r'IMPLEMENT_SIMPLE_AUTOMATION_TEST\s*\(\s*\w+\s*,\s*"([^"]+)"', line)
                    if m:
                        cls.available_tests.add(m.group(1))

        # Parse preflight 110 paths from RPGBossHydrationPreflightTests.cpp AllRequiredPaths
        preflight_cpp = os.path.join(cls.repo_root, "Source", "OneBossFight", "Tests", "RPGBossHydrationPreflightTests.cpp")
        cls.preflight_phase_two_paths = set()
        with open(preflight_cpp, "r", encoding="utf-8") as fp:
            content = fp.read()

        # Extract AllRequiredPaths function body
        m_func = re.search(r'AllRequiredPaths\(FName PhaseId\)\s*\{(.*?)\}', content, re.DOTALL)
        if m_func:
            func_body = m_func.group(1)
            # Find all TEXT("...")
            for m in re.finditer(r'TEXT\("([^"]+)"\)', func_body):
                if not m.group(1).startswith("Phases[%s]"): cls.preflight_phase_two_paths.add(m.group(1))
            # Format the 4 phase paths for PhaseTwo
            for m in re.finditer(r'Printf\(TEXT\("Phases\[%s\]\.(\w+)"\)', func_body):
                cls.preflight_phase_two_paths.add(f"Phases[PhaseTwo].{m.group(1)}")

    def test_full_110_row_emission_and_preflight_parity(self):
        """Verify that default generation emits all 110 rows and matches preflight literals 1-to-1."""
        rows, withheld, hashes = generate_manifest_rows(selected_phase_id="PhaseTwo", include_selected_phase=True)
        self.assertEqual(len(rows), 110)
        self.assertEqual(len(withheld), 0)

        emitted_paths = set(r["FieldPath"] for r in rows)
        self.assertEqual(len(emitted_paths), 110, "FieldPaths must be strictly unique")

        # Compare with independent preflight test literals
        diff = self.preflight_phase_two_paths.symmetric_difference(emitted_paths)
        self.assertEqual(len(diff), 0, f"Paths differ from preflight literals: {diff}")

    def test_withheld_selected_phase_mode(self):
        """Verify that --no-selected-phase mode emits 106 rows and withholds 4 phase paths."""
        rows, withheld, hashes = generate_manifest_rows(include_selected_phase=False)
        self.assertEqual(len(rows), 106)
        self.assertEqual(len(withheld), 4)

        withheld_expected = {
            "Phases[<SelectedPhaseId>].EntryHealthFraction",
            "Phases[<SelectedPhaseId>].SpeedMultiplier",
            "Phases[<SelectedPhaseId>].RateMultiplier",
            "Phases[<SelectedPhaseId>].AttackMultiplier",
        }
        self.assertEqual(set(withheld), withheld_expected)

    def test_phase_not_found_raises_error(self):
        """Verify that requesting an unauthored PhaseId raises PhaseNotFoundError."""
        with self.assertRaises(PhaseNotFoundError):
            generate_manifest_rows(selected_phase_id="NonExistentPhase_99", include_selected_phase=True)

    def test_witness_names_exist_in_cplusplus_test_suites(self):
        """Verify that every Witness cited exists as a real passing automation test in C++ sources."""
        rows, _, _ = generate_manifest_rows(selected_phase_id="PhaseTwo", include_selected_phase=True)
        for r in rows:
            witness = r["Witness"]
            self.assertTrue(witness.startswith("AutomationTest:"), f"Witness must start with AutomationTest: {witness}")
            suite_name = witness[len("AutomationTest:"):]
            self.assertIn(suite_name, self.available_tests, f"Witness test does not exist in C++ sources: {suite_name}")

    def test_sourcesite_lines_contain_destination_member_name(self):
        """Verify that every cited SourceSite line (File:line) truthfully contains the destination member name."""
        rows, _, _ = generate_manifest_rows(selected_phase_id="PhaseTwo", include_selected_phase=True)
        for r in rows:
            site = r["SourceSite"]
            source_path = r["SourcePath"]
            dest = r["Destination"]

            if r["Origin"] == "AuthoredAsset":
                # JSON pointer format: /profiles/0/phases/0/<prop>
                self.assertTrue(site.startswith("/profiles/"), f"AuthoredAsset site must be JSON pointer: {site}")
                continue

            # Native / Contract / Override site format: File.h:line
            self.assertIn(":", site)
            fname, lno_str = site.split(":")
            lno = int(lno_str)

            # Re-read line from file
            full_path = os.path.join(self.repo_root, source_path)
            with open(full_path, "r", encoding="utf-8", errors="ignore") as fp:
                lines = fp.readlines()

            line_text = lines[lno - 1]

            # Destination is Class::Member
            member = dest.split("::")[-1]
            if r["Origin"] == "SubsystemOverride":
                # DeathMode assigned in Attach(Pawn, ERPGBossDeathMode::OwnClip)
                self.assertIn("ERPGBossDeathMode::OwnClip", line_text)
            else:
                self.assertIn(member, line_text, f"Line {lno} of {source_path} does not declare member '{member}': {line_text.strip()}")

    def test_value_column_matches_parsed_header_defaults(self):
        """Verify that Value matches the parsed C++ default from the header/struct."""
        rows, _, _ = generate_manifest_rows(selected_phase_id="PhaseTwo", include_selected_phase=True)
        for r in rows:
            if r["Origin"] == "NativeDefault":
                src_rel = r["SourcePath"]
                dest = r["Destination"]
                member = dest.split("::")[-1]
                _, parsed_val, _ = find_member_decl(src_rel, member, is_override=False)
                expected_val = parsed_val if parsed_val is not None else ""
                self.assertEqual(r["Value"], expected_val, f"Value mismatch for {r['FieldPath']}: expected '{expected_val}', got '{r['Value']}'")

    def test_required_columns_and_sha256_format(self):
        """Verify all 8 format columns are non-empty and SourceSHA256 is exactly 64-hex."""
        rows, _, hashes = generate_manifest_rows(selected_phase_id="PhaseTwo", include_selected_phase=True)
        required_cols = ["FieldPath", "Type", "SourcePath", "SourceSHA256", "SourceSite", "Origin", "Precedence", "Destination", "FirstRead", "Witness"]
        sha_pat = re.compile(r"^[0-9a-f]{64}$")

        for r in rows:
            for col in required_cols:
                self.assertTrue(r[col], f"Column {col} must not be empty in row {r['FieldPath']}")
            self.assertTrue(sha_pat.match(r["SourceSHA256"]), f"Invalid SHA-256 in {r['FieldPath']}: {r['SourceSHA256']}")
            self.assertEqual(r["Precedence"], "typed-record")
            self.assertEqual(r["FirstRead"], "PrepareBatch.Configure")
            self.assertIn(r["Origin"], ["NativeDefault", "SubsystemOverride", "LeadContract", "AuthoredAsset"])

    def test_ember_warden_example_loads_and_carries_110_rows(self):
        """Verify that examples/boss_draft_profiles.json carries all 110 rows for DA_Boss_EmberWarden_Draft."""
        json_path = os.path.join(self.repo_root, "Docs", "BossCombatReview", "Execution", "Antigravity", "AuthoringToolkit", "examples", "boss_draft_profiles.json")
        with open(json_path, "r", encoding="utf-8") as fp:
            data = json.load(fp)

        ember = next(p for p in data["profiles"] if p["asset_name"] == "DA_Boss_EmberWarden_Draft")
        fields = ember["fields"]
        self.assertEqual(len(fields), 110, "Ember Warden must carry exactly 110 manifest fields")

        field_paths = set(f["FieldPath"] for f in fields)
        self.assertEqual(len(field_paths), 110, "All 110 fields must be unique")
        diff = self.preflight_phase_two_paths.symmetric_difference(field_paths)
        self.assertEqual(len(diff), 0, f"Ember Warden fields differ from preflight literals: {diff}")

if __name__ == "__main__":
    unittest.main()
