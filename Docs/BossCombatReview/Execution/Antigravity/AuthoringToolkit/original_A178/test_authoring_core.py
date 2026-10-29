#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_authoring_core.py
======================
Comprehensive offline unit and adversarial test suite for OneBossFight authoring toolkit (AG-CONTENT04 / Part D).

Standard library unittest test suite validating:
    1. Exact native normalization (String.cpp.inl TrimQuotesInline parity)
    2. Exact FName case-insensitive equality without whitespace stripping
    3. Strict canonical path and anti-traversal validation
    4. Finite numeric domain validation (anti-NaN, anti-Infinity, anti-bool)
    5. Build namespace collisions and reserved keywords
    6. Pinned 3-build legacy compatibility contract
    7. Deep source snapshot comparison and drift detection
    8. Cloned catalog readback ordering and parity verification
    9. Draft boss and player profile validation
    10. Partial operation reporting records
"""

import math
import os
import sys
import unittest

# ---------------------------------------------------------------------------
# Import Toolkit Core under Test
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from authoring_core import (
    APPROVED_SOURCE_CATALOG,
    APPROVED_OUTPUT_ROOT,
    APPROVED_BOSS_DRAFTS_ROOT,
    RESERVED_KEYWORDS,
    exact_native_normalize,
    exact_fname_equal,
    exact_fname_in,
    validate_package_path,
    validate_finite_integer,
    validate_finite_float,
    validate_build_namespace_keys,
    validate_pinned_legacy_contract,
    SourceInventorySnapshot,
    verify_cloned_catalog_readback,
    PartialOperationReport,
)
from draft_boss_profiles import validate_boss_profile_data


class TestExactNativeNormalization(unittest.TestCase):
    def test_empty_and_whitespace(self):
        self.assertEqual(exact_native_normalize(""), "")
        self.assertEqual(exact_native_normalize("   "), "")
        self.assertEqual(exact_native_normalize(None), "")

    def test_double_quote_trimming_parity(self):
        # Paired double quotes
        self.assertEqual(exact_native_normalize('"vanguard"'), "vanguard")
        self.assertEqual(exact_native_normalize('  "vanguard"  '), "vanguard")
        # One-sided leading double quote
        self.assertEqual(exact_native_normalize('"vanguard'), "vanguard")
        # One-sided trailing double quote
        self.assertEqual(exact_native_normalize('vanguard"'), "vanguard")
        # Multiple double quotes on both ends
        self.assertEqual(exact_native_normalize('""vanguard""'), "vanguard")
        self.assertEqual(exact_native_normalize('"""vanguard"""'), "vanguard")

    def test_single_quotes_preserved(self):
        # UE5 TrimQuotesInline trims double quotes only; single quotes are preserved characters!
        self.assertEqual(exact_native_normalize("'off'"), "'off'")
        self.assertEqual(exact_native_normalize("'none'"), "'none'")
        self.assertEqual(exact_native_normalize("'vanguard'"), "'vanguard'")
        self.assertEqual(exact_native_normalize("'vanguard"), "'vanguard")
        self.assertEqual(exact_native_normalize("vanguard'"), "vanguard'")

    def test_case_lowering(self):
        self.assertEqual(exact_native_normalize("VANGUARD"), "vanguard")
        self.assertEqual(exact_native_normalize('"ClaymoreCombatStyle"'), "claymorecombatstyle")

    def test_reserved_keywords(self):
        self.assertEqual(exact_native_normalize("none"), "none")
        self.assertEqual(exact_native_normalize('"none"'), "none")
        self.assertEqual(exact_native_normalize("off"), "off")
        self.assertEqual(exact_native_normalize('"off"'), "off")
        # With single quotes, it is NOT the reserved keyword
        self.assertNotEqual(exact_native_normalize("'off'"), "off")


class TestExactFNameEquality(unittest.TestCase):
    def test_case_insensitive_ascii_equality(self):
        self.assertTrue(exact_fname_equal("Strength", "strength"))
        self.assertTrue(exact_fname_equal("STRENGTH", "strength"))
        self.assertTrue(exact_fname_equal("Build_Custom_Vanguard", "build_custom_vanguard"))

    def test_whitespace_is_significant(self):
        # CRITICAL: In Unreal Engine, FName does not strip whitespace!
        self.assertFalse(exact_fname_equal(" Strength ", "Strength"))
        self.assertFalse(exact_fname_equal("Strength", "Strength "))
        self.assertFalse(exact_fname_equal(" Strength", "Strength"))

    def test_membership_helper(self):
        collection = ["Starter", "Strength", "Dex"]
        self.assertTrue(exact_fname_in("strength", collection))
        self.assertTrue(exact_fname_in("DEX", collection))
        self.assertFalse(exact_fname_in("Vanguard", collection))
        self.assertFalse(exact_fname_in(" Strength ", collection))


class TestCanonicalPathValidation(unittest.TestCase):
    def test_valid_paths(self):
        ok, _ = validate_package_path(APPROVED_OUTPUT_ROOT + "DA_Build_Custom_Vanguard", APPROVED_OUTPUT_ROOT)
        self.assertTrue(ok)
        ok, _ = validate_package_path(APPROVED_BOSS_DRAFTS_ROOT + "DA_Boss_EmberWarden_Draft", APPROVED_BOSS_DRAFTS_ROOT)
        self.assertTrue(ok)

    def test_wrong_root_rejection(self):
        ok, err = validate_package_path("/Game/Unapproved/Root/Asset", APPROVED_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertIn("does not start with authorized root", err)

    def test_traversal_rejection(self):
        ok, err = validate_package_path(APPROVED_OUTPUT_ROOT + "../Catalog/DA_CombatCatalog", APPROVED_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertIn("Path traversal", err)

    def test_double_slash_and_backslash_rejection(self):
        ok, err = validate_package_path(APPROVED_OUTPUT_ROOT + "/DA_Build", APPROVED_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertIn("Double slashes", err)

        ok, err = validate_package_path(APPROVED_OUTPUT_ROOT + "\\DA_Build", APPROVED_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertIn("Backslashes", err)

    def test_subobject_colon_rejection(self):
        ok, err = validate_package_path(APPROVED_OUTPUT_ROOT + "DA_Build:SubObject", APPROVED_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertIn("Sub-object colon", err)

    def test_whitespace_rejection(self):
        ok, err = validate_package_path(APPROVED_OUTPUT_ROOT + "DA Build", APPROVED_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertIn("Whitespace", err)


class TestNumericDomainValidation(unittest.TestCase):
    def test_finite_integers(self):
        ok, _ = validate_finite_integer(3, "UiOrder", min_val=0, max_val=10)
        self.assertTrue(ok)
        ok, _ = validate_finite_integer(-1, "LegacySlot", min_val=-1, max_val=2)
        self.assertTrue(ok)

        # Rejection of bool (bool is subclass of int in Python)
        ok, err = validate_finite_integer(True, "LegacySlot")
        self.assertFalse(ok)
        self.assertIn("must be an integer, got bool", err)

        # Rejection of floats, NaNs, strings
        ok, err = validate_finite_integer(3.5, "UiOrder")
        self.assertFalse(ok)
        ok, err = validate_finite_integer("3", "UiOrder")
        self.assertFalse(ok)

    def test_finite_floats(self):
        ok, _ = validate_finite_float(1500.0, "max_health", min_val=0.0)
        self.assertTrue(ok)

        # Rejection of bool
        ok, err = validate_finite_float(True, "max_health")
        self.assertFalse(ok)
        self.assertIn("must be a numeric float, got bool", err)

        # Rejection of NaN
        ok, err = validate_finite_float(float("nan"), "max_health")
        self.assertFalse(ok)
        self.assertIn("is NaN", err)

        # Rejection of Inf / -Inf
        ok, err = validate_finite_float(float("inf"), "max_health")
        self.assertFalse(ok)
        self.assertIn("is Infinity", err)

        ok, err = validate_finite_float(float("-inf"), "max_health")
        self.assertFalse(ok)
        self.assertIn("is Infinity", err)

        # Boundary check
        ok, err = validate_finite_float(-10.0, "max_health", min_val=0.0)
        self.assertFalse(ok)
        self.assertIn("below minimum", err)


class TestNamespaceCollisionValidation(unittest.TestCase):
    def setUp(self):
        self.existing = {
            "starter": "Starter",
            "strength": "Strength",
            "dex": "Dex"
        }

    def test_valid_custom_build_keys(self):
        ok, _, updated = validate_build_namespace_keys(
            "Build_Custom_Vanguard", "vanguard", ["vanguard_alt"], self.existing
        )
        self.assertTrue(ok)
        self.assertIn("vanguard", updated)
        self.assertIn("vanguard_alt", updated)
        self.assertIn("build_custom_vanguard", updated)

    def test_reserved_keyword_rejection(self):
        ok, err, _ = validate_build_namespace_keys(
            "Build_Invalid", "none", [], self.existing
        )
        self.assertFalse(ok)
        self.assertIn("uses reserved keyword 'none'", err)

        ok, err, _ = validate_build_namespace_keys(
            "Build_Invalid", "custom", ['"off"'], self.existing
        )
        self.assertFalse(ok)
        self.assertIn("uses reserved keyword 'off'", err)

    def test_collision_with_existing_build(self):
        ok, err, _ = validate_build_namespace_keys(
            "Build_Custom_Vanguard", "strength", [], self.existing
        )
        self.assertFalse(ok)
        self.assertIn("Namespace collision", err)


class TestPinnedLegacyContractValidation(unittest.TestCase):
    def setUp(self):
        self.valid_weapons = [
            {"WeaponId": "Sword", "StyleName": "SwordCombatStyle"},
            {"WeaponId": "Strength", "StyleName": "ClaymoreCombatStyle"},
            {"WeaponId": "Dex", "StyleName": "DualSwordsCombatStyle"}
        ]
        self.valid_builds = [
            {"BuildId": "Starter", "ConsoleName": "Starter", "DisplayName": "Starter", "UiOrder": 0, "LegacySlot": 0, "WeaponId": "Sword"},
            {"BuildId": "Strength", "ConsoleName": "Strength", "DisplayName": "Strength", "UiOrder": 1, "LegacySlot": 1, "WeaponId": "Strength"},
            {"BuildId": "Dex", "ConsoleName": "Dex", "DisplayName": "Dex", "UiOrder": 2, "LegacySlot": 2, "WeaponId": "Dex"}
        ]

    def test_clean_contract_passes(self):
        ok, errors = validate_pinned_legacy_contract(self.valid_builds, self.valid_weapons)
        self.assertTrue(ok)
        self.assertEqual(len(errors), 0)

    def test_missing_slot_fails(self):
        incomplete_builds = self.valid_builds[:2]  # Missing Dex [2]
        ok, errors = validate_pinned_legacy_contract(incomplete_builds, self.valid_weapons)
        self.assertFalse(ok)
        self.assertTrue(any("requires exactly slots" in e for e in errors))

    def test_duplicate_slot_fails(self):
        dup_builds = list(self.valid_builds)
        dup_builds.append({"BuildId": "Extra", "LegacySlot": 1, "WeaponId": "Strength"})
        ok, errors = validate_pinned_legacy_contract(dup_builds, self.valid_weapons)
        self.assertFalse(ok)
        self.assertTrue(any("Duplicate LegacySlot 1" in e for e in errors))

    def test_wrong_style_fails(self):
        bad_weapons = [
            {"WeaponId": "Sword", "StyleName": "SwordCombatStyle"},
            {"WeaponId": "Strength", "StyleName": "WrongStyle"},
            {"WeaponId": "Dex", "StyleName": "DualSwordsCombatStyle"}
        ]
        ok, errors = validate_pinned_legacy_contract(self.valid_builds, bad_weapons)
        self.assertFalse(ok)
        self.assertTrue(any("StyleName mismatch" in e for e in errors))


class TestSourceSnapshotComparison(unittest.TestCase):
    def setUp(self):
        self.snap1 = SourceInventorySnapshot(
            catalog_path=APPROVED_SOURCE_CATALOG,
            schema_version=1,
            weapons=[{"WeaponId": "Strength", "StyleName": "ClaymoreCombatStyle"}],
            builds=[{"BuildId": "Strength", "LegacySlot": 1}],
            package_dirty_states={APPROVED_SOURCE_CATALOG: False}
        )

    def test_identical_snapshots_pass(self):
        snap2 = SourceInventorySnapshot(
            catalog_path=APPROVED_SOURCE_CATALOG,
            schema_version=1,
            weapons=[{"WeaponId": "Strength", "StyleName": "ClaymoreCombatStyle"}],
            builds=[{"BuildId": "Strength", "LegacySlot": 1}],
            package_dirty_states={APPROVED_SOURCE_CATALOG: False}
        )
        ok, diffs = self.snap1.compare_with(snap2)
        self.assertTrue(ok)
        self.assertEqual(len(diffs), 0)

    def test_package_dirty_drift_detected(self):
        snap2 = SourceInventorySnapshot(
            catalog_path=APPROVED_SOURCE_CATALOG,
            schema_version=1,
            weapons=[{"WeaponId": "Strength", "StyleName": "ClaymoreCombatStyle"}],
            builds=[{"BuildId": "Strength", "LegacySlot": 1}],
            package_dirty_states={APPROVED_SOURCE_CATALOG: True}  # Dirtied!
        )
        ok, diffs = self.snap1.compare_with(snap2)
        self.assertFalse(ok)
        self.assertTrue(any("became dirty" in d for d in diffs))

    def test_field_drift_detected(self):
        snap2 = SourceInventorySnapshot(
            catalog_path=APPROVED_SOURCE_CATALOG,
            schema_version=1,
            weapons=[{"WeaponId": "Strength", "StyleName": "MutatedStyle"}],
            builds=[{"BuildId": "Strength", "LegacySlot": 1}],
            package_dirty_states={APPROVED_SOURCE_CATALOG: False}
        )
        ok, diffs = self.snap1.compare_with(snap2)
        self.assertFalse(ok)
        self.assertTrue(any("field 'StyleName' drifted" in d for d in diffs))


class TestClonedCatalogReadback(unittest.TestCase):
    def setUp(self):
        self.original_builds = [
            {"AssetPath": "/Game/OneBossFight/Data/Catalog/DA_Build_Starter"},
            {"AssetPath": "/Game/OneBossFight/Data/Catalog/DA_Build_Strength"},
            {"AssetPath": "/Game/OneBossFight/Data/Catalog/DA_Build_Dex"}
        ]
        self.new_build = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/DA_Build_Custom_Vanguard"

    def test_valid_readback_passes(self):
        cloned_paths = [b["AssetPath"] for b in self.original_builds] + [self.new_build]
        ok, errs = verify_cloned_catalog_readback(self.original_builds, cloned_paths, self.new_build)
        self.assertTrue(ok)
        self.assertEqual(len(errs), 0)

    def test_order_permutation_fails(self):
        # Permute Starter and Strength
        cloned_paths = [
            "/Game/OneBossFight/Data/Catalog/DA_Build_Strength",
            "/Game/OneBossFight/Data/Catalog/DA_Build_Starter",
            "/Game/OneBossFight/Data/Catalog/DA_Build_Dex",
            self.new_build
        ]
        ok, errs = verify_cloned_catalog_readback(self.original_builds, cloned_paths, self.new_build)
        self.assertFalse(ok)
        self.assertTrue(any("order/path mismatch" in e for e in errs))

    def test_missing_new_build_fails(self):
        cloned_paths = [b["AssetPath"] for b in self.original_builds] + ["/Game/Wrong/Build"]
        ok, errs = verify_cloned_catalog_readback(self.original_builds, cloned_paths, self.new_build)
        self.assertFalse(ok)
        self.assertTrue(any("Last build element mismatch" in e for e in errs))


class TestBossProfileValidation(unittest.TestCase):
    def test_valid_boss_profile(self):
        profile = {
            "asset_name": "DA_Boss_Test_Draft",
            "definition_id": "Boss_Test",
            "presentation_id": "Pres_Test",
            "schema_version": 1,
            "participant_kind": "Boss",
            "stats": {"max_health": 1000.0, "base_poise": 100.0, "poise_recovery_rate": 10.0, "poise_broken_recovery_delay": 3.0},
            "phases": [{"phase_id": "PhaseTwo", "health_threshold_percent": 0.5}],
            "fields": []
        }
        ok, errs = validate_boss_profile_data(profile, [], [])
        self.assertTrue(ok)
        self.assertEqual(len(errs), 0)

    def test_boss_multiple_phases_rejected(self):
        # Backend requires exactly 1 transition phase record
        profile = {
            "asset_name": "DA_Boss_Test_Draft",
            "definition_id": "Boss_Test",
            "presentation_id": "Pres_Test",
            "schema_version": 1,
            "participant_kind": "Boss",
            "stats": {"max_health": 1000.0, "base_poise": 100.0, "poise_recovery_rate": 10.0, "poise_broken_recovery_delay": 3.0},
            "phases": [
                {"phase_id": "PhaseOne", "health_threshold_percent": 1.0},
                {"phase_id": "PhaseTwo", "health_threshold_percent": 0.5}
            ],
            "fields": []
        }
        ok, errs = validate_boss_profile_data(profile, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("requires exactly 1 transition record" in e for e in errs))

    def test_player_participant_phases_rejected(self):
        profile = {
            "asset_name": "DA_Player_Test_Draft",
            "definition_id": "Player_Test",
            "presentation_id": "Pres_Test",
            "schema_version": 1,
            "participant_kind": "Player",
            "stats": {"max_health": 500.0, "base_poise": 50.0, "poise_recovery_rate": 10.0, "poise_broken_recovery_delay": 1.0},
            "phases": [{"phase_id": "PhaseTwo", "health_threshold_percent": 0.5}],  # Player cannot have phases!
            "fields": []
        }
        ok, errs = validate_boss_profile_data(profile, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("Player participant profile must have 0 phases" in e for e in errs))


class TestPartialOperationReport(unittest.TestCase):
    def test_report_structure(self):
        report = PartialOperationReport("test_op")
        report.record_created("/Game/Path1")
        report.record_created("/Game/Path2")
        report.record_saved("/Game/Path1")
        report.record_error("Simulated failure")

        data = report.to_dict()
        self.assertFalse(data["success"])
        self.assertFalse(data["rollback_claimed"])
        self.assertFalse(data["auto_cleanup_performed"])
        self.assertEqual(len(data["created_packages"]), 2)
        self.assertEqual(len(data["saved_packages"]), 1)
        self.assertIn("Simulated failure", data["errors"])


if __name__ == "__main__":
    unittest.main()
