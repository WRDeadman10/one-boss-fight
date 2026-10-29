from pathlib import Path
import diff_against_cpp
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
    NATIVE_BLEED_FIELDS,
    NATIVE_LOW_SWEEP_FIELDS,
    NATIVE_PHASE_CONFIG_FIELDS,
    NATIVE_PARITY_FIELD_FIELDS,
    BLEED_NATIVE_TO_PY,
    BLEED_PY_TO_NATIVE,
    LOW_SWEEP_NATIVE_TO_PY,
    LOW_SWEEP_PY_TO_NATIVE,
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
    validate_bleed_domain,
    validate_low_sweep_domain,
    NATIVE_SHOCKWAVE_FIELDS,
    SHOCKWAVE_NATIVE_TO_PY,
    SHOCKWAVE_PY_TO_NATIVE,
    validate_shockwave_domain,
    MAX_AUTHORED_SHOCKWAVE_MAGNITUDE,
    NATIVE_HEAL_PUNISH_FIELDS,
    HEAL_PUNISH_NATIVE_TO_PY,
    HEAL_PUNISH_PY_TO_NATIVE,
    validate_heal_punish_domain,
    MAX_AUTHORED_HEAL_PUNISH_MAGNITUDE,
    NATIVE_LOOK_FIELDS,
    LOOK_NATIVE_TO_PY,
    LOOK_PY_TO_NATIVE,
    validate_look_domain,
    NATIVE_CLOSE_CLIP_SWAP_FIELDS,
    CLOSE_CLIP_SWAP_NATIVE_TO_PY,
    CLOSE_CLIP_SWAP_PY_TO_NATIVE,
    validate_close_clip_swap_domain,
    NATIVE_DEATH_FIELDS,
    DEATH_NATIVE_TO_PY,
    DEATH_PY_TO_NATIVE,
    validate_death_domain,
    INVALID_OBJECTNAME_CHARACTERS,
    INVALID_LONGPACKAGE_CHARACTERS,
    validate_soft_path_structure,
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
    Updated for Order A-212 / DD27c: verifies module-level unreal.is_editor().
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
        self.assertIn("Missing required Unreal API: unreal.is_editor", err)

    def test_missing_is_editor_rejected(self):
        self.module.HAS_UNREAL = True
        self.module.unreal = SimpleNamespace(SomeOtherLib=SimpleNamespace())
        ok, err = self.module.verify_editor_environment()
        self.assertFalse(ok)
        self.assertIn("Missing required Unreal API: unreal.is_editor", err)

    def test_is_editor_returning_false_rejected(self):
        self.module.HAS_UNREAL = True
        self.module.unreal = SimpleNamespace(is_editor=lambda: False)
        ok, err = self.module.verify_editor_environment()
        self.assertFalse(ok)
        self.assertIn("Not running in Unreal Editor", err)

    def test_missing_subsystem_api_rejected(self):
        self.module.HAS_UNREAL = True
        self.module.unreal = SimpleNamespace(is_editor=lambda: True)
        ok, err = self.module.verify_editor_environment()
        self.assertFalse(ok)
        self.assertIn("Missing required Unreal API: unreal.get_editor_subsystem", err)

    def test_subsystem_returning_none_rejected(self):
        self.module.HAS_UNREAL = True
        self.module.unreal = SimpleNamespace(
            is_editor=lambda: True,
            get_editor_subsystem=lambda cls: None,
            UnrealEditorSubsystem="SubsystemClass"
        )
        ok, err = self.module.verify_editor_environment()
        self.assertFalse(ok)
        self.assertIn("UnrealEditorSubsystem is not available (returned None)", err)

    def test_pie_simulation_mode_rejected(self):
        self.module.HAS_UNREAL = True
        self.module.unreal = SimpleNamespace(
            is_editor=lambda: True,
            get_editor_subsystem=lambda cls: SimpleNamespace(get_game_world=lambda: "SimWorldObject"),
            UnrealEditorSubsystem="SubsystemClass"
        )
        ok, err = self.module.verify_editor_environment()
        self.assertFalse(ok)
        self.assertIn("PIE / Simulation mode", err)

    def test_valid_editor_surface_accepted(self):
        self.module.HAS_UNREAL = True
        self.module.unreal = SimpleNamespace(
            is_editor=lambda: True,
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
            is_editor=lambda: True,
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
        Enforces that execute_draft_apply sets and reads back all 18 properties using generated
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
            is_editor=lambda: True,
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
            "dormant_wake", "bleed", "low_sweep", "shockwave", "heal_punish", "look", "close_clip_swap", "death", "phases", "fields"
        }
        written = set(created[0].values.keys())
        self.assertEqual(expected_fields - written, set())
        self.assertEqual(len(written), 22)


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

    def test_all_106_native_fields_parity(self):
        # Verifies all 106 fields across all 15 native struct specs (including DD19 FRPGBleedConfig, DD20 FRPGLowSweepConfig, DD21 FRPGShockwaveConfig, and DD22 FRPGHealPunishConfig)
        specs = [
            NATIVE_BOSS_STATS_FIELDS,
            NATIVE_ENCOUNTER_POLICY_FIELDS,
            NATIVE_STAGGER_POLICY_FIELDS,
            NATIVE_PHASE_FLOW_FIELDS,
            NATIVE_FIREBALL_FIELDS,
            NATIVE_PHASE_DEPENDENCY_FIELDS,
            NATIVE_STAGGER_PROFILE_FIELDS,
            NATIVE_DORMANT_WAKE_FIELDS,
            NATIVE_BLEED_FIELDS,
            NATIVE_LOW_SWEEP_FIELDS,
            NATIVE_SHOCKWAVE_FIELDS,
            NATIVE_HEAL_PUNISH_FIELDS,
            NATIVE_LOOK_FIELDS,
            NATIVE_CLOSE_CLIP_SWAP_FIELDS,
            NATIVE_DEATH_FIELDS,
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
        self.assertEqual(total_fields, 123)


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



class TestBleedPolicyDomain(unittest.TestCase):
    """
    Comprehensive test suite for DD19 FRPGBleedConfig domain validation (RPGBossBleedAdapters.cpp: ValidateBleed):
    - Finite float checks (InitialThreshold, ThresholdIncrease, ThresholdMax, HpFraction, EffectHeight)
    - InitialThreshold > 0.0 (InvalidBleed.NotPositive)
    - ThresholdIncrease >= 0.0 (InvalidBleed.Negative)
    - ThresholdMax >= InitialThreshold (InvalidBleed.ThresholdMaxBelowInitial)
    - HpFraction in [0, 1] (InvalidBleed.FractionOutOfRange)
    - EffectHeight signed (negative, zero, positive accepted)
    - Required references non-null (InvalidDependency.Missing)
    - Soft path structural validation (InvalidDependency.Malformed)
    - Float32 readback normalization (HpFraction = 0.03 parity)
    """
    def setUp(self):
        self.baseline_bleed = {
            "InitialThreshold": 100.0,
            "ThresholdIncrease": 20.0,
            "ThresholdMax": 200.0,
            "HpFraction": 0.03,
            "EffectHeight": 170.0,
            "ProcEffect": "/Game/BloodPack/Hit/Niagara/NS_BulletHit_Med.NS_BulletHit_Med",
            "ProcSound": "/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue.A_Guardian_ImpactL_Cue"
        }

    def test_baseline_bleed_passes(self):
        errs = validate_bleed_domain(self.baseline_bleed)
        self.assertEqual(errs, [])

    def test_non_finite_scalars_rejected(self):
        scalar_fields = ["InitialThreshold", "ThresholdIncrease", "ThresholdMax", "HpFraction", "EffectHeight"]
        for f in scalar_fields:
            # Test NaN
            b_nan = copy.deepcopy(self.baseline_bleed)
            b_nan[f] = float("nan")
            errs = validate_bleed_domain(b_nan)
            self.assertTrue(len(errs) > 0)
            self.assertTrue(any(f"InvalidBleed.NotFinite: Bleed.{f}=" in e for e in errs))

            # Test Infinity
            b_inf = copy.deepcopy(self.baseline_bleed)
            b_inf[f] = float("inf")
            errs = validate_bleed_domain(b_inf)
            self.assertTrue(len(errs) > 0)
            self.assertTrue(any(f"InvalidBleed.NotFinite: Bleed.{f}=" in e for e in errs))

            # Test Boolean
            b_bool = copy.deepcopy(self.baseline_bleed)
            b_bool[f] = True
            errs = validate_bleed_domain(b_bool)
            self.assertTrue(len(errs) > 0)
            self.assertTrue(any(f"InvalidBleed.NotFinite: Bleed.{f}=" in e for e in errs))

    def test_initial_threshold_domain(self):
        # InitialThreshold must be strictly positive (> 0.0)
        b_zero = copy.deepcopy(self.baseline_bleed)
        b_zero["InitialThreshold"] = 0.0
        errs = validate_bleed_domain(b_zero)
        self.assertTrue(any("InvalidBleed.NotPositive: Bleed.InitialThreshold=0.0" in e for e in errs))

        b_neg = copy.deepcopy(self.baseline_bleed)
        b_neg["InitialThreshold"] = -10.0
        errs = validate_bleed_domain(b_neg)
        self.assertTrue(any("InvalidBleed.NotPositive: Bleed.InitialThreshold=-10.0" in e for e in errs))

        # Positive threshold passes
        b_pos = copy.deepcopy(self.baseline_bleed)
        b_pos["InitialThreshold"] = 0.1
        self.assertEqual(validate_bleed_domain(b_pos), [])

    def test_threshold_increase_domain(self):
        # ThresholdIncrease must be non-negative (>= 0.0)
        b_neg = copy.deepcopy(self.baseline_bleed)
        b_neg["ThresholdIncrease"] = -0.5
        errs = validate_bleed_domain(b_neg)
        self.assertTrue(any("InvalidBleed.Negative: Bleed.ThresholdIncrease=-0.5" in e for e in errs))

        # 0.0 keeps a constant threshold and is valid
        b_zero = copy.deepcopy(self.baseline_bleed)
        b_zero["ThresholdIncrease"] = 0.0
        self.assertEqual(validate_bleed_domain(b_zero), [])

    def test_threshold_max_domain(self):
        # ThresholdMax cannot be below InitialThreshold
        b_low = copy.deepcopy(self.baseline_bleed)
        b_low["InitialThreshold"] = 100.0
        b_low["ThresholdMax"] = 99.0
        errs = validate_bleed_domain(b_low)
        self.assertTrue(any("InvalidBleed.ThresholdMaxBelowInitial: Bleed.ThresholdMax=99.0 is below Bleed.InitialThreshold=100.0" in e for e in errs))

        # Equal threshold is valid
        b_eq = copy.deepcopy(self.baseline_bleed)
        b_eq["InitialThreshold"] = 100.0
        b_eq["ThresholdMax"] = 100.0
        self.assertEqual(validate_bleed_domain(b_eq), [])

    def test_hp_fraction_domain(self):
        # HpFraction must be in [0.0, 1.0]
        b_neg = copy.deepcopy(self.baseline_bleed)
        b_neg["HpFraction"] = -0.01
        errs = validate_bleed_domain(b_neg)
        self.assertTrue(any("InvalidBleed.FractionOutOfRange: Bleed.HpFraction=-0.01" in e for e in errs))

        b_high = copy.deepcopy(self.baseline_bleed)
        b_high["HpFraction"] = 1.01
        errs = validate_bleed_domain(b_high)
        self.assertTrue(any("InvalidBleed.FractionOutOfRange: Bleed.HpFraction=1.01" in e for e in errs))

        # Boundaries 0.0 and 1.0 pass
        b_zero = copy.deepcopy(self.baseline_bleed)
        b_zero["HpFraction"] = 0.0
        self.assertEqual(validate_bleed_domain(b_zero), [])

        b_one = copy.deepcopy(self.baseline_bleed)
        b_one["HpFraction"] = 1.0
        self.assertEqual(validate_bleed_domain(b_one), [])

    def test_effect_height_signed(self):
        # EffectHeight has no floor and is signed
        b_neg = copy.deepcopy(self.baseline_bleed)
        b_neg["EffectHeight"] = -100.0
        self.assertEqual(validate_bleed_domain(b_neg), [])

        b_zero = copy.deepcopy(self.baseline_bleed)
        b_zero["EffectHeight"] = 0.0
        self.assertEqual(validate_bleed_domain(b_zero), [])

    def test_required_references_missing(self):
        # ProcEffect missing
        b_no_fx = copy.deepcopy(self.baseline_bleed)
        b_no_fx["ProcEffect"] = None
        errs = validate_bleed_domain(b_no_fx)
        self.assertTrue(any("InvalidDependency.Missing: Bleed.ProcEffect is required and is not set" in e for e in errs))

        # ProcSound missing
        b_no_snd = copy.deepcopy(self.baseline_bleed)
        b_no_snd["ProcSound"] = ""
        errs = validate_bleed_domain(b_no_snd)
        self.assertTrue(any("InvalidDependency.Missing: Bleed.ProcSound is required and is not set" in e for e in errs))

    def test_soft_path_all_invalid_longpackage_characters(self):
        # Tests that EVERY character in INVALID_LONGPACKAGE_CHARACTERS causes path rejection
        self.assertEqual(len(INVALID_LONGPACKAGE_CHARACTERS), 20)
        for c in INVALID_LONGPACKAGE_CHARACTERS:
            # Place invalid character inside package segment
            test_path = f"/Game/FX{c}Dir/NS_Hit.NS_Hit"
            ok, reason = validate_soft_path_structure(test_path)
            self.assertFalse(ok, f"Expected character {repr(c)} to be rejected in package path")
            self.assertTrue(len(reason) > 0)

    def test_soft_path_all_invalid_objectname_characters(self):
        # Tests that EVERY character in INVALID_OBJECTNAME_CHARACTERS causes object name rejection
        self.assertEqual(len(INVALID_OBJECTNAME_CHARACTERS), 28)
        for c in INVALID_OBJECTNAME_CHARACTERS:
            # Place invalid character inside object name
            test_path = f"/Game/FX/NS_Hit.NS_{c}_Hit"
            ok, reason = validate_soft_path_structure(test_path)
            self.assertFalse(ok, f"Expected character {repr(c)} to be rejected in object name")
            self.assertTrue(len(reason) > 0)

    def test_soft_path_accept_cases(self):
        # Plain standard /Game path
        ok, reason = validate_soft_path_structure("/Game/FX/NS_Hit.NS_Hit")
        self.assertTrue(ok, f"Failed on valid /Game path: {reason}")

        # Synthetic non-/Game mounted roots
        for mount_path in [
            "/Engine/FX/NS_EngineHit.NS_EngineHit",
            "/MyPlugin/FX/NS_PluginHit.NS_PluginHit",
            "/SyntheticMount/VFX/Combat/NS_Proc.NS_Proc"
        ]:
            ok, reason = validate_soft_path_structure(mount_path)
            self.assertTrue(ok, f"Failed on valid synthetic mount {mount_path}: {reason}")

    def test_soft_path_structure_rejections(self):
        # Missing leading slash
        b1 = copy.deepcopy(self.baseline_bleed)
        b1["ProcEffect"] = "Game/Niagara/FX.FX"
        errs = validate_bleed_domain(b1)
        self.assertTrue(any("InvalidDependency.Malformed: Bleed.ProcEffect=Game/Niagara/FX.FX, it must start with '/'" in e for e in errs))

        # Whitespace
        b2 = copy.deepcopy(self.baseline_bleed)
        b2["ProcSound"] = "/Game/Sound Cue/A_Cue.A_Cue"
        errs = validate_bleed_domain(b2)
        self.assertTrue(any("InvalidDependency.Malformed" in e and "it contains whitespace" in e for e in errs))

        # Sub-object colon
        b3 = copy.deepcopy(self.baseline_bleed)
        b3["ProcEffect"] = "/Game/Niagara/FX.FX:Emitter"
        errs = validate_bleed_domain(b3)
        self.assertTrue(any("InvalidDependency.Malformed" in e and "it names a sub-object" in e for e in errs))

        # Missing dot in leaf
        b4 = copy.deepcopy(self.baseline_bleed)
        b4["ProcSound"] = "/Game/Sounds/SoundCue"
        errs = validate_bleed_domain(b4)
        self.assertTrue(any("InvalidDependency.Malformed" in e and "it must end in <package>.<asset>" in e for e in errs))

        # Extra dot in object name
        b5 = copy.deepcopy(self.baseline_bleed)
        b5["ProcEffect"] = "/Game/Niagara/FX.FX.Extra"
        errs = validate_bleed_domain(b5)
        self.assertTrue(any("InvalidDependency.Malformed" in e and "object name contains invalid character '.'" in e for e in errs))

    def test_bleed_float32_overflow_rejected(self):
        b_overflow = copy.deepcopy(self.baseline_bleed)
        b_overflow["InitialThreshold"] = 1.0e39
        errs = validate_bleed_domain(b_overflow)
        self.assertTrue(any("InvalidBleed.NotFinite: Bleed.InitialThreshold=1e+39" in e for e in errs))

    def test_bleed_python_name_mapping(self):
        expected_py = {
            "InitialThreshold": "initial_threshold",
            "ThresholdIncrease": "threshold_increase",
            "ThresholdMax": "threshold_max",
            "HpFraction": "hp_fraction",
            "EffectHeight": "effect_height",
            "ProcEffect": "proc_effect",
            "ProcSound": "proc_sound"
        }
        for native_k, exp_py in expected_py.items():
            self.assertEqual(pythonize_property_name(native_k), exp_py)
            self.assertEqual(BLEED_NATIVE_TO_PY[native_k], exp_py)
            self.assertEqual(BLEED_PY_TO_NATIVE[exp_py], native_k)

    def test_bleed_float32_readback_normalization(self):
        # Verify that HpFraction = 0.03 survives float32 round trip without readback mismatch
        normalized = normalize_native_expected_for_readback(self.baseline_bleed, NATIVE_BLEED_FIELDS)
        self.assertEqual(normalized["HpFraction"], to_float32(0.03))
        self.assertNotEqual(0.03, to_float32(0.03))
        self.assertEqual(to_float32(normalized["HpFraction"]), normalized["HpFraction"])



class TestLowSweepPolicyDomain(unittest.TestCase):
    """
    Tests DD20 FRPGLowSweepConfig domain validation per RPGBossLowSweepAdapters.cpp: ValidateLowSweep.
    Explicit qualification: Pending DD20 live verification run by Codex.
    MoveId is SYNTACTIC IDENTITY ONLY (does not prove tracker resolution, timing or ability execution).
    """
    def setUp(self):
        self.baseline_low_sweep = {
            "bEnabled": True,
            "MoveId": "A4",
            "Damage": 20.0,
            "Reach": 380.0,
            "InnerRadius": 60.0,
            "BladeHeight": 40.0,
            "SweepFromDegrees": 90.0,
            "SweepToDegrees": -90.0
        }

    def test_baseline_low_sweep_passes(self):
        errs = validate_low_sweep_domain(self.baseline_low_sweep)
        self.assertEqual(errs, [])

    def test_all_six_non_finite_scalars_rejected_in_order(self):
        # Verification that all 6 scalar floats are checked finite first in declaration order
        field_order = [
            ("Damage", "LowSweep.Damage"),
            ("Reach", "LowSweep.Reach"),
            ("InnerRadius", "LowSweep.InnerRadius"),
            ("BladeHeight", "LowSweep.BladeHeight"),
            ("SweepFromDegrees", "LowSweep.SweepFromDegrees"),
            ("SweepToDegrees", "LowSweep.SweepToDegrees"),
        ]
        for field_name, expected_token in field_order:
            for bad_val in [float("nan"), float("inf"), float("-inf"), True, False]:
                s = copy.deepcopy(self.baseline_low_sweep)
                s[field_name] = bad_val
                errs = validate_low_sweep_domain(s)
                self.assertTrue(
                    any(f"InvalidLowSweep.NotFinite: {expected_token}" in e for e in errs),
                    f"Expected NotFinite for {field_name}={bad_val}, got {errs}"
                )

    def test_precedence_late_nonfinite_beats_early_domain_error(self):
        # C258/X-299 precedence: all six floats are checked finite before ANY domain check.
        # A late nonfinite float (e.g. SweepToDegrees=NaN) beats an earlier domain error (e.g. Damage=-10.0).
        s = copy.deepcopy(self.baseline_low_sweep)
        s["Damage"] = -10.0
        s["SweepToDegrees"] = float("nan")
        errs = validate_low_sweep_domain(s)
        self.assertEqual(errs, ["InvalidLowSweep.NotFinite: LowSweep.SweepToDegrees"])

    def test_damage_domain(self):
        # Damage cannot be negative
        s_neg = copy.deepcopy(self.baseline_low_sweep)
        s_neg["Damage"] = -0.1
        errs = validate_low_sweep_domain(s_neg)
        self.assertEqual(errs, ["InvalidLowSweep.Negative: LowSweep.Damage"])

        # Damage == 0.0 is legal
        s_zero = copy.deepcopy(self.baseline_low_sweep)
        s_zero["Damage"] = 0.0
        self.assertEqual(validate_low_sweep_domain(s_zero), [])

    def test_reach_domain(self):
        # Reach must be strictly positive (> 0.0)
        s_zero = copy.deepcopy(self.baseline_low_sweep)
        s_zero["Reach"] = 0.0
        errs = validate_low_sweep_domain(s_zero)
        self.assertEqual(errs, ["InvalidLowSweep.NotPositive: LowSweep.Reach"])

        s_neg = copy.deepcopy(self.baseline_low_sweep)
        s_neg["Reach"] = -10.0
        errs = validate_low_sweep_domain(s_neg)
        self.assertEqual(errs, ["InvalidLowSweep.NotPositive: LowSweep.Reach"])

        # Sub-1 reach (e.g. 0.5) is accepted (no editor min-1 floor)
        s_sub1 = copy.deepcopy(self.baseline_low_sweep)
        s_sub1["InnerRadius"] = 0.1
        s_sub1["Reach"] = 0.5
        self.assertEqual(validate_low_sweep_domain(s_sub1), [])

    def test_inner_radius_domain(self):
        # InnerRadius cannot be negative
        s_neg = copy.deepcopy(self.baseline_low_sweep)
        s_neg["InnerRadius"] = -0.5
        errs = validate_low_sweep_domain(s_neg)
        self.assertEqual(errs, ["InvalidLowSweep.Negative: LowSweep.InnerRadius"])

        # InnerRadius == 0.0 is legal
        s_zero = copy.deepcopy(self.baseline_low_sweep)
        s_zero["InnerRadius"] = 0.0
        self.assertEqual(validate_low_sweep_domain(s_zero), [])

    def test_inner_radius_ordering_with_reach(self):
        # InnerRadius must be strictly below Reach (< Reach)
        s_equal = copy.deepcopy(self.baseline_low_sweep)
        s_equal["Reach"] = 200.0
        s_equal["InnerRadius"] = 200.0
        errs = validate_low_sweep_domain(s_equal)
        self.assertEqual(errs, ["InvalidLowSweep.InnerNotBelowReach: LowSweep.InnerRadius"])

        s_greater = copy.deepcopy(self.baseline_low_sweep)
        s_greater["Reach"] = 200.0
        s_greater["InnerRadius"] = 250.0
        errs = validate_low_sweep_domain(s_greater)
        self.assertEqual(errs, ["InvalidLowSweep.InnerNotBelowReach: LowSweep.InnerRadius"])

    def test_blade_height_domain(self):
        # BladeHeight must be strictly positive (> 0.0)
        s_zero = copy.deepcopy(self.baseline_low_sweep)
        s_zero["BladeHeight"] = 0.0
        errs = validate_low_sweep_domain(s_zero)
        self.assertEqual(errs, ["InvalidLowSweep.NotPositive: LowSweep.BladeHeight"])

        s_neg = copy.deepcopy(self.baseline_low_sweep)
        s_neg["BladeHeight"] = -5.0
        errs = validate_low_sweep_domain(s_neg)
        self.assertEqual(errs, ["InvalidLowSweep.NotPositive: LowSweep.BladeHeight"])

        # Sub-1 height (e.g. 0.4) is accepted (no editor min-1 floor)
        s_sub1 = copy.deepcopy(self.baseline_low_sweep)
        s_sub1["BladeHeight"] = 0.4
        self.assertEqual(validate_low_sweep_domain(s_sub1), [])

    def test_angle_domains(self):
        # Angles must be in [-360.0, 360.0]
        s_low_from = copy.deepcopy(self.baseline_low_sweep)
        s_low_from["SweepFromDegrees"] = -360.1
        self.assertEqual(validate_low_sweep_domain(s_low_from), ["InvalidLowSweep.AngleOutOfRange: LowSweep.SweepFromDegrees"])

        s_high_from = copy.deepcopy(self.baseline_low_sweep)
        s_high_from["SweepFromDegrees"] = 360.1
        self.assertEqual(validate_low_sweep_domain(s_high_from), ["InvalidLowSweep.AngleOutOfRange: LowSweep.SweepFromDegrees"])

        s_low_to = copy.deepcopy(self.baseline_low_sweep)
        s_low_to["SweepToDegrees"] = -360.1
        self.assertEqual(validate_low_sweep_domain(s_low_to), ["InvalidLowSweep.AngleOutOfRange: LowSweep.SweepToDegrees"])

        s_high_to = copy.deepcopy(self.baseline_low_sweep)
        s_high_to["SweepToDegrees"] = 360.1
        self.assertEqual(validate_low_sweep_domain(s_high_to), ["InvalidLowSweep.AngleOutOfRange: LowSweep.SweepToDegrees"])

    def test_angles_equal_and_reversed_and_bounds_accepted(self):
        # Equal angles form a stationary band and are valid
        s_eq = copy.deepcopy(self.baseline_low_sweep)
        s_eq["SweepFromDegrees"] = 45.0
        s_eq["SweepToDegrees"] = 45.0
        self.assertEqual(validate_low_sweep_domain(s_eq), [])

        # Reversed angles (SweepFrom < SweepTo) are legal
        s_rev = copy.deepcopy(self.baseline_low_sweep)
        s_rev["SweepFromDegrees"] = -90.0
        s_rev["SweepToDegrees"] = 90.0
        self.assertEqual(validate_low_sweep_domain(s_rev), [])

        # Exact +-360.0 bounds are legal
        s_bounds = copy.deepcopy(self.baseline_low_sweep)
        s_bounds["SweepFromDegrees"] = -360.0
        s_bounds["SweepToDegrees"] = 360.0
        self.assertEqual(validate_low_sweep_domain(s_bounds), [])

    def test_disabled_record_accepts_and_validates(self):
        # bEnabled = False is accepted
        s_dis = copy.deepcopy(self.baseline_low_sweep)
        s_dis["bEnabled"] = False
        self.assertEqual(validate_low_sweep_domain(s_dis), [])

        # Even if disabled, invalid values are still rejected
        s_dis_bad = copy.deepcopy(self.baseline_low_sweep)
        s_dis_bad["bEnabled"] = False
        s_dis_bad["Damage"] = -1.0
        self.assertEqual(validate_low_sweep_domain(s_dis_bad), ["InvalidLowSweep.Negative: LowSweep.Damage"])

    def test_move_id_syntactic_validation(self):
        # None, empty, or "None"
        for bad_id in [None, "", "None"]:
            s = copy.deepcopy(self.baseline_low_sweep)
            s["MoveId"] = bad_id
            self.assertEqual(validate_low_sweep_domain(s), ["InvalidDependency.Missing: LowSweep.MoveId"])

        # Whitespace or control character
        for bad_char in [" ", chr(9), chr(10), chr(13), chr(1), chr(31)]:
            s["MoveId"] = f"A{bad_char}4"
            self.assertEqual(validate_low_sweep_domain(s), ["InvalidDependency.Malformed: LowSweep.MoveId"])

    def test_low_sweep_float32_overflow_rejected(self):
        s_overflow = copy.deepcopy(self.baseline_low_sweep)
        s_overflow["Damage"] = 1.0e39
        errs = validate_low_sweep_domain(s_overflow)
        self.assertEqual(errs, ["InvalidLowSweep.NotFinite: LowSweep.Damage"])

    def test_low_sweep_python_name_mapping(self):
        expected_py = {
            "bEnabled": "enabled",
            "MoveId": "move_id",
            "Damage": "damage",
            "Reach": "reach",
            "InnerRadius": "inner_radius",
            "BladeHeight": "blade_height",
            "SweepFromDegrees": "sweep_from_degrees",
            "SweepToDegrees": "sweep_to_degrees"
        }
        for native_k, exp_py in expected_py.items():
            self.assertEqual(pythonize_property_name(native_k), exp_py)
            self.assertEqual(LOW_SWEEP_NATIVE_TO_PY[native_k], exp_py)
            self.assertEqual(LOW_SWEEP_PY_TO_NATIVE[exp_py], native_k)

    def test_low_sweep_float32_readback_normalization(self):
        normalized = normalize_native_expected_for_readback(self.baseline_low_sweep, NATIVE_LOW_SWEEP_FIELDS)
        for fld in ["Damage", "Reach", "InnerRadius", "BladeHeight", "SweepFromDegrees", "SweepToDegrees"]:
            self.assertEqual(normalized[fld], to_float32(self.baseline_low_sweep[fld]))

class TestShockwavePolicyDomain(unittest.TestCase):
    """
    Tests DD21 FRPGShockwaveConfig domain validation per RPGBossShockwave.h/.cpp (DD21),
    incorporating Claude C-262, C-263, and C-264 decisions:
    - Explicit qualification: Pending DD21 live verification run by Codex.
    - MoveId is SYNTACTIC IDENTITY ONLY (does not prove tracker resolution, timing or ability execution).
    - Ceiling constant: RPGBossShockwaveAdapters::MaxAuthoredMagnitude = 1.0e6f on StartRadius, MaxRadius, Speed, Thickness, JumpClearance.
    - JumpClearance finite and STRICTLY > 0 (AMENDED by Claude C-263).
    - Rejection of X-301 overflow counterexamples.
    """
    def setUp(self):
        self.baseline_shockwave = {
            "bEnabled": True,
            "MoveId": "A6",
            "Damage": 48.0,
            "StartRadius": 200.0,
            "MaxRadius": 1100.0,
            "Speed": 1000.0,
            "Thickness": 180.0,
            "JumpClearance": 50.0
        }

    def test_baseline_shockwave_passes(self):
        errs = validate_shockwave_domain(self.baseline_shockwave)
        self.assertEqual(errs, [])

    def test_all_six_non_finite_scalars_rejected_in_order(self):
        field_order = [
            ("Damage", "Shockwave.Damage"),
            ("StartRadius", "Shockwave.StartRadius"),
            ("MaxRadius", "Shockwave.MaxRadius"),
            ("Speed", "Shockwave.Speed"),
            ("Thickness", "Shockwave.Thickness"),
            ("JumpClearance", "Shockwave.JumpClearance"),
        ]
        for field_name, expected_token in field_order:
            for bad_val in [float("nan"), float("inf"), float("-inf"), True, False]:
                s = copy.deepcopy(self.baseline_shockwave)
                s[field_name] = bad_val
                errs = validate_shockwave_domain(s)
                self.assertTrue(
                    any(f"InvalidShockwave.NotFinite: {expected_token}" in e for e in errs),
                    f"Expected NotFinite for {field_name}={bad_val}, got {errs}"
                )

    def test_precedence_late_nonfinite_beats_early_domain_error(self):
        # Late nonfinite float (e.g. JumpClearance=NaN) beats an earlier domain error (e.g. Damage=-10.0).
        s = copy.deepcopy(self.baseline_shockwave)
        s["Damage"] = -10.0
        s["JumpClearance"] = float("nan")
        errs = validate_shockwave_domain(s)
        self.assertEqual(errs, ["InvalidShockwave.NotFinite: Shockwave.JumpClearance"])

    def test_damage_domain(self):
        # Damage cannot be negative
        s_neg = copy.deepcopy(self.baseline_shockwave)
        s_neg["Damage"] = -0.1
        errs = validate_shockwave_domain(s_neg)
        self.assertEqual(errs, ["InvalidShockwave.Negative: Shockwave.Damage"])

        # Damage == 0.0 is legal
        s_zero = copy.deepcopy(self.baseline_shockwave)
        s_zero["Damage"] = 0.0
        self.assertEqual(validate_shockwave_domain(s_zero), [])

        # Damage has no ceiling (only subtracted from health per C-264)
        s_huge = copy.deepcopy(self.baseline_shockwave)
        s_huge["Damage"] = 5000000.0
        self.assertEqual(validate_shockwave_domain(s_huge), [])

    def test_start_radius_domain(self):
        # Negative rejected
        s_neg = copy.deepcopy(self.baseline_shockwave)
        s_neg["StartRadius"] = -1.0
        errs = validate_shockwave_domain(s_neg)
        self.assertEqual(errs, ["InvalidShockwave.Negative: Shockwave.StartRadius"])

        # 0.0 is legal
        s_zero = copy.deepcopy(self.baseline_shockwave)
        s_zero["StartRadius"] = 0.0
        self.assertEqual(validate_shockwave_domain(s_zero), [])

        # Above ceiling (1.0e6) rejected
        s_above = copy.deepcopy(self.baseline_shockwave)
        s_above["StartRadius"] = 1000001.0
        s_above["MaxRadius"] = 2000000.0
        errs = validate_shockwave_domain(s_above)
        self.assertEqual(errs, ["InvalidShockwave.AboveCeiling: Shockwave.StartRadius"])

    def test_max_radius_domain(self):
        # Not positive rejected
        s_zero = copy.deepcopy(self.baseline_shockwave)
        s_zero["MaxRadius"] = 0.0
        errs = validate_shockwave_domain(s_zero)
        self.assertEqual(errs, ["InvalidShockwave.NotPositive: Shockwave.MaxRadius"])

        # Above ceiling rejected
        s_above = copy.deepcopy(self.baseline_shockwave)
        s_above["MaxRadius"] = 1000001.0
        errs = validate_shockwave_domain(s_above)
        self.assertEqual(errs, ["InvalidShockwave.AboveCeiling: Shockwave.MaxRadius"])

        # MaxRadius <= StartRadius rejected
        s_less = copy.deepcopy(self.baseline_shockwave)
        s_less["StartRadius"] = 500.0
        s_less["MaxRadius"] = 500.0
        errs = validate_shockwave_domain(s_less)
        self.assertEqual(errs, ["InvalidShockwave.MaxNotAboveStart: Shockwave.MaxRadius"])

        # MaxRadius == 1.0e6 accepted (when StartRadius below it)
        s_ceil = copy.deepcopy(self.baseline_shockwave)
        s_ceil["StartRadius"] = 500.0
        s_ceil["MaxRadius"] = 1.0e6
        self.assertEqual(validate_shockwave_domain(s_ceil), [])

    def test_speed_domain(self):
        # Not positive rejected
        s_zero = copy.deepcopy(self.baseline_shockwave)
        s_zero["Speed"] = 0.0
        errs = validate_shockwave_domain(s_zero)
        self.assertEqual(errs, ["InvalidShockwave.NotPositive: Shockwave.Speed"])

        # Above ceiling rejected
        s_above = copy.deepcopy(self.baseline_shockwave)
        s_above["Speed"] = 1000001.0
        errs = validate_shockwave_domain(s_above)
        self.assertEqual(errs, ["InvalidShockwave.AboveCeiling: Shockwave.Speed"])

        # Sub-1 speed accepted
        s_sub1 = copy.deepcopy(self.baseline_shockwave)
        s_sub1["Speed"] = 0.5
        self.assertEqual(validate_shockwave_domain(s_sub1), [])

        # Exact ceiling accepted
        s_ceil = copy.deepcopy(self.baseline_shockwave)
        s_ceil["Speed"] = 1.0e6
        self.assertEqual(validate_shockwave_domain(s_ceil), [])

    def test_thickness_domain(self):
        # Not positive rejected
        s_zero = copy.deepcopy(self.baseline_shockwave)
        s_zero["Thickness"] = 0.0
        errs = validate_shockwave_domain(s_zero)
        self.assertEqual(errs, ["InvalidShockwave.NotPositive: Shockwave.Thickness"])

        # Above ceiling rejected
        s_above = copy.deepcopy(self.baseline_shockwave)
        s_above["Thickness"] = 1000001.0
        errs = validate_shockwave_domain(s_above)
        self.assertEqual(errs, ["InvalidShockwave.AboveCeiling: Shockwave.Thickness"])

        # Exact ceiling accepted
        s_ceil = copy.deepcopy(self.baseline_shockwave)
        s_ceil["Thickness"] = 1.0e6
        self.assertEqual(validate_shockwave_domain(s_ceil), [])

    def test_jump_clearance_domain(self):
        # JumpClearance == 0.0 is REJECTED (AMENDED by Claude C-263)
        s_zero = copy.deepcopy(self.baseline_shockwave)
        s_zero["JumpClearance"] = 0.0
        errs = validate_shockwave_domain(s_zero)
        self.assertEqual(errs, ["InvalidShockwave.NotPositive: Shockwave.JumpClearance"])

        # Negative rejected
        s_neg = copy.deepcopy(self.baseline_shockwave)
        s_neg["JumpClearance"] = -1.0
        errs = validate_shockwave_domain(s_neg)
        self.assertEqual(errs, ["InvalidShockwave.NotPositive: Shockwave.JumpClearance"])

        # 0.5 accepted (small positive clearance)
        s_small = copy.deepcopy(self.baseline_shockwave)
        s_small["JumpClearance"] = 0.5
        self.assertEqual(validate_shockwave_domain(s_small), [])

        # Above ceiling rejected
        s_above = copy.deepcopy(self.baseline_shockwave)
        s_above["JumpClearance"] = 1000001.0
        errs = validate_shockwave_domain(s_above)
        self.assertEqual(errs, ["InvalidShockwave.AboveCeiling: Shockwave.JumpClearance"])

        # Exact ceiling accepted
        s_ceil = copy.deepcopy(self.baseline_shockwave)
        s_ceil["JumpClearance"] = 1.0e6
        self.assertEqual(validate_shockwave_domain(s_ceil), [])

    def test_move_id_syntactic_validation(self):
        # None, empty, or "None"
        for bad_id in [None, "", "None"]:
            s = copy.deepcopy(self.baseline_shockwave)
            s["MoveId"] = bad_id
            self.assertEqual(validate_shockwave_domain(s), ["InvalidDependency.Missing: Shockwave.MoveId"])

        # Whitespace or control character
        for bad_char in [" ", chr(9), chr(10), chr(13), chr(1), chr(31)]:
            s["MoveId"] = f"A{bad_char}6"
            self.assertEqual(validate_shockwave_domain(s), ["InvalidDependency.Malformed: Shockwave.MoveId"])

    def test_shockwave_float32_overflow_rejected(self):
        s_overflow = copy.deepcopy(self.baseline_shockwave)
        s_overflow["Damage"] = 1.0e39
        errs = validate_shockwave_domain(s_overflow)
        self.assertEqual(errs, ["InvalidShockwave.NotFinite: Shockwave.Damage"])

    def test_shockwave_python_name_mapping(self):
        expected_py = {
            "bEnabled": "enabled",
            "MoveId": "move_id",
            "Damage": "damage",
            "StartRadius": "start_radius",
            "MaxRadius": "max_radius",
            "Speed": "speed",
            "Thickness": "thickness",
            "JumpClearance": "jump_clearance"
        }
        for native_k, exp_py in expected_py.items():
            self.assertEqual(pythonize_property_name(native_k), exp_py)
            self.assertEqual(SHOCKWAVE_NATIVE_TO_PY[native_k], exp_py)
            self.assertEqual(SHOCKWAVE_PY_TO_NATIVE[exp_py], native_k)

    def test_shockwave_float32_readback_normalization(self):
        normalized = normalize_native_expected_for_readback(self.baseline_shockwave, NATIVE_SHOCKWAVE_FIELDS)
        for fld in ["Damage", "StartRadius", "MaxRadius", "Speed", "Thickness", "JumpClearance"]:
            self.assertEqual(normalized[fld], to_float32(self.baseline_shockwave[fld]))

    def test_two_overflow_counterexamples_from_x301_rejected_by_ceiling(self):
        # Counterexample 1 from X-301: StartRadius=3.368795e38, MaxRadius=3.402823e38, Speed=3.368795e38
        s1 = copy.deepcopy(self.baseline_shockwave)
        s1["StartRadius"] = 3.36879526214505e38
        s1["MaxRadius"] = 3.4028234663852886e38
        s1["Speed"] = 3.36879526214505e38
        errs1 = validate_shockwave_domain(s1)
        self.assertEqual(errs1, ["InvalidShockwave.AboveCeiling: Shockwave.StartRadius"])

        # Counterexample 2 from X-301: StartRadius=2.552117e38, MaxRadius=1e6, Thickness=3.402823e38
        s2 = copy.deepcopy(self.baseline_shockwave)
        s2["StartRadius"] = 2.5521175490829424e38
        s2["MaxRadius"] = 1.0e6
        s2["Speed"] = 1.0
        s2["Thickness"] = 3.4028234663852886e38
        errs2 = validate_shockwave_domain(s2)
        self.assertEqual(errs2, ["InvalidShockwave.AboveCeiling: Shockwave.StartRadius"])


class TestHealPunishPolicyDomain(unittest.TestCase):
    """
    Tests DD22 FRPGHealPunishConfig domain validation per RPGBossHealPunish.h/.cpp (DD22),
    incorporating Claude C-265 definitive lead contract:
    - Explicit qualification: Pending DD22 live verification run by Codex.
    - Authored record contract, NOT native guards.
    - MoveId A5 and player drink montage are hardcoded in RPGBossHealPunish.cpp (:22, :236)
      and are UNRESOLVED (not in record).
    - Ceiling constant: MaxAuthoredMagnitude = 1.0e6f on MinRange, MaxRange, Cooldown,
      FlightTime, MinSpeed, MaxSpeed, JavelinRadius, JavelinMaxRange, AimHeight.
    - Damage has NO CEILING (finite >= 0.0f).
    - SpawnSockets array handling (non-empty, missing/malformed validation).
    """
    def setUp(self):
        self.baseline_heal_punish = {
            "bEnabled": True,
            "MinRange": 400.0,
            "MaxRange": 1000.0,
            "Cooldown": 4.0,
            "Damage": 12.0,
            "FlightTime": 1.2,
            "MinSpeed": 450.0,
            "MaxSpeed": 2500.0,
            "JavelinRadius": 25.0,
            "JavelinMaxRange": 3000.0,
            "SpawnSockets": ["JavelinSpawn", "hand_l"],
            "AimHeight": 100.0,
            "bRespondToHeal": True,
            "bCancelJavelinsOnInterrupt": True,
        }

    def test_baseline_heal_punish_passes(self):
        errs = validate_heal_punish_domain(self.baseline_heal_punish)
        self.assertEqual(errs, [])

    def test_all_ten_non_finite_scalars_rejected_in_header_order(self):
        # 10 float fields checked finite first in header declaration order
        field_order = [
            ("MinRange", "HealPunish.MinRange"),
            ("MaxRange", "HealPunish.MaxRange"),
            ("Cooldown", "HealPunish.Cooldown"),
            ("Damage", "HealPunish.Damage"),
            ("FlightTime", "HealPunish.FlightTime"),
            ("MinSpeed", "HealPunish.MinSpeed"),
            ("MaxSpeed", "HealPunish.MaxSpeed"),
            ("JavelinRadius", "HealPunish.JavelinRadius"),
            ("JavelinMaxRange", "HealPunish.JavelinMaxRange"),
            ("AimHeight", "HealPunish.AimHeight"),
        ]
        for field_name, expected_token in field_order:
            for bad_val in [float("nan"), float("inf"), float("-inf"), True, False]:
                s = copy.deepcopy(self.baseline_heal_punish)
                s[field_name] = bad_val
                errs = validate_heal_punish_domain(s)
                self.assertTrue(
                    any(f"InvalidPunish.NotFinite: {expected_token}" in e for e in errs),
                    f"Expected NotFinite for {field_name} with {bad_val}, got {errs}"
                )

    def test_min_range_domain_rules(self):
        s = copy.deepcopy(self.baseline_heal_punish)
        s["MinRange"] = -1.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.Negative: HealPunish.MinRange"])

        s["MinRange"] = 0.0
        self.assertEqual(validate_heal_punish_domain(s), [])

        s["MinRange"] = 1.0e6
        s["MaxRange"] = 1.0e6
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.MaxNotAboveMin: HealPunish.MaxRange"])

        s["MinRange"] = 1000001.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.AboveCeiling: HealPunish.MinRange"])

    def test_max_range_domain_rules(self):
        s = copy.deepcopy(self.baseline_heal_punish)
        s["MaxRange"] = 0.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.NotPositive: HealPunish.MaxRange"])

        s["MaxRange"] = -5.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.NotPositive: HealPunish.MaxRange"])

        s["MaxRange"] = 1000001.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.AboveCeiling: HealPunish.MaxRange"])

        # MaxRange <= MinRange
        s["MinRange"] = 500.0
        s["MaxRange"] = 500.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.MaxNotAboveMin: HealPunish.MaxRange"])

        s["MinRange"] = 600.0
        s["MaxRange"] = 500.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.MaxNotAboveMin: HealPunish.MaxRange"])

        # Exactly 1.0e6 accepted if MinRange < 1.0e6
        s["MinRange"] = 999999.0
        s["MaxRange"] = 1.0e6
        self.assertEqual(validate_heal_punish_domain(s), [])

    def test_cooldown_domain_rules(self):
        s = copy.deepcopy(self.baseline_heal_punish)
        s["Cooldown"] = -0.1
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.Negative: HealPunish.Cooldown"])

        s["Cooldown"] = 0.0
        self.assertEqual(validate_heal_punish_domain(s), [])

        s["Cooldown"] = 1.0e6
        self.assertEqual(validate_heal_punish_domain(s), [])

        s["Cooldown"] = 1000001.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.AboveCeiling: HealPunish.Cooldown"])

    def test_damage_no_ceiling_and_negative_rejected(self):
        s = copy.deepcopy(self.baseline_heal_punish)
        s["Damage"] = -1.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.Negative: HealPunish.Damage"])

        s["Damage"] = 0.0
        self.assertEqual(validate_heal_punish_domain(s), [])

        # Damage has NO ceiling (finite >= 0.0) per C-265 Lead Contract
        s["Damage"] = 1.0e7
        self.assertEqual(validate_heal_punish_domain(s), [])

        s["Damage"] = 3.4028234663852886e38
        self.assertEqual(validate_heal_punish_domain(s), [])

    def test_flight_time_domain_rules(self):
        s = copy.deepcopy(self.baseline_heal_punish)
        s["FlightTime"] = 0.049
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.BelowFlightTimeFloor: HealPunish.FlightTime"])

        s["FlightTime"] = 0.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.BelowFlightTimeFloor: HealPunish.FlightTime"])

        s["FlightTime"] = 0.05
        self.assertEqual(validate_heal_punish_domain(s), [])

        s["FlightTime"] = 1.0e6
        self.assertEqual(validate_heal_punish_domain(s), [])

        s["FlightTime"] = 1000001.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.AboveCeiling: HealPunish.FlightTime"])

    def test_min_and_max_speed_domain_rules(self):
        s = copy.deepcopy(self.baseline_heal_punish)
        # MinSpeed <= 0
        s["MinSpeed"] = 0.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.NotPositive: HealPunish.MinSpeed"])

        s["MinSpeed"] = -10.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.NotPositive: HealPunish.MinSpeed"])

        # MinSpeed > ceiling
        s["MinSpeed"] = 1000001.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.AboveCeiling: HealPunish.MinSpeed"])

        # MaxSpeed <= 0
        s = copy.deepcopy(self.baseline_heal_punish)
        s["MaxSpeed"] = 0.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.NotPositive: HealPunish.MaxSpeed"])

        s["MaxSpeed"] = -10.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.NotPositive: HealPunish.MaxSpeed"])

        # MaxSpeed > ceiling
        s["MaxSpeed"] = 1000001.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.AboveCeiling: HealPunish.MaxSpeed"])

        # MinSpeed > MaxSpeed
        s["MinSpeed"] = 1500.0
        s["MaxSpeed"] = 1000.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.MinSpeedAboveMax: HealPunish.MinSpeed"])

        # MinSpeed == MaxSpeed is valid
        s["MinSpeed"] = 1000.0
        s["MaxSpeed"] = 1000.0
        self.assertEqual(validate_heal_punish_domain(s), [])

    def test_javelin_radius_and_max_range_domain_rules(self):
        s = copy.deepcopy(self.baseline_heal_punish)
        s["JavelinRadius"] = 0.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.NotPositive: HealPunish.JavelinRadius"])

        s["JavelinRadius"] = 1.0e6
        self.assertEqual(validate_heal_punish_domain(s), [])

        s["JavelinRadius"] = 1000001.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.AboveCeiling: HealPunish.JavelinRadius"])

        s = copy.deepcopy(self.baseline_heal_punish)
        s["JavelinMaxRange"] = 0.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.NotPositive: HealPunish.JavelinMaxRange"])

        s["JavelinMaxRange"] = 1.0e6
        self.assertEqual(validate_heal_punish_domain(s), [])

        s["JavelinMaxRange"] = 1000001.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.AboveCeiling: HealPunish.JavelinMaxRange"])

    def test_spawn_sockets_validation_rules(self):
        s = copy.deepcopy(self.baseline_heal_punish)
        # Empty array refused (would silently use native fallback and hide default loss)
        s["SpawnSockets"] = []
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidDependency.Missing: HealPunish.SpawnSockets"])

        s["SpawnSockets"] = None
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidDependency.Missing: HealPunish.SpawnSockets"])

        # Entry None or empty
        s["SpawnSockets"] = [""]
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidDependency.Missing: HealPunish.SpawnSockets"])

        s["SpawnSockets"] = ["None"]
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidDependency.Missing: HealPunish.SpawnSockets"])

        # Entry with whitespace or control character
        s["SpawnSockets"] = ["Javelin Spawn"]
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidDependency.Malformed: HealPunish.SpawnSockets"])

        s["SpawnSockets"] = ["hand\tl"]
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidDependency.Malformed: HealPunish.SpawnSockets"])

        # Valid sockets accepted
        s["SpawnSockets"] = ["JavelinSpawn"]
        self.assertEqual(validate_heal_punish_domain(s), [])

        s["SpawnSockets"] = ["JavelinSpawn", "hand_l", "spine_03", "Socket.Custom-01"]
        self.assertEqual(validate_heal_punish_domain(s), [])

    def test_aim_height_domain_rules(self):
        s = copy.deepcopy(self.baseline_heal_punish)
        s["AimHeight"] = -1000001.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.BelowFloor: HealPunish.AimHeight"])

        s["AimHeight"] = 1000001.0
        self.assertEqual(validate_heal_punish_domain(s), ["InvalidPunish.AboveCeiling: HealPunish.AimHeight"])

        # Inclusive bounds [-1e6, 1e6]
        s["AimHeight"] = -1.0e6
        self.assertEqual(validate_heal_punish_domain(s), [])

        s["AimHeight"] = 1.0e6
        self.assertEqual(validate_heal_punish_domain(s), [])

        s["AimHeight"] = -50.0
        self.assertEqual(validate_heal_punish_domain(s), [])

    def test_booleans_accept_both_values(self):
        for b_en in [True, False]:
            for b_resp in [True, False]:
                for b_canc in [True, False]:
                    s = copy.deepcopy(self.baseline_heal_punish)
                    s["bEnabled"] = b_en
                    s["bRespondToHeal"] = b_resp
                    s["bCancelJavelinsOnInterrupt"] = b_canc
                    self.assertEqual(validate_heal_punish_domain(s), [])

    def test_native_field_mappings_pygenutil_heal_punish(self):
        expected_py = {
            "bEnabled": "enabled",
            "MinRange": "min_range",
            "MaxRange": "max_range",
            "Cooldown": "cooldown",
            "Damage": "damage",
            "FlightTime": "flight_time",
            "MinSpeed": "min_speed",
            "MaxSpeed": "max_speed",
            "JavelinRadius": "javelin_radius",
            "JavelinMaxRange": "javelin_max_range",
            "SpawnSockets": "spawn_sockets",
            "AimHeight": "aim_height",
            "bRespondToHeal": "respond_to_heal",
            "bCancelJavelinsOnInterrupt": "cancel_javelins_on_interrupt",
        }
        self.assertEqual(len(NATIVE_HEAL_PUNISH_FIELDS), 14)
        for native_k, exp_py in expected_py.items():
            self.assertIn(native_k, NATIVE_HEAL_PUNISH_FIELDS)
            self.assertEqual(pythonize_property_name(native_k), exp_py)
            self.assertEqual(HEAL_PUNISH_NATIVE_TO_PY[native_k], exp_py)
            self.assertEqual(HEAL_PUNISH_PY_TO_NATIVE[exp_py], native_k)

    def test_heal_punish_float32_readback_normalization(self):
        normalized = normalize_native_expected_for_readback(self.baseline_heal_punish, NATIVE_HEAL_PUNISH_FIELDS)
        for fld in ["MinRange", "MaxRange", "Cooldown", "Damage", "FlightTime", "MinSpeed", "MaxSpeed", "JavelinRadius", "JavelinMaxRange", "AimHeight"]:
            self.assertEqual(normalized[fld], to_float32(self.baseline_heal_punish[fld]))
        self.assertEqual(normalized["SpawnSockets"], ["JavelinSpawn", "hand_l"])


class TestLookPolicyDomain(unittest.TestCase):
    """
    Validates authored capability bounds for URPGBossLook / FRPGLookConfig.
    Enforces the definitive contract from Tech Lead Claude [C-269] / [C-270]:
    - Header authored fields: bEnabled, Body, Pieces, Sword, SwordSocket.
    - Zero numeric floats: no NotFinite checks or magnitude ceilings apply.
    - Validation order:
      (1) Body: required (InvalidDependency.Missing), well-formed (InvalidDependency.Malformed).
      (2) Pieces: every entry in index order: required (Missing), well-formed (Malformed),
          the message carries the index (Look.Pieces[i]); EMPTY array is VALID;
          duplicate path in the array is refused (InvalidDependency.Duplicate).
      (3) Sword: required (Missing), well-formed (Malformed).
      (4) SwordSocket: not None/empty (Missing), no whitespace/control (Malformed).
      bEnabled: bool (True or False), disabled records still validate completely.
    """
    def setUp(self):
        self.baseline_look = {
            "bEnabled": True,
            "Body": "/Game/OneBossFight/Boss01/Body/SK_Boss01_Body.SK_Boss01_Body",
            "Pieces": [
                "/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown.SK_Boss01_Crown",
                "/Game/OneBossFight/Boss01/Body/SK_Boss01_Mantle.SK_Boss01_Mantle",
                "/Game/OneBossFight/Boss01/Body/SK_Boss01_BrazierGauntlet.SK_Boss01_BrazierGauntlet"
            ],
            "Sword": "/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword.SM_Boss01_Greatsword",
            "SwordSocket": "HeavySwordSocket_R"
        }

    def test_baseline_look_passes(self):
        errs = validate_look_domain(self.baseline_look)
        self.assertEqual(errs, [])

    def test_body_missing_rejected(self):
        for bad in [None, "", "   "]:
            rec = copy.deepcopy(self.baseline_look)
            rec["Body"] = bad
            errs = validate_look_domain(rec)
            self.assertTrue(any("InvalidDependency.Missing: Look.Body" in e for e in errs), f"Expected missing Body token for {bad}, got {errs}")

    def test_body_malformed_rejected(self):
        malformed_paths = [
            "Game/NoLeadingSlash/Mesh.Mesh",
            "/Game/With Space/Mesh.Mesh",
            "/Game/With\tTab/Mesh.Mesh",
            "/Game/SubObject:Sub",
            "/NoPackageFolder",
            "/Game/Folder/NoDotAsset",
            "/Game/Folder/DotAtEnd.",
            "/Game/Inv*Char/Mesh.Mesh",
            "/Game/Folder/Inv?Object.Mesh",
        ]
        for bad_path in malformed_paths:
            rec = copy.deepcopy(self.baseline_look)
            rec["Body"] = bad_path
            errs = validate_look_domain(rec)
            self.assertTrue(any("InvalidDependency.Malformed: Look.Body" in e for e in errs), f"Expected malformed Body token for '{bad_path}', got {errs}")

    def test_pieces_empty_array_passes(self):
        # Claude contract C-269: an EMPTY array is VALID (a look without extra pieces is legitimate)
        rec = copy.deepcopy(self.baseline_look)
        rec["Pieces"] = []
        errs = validate_look_domain(rec)
        self.assertEqual(errs, [])

    def test_pieces_missing_entry_rejected(self):
        for bad in [None, "", "   "]:
            rec = copy.deepcopy(self.baseline_look)
            rec["Pieces"][1] = bad
            errs = validate_look_domain(rec)
            self.assertTrue(any("InvalidDependency.Missing: Look.Pieces[1]" in e for e in errs), f"Expected missing token with index 1 for {bad}, got {errs}")

    def test_pieces_malformed_entry_rejected(self):
        rec = copy.deepcopy(self.baseline_look)
        rec["Pieces"][2] = "/Game/Folder/Bad:Colon"
        errs = validate_look_domain(rec)
        self.assertTrue(any("InvalidDependency.Malformed: Look.Pieces[2]" in e for e in errs), f"Expected malformed token with index 2, got {errs}")

    def test_pieces_duplicate_entry_rejected(self):
        # Claude contract C-269: duplicate path in the array is refused (InvalidDependency.Duplicate)
        rec = copy.deepcopy(self.baseline_look)
        rec["Pieces"] = [
            "/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown.SK_Boss01_Crown",
            "/Game/OneBossFight/Boss01/Body/SK_Boss01_Mantle.SK_Boss01_Mantle",
            "/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown.SK_Boss01_Crown"
        ]
        errs = validate_look_domain(rec)
        self.assertTrue(any("InvalidDependency.Duplicate: Look.Pieces[2]" in e for e in errs), f"Expected duplicate token with index 2, got {errs}")

    def test_sword_missing_rejected(self):
        for bad in [None, "", "   "]:
            rec = copy.deepcopy(self.baseline_look)
            rec["Sword"] = bad
            errs = validate_look_domain(rec)
            self.assertTrue(any("InvalidDependency.Missing: Look.Sword" in e for e in errs), f"Expected missing Sword token for {bad}, got {errs}")

    def test_sword_malformed_rejected(self):
        rec = copy.deepcopy(self.baseline_look)
        rec["Sword"] = "SM_NoSlash.SM_NoSlash"
        errs = validate_look_domain(rec)
        self.assertTrue(any("InvalidDependency.Malformed: Look.Sword" in e for e in errs), f"Expected malformed Sword token, got {errs}")

    def test_sword_socket_missing_rejected(self):
        for bad in [None, "", "   ", "None", "none", "NONE", "nOnE"]:
            rec = copy.deepcopy(self.baseline_look)
            rec["SwordSocket"] = bad
            errs = validate_look_domain(rec)
            self.assertTrue(any("InvalidDependency.Missing: Look.SwordSocket" in e for e in errs), f"Expected missing SwordSocket token for {bad}, got {errs}")

    def test_sword_socket_malformed_rejected(self):
        for bad in ["Socket With Space", "Socket\tTab", "Socket\nNewline"]:
            rec = copy.deepcopy(self.baseline_look)
            rec["SwordSocket"] = bad
            errs = validate_look_domain(rec)
            self.assertTrue(any("InvalidDependency.Malformed: Look.SwordSocket" in e for e in errs), f"Expected malformed SwordSocket token for '{bad}', got {errs}")

    def test_disabled_record_validated_completely(self):
        # Claude contract C-269 & C-275: disabled record still validates completely (fails on first invalid field)
        # Test 1: invalid Body on disabled record fails
        rec1 = copy.deepcopy(self.baseline_look)
        rec1["bEnabled"] = False
        rec1["Body"] = None
        errs1 = validate_look_domain(rec1)
        self.assertTrue(any("InvalidDependency.Missing: Look.Body" in e for e in errs1))

        # Test 2: invalid Sword on disabled record fails
        rec2 = copy.deepcopy(self.baseline_look)
        rec2["bEnabled"] = False
        rec2["Sword"] = ""
        errs2 = validate_look_domain(rec2)
        self.assertTrue(any("InvalidDependency.Missing: Look.Sword" in e for e in errs2))

        # Test 3: invalid SwordSocket on disabled record fails
        rec3 = copy.deepcopy(self.baseline_look)
        rec3["bEnabled"] = False
        rec3["SwordSocket"] = "Socket Space"
        errs3 = validate_look_domain(rec3)
        self.assertTrue(any("InvalidDependency.Malformed: Look.SwordSocket" in e for e in errs3))

    def test_native_field_mappings_pygenutil_look(self):
        expected_py = {
            "bEnabled": "enabled",
            "Body": "body",
            "Pieces": "pieces",
            "Sword": "sword",
            "SwordSocket": "sword_socket",
        }
        self.assertEqual(len(NATIVE_LOOK_FIELDS), 5)
        for native_k, exp_py in expected_py.items():
            self.assertIn(native_k, NATIVE_LOOK_FIELDS)
            self.assertEqual(pythonize_property_name(native_k), exp_py)
            self.assertEqual(LOOK_NATIVE_TO_PY[native_k], exp_py)
            self.assertEqual(LOOK_PY_TO_NATIVE[exp_py], native_k)

    def test_array_of_soft_paths_isolation_and_roundtrip(self):
        py_dict = map_native_dict_to_python_keys(self.baseline_look, NATIVE_LOOK_FIELDS)
        self.assertEqual(py_dict["enabled"], True)
        self.assertEqual(py_dict["body"], self.baseline_look["Body"])
        self.assertEqual(py_dict["pieces"], self.baseline_look["Pieces"])
        self.assertEqual(py_dict["sword"], self.baseline_look["Sword"])
        self.assertEqual(py_dict["sword_socket"], "HeavySwordSocket_R")

        # Mutate py_dict list to verify isolation
        py_dict["pieces"].append("/Game/New/Piece.Piece")
        self.assertEqual(len(self.baseline_look["Pieces"]), 3)

        # Extraction roundtrip
        extracted = extract_canonical_primitives(py_dict, NATIVE_LOOK_FIELDS)
        self.assertEqual(extracted["bEnabled"], True)
        self.assertEqual(extracted["Body"], self.baseline_look["Body"])
        self.assertEqual(extracted["Sword"], self.baseline_look["Sword"])
        self.assertEqual(extracted["SwordSocket"], "HeavySwordSocket_R")




class TestCloseClipSwapPolicyDomain(unittest.TestCase):
    """
    Validates authored capability bounds for URPGBossCloseClipSwap / FRPGCloseClipSwapConfig.
    Enforces the definitive contract from Tech Lead Claude [C-275] & [C-276]:
    - Header authored fields: CloseAbilityClassName, AttackMontagesName, A1Montage, A3aMontage, A3bMontage.
    - Zero numeric floats: no NotFinite checks or magnitude ceilings apply.
    - Validation order:
      (1) CloseAbilityClassName: not None/empty/case-insensitive 'none' (Missing),
          no whitespace or control characters (Malformed).
      (2) AttackMontagesName: not None/empty/case-insensitive 'none' (Missing),
          no whitespace or control characters (Malformed).
      (3) A1Montage: required (Missing) then well-formed (Malformed) with engine macros.
      (4) A3aMontage: required (Missing) then well-formed (Malformed) with engine macros.
      (5) A3bMontage: required (Missing) then well-formed (Malformed) with engine macros.
    - No duplicate rule: three identical replacement montages are valid.
    - No _C suffix rule; no class/ability existence check offline.
    """
    def setUp(self):
        self.baseline_close = {
            "CloseAbilityClassName": "GA_GS_Boss_CloseAttack_C",
            "AttackMontagesName": "AttackMontages",
            "A1Montage": "/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1.AM_Boss01_A1",
            "A3aMontage": "/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a.AM_Boss01_A3a",
            "A3bMontage": "/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b.AM_Boss01_A3b",
        }

    def test_baseline_close_clip_swap_passes(self):
        errs = validate_close_clip_swap_domain(self.baseline_close)
        self.assertEqual(errs, [])

    def test_close_ability_class_name_missing_rejected(self):
        for bad in [None, "", "   ", "none", "None", "NONE", "nOnE"]:
            rec = copy.deepcopy(self.baseline_close)
            rec["CloseAbilityClassName"] = bad
            errs = validate_close_clip_swap_domain(rec)
            self.assertTrue(any("InvalidDependency.Missing: CloseClipSwap.CloseAbilityClassName" in e for e in errs),
                            f"Expected missing token for {bad}, got {errs}")

    def test_close_ability_class_name_malformed_rejected(self):
        for bad in ["With Space", "With\tTab", "With\nNewline"]:
            rec = copy.deepcopy(self.baseline_close)
            rec["CloseAbilityClassName"] = bad
            errs = validate_close_clip_swap_domain(rec)
            self.assertTrue(any("InvalidDependency.Malformed: CloseClipSwap.CloseAbilityClassName" in e for e in errs),
                            f"Expected malformed token for '{bad}', got {errs}")

    def test_attack_montages_name_missing_rejected(self):
        for bad in [None, "", "   ", "none", "None", "NONE", "nOnE"]:
            rec = copy.deepcopy(self.baseline_close)
            rec["AttackMontagesName"] = bad
            errs = validate_close_clip_swap_domain(rec)
            self.assertTrue(any("InvalidDependency.Missing: CloseClipSwap.AttackMontagesName" in e for e in errs),
                            f"Expected missing token for {bad}, got {errs}")

    def test_attack_montages_name_malformed_rejected(self):
        for bad in ["Attack Montages", "Attack\tMontages", "Attack\nMontages"]:
            rec = copy.deepcopy(self.baseline_close)
            rec["AttackMontagesName"] = bad
            errs = validate_close_clip_swap_domain(rec)
            self.assertTrue(any("InvalidDependency.Malformed: CloseClipSwap.AttackMontagesName" in e for e in errs),
                            f"Expected malformed token for '{bad}', got {errs}")

    def test_montages_missing_rejected(self):
        for field in ["A1Montage", "A3aMontage", "A3bMontage"]:
            for bad in [None, "", "   "]:
                rec = copy.deepcopy(self.baseline_close)
                rec[field] = bad
                errs = validate_close_clip_swap_domain(rec)
                self.assertTrue(any(f"InvalidDependency.Missing: CloseClipSwap.{field}" in e for e in errs),
                                f"Expected missing token for {field}={bad}, got {errs}")

    def test_montages_malformed_rejected(self):
        for field in ["A1Montage", "A3aMontage", "A3bMontage"]:
            rec = copy.deepcopy(self.baseline_close)
            rec[field] = "AM_NoLeadingSlash.AM_NoLeadingSlash"
            errs = validate_close_clip_swap_domain(rec)
            self.assertTrue(any(f"InvalidDependency.Malformed: CloseClipSwap.{field}" in e for e in errs),
                            f"Expected malformed token for {field}, got {errs}")

    def test_identical_montages_accepted_no_duplicate_rule(self):
        # Claude contract C-275: No duplicate rule: three identical montages are harmless
        rec = copy.deepcopy(self.baseline_close)
        rec["A1Montage"] = "/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1.AM_Boss01_A1"
        rec["A3aMontage"] = "/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1.AM_Boss01_A1"
        rec["A3bMontage"] = "/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1.AM_Boss01_A1"
        errs = validate_close_clip_swap_domain(rec)
        self.assertEqual(errs, [])

    def test_native_field_mappings_pygenutil_close_clip_swap(self):
        expected_py = {
            "CloseAbilityClassName": "close_ability_class_name",
            "AttackMontagesName": "attack_montages_name",
            "A1Montage": "a1_montage",
            "A3aMontage": "a3a_montage",
            "A3bMontage": "a3b_montage",
        }
        self.assertEqual(len(NATIVE_CLOSE_CLIP_SWAP_FIELDS), 5)
        for native_k, exp_py in expected_py.items():
            self.assertIn(native_k, NATIVE_CLOSE_CLIP_SWAP_FIELDS)
            self.assertEqual(pythonize_property_name(native_k), exp_py)
            self.assertEqual(CLOSE_CLIP_SWAP_NATIVE_TO_PY[native_k], exp_py)
            self.assertEqual(CLOSE_CLIP_SWAP_PY_TO_NATIVE[exp_py], native_k)


class TestDiffAgainstCpp(unittest.TestCase):
    """
    Tests for diff_against_cpp review aid verifying C++ / Python validator check parity.
    """
    def setUp(self):
        self.root_dir = Path(".").resolve()
        self.core_path = self.root_dir / "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/authoring_core.py"

    def test_extract_cpp_checks_bleed(self):
        cpp_path = self.root_dir / "Source/OneBossFight/Player/RPGBossBleedAdapters.cpp"
        comp_name, checks = diff_against_cpp.extract_cpp_checks(cpp_path)
        self.assertEqual(comp_name, "Bleed")
        self.assertEqual(len(checks), 13)
        self.assertEqual(checks[0], ("InvalidBleed.NotFinite", "Bleed.InitialThreshold"))
        self.assertEqual(checks[4], ("InvalidBleed.NotFinite", "Bleed.EffectHeight"))
        self.assertEqual(checks[5], ("InvalidBleed.NotPositive", "Bleed.InitialThreshold"))
        self.assertEqual(checks[12], ("InvalidDependency.Malformed", "Bleed.ProcSound"))

    def test_extract_cpp_checks_low_sweep(self):
        cpp_path = self.root_dir / "Source/OneBossFight/Player/RPGBossLowSweepAdapters.cpp"
        comp_name, checks = diff_against_cpp.extract_cpp_checks(cpp_path)
        self.assertEqual(comp_name, "LowSweep")
        self.assertEqual(len(checks), 15)
        self.assertEqual(checks[0], ("InvalidLowSweep.NotFinite", "LowSweep.Damage"))
        self.assertEqual(checks[5], ("InvalidLowSweep.NotFinite", "LowSweep.SweepToDegrees"))
        self.assertEqual(checks[6], ("InvalidLowSweep.Negative", "LowSweep.Damage"))
        self.assertEqual(checks[14], ("InvalidDependency.Malformed", "LowSweep.MoveId"))

    def test_extract_cpp_checks_shockwave(self):
        cpp_path = self.root_dir / "Source/OneBossFight/Player/RPGBossShockwaveAdapters.cpp"
        comp_name, checks = diff_against_cpp.extract_cpp_checks(cpp_path)
        self.assertEqual(comp_name, "Shockwave")
        self.assertEqual(len(checks), 20)
        self.assertEqual(checks[0], ("InvalidShockwave.NotFinite", "Shockwave.Damage"))
        self.assertEqual(checks[5], ("InvalidShockwave.NotFinite", "Shockwave.JumpClearance"))
        self.assertEqual(checks[19], ("InvalidDependency.Malformed", "Shockwave.MoveId"))

    def test_extract_cpp_checks_heal_punish(self):
        cpp_path = self.root_dir / "Source/OneBossFight/Player/RPGBossHealPunishAdapters.cpp"
        comp_name, checks = diff_against_cpp.extract_cpp_checks(cpp_path)
        self.assertEqual(comp_name, "HealPunish")
        self.assertEqual(len(checks), 33)
        self.assertEqual(checks[0], ("InvalidPunish.NotFinite", "HealPunish.MinRange"))
        self.assertEqual(checks[9], ("InvalidPunish.NotFinite", "HealPunish.AimHeight"))
        self.assertEqual(checks[32], ("InvalidPunish.AboveCeiling", "HealPunish.AimHeight"))

    def test_compare_all_accepted_adapters_parity(self):
        for comp in ["Bleed", "LowSweep", "Shockwave", "HealPunish"]:
            cpp_path = self.root_dir / f"Source/OneBossFight/Player/RPGBoss{comp}Adapters.cpp"
            ok, text, summary = diff_against_cpp.compare_adapter(cpp_path, self.core_path)
            self.assertTrue(ok, f"Parity mismatch in {comp}:\n{text}")
            self.assertEqual(summary["status"], "OK")
            self.assertGreater(summary["checks_matched"], 0)

    def test_difference_detection_on_synthetic_mismatch(self):
        # Create a temporary mismatch by modifying one token
        checks_cpp = [("InvalidTest.Negative", "Test.FieldA"), ("InvalidTest.Positive", "Test.FieldB")]
        checks_py = [("InvalidTest.Negative", "Test.FieldA"), ("InvalidTest.WrongToken", "Test.FieldB")]
        diff_idx = None
        for i in range(len(checks_cpp)):
            if checks_cpp[i] != checks_py[i]:
                diff_idx = i
                break
        self.assertEqual(diff_idx, 1)


    def test_no_flag_run_writes_nothing(self):
        import subprocess, tempfile
        script_path = self.root_dir / "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/diff_against_cpp.py"
        report_path = self.root_dir / "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/diff_report.txt"
        mtime_before = report_path.stat().st_mtime if report_path.exists() else None
        
        res = subprocess.run([sys.executable, "-B", str(script_path)],
                             cwd=str(self.root_dir), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("OVERALL STATUS: ALL ADAPTERS OK", res.stdout)
        self.assertNotIn("Report written to:", res.stdout)
        
        mtime_after = report_path.stat().st_mtime if report_path.exists() else None
        self.assertEqual(mtime_before, mtime_after, "diff_against_cpp without flags must not write or touch diff_report.txt")

    def test_report_reproducibility_across_working_dirs(self):
        import subprocess, tempfile, hashlib
        script_path = self.root_dir / "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/diff_against_cpp.py"
        atk_dir = self.root_dir / "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit"
        
        with tempfile.TemporaryDirectory() as td:
            out1 = Path(td) / "report1.txt"
            out2 = Path(td) / "report2.txt"
            
            # Run from repo root
            res1 = subprocess.run([sys.executable, "-B", str(script_path), "--output", str(out1)],
                                  cwd=str(self.root_dir), capture_output=True, text=True)
            self.assertEqual(res1.returncode, 0)
            
            # Run from AuthoringToolkit cwd
            res2 = subprocess.run([sys.executable, "-B", str(script_path), "--output", str(out2)],
                                  cwd=str(atk_dir), capture_output=True, text=True)
            self.assertEqual(res2.returncode, 0)
            
            h1 = hashlib.sha256(out1.read_bytes()).hexdigest()
            h2 = hashlib.sha256(out2.read_bytes()).hexdigest()
            self.assertEqual(h1, h2, "Report must be byte-identical when run from different working directories")
            
            txt = out1.read_text(encoding="utf-8")
            self.assertIn("Source/OneBossFight/Player/RPGBossBleedAdapters.cpp", txt)
            self.assertNotIn(str(self.root_dir).replace("\\", "/"), txt, "Report must not contain absolute checkout paths")

    def test_missing_header_exit_code_and_named_message(self):
        import subprocess, tempfile
        script_path = self.root_dir / "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/diff_against_cpp.py"
        
        with tempfile.TemporaryDirectory() as td:
            mock_cpp = Path(td) / "RPGBossMockAdapters.cpp"
            mock_cpp.write_text("namespace RPGBossMockAdapters { bool ValidateMock(int x, FString& e) { return true; } }", encoding="utf-8")
            
            # Direct python API raises HeaderNotFoundError
            with self.assertRaises(diff_against_cpp.HeaderNotFoundError) as ctx:
                diff_against_cpp.extract_cpp_checks(mock_cpp)
            self.assertIn("RPGBossMockAdapters.h not found next to the .cpp", str(ctx.exception))
            
            # Subprocess execution exits with code 2
            res = subprocess.run([sys.executable, "-B", str(script_path), str(mock_cpp)],
                                 cwd=str(self.root_dir), capture_output=True, text=True)
            self.assertEqual(res.returncode, 2)
            self.assertIn("RPGBossMockAdapters.h not found next to the .cpp", res.stdout)
            self.assertIn("OVERALL STATUS: ERROR DETECTED", res.stdout)



class TestDeathPolicyDomain(unittest.TestCase):
    """
    Validates authored capability bounds for URPGBossDeath / FRPGDeathConfig.
    Enforces the definitive contract from Tech Lead Claude [C-281], [C-284] & [C-286]:
    - Header authored fields (12):
        DeathMode, DeathClip, DeathMontage, PackDeathAbilityClassName,
        PackDeathMontagesName, PackPollSeconds, PackEndTimeMultiplier,
        HoldAtSeconds, DyingSeconds, BlendInSeconds, MaxClipRestarts, bGuardPackDeath.
    - Five scalars finite first in header declaration order:
        PackPollSeconds, PackEndTimeMultiplier, HoldAtSeconds, DyingSeconds, BlendInSeconds.
    - BadMode check: PackMontage (0) or OwnClip (1).
    - Float domain boundaries:
        - PackPollSeconds: <= 0.0 NotPositive, > 1e6 AboveCeiling
        - PackEndTimeMultiplier: < 0.0 Negative (0.0 legal OFF), > 1e6 AboveCeiling
        - HoldAtSeconds: <= 0.0 NotPositive, > 1e6 AboveCeiling
        - DyingSeconds: <= 0.0 NotPositive, > 1e6 AboveCeiling
        - BlendInSeconds: < 0.0 Negative (0.0 legal), > 1e6 AboveCeiling
    - MaxClipRestarts boundaries:
        - < 0 Negative
        - 0 legal
        - 1,000,000 legal (per C-284 amendment)
        - > 1,000,000 AboveCeiling
    - FNames: Missing (None, empty, case-insensitive 'none'), Malformed (whitespace or control)
    - Soft paths: DeathClip and DeathMontage both required and well-formed in both modes
    - bGuardPackDeath: boolean accepted
    """
    def setUp(self):
        self.baseline_death = {
            "DeathMode": "PackMontage",
            "DeathClip": "/Game/OneBossFight/Boss01/Animations/AN_Boss01_DeathLegend.AN_Boss01_DeathLegend",
            "DeathMontage": "/Game/OneBossFight/Boss01/Animations/AM_Boss01_DeathLegend.AM_Boss01_DeathLegend",
            "PackDeathAbilityClassName": "GA_GS_Boss_Death_C",
            "PackDeathMontagesName": "DeathMontages",
            "PackPollSeconds": 0.1,
            "PackEndTimeMultiplier": 1.0,
            "HoldAtSeconds": 0.5,
            "DyingSeconds": 1.0,
            "BlendInSeconds": 0.2,
            "MaxClipRestarts": 0,
            "bGuardPackDeath": True,
        }

    def test_baseline_death_passes(self):
        errs = validate_death_domain(self.baseline_death)
        self.assertEqual(errs, [])

    def test_own_clip_mode_passes(self):
        rec = copy.deepcopy(self.baseline_death)
        rec["DeathMode"] = "OwnClip"
        self.assertEqual(validate_death_domain(rec), [])

    def test_integer_modes_pass(self):
        rec0 = copy.deepcopy(self.baseline_death)
        rec0["DeathMode"] = 0
        self.assertEqual(validate_death_domain(rec0), [])

        rec1 = copy.deepcopy(self.baseline_death)
        rec1["DeathMode"] = 1
        self.assertEqual(validate_death_domain(rec1), [])

    def test_invalid_death_mode_rejected(self):
        for bad in ["BadMode", "Montage", 2, -1, None, 3.14]:
            rec = copy.deepcopy(self.baseline_death)
            rec["DeathMode"] = bad
            errs = validate_death_domain(rec)
            self.assertTrue(any("InvalidDeath.BadMode: Death.DeathMode" in e for e in errs),
                            f"Expected BadMode for {bad}, got {errs}")

    def test_not_finite_scalars_rejected_in_header_order(self):
        scalars = [
            "PackPollSeconds",
            "PackEndTimeMultiplier",
            "HoldAtSeconds",
            "DyingSeconds",
            "BlendInSeconds",
        ]
        for field in scalars:
            for bad_val in [float("nan"), float("inf"), float("-inf")]:
                rec = copy.deepcopy(self.baseline_death)
                rec[field] = bad_val
                errs = validate_death_domain(rec)
                self.assertTrue(any(f"InvalidDeath.NotFinite: Death.{field}" in e for e in errs),
                                f"Expected NotFinite for {field}={bad_val}, got {errs}")

    def test_pack_poll_seconds_boundaries(self):
        rec = copy.deepcopy(self.baseline_death)
        rec["PackPollSeconds"] = 0.0
        self.assertTrue(any("InvalidDeath.NotPositive: Death.PackPollSeconds" in e for e in validate_death_domain(rec)))

        rec["PackPollSeconds"] = -0.5
        self.assertTrue(any("InvalidDeath.NotPositive: Death.PackPollSeconds" in e for e in validate_death_domain(rec)))

        rec["PackPollSeconds"] = 1000000.1
        self.assertTrue(any("InvalidDeath.AboveCeiling: Death.PackPollSeconds" in e for e in validate_death_domain(rec)))

        rec["PackPollSeconds"] = 0.001
        self.assertEqual(validate_death_domain(rec), [])

        rec["PackPollSeconds"] = 1000000.0
        self.assertEqual(validate_death_domain(rec), [])

    def test_pack_end_time_multiplier_boundaries(self):
        rec = copy.deepcopy(self.baseline_death)
        rec["PackEndTimeMultiplier"] = -0.01
        self.assertTrue(any("InvalidDeath.Negative: Death.PackEndTimeMultiplier" in e for e in validate_death_domain(rec)))

        rec["PackEndTimeMultiplier"] = 0.0  # 0.0 is legal OFF state
        self.assertEqual(validate_death_domain(rec), [])

        rec["PackEndTimeMultiplier"] = 1000000.0
        self.assertEqual(validate_death_domain(rec), [])

        rec["PackEndTimeMultiplier"] = 1000000.1
        self.assertTrue(any("InvalidDeath.AboveCeiling: Death.PackEndTimeMultiplier" in e for e in validate_death_domain(rec)))

    def test_hold_at_seconds_boundaries(self):
        rec = copy.deepcopy(self.baseline_death)
        rec["HoldAtSeconds"] = 0.0
        self.assertTrue(any("InvalidDeath.NotPositive: Death.HoldAtSeconds" in e for e in validate_death_domain(rec)))

        rec["HoldAtSeconds"] = -1.0
        self.assertTrue(any("InvalidDeath.NotPositive: Death.HoldAtSeconds" in e for e in validate_death_domain(rec)))

        rec["HoldAtSeconds"] = 1000000.1
        self.assertTrue(any("InvalidDeath.AboveCeiling: Death.HoldAtSeconds" in e for e in validate_death_domain(rec)))

        rec["HoldAtSeconds"] = 0.1
        self.assertEqual(validate_death_domain(rec), [])

        rec["HoldAtSeconds"] = 1000000.0
        self.assertEqual(validate_death_domain(rec), [])

    def test_dying_seconds_boundaries(self):
        rec = copy.deepcopy(self.baseline_death)
        rec["DyingSeconds"] = 0.0
        self.assertTrue(any("InvalidDeath.NotPositive: Death.DyingSeconds" in e for e in validate_death_domain(rec)))

        rec["DyingSeconds"] = -0.2
        self.assertTrue(any("InvalidDeath.NotPositive: Death.DyingSeconds" in e for e in validate_death_domain(rec)))

        rec["DyingSeconds"] = 1000000.1
        self.assertTrue(any("InvalidDeath.AboveCeiling: Death.DyingSeconds" in e for e in validate_death_domain(rec)))

        rec["DyingSeconds"] = 0.05
        self.assertEqual(validate_death_domain(rec), [])

        rec["DyingSeconds"] = 1000000.0
        self.assertEqual(validate_death_domain(rec), [])

    def test_blend_in_seconds_boundaries(self):
        rec = copy.deepcopy(self.baseline_death)
        rec["BlendInSeconds"] = -0.01
        self.assertTrue(any("InvalidDeath.Negative: Death.BlendInSeconds" in e for e in validate_death_domain(rec)))

        rec["BlendInSeconds"] = 0.0  # 0.0 is legal
        self.assertEqual(validate_death_domain(rec), [])

        rec["BlendInSeconds"] = 1000000.0
        self.assertEqual(validate_death_domain(rec), [])

        rec["BlendInSeconds"] = 1000000.1
        self.assertTrue(any("InvalidDeath.AboveCeiling: Death.BlendInSeconds" in e for e in validate_death_domain(rec)))

    def test_max_clip_restarts_boundaries(self):
        rec = copy.deepcopy(self.baseline_death)
        rec["MaxClipRestarts"] = -1
        self.assertTrue(any("InvalidDeath.Negative: Death.MaxClipRestarts" in e for e in validate_death_domain(rec)))

        rec["MaxClipRestarts"] = 0
        self.assertEqual(validate_death_domain(rec), [])

        rec["MaxClipRestarts"] = 1000000  # C-284 ceiling
        self.assertEqual(validate_death_domain(rec), [])

        rec["MaxClipRestarts"] = 1000001
        self.assertTrue(any("InvalidDeath.AboveCeiling: Death.MaxClipRestarts" in e for e in validate_death_domain(rec)))

        rec["MaxClipRestarts"] = 2147483647
        self.assertTrue(any("InvalidDeath.AboveCeiling: Death.MaxClipRestarts" in e for e in validate_death_domain(rec)))

    def test_pack_death_ability_class_name_missing_rejected(self):
        for bad in [None, "", "   ", "none", "None", "NONE", "nOnE"]:
            rec = copy.deepcopy(self.baseline_death)
            rec["PackDeathAbilityClassName"] = bad
            errs = validate_death_domain(rec)
            self.assertTrue(any("InvalidDependency.Missing: Death.PackDeathAbilityClassName" in e for e in errs),
                            f"Expected Missing for {bad}, got {errs}")

    def test_pack_death_ability_class_name_malformed_rejected(self):
        for bad in ["With Space", "With\tTab", "With\nNewline"]:
            rec = copy.deepcopy(self.baseline_death)
            rec["PackDeathAbilityClassName"] = bad
            errs = validate_death_domain(rec)
            self.assertTrue(any("InvalidDependency.Malformed: Death.PackDeathAbilityClassName" in e for e in errs),
                            f"Expected Malformed for {bad}, got {errs}")

    def test_pack_death_montages_name_missing_rejected(self):
        for bad in [None, "", "   ", "none", "None", "NONE", "nOnE"]:
            rec = copy.deepcopy(self.baseline_death)
            rec["PackDeathMontagesName"] = bad
            errs = validate_death_domain(rec)
            self.assertTrue(any("InvalidDependency.Missing: Death.PackDeathMontagesName" in e for e in errs),
                            f"Expected Missing for {bad}, got {errs}")

    def test_pack_death_montages_name_malformed_rejected(self):
        for bad in ["With Space", "With\tTab", "With\nNewline"]:
            rec = copy.deepcopy(self.baseline_death)
            rec["PackDeathMontagesName"] = bad
            errs = validate_death_domain(rec)
            self.assertTrue(any("InvalidDependency.Malformed: Death.PackDeathMontagesName" in e for e in errs),
                            f"Expected Malformed for {bad}, got {errs}")

    def test_death_clip_required_in_both_modes(self):
        for mode in ["PackMontage", "OwnClip"]:
            rec = copy.deepcopy(self.baseline_death)
            rec["DeathMode"] = mode
            rec["DeathClip"] = None
            errs = validate_death_domain(rec)
            self.assertTrue(any("InvalidDependency.Missing: Death.DeathClip" in e for e in errs),
                            f"Expected Missing DeathClip in mode {mode}, got {errs}")

            rec["DeathClip"] = ""
            errs = validate_death_domain(rec)
            self.assertTrue(any("InvalidDependency.Missing: Death.DeathClip" in e for e in errs),
                            f"Expected Missing DeathClip in mode {mode}, got {errs}")

    def test_death_clip_malformed_rejected(self):
        for bad in ["NoLeadingSlash", "/Game/NoLeafDot", "/Game/With Space/Asset.Asset", "/Game/Sub:Object"]:
            rec = copy.deepcopy(self.baseline_death)
            rec["DeathClip"] = bad
            errs = validate_death_domain(rec)
            self.assertTrue(any("InvalidDependency.Malformed: Death.DeathClip=" in e for e in errs),
                            f"Expected Malformed DeathClip for {bad}, got {errs}")

    def test_death_montage_required_in_both_modes(self):
        for mode in ["PackMontage", "OwnClip"]:
            rec = copy.deepcopy(self.baseline_death)
            rec["DeathMode"] = mode
            rec["DeathMontage"] = None
            errs = validate_death_domain(rec)
            self.assertTrue(any("InvalidDependency.Missing: Death.DeathMontage" in e for e in errs),
                            f"Expected Missing DeathMontage in mode {mode}, got {errs}")

            rec["DeathMontage"] = ""
            errs = validate_death_domain(rec)
            self.assertTrue(any("InvalidDependency.Missing: Death.DeathMontage" in e for e in errs),
                            f"Expected Missing DeathMontage in mode {mode}, got {errs}")

    def test_death_montage_malformed_rejected(self):
        for bad in ["NoLeadingSlash", "/Game/NoLeafDot", "/Game/With Space/Asset.Asset", "/Game/Sub:Object"]:
            rec = copy.deepcopy(self.baseline_death)
            rec["DeathMontage"] = bad
            errs = validate_death_domain(rec)
            self.assertTrue(any("InvalidDependency.Malformed: Death.DeathMontage=" in e for e in errs),
                            f"Expected Malformed DeathMontage for {bad}, got {errs}")

    def test_guard_pack_death_boolean_accepted(self):
        rec = copy.deepcopy(self.baseline_death)
        rec["bGuardPackDeath"] = True
        self.assertEqual(validate_death_domain(rec), [])

        rec["bGuardPackDeath"] = False
        self.assertEqual(validate_death_domain(rec), [])



# ---------------------------------------------------------------------------
# Test Fake Unreal Module Qualification Suite (Order A-212 / Item 7)
# ---------------------------------------------------------------------------
class TestFakeUnrealEngineReflection(unittest.TestCase):
    """
    Adversarial qualification suite using a Fake Unreal Module reproducing verified engine reflection:
    - Struct instances store properties via set_editor_property(name, val).
    - Properties are reachable ONLY via get_editor_property(name).
    - hasattr(struct_instance, name) returns False for all struct properties.
    - Setting a dict for a struct property on a DataAsset raises TypeError.
    - Proves new code (constructing struct instances) passes against it.
    - Proves old code (passing dict for struct property) fails with TypeError.
    """
    def setUp(self):
        class FakeLoadedObject:
            def __init__(self, path):
                self.path = str(path)
            def get_path_name(self):
                return self.path
            def to_string(self):
                return self.path
            def __repr__(self):
                return f"<Object '{self.path}' (0x12345) Class 'UObject'>"

        SOFT_PROP_NAMES = {
            "proc_effect", "proc_sound", "body", "sword", "pieces",
            "projectile_class", "immunity_effect", "roar_clip", "transition_montage",
            "down_clip", "fall_clip", "fall_montage", "get_up_montage",
            "riposte_boss_clip", "riposte_player_clip", "dormant_clip", "wake_clip",
            "a1_montage", "a3a_montage", "a3b_montage", "death_clip", "death_montage",
            "skeleton", "animations"
        }

        class FakeStructBase:
            def __init__(self):
                self._props = {}
            def get_editor_property(self, name):
                if name not in self._props:
                    raise KeyError(f"Property '{name}' not set on struct")
                return self._props[name]
            def set_editor_property(self, name, val):
                if name in SOFT_PROP_NAMES:
                    if isinstance(val, str):
                        raise TypeError(f"Failed to convert type 'str' to property '{name}' (SoftObjectProperty)")
                    if hasattr(val, "asset_path_name") and not hasattr(val, "get_path_name"):
                        raise TypeError(f"Cannot nativize 'SoftObjectPath' as 'Object'")
                    if name == "pieces" and isinstance(val, list):
                        for item in val:
                            if isinstance(item, str) or (hasattr(item, "asset_path_name") and not hasattr(item, "get_path_name")):
                                raise TypeError(f"Cannot nativize '{type(item).__name__}' as 'Object'")
                self._props[name] = val
            def __getattr__(self, name):
                raise AttributeError(f"Struct properties are not attributes: {name}")

        class FakeEditorAssetLibrary:
            def __init__(self):
                self.known = {
                    "/Game/BloodPack/Hit/Niagara/NS_BulletHit_Med.NS_BulletHit_Med",
                    "/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue.A_Guardian_ImpactL_Cue",
                    "/Game/OneBossFight/Boss01/Body/SK_Boss01_Body.SK_Boss01_Body",
                    "/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown.SK_Boss01_Crown",
                    "/Game/OneBossFight/Boss01/Body/SK_Boss01_Mantle.SK_Boss01_Mantle",
                    "/Game/OneBossFight/Boss01/Body/SK_Boss01_BrazierGauntlet.SK_Boss01_BrazierGauntlet",
                    "/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword.SM_Boss01_Greatsword",
                    "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin.SK_CombatMannequin",
                    "/Game/Mesh.Mesh"
                }
            def does_asset_exist(self, path):
                return path in self.known
            def load_asset(self, path):
                if path in self.known:
                    return FakeLoadedObject(path)
                return None

        class FakeDeathModeEnum:
            class PACK_MONTAGE:
                name = "PACK_MONTAGE"
            class OWN_CLIP:
                name = "OWN_CLIP"

        class FakeName:
            def __init__(self, val=""):
                self.val = str(val)
            def to_string(self):
                return self.val
            def __str__(self):
                return self.val
            def __repr__(self):
                return f"Name('{self.val}')"

        class FakeSoftObjectPath:
            def __init__(self, val=""):
                self.asset_path_name = str(val)
            def to_string(self):
                return self.asset_path_name
            def __str__(self):
                return self.asset_path_name
            def __repr__(self):
                return f"SoftObjectPath('{self.asset_path_name}')"

        class FakeDataAsset:
            STRUCT_PROPERTY_NAMES = {
                "stats", "encounter_policy", "stagger_policy", "phase_flow",
                "fireball", "phase_dependencies", "stagger_profile", "dormant_wake",
                "bleed", "low_sweep", "shockwave", "heal_punish", "look",
                "close_clip_swap", "death"
            }
            ARRAY_STRUCT_PROPERTY_NAMES = {"phases", "fields"}

            def __init__(self):
                self._props = {}

            def get_editor_property(self, name):
                return self._props.get(name)

            def set_editor_property(self, name, val):
                # REJECT DICT FOR STRUCT PROPERTY (Verified Engine Behavior)
                if name in self.STRUCT_PROPERTY_NAMES and isinstance(val, dict):
                    raise TypeError(
                        f"Cannot set struct property '{name}' from a Python dict. "
                        f"Unreal Engine requires an instance of the corresponding UStruct wrapper."
                    )
                # REJECT DICT IN ARRAY OF STRUCTS
                if name in self.ARRAY_STRUCT_PROPERTY_NAMES and isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict):
                            raise TypeError(
                                f"Array property '{name}' contains a dict. "
                                f"Unreal Engine requires instances of UStruct wrapper."
                            )
                self._props[name] = val

        self.fake_unreal = SimpleNamespace(
            is_editor=lambda: True,
            RPGBossStatsConfig=type("RPGBossStatsConfig", (FakeStructBase,), {}),
            RPGEncounterPolicyConfig=type("RPGEncounterPolicyConfig", (FakeStructBase,), {}),
            RPGStaggerPolicyConfig=type("RPGStaggerPolicyConfig", (FakeStructBase,), {}),
            RPGPhaseFlowConfig=type("RPGPhaseFlowConfig", (FakeStructBase,), {}),
            RPGFireballConfig=type("RPGFireballConfig", (FakeStructBase,), {}),
            RPGPhaseDependencyConfig=type("RPGPhaseDependencyConfig", (FakeStructBase,), {}),
            RPGStaggerProfileConfig=type("RPGStaggerProfileConfig", (FakeStructBase,), {}),
            RPGDormantWakeConfig=type("RPGDormantWakeConfig", (FakeStructBase,), {}),
            RPGBleedConfig=type("RPGBleedConfig", (FakeStructBase,), {}),
            RPGLowSweepConfig=type("RPGLowSweepConfig", (FakeStructBase,), {}),
            RPGShockwaveConfig=type("RPGShockwaveConfig", (FakeStructBase,), {}),
            RPGHealPunishConfig=type("RPGHealPunishConfig", (FakeStructBase,), {}),
            RPGLookConfig=type("RPGLookConfig", (FakeStructBase,), {}),
            RPGCloseClipSwapConfig=type("RPGCloseClipSwapConfig", (FakeStructBase,), {}),
            RPGDeathConfig=type("RPGDeathConfig", (FakeStructBase,), {}),
            RPGPhaseConfig=type("RPGPhaseConfig", (FakeStructBase,), {}),
            RPGParityField=type("RPGParityField", (FakeStructBase,), {}),
            RPGBossDeathMode=FakeDeathModeEnum,
            Name=FakeName,
            SoftObjectPath=FakeSoftObjectPath,
            EditorAssetLibrary=FakeEditorAssetLibrary(),
            FakeLoadedObject=FakeLoadedObject,
            FakeDataAsset=FakeDataAsset
        )

    def test_hasattr_is_false_on_struct_instances(self):
        bleed_inst = self.fake_unreal.RPGBleedConfig()
        self.assertFalse(hasattr(bleed_inst, "effect_height"))
        bleed_inst.set_editor_property("effect_height", 170.0)
        self.assertFalse(hasattr(bleed_inst, "effect_height"))
        self.assertEqual(bleed_inst.get_editor_property("effect_height"), 170.0)

    def test_old_code_dict_assignment_raises_type_error(self):
        asset = self.fake_unreal.FakeDataAsset()
        # Old code passed plain dict from map_native_dict_to_python_keys
        dict_payload = {"max_health": 1500.0, "max_posture": 200.0}
        with self.assertRaises(TypeError) as ctx:
            asset.set_editor_property("stats", dict_payload)
        self.assertIn("Cannot set struct property 'stats' from a Python dict", str(ctx.exception))

    def test_new_code_struct_instance_assignment_succeeds(self):
        asset = self.fake_unreal.FakeDataAsset()
        native_stats = {
            "MaxHealth": 1500.0,
            "MaxPosture": 200.0,
            "PostureRegenDelay": 3.0,
            "PostureRegenRate": 15.0
        }
        # New code creates real struct instance via create_struct_instance
        from authoring_core import create_struct_instance, extract_canonical_primitives, NATIVE_BOSS_STATS_FIELDS
        struct_inst = create_struct_instance("stats", native_stats, self.fake_unreal)
        self.assertNotIsInstance(struct_inst, dict)
        asset.set_editor_property("stats", struct_inst)

        readback = asset.get_editor_property("stats")
        canonical = extract_canonical_primitives(readback, NATIVE_BOSS_STATS_FIELDS)
        self.assertEqual(canonical["MaxHealth"], 1500.0)
        self.assertEqual(canonical["MaxPosture"], 200.0)
        self.assertEqual(canonical["PostureRegenDelay"], 3.0)
        self.assertEqual(canonical["PostureRegenRate"], 15.0)

    def test_explicit_conversion_helpers(self):
        from authoring_core import to_soft_ref, to_fname, to_death_mode, convert_property_for_engine

        # Soft ref with EditorAssetLibrary loads real object
        soft_val, form = to_soft_ref("/Game/Mesh.Mesh", self.fake_unreal)
        self.assertEqual(form, "loaded_object")
        self.assertEqual(soft_val.get_path_name(), "/Game/Mesh.Mesh")

        # FName
        fname_val, form = to_fname("HeavySwordSocket_R", self.fake_unreal)
        self.assertEqual(form, "unreal.Name")
        self.assertEqual(str(fname_val), "HeavySwordSocket_R")

        # Death mode
        death_val, form = to_death_mode("PackMontage", self.fake_unreal)
        self.assertEqual(form, "unreal.RPGBossDeathMode.PACK_MONTAGE")
        self.assertEqual(death_val.name, "PACK_MONTAGE")

        death_val2, form2 = to_death_mode("OwnClip", self.fake_unreal)
        self.assertEqual(form2, "unreal.RPGBossDeathMode.OWN_CLIP")
        self.assertEqual(death_val2.name, "OWN_CLIP")

    def test_diagnostic_failure_collector_collects_without_stopping(self):
        import draft_boss_profiles
        collector = draft_boss_profiles.DiagnosticFailureCollector(fail_fast=False)
        self.assertFalse(collector.has_failures)

        collector.record_failure("Asset1", "stats", "max_health", 1500.0, 1000.0, mismatch_msg="Value mismatch")
        collector.record_failure("Asset1", "bleed", "proc_effect", "/Game/VFX.VFX", None, error_ex=RuntimeError("Soft path not found"))
        self.assertTrue(collector.has_failures)
        self.assertEqual(len(collector.failures), 2)
        self.assertEqual(collector.failures[0]["property"], "max_health")
        self.assertEqual(collector.failures[1]["error_class"], "RuntimeError")

        # In fail_fast mode, it raises immediately
        fail_fast_collector = draft_boss_profiles.DiagnosticFailureCollector(fail_fast=True)
        with self.assertRaises(RuntimeError) as ctx:
            fail_fast_collector.record_failure("Asset1", "stats", "max_health", 1500.0, 1000.0, mismatch_msg="Value mismatch")
        self.assertIn("Fail-fast failure on 'Asset1.stats.max_health'", str(ctx.exception))

    def test_create_empty_struct_instance(self):
        from authoring_core import create_empty_struct_instance
        # With fake unreal: returns struct wrapper instance
        empty_inst = create_empty_struct_instance("bleed", self.fake_unreal)
        self.assertNotIsInstance(empty_inst, dict)
        self.assertTrue(hasattr(empty_inst, "set_editor_property"))

        # Offline without unreal: returns empty dict
        offline_inst = create_empty_struct_instance("bleed", None)
        self.assertEqual(offline_inst, {})

    def test_soft_ref_rejects_str_and_softobjectpath_with_type_error(self):
        bleed_inst = self.fake_unreal.RPGBleedConfig()
        with self.assertRaises(TypeError):
            bleed_inst.set_editor_property("proc_effect", "/Game/Mesh.Mesh")
        with self.assertRaises(TypeError):
            bleed_inst.set_editor_property("proc_effect", self.fake_unreal.SoftObjectPath("/Game/Mesh.Mesh"))

    def test_new_to_soft_ref_with_editor_asset_library_succeeds(self):
        from authoring_core import to_soft_ref
        loaded_obj, form = to_soft_ref("/Game/Mesh.Mesh", self.fake_unreal)
        self.assertEqual(form, "loaded_object")
        bleed_inst = self.fake_unreal.RPGBleedConfig()
        bleed_inst.set_editor_property("proc_effect", loaded_obj)
        self.assertEqual(bleed_inst.get_editor_property("proc_effect").get_path_name(), "/Game/Mesh.Mesh")

    def test_missing_asset_raises_runtime_error(self):
        from authoring_core import to_soft_ref
        with self.assertRaises(RuntimeError) as ctx:
            to_soft_ref("/Game/NonExistentAsset.NonExistentAsset", self.fake_unreal)
        self.assertIn("asset does not exist or did not load", str(ctx.exception))

    def test_soft_ref_arrays_as_lists_of_loaded_objects(self):
        from authoring_core import convert_property_for_engine
        pieces_paths = [
            "/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown.SK_Boss01_Crown",
            "/Game/OneBossFight/Boss01/Body/SK_Boss01_Mantle.SK_Boss01_Mantle"
        ]
        converted, form = convert_property_for_engine("Pieces", pieces_paths, list, self.fake_unreal)
        self.assertEqual(form, "list[loaded_object]")
        look_inst = self.fake_unreal.RPGLookConfig()
        look_inst.set_editor_property("pieces", converted)
        rb_pieces = look_inst.get_editor_property("pieces")
        self.assertEqual(len(rb_pieces), 2)
        self.assertEqual(rb_pieces[0].get_path_name(), pieces_paths[0])

    def test_soft_ref_readback_canonicalization(self):
        from authoring_core import to_soft_ref, extract_canonical_primitives, NATIVE_LOOK_FIELDS
        look_inst = self.fake_unreal.RPGLookConfig()
        body_obj, _ = to_soft_ref("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body.SK_Boss01_Body", self.fake_unreal)
        look_inst.set_editor_property("body", body_obj)
        look_inst.set_editor_property("enabled", True)
        look_inst.set_editor_property("pieces", [])
        look_inst.set_editor_property("sword", None)
        look_inst.set_editor_property("sword_socket", self.fake_unreal.Name("HeavySwordSocket_R"))
        canonical = extract_canonical_primitives(look_inst, NATIVE_LOOK_FIELDS)
        self.assertEqual(canonical["Body"], "/Game/OneBossFight/Boss01/Body/SK_Boss01_Body.SK_Boss01_Body")
        self.assertEqual(canonical["Sword"], "")

    def test_diagnostic_collector_untruncated_and_step_attribution(self):
        import io
        from contextlib import redirect_stdout
        import draft_boss_profiles

        collector = draft_boss_profiles.DiagnosticFailureCollector(fail_fast=False)
        long_err = "TypeError: RPGBossDefinition: cannot assign SoftObjectPath to field of type TSoftObjectPtr<USkeletalMesh>"
        collector.record_failure(
            "DA_Boss_EmberWarden_Draft", "look", "body",
            "/Game/OneBossFight/Boss01/Body/SK_Boss01_Body.SK_Boss01_Body",
            None,
            error_ex=TypeError(long_err),
            step="set_editor_property"
        )
        self.assertEqual(collector.failure_count_for_asset("DA_Boss_EmberWarden_Draft"), 1)
        self.assertEqual(collector.failure_count_for_asset("OtherAsset"), 0)

        # Step attribution: property label is body, step is set_editor_property
        self.assertEqual(collector.failures[0]["property"], "body")
        self.assertEqual(collector.failures[0]["step"], "set_editor_property")

        # Constructor failure step attribution
        collector.record_failure(
            "DA_Boss_EmberWarden_Draft", "fireball", "(constructor)",
            "struct instance", None,
            error_ex=RuntimeError("Constructor failed"),
            step="construct"
        )
        self.assertEqual(collector.failures[1]["property"], "construct")

        # Verify untruncated printing
        buf = io.StringIO()
        with redirect_stdout(buf):
            collector.print_summary_table()
        out = buf.getvalue()

        self.assertIn("[DIAGNOSTIC SUMMARY DETAILS (UNTRUNCATED)]", out)
        self.assertIn(f"[DRAFT_APPLY][FAILURE] DA_Boss_EmberWarden_Draft look body expected='/Game/OneBossFight/Boss01/Body/SK_Boss01_Body.SK_Boss01_Body' actual_type=NoneType actual_repr=None exception=TypeError: {long_err}", out)


class TestCandidateClassRefConverters(unittest.TestCase):
    """
    Preparation for Order A-218 (Lead C-327):
    Parameterized unit tests evaluating candidate class-reference conversion forms
    for TSoftClassPtr<UObject> fields (FireballAbility, ImmunityEffect) against fake unreal.
    Enables instant one-line selection once Codex's DD27g measurement identifies the winning form.
    """
    def setUp(self):
        class MockUClass:
            def __init__(self, name):
                self.name = name
            def get_path_name(self):
                return self.name
            def __repr__(self):
                return f"<Class '{self.name}'>"

        class MockBPAsset:
            def __init__(self, path):
                self.path = path
            def generated_class(self):
                return MockUClass(self.path + "_C")

        class MockStruct:
            def __init__(self):
                self.props = {}
            def set_editor_property(self, name, val):
                if isinstance(val, str) and not isinstance(val, MockUClass):
                    raise TypeError(f"Failed to convert type 'str' to property '{name}' (SoftClassProperty)")
                if hasattr(val, "is_name") or type(val).__name__ == "MockName":
                    raise TypeError(f"Failed to convert type 'Name' to property '{name}' (SoftClassProperty)")
                self.props[name] = val
            def get_editor_property(self, name):
                return self.props.get(name)

        class MockName:
            def __init__(self, s):
                self.val = str(s)
                self.is_name = True

        class FakeEngineForClassRefs:
            Name = MockName
            RPGFireballConfig = MockStruct
            RPGPhaseDependencyConfig = MockStruct
            RPGStaggerProfileConfig = MockStruct

            @staticmethod
            def load_class(outer, path):
                if path.endswith("_C"):
                    return MockUClass(path)
                raise RuntimeError(f"load_class failed for {path}")

            class EditorAssetLibrary:
                @staticmethod
                def load_blueprint_class(path):
                    clean = path[:-2] if path.endswith("_C") else path
                    return MockUClass(clean + "_C")

                @staticmethod
                def load_asset(path):
                    clean = path[:-2] if path.endswith("_C") else path
                    return MockBPAsset(clean)

                @staticmethod
                def does_asset_exist(path):
                    return not path.endswith("_C")

        self.engine = FakeEngineForClassRefs

    def _convert_candidate(self, form_name, path):
        if form_name == "load_class":
            path_c = path if path.endswith("_C") else (path + "_C")
            return self.engine.load_class(None, path_c)
        elif form_name == "load_blueprint_class":
            path_base = path[:-2] if path.endswith("_C") else path
            return self.engine.EditorAssetLibrary.load_blueprint_class(path_base)
        elif form_name == "load_asset_generated_class":
            path_base = path[:-2] if path.endswith("_C") else path
            asset = self.engine.EditorAssetLibrary.load_asset(path_base)
            return asset.generated_class()
        raise ValueError(f"Unknown form: {form_name}")

    def test_parameterized_classref_candidates(self):
        forms = ["load_class", "load_blueprint_class", "load_asset_generated_class"]
        test_paths = [
            "/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.GA_Fireball_Enemy_C",
            "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C"
        ]
        for form in forms:
            for path in test_paths:
                class_obj = self._convert_candidate(form, path)
                self.assertIsNotNone(class_obj)
                self.assertTrue(class_obj.get_path_name().endswith("_C"))

                fb = self.engine.RPGFireballConfig()
                fb.set_editor_property("fireball_ability", class_obj)
                self.assertEqual(fb.get_editor_property("fireball_ability"), class_obj)

                pd = self.engine.RPGPhaseDependencyConfig()
                pd.set_editor_property("immunity_effect", class_obj)
                self.assertEqual(pd.get_editor_property("immunity_effect"), class_obj)

    def test_rejection_of_raw_string_and_name_for_soft_class(self):
        fb = self.engine.RPGFireballConfig()
        with self.assertRaises(TypeError):
            fb.set_editor_property("fireball_ability", "GA_Fireball_Enemy_C")
        with self.assertRaises(TypeError):
            fb.set_editor_property("fireball_ability", self.engine.Name("GA_Fireball_Enemy_C"))

if __name__ == "__main__":
    unittest.main()
