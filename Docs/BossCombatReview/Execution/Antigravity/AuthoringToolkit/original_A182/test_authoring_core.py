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
    10. Backend native capability constraints (health floor > 1.0, damage scale floor >= 1.0, 0.0 < fraction <= 1.0)
    11. Strict fail-closed editor environment guard and API presence verification
    12. Recording fake writer verification (zero omitted typed fields on apply)
    13. Partial operation reporting records
    14. Engine property-name rules (PyGenUtil.cpp:1833-1855 repeated b+Upper and In+Upper stripping, self->_self, SourceSHA256)
    15. Float32 IEEE 754 precision, overflow rejection, and fake storage parity
    16. Readback fallback removal (strict generated property access on wrappers and dicts)

Offline Float64 Qualification:
    All offline tests run in CPython float64, which does NOT certify native float32 conversion
    or input-mode parity. The authoring toolkit uses struct.pack('f') / struct.unpack('f')
    to simulate native float32 truncation and verify that valid float32 values survive round-trip,
    but offline execution does not execute native UE5.5 C++ serialization, memory layouts, or
    input-mode controller parity.
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
    NATIVE_HEALTH_OVERRIDE_FLOOR,
    NATIVE_DAMAGE_SCALE_FLOOR,
    NATIVE_CRITICAL_MULTIPLIER_FLOOR,
    NATIVE_BOSS_STATS_FIELDS,
    NATIVE_ENCOUNTER_POLICY_FIELDS,
    NATIVE_STAGGER_POLICY_FIELDS,
    NATIVE_PHASE_FLOW_FIELDS,
    NATIVE_FIREBALL_FIELDS,
    NATIVE_PHASE_DEPENDENCY_FIELDS,
    NATIVE_STAGGER_PROFILE_FIELDS,
    NATIVE_DORMANT_WAKE_FIELDS,
    NATIVE_PHASE_CONFIG_FIELDS,
    NATIVE_PARITY_FIELD_FIELDS,
    pythonize_property_name,
    map_native_dict_to_python_keys,
    extract_canonical_primitives,
    to_float32,
    normalize_native_expected_for_readback,
    FLOAT32_MAX,
    FLOAT32_MIN,
    validate_boss_stats_domain,
    validate_encounter_policy_domain,
    validate_stagger_policy_domain,
    validate_phase_flow_domain,
    validate_fireball_domain,
    validate_phase_config_domain,
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
from draft_boss_profiles import (
    validate_boss_profile_data,
    execute_draft_apply,
    verify_editor_environment,
)


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
        bad_builds = copy.deepcopy(self.valid_builds)
        bad_builds[0]["WeaponId"] = "Sword"
        ok, errors = validate_pinned_legacy_contract(bad_builds, self.valid_weapons)
        self.assertFalse(ok)
        self.assertTrue(any("Slot 0 WeaponId mismatch" in e for e in errors))

    def test_plural_dualswords_style_fails(self):
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

    def test_entry_health_fraction_strict_domain(self):
        # RPGBossPhaseAdapters.cpp:122: Record->EntryHealthFraction <= 0.f || Record->EntryHealthFraction > 1.f
        # 0.0 is strictly illegal! (Must be ABOVE 0)
        p_zero = copy.deepcopy(self.baseline_boss)
        p_zero["phases"][0]["EntryHealthFraction"] = 0.0
        ok, errs = validate_boss_profile_data(p_zero, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("expected strictly above 0.0" in e for e in errs))

        # Negative is illegal
        p_neg = copy.deepcopy(self.baseline_boss)
        p_neg["phases"][0]["EntryHealthFraction"] = -0.1
        ok, errs = validate_boss_profile_data(p_neg, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("expected strictly above 0.0" in e for e in errs))

        # 1.0 is legal boundary
        p1 = copy.deepcopy(self.baseline_boss)
        p1["phases"][0]["EntryHealthFraction"] = 1.0
        ok, errs = validate_boss_profile_data(p1, [], [])
        self.assertTrue(ok)

        # > 1.0 is illegal
        p_bad = copy.deepcopy(self.baseline_boss)
        p_bad["phases"][0]["EntryHealthFraction"] = 1.25
        ok, errs = validate_boss_profile_data(p_bad, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("expected strictly above 0.0" in e for e in errs))

    def test_attack_multiplier_floor(self):
        # RPGBossPhaseAdapters.cpp:149: Record->AttackMultiplier < NativeDamageScaleFloor (1.0)
        p_low = copy.deepcopy(self.baseline_boss)
        p_low["phases"][0]["AttackMultiplier"] = 0.8
        ok, errs = validate_boss_profile_data(p_low, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("native damage scale floor" in e for e in errs))

        p_floor = copy.deepcopy(self.baseline_boss)
        p_floor["phases"][0]["AttackMultiplier"] = 1.0
        ok, errs = validate_boss_profile_data(p_floor, [], [])
        self.assertTrue(ok)

    def test_speed_and_rate_multipliers_positive(self):
        # RPGBossPhaseAdapters.cpp:131: Multiplier.Value <= 0.f
        p_zero = copy.deepcopy(self.baseline_boss)
        p_zero["phases"][0]["SpeedMultiplier"] = 0.0
        ok, errs = validate_boss_profile_data(p_zero, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("must be strictly positive" in e for e in errs))

        p_rate_neg = copy.deepcopy(self.baseline_boss)
        p_rate_neg["phases"][0]["RateMultiplier"] = -1.0
        ok, errs = validate_boss_profile_data(p_rate_neg, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("must be strictly positive" in e for e in errs))

    def test_health_and_posture_native_floors(self):
        # RPGBossStatsAdapters.cpp:95: Stats.MaxHealth <= NativeHealthOverrideFloor (1.0)
        p_hp = copy.deepcopy(self.baseline_boss)
        p_hp["stats"]["MaxHealth"] = 1.0
        ok, errs = validate_boss_profile_data(p_hp, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("native health override floor" in e for e in errs))

        # RPGBossStatsAdapters.cpp:79: Stats.MaxPosture <= 0.f
        p_posture = copy.deepcopy(self.baseline_boss)
        p_posture["stats"]["MaxPosture"] = 0.0
        ok, errs = validate_boss_profile_data(p_posture, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("must be strictly positive" in e for e in errs))

    def test_boss_multiple_phases_rejected(self):
        p = copy.deepcopy(self.baseline_boss)
        p["phases"].append(copy.deepcopy(p["phases"][0]))
        ok, errs = validate_boss_profile_data(p, [], [])
        self.assertFalse(ok)
        self.assertTrue(any("requires exactly 1 transition record" in e for e in errs))


class TestFailClosedEditorGuard(unittest.TestCase):
    """
    Dedicated adversarial test suite verifying that verify_editor_environment fails closed
    upon absence of ANY required Unreal API or when PIE world is active.
    """
    def setUp(self):
        import draft_boss_profiles
        self.module = draft_boss_profiles
        self.orig_unreal = self.module.unreal
        self.orig_has_unreal = self.module.HAS_UNREAL

    def tearDown(self):
        self.module.unreal = self.orig_unreal
        self.module.HAS_UNREAL = self.orig_has_unreal

    def test_offline_environment_rejected(self):
        self.module.HAS_UNREAL = False
        self.module.unreal = None
        ok, err = self.module.verify_editor_environment()
        self.assertFalse(ok)
        self.assertIn("running in pure offline Python", err)

    def test_empty_unreal_namespace_rejected(self):
        self.module.HAS_UNREAL = True
        self.module.unreal = SimpleNamespace()
        ok, err = self.module.verify_editor_environment()
        self.assertFalse(ok)
        self.assertIn("Missing required Unreal API: unreal.SystemLibrary", err)

    def test_missing_is_editor_rejected(self):
        self.module.HAS_UNREAL = True
        self.module.unreal = SimpleNamespace(SystemLibrary=SimpleNamespace())
        ok, err = self.module.verify_editor_environment()
        self.assertFalse(ok)
        self.assertIn("Missing required Unreal API: unreal.SystemLibrary.is_editor", err)

    def test_is_editor_returning_false_rejected(self):
        self.module.HAS_UNREAL = True
        self.module.unreal = SimpleNamespace(SystemLibrary=SimpleNamespace(is_editor=lambda: False))
        ok, err = self.module.verify_editor_environment()
        self.assertFalse(ok)
        self.assertIn("Not running in Unreal Editor", err)

    def test_missing_subsystem_api_rejected(self):
        self.module.HAS_UNREAL = True
        self.module.unreal = SimpleNamespace(SystemLibrary=SimpleNamespace(is_editor=lambda: True))
        ok, err = self.module.verify_editor_environment()
        self.assertFalse(ok)
        self.assertIn("Missing required Unreal API: unreal.get_editor_subsystem", err)

    def test_subsystem_returning_none_rejected(self):
        self.module.HAS_UNREAL = True
        self.module.unreal = SimpleNamespace(
            SystemLibrary=SimpleNamespace(is_editor=lambda: True),
            get_editor_subsystem=lambda cls: None,
            UnrealEditorSubsystem="SubsystemClass"
        )
        ok, err = self.module.verify_editor_environment()
        self.assertFalse(ok)
        self.assertIn("UnrealEditorSubsystem is not available (returned None)", err)

    def test_pie_simulation_mode_rejected(self):
        self.module.HAS_UNREAL = True
        self.module.unreal = SimpleNamespace(
            SystemLibrary=SimpleNamespace(is_editor=lambda: True),
            get_editor_subsystem=lambda cls: SimpleNamespace(get_game_world=lambda: "SimWorldObject"),
            UnrealEditorSubsystem="SubsystemClass"
        )
        ok, err = self.module.verify_editor_environment()
        self.assertFalse(ok)
        self.assertIn("PIE / Simulation mode", err)

    def test_valid_editor_surface_accepted(self):
        self.module.HAS_UNREAL = True
        self.module.unreal = SimpleNamespace(
            SystemLibrary=SimpleNamespace(is_editor=lambda: True),
            get_editor_subsystem=lambda cls: SimpleNamespace(get_game_world=lambda: None),
            UnrealEditorSubsystem="SubsystemClass"
        )
        ok, err = self.module.verify_editor_environment()
        self.assertTrue(ok)
        self.assertEqual(err, "")


class TestPythonPropertyMapping(unittest.TestCase):
    def test_pythonize_property_names(self):
        # PascalCase to snake_case
        self.assertEqual(pythonize_property_name("MaxHealth", False), "max_health")
        self.assertEqual(pythonize_property_name("MaxPosture", False), "max_posture")
        self.assertEqual(pythonize_property_name("PostureRegenDelay", False), "posture_regen_delay")
        self.assertEqual(pythonize_property_name("RiposteAlignSeconds", False), "riposte_align_seconds")
        self.assertEqual(pythonize_property_name("FireballCooldown", False), "fireball_cooldown")
        self.assertEqual(pythonize_property_name("HitStunAbilityClassName", False), "hit_stun_ability_class_name")
        self.assertEqual(pythonize_property_name("EntryHealthFraction", False), "entry_health_fraction")

        # Boolean prefix stripping ('b' followed by uppercase stripped)
        self.assertEqual(pythonize_property_name("bResetOnPlayerRespawn", True), "reset_on_player_respawn")
        self.assertEqual(pythonize_property_name("bHoldPostureAtZero", True), "hold_posture_at_zero")
        self.assertEqual(pythonize_property_name("bUseRoarClip", True), "use_roar_clip")
        self.assertEqual(pythonize_property_name("bPausePostureInTransition", True), "pause_posture_in_transition")
        self.assertEqual(pythonize_property_name("bLockLeapUntilPhaseTwo", True), "lock_leap_until_phase_two")
        self.assertEqual(pythonize_property_name("bFireballEnabled", True), "fireball_enabled")
        self.assertEqual(pythonize_property_name("bUseClips", True), "use_clips")
        self.assertEqual(pythonize_property_name("bUseRiposteClips", True), "use_riposte_clips")
        self.assertEqual(pythonize_property_name("bCriticalOnEveryHit", True), "critical_on_every_hit")

    def test_map_native_dict_to_python_keys(self):
        native_stats = {"MaxHealth": 500.0, "MaxPosture": 100.0, "PostureRegenDelay": 3.0, "PostureRegenRate": 10.0}
        py_stats = map_native_dict_to_python_keys(native_stats, NATIVE_BOSS_STATS_FIELDS)
        self.assertEqual(py_stats["max_health"], 500.0)
        self.assertEqual(py_stats["max_posture"], 100.0)
        self.assertNotIn("MaxHealth", py_stats)

        native_stagger = {"StaggerSeconds": 5.0, "RiposteAlignSeconds": 0.3, "bHoldPostureAtZero": False, "CriticalMultiplier": 2.5}
        py_stagger = map_native_dict_to_python_keys(native_stagger, NATIVE_STAGGER_POLICY_FIELDS)
        self.assertEqual(py_stagger["riposte_align_seconds"], 0.3)
        self.assertEqual(py_stagger["hold_posture_at_zero"], False)
        self.assertNotIn("bHoldPostureAtZero", py_stagger)

    def test_extract_canonical_primitives_roundtrip(self):
        class FakeWrapper:
            def __init__(self, d):
                for k, v in d.items():
                    setattr(self, k, v)

        native_stagger = {
            "StaggerSeconds": 5.0, "FreezeAtPosition": 0.0, "CriticalMultiplier": 2.5,
            "RiposteRange": 300.0, "RiposteConeDegrees": 90.0, "RiposteFacingDegrees": 180.0,
            "RiposteArmSeconds": 1.5, "RipostePlayerStartGap": 50.0, "RiposteAlignSeconds": 0.3,
            "RiposteImpactSeconds": 0.5, "RiposteBaseDamage": 40.0, "CooldownSeconds": 10.0,
            "GetUpRate": 0.6, "bHoldPostureAtZero": False
        }
        py_mapped = map_native_dict_to_python_keys(native_stagger, NATIVE_STAGGER_POLICY_FIELDS)
        wrapper = FakeWrapper(py_mapped)
        canonical = extract_canonical_primitives(wrapper, NATIVE_STAGGER_POLICY_FIELDS)
        self.assertEqual(canonical, native_stagger)


class TestScalarDomainTable(unittest.TestCase):
    def test_stagger_policy_domain(self):
        # CriticalMultiplier floor >= 1.0 (NATIVE_CRITICAL_MULTIPLIER_FLOOR)
        self.assertTrue(validate_stagger_policy_domain({"CriticalMultiplier": 0.9}))
        self.assertFalse(validate_stagger_policy_domain({"CriticalMultiplier": 1.0}))
        self.assertFalse(validate_stagger_policy_domain({"CriticalMultiplier": 2.5}))

        # Non-negative scalars (0.0 is legal boundary)
        for field in ("StaggerSeconds", "FreezeAtPosition", "RiposteRange", "RiposteArmSeconds",
                      "RipostePlayerStartGap", "RiposteImpactSeconds", "RiposteBaseDamage", "CooldownSeconds"):
            self.assertTrue(validate_stagger_policy_domain({field: -0.1}))
            self.assertFalse(validate_stagger_policy_domain({field: 0.0}))
            self.assertFalse(validate_stagger_policy_domain({field: 10.0}))

        # Strictly positive division fields
        for pos_field in ("RiposteAlignSeconds", "GetUpRate"):
            self.assertTrue(validate_stagger_policy_domain({pos_field: 0.0}))
            self.assertTrue(validate_stagger_policy_domain({pos_field: -1.0}))
            self.assertFalse(validate_stagger_policy_domain({pos_field: 0.01}))

        # Angular ranges [0.0, 360.0]
        for ang_field in ("RiposteConeDegrees", "RiposteFacingDegrees"):
            self.assertTrue(validate_stagger_policy_domain({ang_field: -1.0}))
            self.assertTrue(validate_stagger_policy_domain({ang_field: 360.1}))
            self.assertFalse(validate_stagger_policy_domain({ang_field: 0.0}))
            self.assertFalse(validate_stagger_policy_domain({ang_field: 180.0}))
            self.assertFalse(validate_stagger_policy_domain({ang_field: 360.0}))

    def test_encounter_policy_domain(self):
        self.assertTrue(validate_encounter_policy_domain({"GateRadius": -1.0}))
        self.assertFalse(validate_encounter_policy_domain({"GateRadius": 0.0}))  # 0 is legal (no gate)
        self.assertFalse(validate_encounter_policy_domain({"GateRadius": 1200.0}))

    def test_phase_flow_domain(self):
        self.assertTrue(validate_phase_flow_domain({"TransitionSeconds": -0.5}))
        self.assertFalse(validate_phase_flow_domain({"TransitionSeconds": 0.0}))
        self.assertFalse(validate_phase_flow_domain({"TransitionSeconds": 3.0}))

    def test_fireball_domain(self):
        # Cooldown min >= 0, max >= min
        self.assertTrue(validate_fireball_domain({"FireballCooldown": [-1.0, 10.0]}))
        self.assertTrue(validate_fireball_domain({"FireballCooldown": [15.0, 10.0]}))
        self.assertFalse(validate_fireball_domain({"FireballCooldown": [0.0, 10.0]}))
        self.assertFalse(validate_fireball_domain({"FireballCooldown": [10.0, 10.0]}))

        # Ranges
        self.assertTrue(validate_fireball_domain({"FireballMinRange": -10.0}))
        self.assertTrue(validate_fireball_domain({"FireballMinRange": 1000.0, "FireballMaxRange": 500.0}))
        self.assertFalse(validate_fireball_domain({"FireballMinRange": 0.0, "FireballMaxRange": 2000.0}))


class TestRecordingFakeWriter(unittest.TestCase):
    def setUp(self):
        import draft_boss_profiles
        self.module = draft_boss_profiles
        self.orig_unreal = self.module.unreal
        self.orig_has_unreal = self.module.HAS_UNREAL

    def tearDown(self):
        self.module.unreal = self.orig_unreal
        self.module.HAS_UNREAL = self.orig_has_unreal

    def test_apply_fails_closed_when_api_missing(self):
        incomplete_fake = SimpleNamespace(
            SystemLibrary=SimpleNamespace(is_editor=lambda: True),
            get_editor_subsystem=lambda cls: SimpleNamespace(get_game_world=lambda: None),
            UnrealEditorSubsystem="SubsystemClass",
            AssetToolsHelpers=SimpleNamespace(get_asset_tools=lambda: SimpleNamespace(create_asset=lambda *a: None))
        )
        self.module.HAS_UNREAL = True
        self.module.unreal = incomplete_fake
        success = execute_draft_apply({"profiles": []}, save_requested=False)
        self.assertFalse(success)

    def test_apply_writes_and_verifies_all_properties_with_python_mapping(self):
        """
        Enforces that execute_draft_apply sets and reads back all 15 properties using generated
        Python property names (PyGenUtil parity). The fake struct wrapper only populates attributes
        for pythonized property keys, ensuring that raw CamelCase dicts would cause default-loss
        and be rejected during readback verification.
        """
        class PyWrapperStructFake:
            def __init__(self, raw_val):
                # raw_val is expected to be a dictionary with pythonized keys.
                # In real Unreal Engine, C++ float properties are stored as float32 single-precision.
                # Storing float32 ensures that offline readback verification cannot hide precision drift.
                if isinstance(raw_val, dict):
                    for k, v in raw_val.items():
                        if isinstance(v, float):
                            setattr(self, k, to_float32(v))
                        elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], float):
                            setattr(self, k, [to_float32(x) for x in v])
                        else:
                            setattr(self, k, v)
                else:
                    self._val = raw_val

        class RecordedAsset:
            def __init__(self):
                self.values = {}
            def set_editor_property(self, key, value):
                # Wrap structs and phase/field items in PyWrapperStructFake
                if isinstance(value, dict):
                    self.values[key] = PyWrapperStructFake(value)
                elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    self.values[key] = [PyWrapperStructFake(item) for item in value]
                else:
                    self.values[key] = value
            def get_editor_property(self, key):
                return self.values[key]

        created = []
        class Tools:
            def create_asset(self, *args):
                val = RecordedAsset()
                created.append(val)
                return val

        valid_fake = SimpleNamespace(
            SystemLibrary=SimpleNamespace(is_editor=lambda: True),
            get_editor_subsystem=lambda cls: SimpleNamespace(get_game_world=lambda: None),
            UnrealEditorSubsystem="SubsystemClass",
            AssetToolsHelpers=SimpleNamespace(get_asset_tools=lambda: Tools()),
            load_class=lambda *args: "RecordingFakeClass",
            EditorAssetLibrary=SimpleNamespace(does_asset_exist=lambda _: False),
            DataAssetFactory=RecordedAsset,
            Name=lambda v: SimpleNamespace(to_string=lambda: str(v)),
            SoftObjectPath=lambda v: SimpleNamespace(to_string=lambda: str(v)),
        )

        json_path = os.path.join(_SCRIPT_DIR, "examples", "boss_draft_profiles.json")
        with open(json_path, "r", encoding="utf-8") as f:
            profiles = json.load(f)["profiles"]

        self.module.unreal = valid_fake
        self.module.HAS_UNREAL = True

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



class TestEnginePropertyNameRules(unittest.TestCase):
    """
    Tests engine-accurate Python property name generation per UE5.5 PyGenUtil.cpp:1833-1855:
    - Repeated stripping of leading 'b' + uppercase and 'In' + uppercase for ANY property type.
    - Reserved keyword mapping: 'self' -> '_self'.
    - Pinned test for 'SourceSHA256' -> 'source_sha256'.
    - Verification across all 64 native fields.
    """
    def test_repeated_prefix_stripping(self):
        # Leading 'b' + uppercase on boolean and non-boolean properties
        self.assertEqual(pythonize_property_name("bMultiplier"), "multiplier")
        self.assertEqual(pythonize_property_name("bResetOnPlayerRespawn"), "reset_on_player_respawn")
        # Leading 'In' + uppercase on parameters / inputs
        self.assertEqual(pythonize_property_name("InDamage"), "damage")
        self.assertEqual(pythonize_property_name("InHealthFraction"), "health_fraction")
        # Repeated combinations (b + In, In + b, multiple In)
        self.assertEqual(pythonize_property_name("bInDamage"), "damage")
        self.assertEqual(pythonize_property_name("bInInDamage"), "damage")
        self.assertEqual(pythonize_property_name("bInInTest"), "test")

    def test_pinned_source_sha256(self):
        # In UE5.5 CamelCaseBreakIterator, digits stay with the preceding uppercase run
        self.assertEqual(pythonize_property_name("SourceSHA256"), "source_sha256")

    def test_reserved_keyword_self(self):
        # PyGenUtil maps 'self' identifier to '_self'
        self.assertEqual(pythonize_property_name("self"), "_self")
        self.assertEqual(pythonize_property_name("Self"), "_self")

    def test_non_bool_b_prefix(self):
        # Engine rule is type-independent: b + uppercase is stripped regardless of declared type
        self.assertEqual(pythonize_property_name("bScale"), "scale")
        self.assertEqual(pythonize_property_name("bAngleDegrees"), "angle_degrees")

    def test_all_64_native_fields_parity(self):
        # Verifies all 64 fields across all 10 native struct specs
        specs = [
            NATIVE_BOSS_STATS_FIELDS,
            NATIVE_ENCOUNTER_POLICY_FIELDS,
            NATIVE_STAGGER_POLICY_FIELDS,
            NATIVE_PHASE_FLOW_FIELDS,
            NATIVE_FIREBALL_FIELDS,
            NATIVE_PHASE_DEPENDENCY_FIELDS,
            NATIVE_STAGGER_PROFILE_FIELDS,
            NATIVE_DORMANT_WAKE_FIELDS,
            NATIVE_PHASE_CONFIG_FIELDS,
            NATIVE_PARITY_FIELD_FIELDS,
        ]
        total_fields = 0
        for spec in specs:
            for native_name in spec:
                total_fields += 1
                py_name = pythonize_property_name(native_name)
                self.assertTrue(len(py_name) > 0)
                self.assertEqual(py_name, py_name.lower())
                self.assertNotIn(" ", py_name)
        self.assertEqual(total_fields, 64)


class TestFloat32RoundTripAndStorage(unittest.TestCase):
    """
    Tests IEEE 754 32-bit single precision truncation, overflow detection, and readback parity:
    - Verifies that offline float64 checks do NOT certify native float32 conversion or input-mode parity.
    - Round-trip values (0.03, 0.35, 0.6) demonstrate precision loss in float64.
    - Refuses requested values that are finite in float64 but overflow float32.
    - Verifies that direct float64 comparison fails against float32 storage, while normalize_native_expected_for_readback succeeds.
    """
    def test_float32_precision_round_trip(self):
        v = 0.03
        f32 = to_float32(v)
        self.assertNotEqual(v, f32)
        self.assertEqual(f32, 0.029999999329447746)
        # Idempotent round trip
        self.assertEqual(to_float32(f32), f32)

        v2 = 0.35
        f32_2 = to_float32(v2)
        self.assertNotEqual(v2, f32_2)
        self.assertEqual(f32_2, 0.3499999940395355)

        v3 = 0.6
        f32_3 = to_float32(v3)
        self.assertNotEqual(v3, f32_3)
        self.assertEqual(f32_3, 0.6000000238418579)

    def test_float32_overflow_rejection(self):
        # Finite in float64, overflows float32 (> 3.4028235e+38)
        overflow_val = 1.0e39
        with self.assertRaises(ValueError):
            to_float32(overflow_val)

        with self.assertRaises(ValueError):
            to_float32(-1.0e39)

        # validate_finite_float also rejects float32 overflow
        ok, err = validate_finite_float(overflow_val, "TestField")
        self.assertFalse(ok)
        self.assertIn("overflows 32-bit", err)

    def test_normalize_native_expected_for_readback(self):
        raw_phase = {
            "PhaseId": "P1",
            "EntryHealthFraction": 0.35,
            "SpeedMultiplier": 0.03,
            "RateMultiplier": 0.6,
            "AttackMultiplier": 1.0
        }
        norm = normalize_native_expected_for_readback(raw_phase, NATIVE_PHASE_CONFIG_FIELDS)
        self.assertEqual(norm["PhaseId"], "P1")
        self.assertEqual(norm["EntryHealthFraction"], to_float32(0.35))
        self.assertEqual(norm["SpeedMultiplier"], to_float32(0.03))
        self.assertEqual(norm["RateMultiplier"], to_float32(0.6))
        self.assertEqual(norm["AttackMultiplier"], 1.0)

    def test_regression_old_float64_comparison_fails_against_float32_store(self):
        class StructWrapperWithFloat32:
            def __init__(self):
                self.phase_id = "P1"
                self.entry_health_fraction = to_float32(0.35)
                self.speed_multiplier = to_float32(0.03)
                self.rate_multiplier = to_float32(0.6)
                self.attack_multiplier = 1.0

        wrapper = StructWrapperWithFloat32()
        canonical = extract_canonical_primitives(wrapper, NATIVE_PHASE_CONFIG_FIELDS)

        raw_expected = {
            "PhaseId": "P1",
            "EntryHealthFraction": 0.35,
            "SpeedMultiplier": 0.03,
            "RateMultiplier": 0.6,
            "AttackMultiplier": 1.0
        }

        # OLD COMPARISON: Fails because 0.3499999940395355 != 0.35
        self.assertNotEqual(canonical, raw_expected)

        # NEW COMPARISON: Succeeds after float32 round-trip normalization
        normalized_expected = normalize_native_expected_for_readback(raw_expected, NATIVE_PHASE_CONFIG_FIELDS)
        self.assertEqual(canonical, normalized_expected)


class TestNoReadbackFallback(unittest.TestCase):
    """
    Enforces strict removal of CamelCase fallback in extract_canonical_primitives:
    - Struct wrappers expose ONLY generated Python names; CamelCase-only wrapper must raise AttributeError.
    - Dictionaries expose ONLY generated Python keys; CamelCase-only dict must raise KeyError.
    """
    def test_camelcase_wrapper_raises_attribute_error(self):
        class CamelCaseOnlyWrapper:
            def __init__(self):
                self.MaxHealth = 1500.0
                self.MaxPosture = 200.0

        wrapper = CamelCaseOnlyWrapper()
        with self.assertRaises(AttributeError) as ctx:
            extract_canonical_primitives(wrapper, NATIVE_BOSS_STATS_FIELDS)
        self.assertIn("Struct wrapper missing generated attribute 'max_health'", str(ctx.exception))
        self.assertIn("native CamelCase name 'MaxHealth' is not exposed", str(ctx.exception))

    def test_camelcase_dict_raises_key_error(self):
        camel_dict = {
            "MaxHealth": 1500.0,
            "MaxPosture": 200.0
        }
        with self.assertRaises(KeyError) as ctx:
            extract_canonical_primitives(camel_dict, NATIVE_BOSS_STATS_FIELDS)
        self.assertIn("Missing generated property 'max_health'", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
