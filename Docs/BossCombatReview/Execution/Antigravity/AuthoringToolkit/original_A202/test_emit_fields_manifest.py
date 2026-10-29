#!/usr/bin/env python3
"""
test_emit_fields_manifest.py - Unit Tests for FRPGParityField Parity Manifest Generator

Tests the manifest generator (emit_fields_manifest.py) against the C-294 Lead Conventions:
  - Exact 110-path coverage (106 known clusters + 4 phase-dependent gaps).
  - Format checks: 64-hex SHA-256 hashes matching IsSHA256() format.
  - Strict non-emptiness across all 8 required metadata columns.
  - Path alignment with DD26 RPGBossHydrationPreflight literals.
  - C++ adapter symbol and source site verification.
"""

import hashlib
import json
import os
import re
import unittest

from Docs.BossCombatReview.Execution.Antigravity.AuthoringToolkit.emit_fields_manifest import (
    ALL_PREFLIGHT_110_PATHS,
    KNOWN_FIELDS_SPEC,
    MANIFEST_GAPS,
    compute_file_sha256,
    find_repo_root,
    generate_manifest_rows,
    get_manifest_gaps
)


class TestEmitFieldsManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = find_repo_root()
        cls.rows_camel, cls.pins = generate_manifest_rows(cls.repo_root, key_format="CamelCase")
        cls.rows_snake, _ = generate_manifest_rows(cls.repo_root, key_format="snake_case")
        cls.gaps = get_manifest_gaps()

    def test_row_and_gap_counts(self):
        """Verifies exactly 106 known rows and 4 gaps totaling 110 DD26 paths."""
        self.assertEqual(len(self.rows_camel), 106)
        self.assertEqual(len(self.rows_snake), 106)
        self.assertEqual(len(self.gaps), 4)
        self.assertEqual(len(self.rows_camel) + len(self.gaps), 110)

    def test_field_paths_match_preflight_literals(self):
        """Verifies that all 106 generated paths and 4 gaps match DD26 preflight literals."""
        known_paths = set(r["FieldPath"] for r in self.rows_camel)
        gap_templates = set(g["FieldPath"] for g in self.gaps)

        # Check uniqueness
        self.assertEqual(len(known_paths), 106, "All 106 generated FieldPaths must be unique")

        # Check that all preflight literals are accounted for
        preflight_set = set(ALL_PREFLIGHT_110_PATHS)
        for p in known_paths:
            self.assertIn(p, preflight_set, f"Generated path {p} not in preflight literals")
        for g in gap_templates:
            self.assertIn(g, preflight_set, f"Gap path {g} not in preflight literals")

    def test_required_eight_columns_non_empty(self):
        """
        Verifies that for every row, the 8 columns validated for non-emptiness by
        CompileParticipantImpl (RPGEncounterBinding.cpp:106-109) are non-empty strings:
        Type, SourcePath, SourceSite, Origin, Precedence, Destination, FirstRead, Witness.
        """
        required_cols = [
            "Type", "SourcePath", "SourceSite", "Origin",
            "Precedence", "Destination", "FirstRead", "Witness"
        ]
        for row in self.rows_camel:
            path = row.get("FieldPath", "<unknown>")
            for col in required_cols:
                val = row.get(col)
                self.assertIsNotNone(val, f"Row {path} missing required column '{col}'")
                self.assertIsInstance(val, str, f"Row {path} column '{col}' must be string")
                self.assertTrue(len(val.strip()) > 0, f"Row {path} column '{col}' must not be empty")

    def test_source_sha256_format_and_live_integrity(self):
        """
        Verifies that SourceSHA256 is exactly 64 hexadecimal characters (IsSHA256),
        and matches the live SHA-256 hash of SourcePath in the working tree.
        """
        hex_pattern = re.compile(r"^[0-9a-fA-F]{64}$")
        for row in self.rows_camel:
            path = row["FieldPath"]
            srel = row["SourcePath"]
            sha = row["SourceSHA256"]

            self.assertEqual(len(sha), 64, f"Row {path} SourceSHA256 length must be 64, got {len(sha)}")
            self.assertTrue(hex_pattern.match(sha), f"Row {path} SourceSHA256 contains non-hex characters")

            # Check live hash
            live_hash, _ = compute_file_sha256(self.repo_root, srel)
            self.assertEqual(sha, live_hash, f"Row {path} SourceSHA256 does not match live file {srel}")

    def test_origin_allowed_values(self):
        """Verifies Origin belongs to the Lead taxonomy: NativeDefault, SubsystemOverride, LeadContract, AuthoredAsset."""
        allowed_origins = {"NativeDefault", "SubsystemOverride", "LeadContract", "AuthoredAsset"}
        for row in self.rows_camel:
            path = row["FieldPath"]
            origin = row["Origin"]
            self.assertIn(origin, allowed_origins, f"Row {path} has invalid Origin '{origin}'")

    def test_precedence_and_first_read_conventions(self):
        """Verifies Precedence is 'typed-record' and FirstRead is 'PrepareBatch.Configure'."""
        for row in self.rows_camel:
            self.assertEqual(row["Precedence"], "typed-record")
            self.assertEqual(row["FirstRead"], "PrepareBatch.Configure")

    def test_witness_format(self):
        """Verifies Witness format starts with AutomationTest:OneBossFight.Binding."""
        for row in self.rows_camel:
            witness = row["Witness"]
            self.assertTrue(witness.startswith("AutomationTest:OneBossFight.Binding."),
                            f"Witness '{witness}' does not match expected automation test prefix")

    def test_death_mode_subsystem_override(self):
        """Verifies Death.DeathMode is truthfully marked SubsystemOverride with value OwnClip."""
        death_mode_row = next((r for r in self.rows_camel if r["FieldPath"] == "Death.DeathMode"), None)
        self.assertIsNotNone(death_mode_row, "Death.DeathMode row must exist")
        self.assertEqual(death_mode_row["Origin"], "SubsystemOverride")
        self.assertEqual(death_mode_row["Value"], "OwnClip")
        self.assertIn("RPGPlayerMovesSubsystem.cpp", death_mode_row["SourcePath"])

    def test_ember_warden_example_carries_manifest(self):
        """Verifies examples/boss_draft_profiles.json carries all 106 rows on Ember Warden."""
        json_path = os.path.join(self.repo_root, "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json")
        self.assertTrue(os.path.exists(json_path), f"boss_draft_profiles.json not found at {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        ember = next((p for p in data.get("profiles", []) if p.get("asset_name") == "DA_Boss_EmberWarden_Draft"), None)
        self.assertIsNotNone(ember, "DA_Boss_EmberWarden_Draft profile must exist")
        fields = ember.get("fields", [])
        self.assertEqual(len(fields), 106, f"Ember Warden must carry exactly 106 fields, found {len(fields)}")


if __name__ == "__main__":
    unittest.main()
