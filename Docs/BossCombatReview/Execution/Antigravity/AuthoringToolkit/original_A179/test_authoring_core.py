#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_authoring_core.py
======================
Comprehensive offline unit and adversarial test suite for OneBossFight authoring toolkit
(AG-CONTENT04 / Deliverable D).

Standard library unittest test suite validating:
    1. Exact native normalization (String.cpp.inl TrimQuotesInline parity: at most 1 quote stripped)
    2. Exact FName case-insensitive equality without whitespace stripping
    3. Strict canonical path and anti-traversal validation
    4. Finite numeric domain validation (anti-NaN, anti-Infinity, anti-bool)
    5. Build namespace collisions and reserved keywords
    6. Pinned 3-build legacy compatibility contract (Starter/SwordCombatStyle, Dex/DualSwordCombatStyle)
    7. Deep source snapshot comparison, mutation isolation, and package set drift detection
    8. Cloned catalog readback ordering and parity verification
    9. Draft boss and player profile validation against native URPGBossDefinition schema
    10. Recording fake writer verification (zero omitted typed fields on apply)
    11. Partial operation reporting records
"""

import copy
import json
import math
import os
import sys
import unittest
from types import SimpleNamespace

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
    PINNED_LEGACY_CONTRACT,
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
from draft_boss_profiles import validate_boss_profile_data, execute_draft_apply


class TestExactNativeNormalization(unittest.TestCase):
    def test_empty_and_whitespace(self):
        self.assertEqual(exact_native_normalize(""), "")
        self.assertEqual(exact_native_normalize("   "), "")
        self.assertEqual(exact_native_normalize(None), "")

    def test_double_quote_trimming_parity(self):
        # Paired double quotes (removes at most one at each end)
        self.assertEqual(exact_native_normalize('"vanguard"'), "vanguard")
        self.assertEqual(exact_native_normalize('  "vanguard"  '), "vanguard")
        # One-sided leading double quote
        self.assertEqual(exact_native_normalize('"vanguard'), "vanguard")
        # One-sided trailing double quote
        self.assertEqual(exact_native_normalize('vanguard"'), "vanguard")
        # Repeated double quotes: UE5.5 String.cpp.inl TrimQuotesInline removes at most ONE!
        self.assertEqual(exact_native_normalize('""off""'), '"off"')
        self.assertEqual(exact_native_normalize('""vanguard""'), '"vanguard"')
        self.assertEqual(exact_native_normalize('"""vanguard"""'), '""vanguard""')

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
        # Repeated quotes leave '"off"' which is NOT the bare reserved keyword 'off'
        self.assertEqual(exact_native_normalize('""off""'), '"off"')
        self.assertNotEqual(exact_native_normalize('""off""'), 'off')


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
        ok, _ = validate_finite_float(1500.0, "MaxHealth", min_val=0.0)
        self.assertTrue(ok)

        # Rejection of bool
        ok, err = validate_finite_float(True, "MaxHealth")
        self.assertFalse(ok)
        self.assertIn("must be a numeric float, got bool", err)

        # Rejection of NaN
        ok, err = validate_finite_float(float("nan"), "MaxHealth")
        self.assertFalse(ok)
        self.assertIn("is NaN", err)

        # Rejection of Inf / -Inf
        ok, err = validate_finite_float(float("inf"), "MaxHealth")
        self.assertFalse(ok)
        self.assertIn("is Infinity", err)

        ok, err = validate_finite_float(float("-inf"), "MaxHealth")
        self.assertFalse(ok)
        self.assertIn("is Infinity", err)

        # Boundary check
        ok, err = validate_finite_float(-10.0, "MaxHealth", min_val=0.0)
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
        # Native contract: Starter uses WeaponId Starter / SwordCombatStyle; Dex uses DualSwordCombatStyle (singular)
        self.valid_weapons = [
            {"WeaponId": "Starter", "StyleName": "SwordCombatStyle"},
            {"WeaponId": "Strength", "StyleName": "ClaymoreCombatStyle"},
            {"WeaponId": "Dex", "StyleName": "DualSwordCombatStyle"}
        ]
        self.valid_builds = [
            {"BuildId": "Starter", "ConsoleName": "Starter", "DisplayName": "Starter", "UiOrder": 0, "LegacySlot": 0, "WeaponId": "Starter"},
            {"BuildId": "Strength", "ConsoleName": "Strength", "DisplayName": "Strength", "UiOrder": 1, "LegacySlot": 1, "WeaponId": "Strength"},
            {"BuildId": "Dex", "ConsoleName": "Dex", "DisplayName": "Dex", "UiOrder": 2, "LegacySlot": 2, "WeaponId": "Dex"}
        ]

    def test_clean_contract_passes(self):
        ok, errors = validate_pinned_legacy_contract(self.valid_builds, self.valid_weapons)
        self.assertTrue(ok)
        self.assertEqual(len(errors), 0)

    def test_invented_sword_id_fails(self):
        # Fails if Starter WeaponId is incorrectly given as 'Sword'
        bad_builds = copy.deepcopy(self.valid_builds)
        bad_builds[0]["WeaponId"] = "Sword"
        ok, errors = validate_pinned_legacy_contract(bad_builds, self.valid_weapons)
        self.assertFalse(ok)
        self.assertTrue(any("Slot 0 WeaponId mismatch" in e for e in errors))

    def test_plural_dualswords_style_fails(self):
        # Fails if Dex style is plural 'DualSwordsCombatStyle' instead of native 'DualSwordCombatStyle'
        bad_weapons = copy.deepcopy(self.valid_weapons)
        bad_weapons[2]["StyleName"] = "DualSwordsCombatStyle"
        ok, errors = validate_pinned_legacy_contract(self.valid_builds, bad_weapons)
        self.assertFalse(ok)
        self.assertTrue(any("Slot 2 weapon StyleName mismatch" in e for e in errors))

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


class TestSourceSnapshotComparison(unittest.TestCase):
    def setUp(self):
        self.snap1 = SourceInventorySnapshot(
            catalog_path=APPROVED_SOURCE_CATALOG,
            schema_version=1,
            weapons=[{"WeaponId": "Strength", "StyleName": "ClaymoreCombatStyle"}],
            builds=[{"BuildId": "Strength", "LegacySlot": 1, "Aliases": ["str"]}],
            package_dirty_states={APPROVED_SOURCE_CATALOG: False}
        )

    def test_identical_snapshots_pass(self):
        snap2 = SourceInventorySnapshot(
            catalog_path=APPROVED_SOURCE_CATALOG,
            schema_version=1,
            weapons=[{"WeaponId": "Strength", "StyleName": "ClaymoreCombatStyle"}],
            builds=[{"BuildId": "Strength", "LegacySlot": 1, "Aliases": ["str"]}],
            package_dirty_states={APPROVED_SOURCE_CATALOG: False}
        )
        ok, diffs = self.snap1.compare_with(snap2)
        self.assertTrue(ok)
        self.assertEqual(len(diffs), 0)

    def test_mutation_after_snapshot_isolated(self):
        # Regression probe for deep copy: mutating source builds after snapshot MUST NOT alter snapshot baseline!
        source_builds = [{"BuildId": "Starter", "Aliases": ["original"]}]
        snap = SourceInventorySnapshot(APPROVED_SOURCE_CATALOG, 1, [], source_builds, {APPROVED_SOURCE_CATALOG: False})
        source_builds[0]["Aliases"].append("mutated_after")
        after = SourceInventorySnapshot(APPROVED_SOURCE_CATALOG, 1, [], source_builds, {APPROVED_SOURCE_CATALOG: False})

        ok, diffs = snap.compare_with(after)
        self.assertFalse(ok)
        self.assertTrue(any("drifted" in d for d in diffs))

    def test_package_dirty_drift_detected(self):
        snap2 = SourceInventorySnapshot(
            catalog_path=APPROVED_SOURCE_CATALOG,
            schema_version=1,
            weapons=[{"WeaponId": "Strength", "StyleName": "ClaymoreCombatStyle"}],
            builds=[{"BuildId": "Strength", "LegacySlot": 1, "Aliases": ["str"]}],
            package_dirty_states={APPROVED_SOURCE_CATALOG: True}  # Dirtied!
        )
        ok, diffs = self.snap1.compare_with(snap2)
        self.assertFalse(ok)
        self.assertTrue(any("Package dirty state changed" in d for d in diffs))

    def test_missing_package_in_snapshot_detected(self):
        # Missing package in comparison snapshot
        snap2 = SourceInventorySnapshot(
            catalog_path=APPROVED_SOURCE_CATALOG,
            schema_version=1,
            weapons=[{"WeaponId": "Strength", "StyleName": "ClaymoreCombatStyle"}],
            builds=[{"BuildId": "Strength", "LegacySlot": 1, "Aliases": ["str"]}],
            package_dirty_states={}  # Missing!
        )
        ok, diffs = self.snap1.compare_with(snap2)
        self.assertFalse(ok)
        self.assertTrue(any("missing from snapshot" in d for d in diffs))


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
    def setUp(self):
        json_path = os.path.join(_SCRIPT_DIR, "examples", "boss_draft_profiles.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.baseline_boss = data["profiles"][0]

    def test_baseline_boss_profile_passes(self):
        ok, errs = validate_boss_profile_data(copy.deepcopy(self.baseline_boss), [], [])
        self.assertTrue(ok)
        self.assertEqual(len(errs), 0)

    def test_nan_numeric_value_rejected(self):
        changed = copy.deepcopy(self.baseline_boss)
        changed["stats"]["MaxHealth"] = float("nan")
        ok, errs = validate_boss_profile_data(changed, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("is NaN" in e for e in errs))

    def test_nan_phase_multiplier_rejected(self):
        changed = copy.deepcopy(self.baseline_boss)
        changed["phases"][0]["SpeedMultiplier"] = float("nan")
        ok, errs = validate_boss_profile_data(changed, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("is NaN" in e for e in errs))

    def test_unknown_invented_field_rejected(self):
        changed = copy.deepcopy(self.baseline_boss)
        changed["encounter_policy"]["auto_target_player"] = True
        ok, errs = validate_boss_profile_data(changed, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("unknown native property" in e for e in errs))

    def test_invalid_bool_type_rejected(self):
        changed = copy.deepcopy(self.baseline_boss)
        changed["encounter_policy"]["bResetOnPlayerRespawn"] = "not-a-bool"
        ok, errs = validate_boss_profile_data(changed, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("expected bool" in e for e in errs))

    def test_entry_health_fraction_domain(self):
        # 0.0 and 1.0 are legal boundaries
        p0 = copy.deepcopy(self.baseline_boss)
        p0["phases"][0]["EntryHealthFraction"] = 0.0
        ok, errs = validate_boss_profile_data(p0, [], [])
        self.assertTrue(ok)

        p1 = copy.deepcopy(self.baseline_boss)
        p1["phases"][0]["EntryHealthFraction"] = 1.0
        ok, errs = validate_boss_profile_data(p1, [], [])
        self.assertTrue(ok)

        # > 1.0 or < 0.0 rejected
        p_bad = copy.deepcopy(self.baseline_boss)
        p_bad["phases"][0]["EntryHealthFraction"] = 1.25
        ok, errs = validate_boss_profile_data(p_bad, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("outside valid range" in e for e in errs))

    def test_boss_multiple_phases_rejected(self):
        p = copy.deepcopy(self.baseline_boss)
        p["phases"].append(copy.deepcopy(p["phases"][0]))
        ok, errs = validate_boss_profile_data(p, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("requires exactly 1 transition record" in e for e in errs))


class TestRecordingFakeWriter(unittest.TestCase):
    def test_apply_writes_and_verifies_all_properties(self):
        """
        Uses Codex's recording fake pattern to prove that execute_draft_apply writes
        and reads back all 15 typed properties with ZERO omissions.
        """
        class RecordedAsset:
            def __init__(self):
                self.values = {}
            def set_editor_property(self, key, value):
                self.values[key] = value
            def get_editor_property(self, key):
                return self.values[key]

        created = []
        class Tools:
            def create_asset(self, *args):
                val = RecordedAsset()
                created.append(val)
                return val

        fake_unreal = SimpleNamespace(
            AssetToolsHelpers=SimpleNamespace(get_asset_tools=lambda: Tools()),
            load_class=lambda *args: "RecordingFakeClass",
            EditorAssetLibrary=SimpleNamespace(does_asset_exist=lambda _: False),
            DataAssetFactory=RecordedAsset,
            Name=lambda v: v,
            SoftObjectPath=lambda v: v,
        )

        # Load real example profile
        json_path = os.path.join(_SCRIPT_DIR, "examples", "boss_draft_profiles.json")
        with open(json_path, "r", encoding="utf-8") as f:
            profiles = json.load(f)["profiles"]

        import draft_boss_profiles
        orig_unreal = draft_boss_profiles.unreal
        orig_has_unreal = draft_boss_profiles.HAS_UNREAL
        try:
            draft_boss_profiles.unreal = fake_unreal
            draft_boss_profiles.HAS_UNREAL = True

            plan = {"profiles": [copy.deepcopy(profiles[0])]}
            success = execute_draft_apply(plan, save_requested=False)
            self.assertTrue(success)

            expected_fields = {
                "schema", "definition_id", "presentation_id", "skeleton",
                "animations", "stats", "encounter_policy", "stagger_policy",
                "phase_flow", "fireball", "phase_dependencies", "stagger_profile",
                "dormant_wake", "phases", "fields"
            }
            written = set(created[0].values.keys())
            self.assertEqual(expected_fields - written, set())
            self.assertEqual(len(written), 15)

        finally:
            draft_boss_profiles.unreal = orig_unreal
            draft_boss_profiles.HAS_UNREAL = orig_has_unreal


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
