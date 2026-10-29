#!/usr/bin/env python3
"""
test_probe_unreal_api.py - Unit Tests for Read-Only Unreal API Reflection Probe

Authored for Task Orders A-206 / A-207 / A-209 (Directives C-301 / C-302 / C-305).
Tests static AST attribute chain extraction, C++ type candidate derivation,
prefix stripping logic, pythonized struct property extraction,
offline execution notice, runtime report formatting with a mock `unreal` module,
and Stage 2 `--instances` in-memory struct / CDO inspection.
"""

import os
import sys
import unittest

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

from Docs.BossCombatReview.Execution.Antigravity.AuthoringToolkit.probe_unreal_api import (
    strip_unreal_prefix,
    extract_cpp_types_from_header,
    extract_candidate_types_from_cpp,
    extract_static_chains,
    extract_python_property_names,
    resolve_unreal_chain,
    run_probe,
    SPEC_TO_STRUCT_MAP
)

class MockSystemLibrary:
    pass

class MockEditorAssetLibrary:
    @staticmethod
    def does_asset_exist(path):
        return True

class MockAssetTools:
    @staticmethod
    def create_asset(asset_name, package_path, asset_class, factory):
        return None

class MockAssetToolsHelpers:
    @staticmethod
    def get_asset_tools():
        return MockAssetTools()

class MockBleedConfig:
    effect_height = 100.0
    hp_fraction = 0.03
    initial_threshold = 100.0
    proc_effect = ""
    proc_sound = ""
    threshold_increase = 10.0
    threshold_max = 300.0
    def _private_func(self):
        pass
    def get_editor_property(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        raise AttributeError(f"Property {name} not found")

class MockBossDefinitionCDO:
    schema = 1
    definition_id = "DA_Boss_EmberWarden"
    presentation_id = "Presentation_EmberWarden"
    skeleton = "/Game/Skeleton"
    animations = []
    phases = []
    fields = []
    stats = None
    encounter_policy = None
    stagger_policy = None
    phase_flow = None
    fireball = None
    phase_dependencies = None
    stagger_profile = None
    dormant_wake = None
    bleed = None
    low_sweep = None
    shockwave = None
    heal_punish = None
    look = None
    close_clip_swap = None
    death = None
    def get_editor_property(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        raise AttributeError(f"Property {name} not found")

class MockRPGBossDefinitionClass:
    @staticmethod
    def get_default_object():
        return MockBossDefinitionCDO()

class MockDeathModeEnum:
    OwnClip = 0
    PackMontage = 1

class MockUnrealModule:
    """Mock `unreal` module simulating partial engine reflection presence."""
    def __init__(self):
        self.SystemLibrary = MockSystemLibrary()
        self.EditorAssetLibrary = MockEditorAssetLibrary()
        self.AssetToolsHelpers = MockAssetToolsHelpers()
        self.AssetTools = MockAssetTools()
        self.RPGBleedConfig = MockBleedConfig
        self.RPGBossDeathMode = MockDeathModeEnum
        self.RPGBossDefinition = MockRPGBossDefinitionClass
        self.is_editor = lambda: True
        # Symbols matching filter keywords
        self.RPGCombatContextSubsystem = object()
        self.EditorUtilitySubsystem = object()

    def load_class(self, outer, path):
        return None

class TestProbeUnrealApi(unittest.TestCase):

    def test_strip_unreal_prefix(self):
        """Verify stripping of Unreal C++ prefixes (F, U, A, E) followed by uppercase."""
        self.assertEqual(strip_unreal_prefix("FRPGBleedConfig"), "RPGBleedConfig")
        self.assertEqual(strip_unreal_prefix("FRPGDeathConfig"), "RPGDeathConfig")
        self.assertEqual(strip_unreal_prefix("URPGBossDefinition"), "RPGBossDefinition")
        self.assertEqual(strip_unreal_prefix("ARPGEncounterBinding"), "RPGEncounterBinding")
        self.assertEqual(strip_unreal_prefix("ERPGBossDeathMode"), "RPGBossDeathMode")
        # Non-prefixed or edge names
        self.assertEqual(strip_unreal_prefix("CustomType"), "CustomType")
        self.assertEqual(strip_unreal_prefix("F"), "F")
        self.assertEqual(strip_unreal_prefix("float"), "float")

    def test_extract_cpp_types_from_header_fixture(self):
        """Verify candidate extraction and prefix-stripping from a small header fixture."""
        fixture = """
        USTRUCT(BlueprintType)
        struct ONEBOSSFIGHT_API FTestStatsConfig
        {
            GENERATED_BODY()
            UPROPERTY(EditAnywhere) float MaxHealth = 100.f;
        };

        UENUM(BlueprintType)
        enum class ETestPhaseMode : uint8
        {
            PhaseOne,
            PhaseTwo
        };

        UCLASS(ClassGroup=(Boss))
        class ONEBOSSFIGHT_API UTestBossAsset : public UPrimaryDataAsset
        {
            GENERATED_BODY()
        };
        """
        types = extract_cpp_types_from_header(fixture)
        self.assertEqual(len(types), 3)

        kinds = {t[0] for t in types}
        self.assertEqual(kinds, {"USTRUCT", "UENUM", "UCLASS"})

        cpp_names = [t[1] for t in types]
        py_names = [t[2] for t in types]
        self.assertEqual(cpp_names, ["FTestStatsConfig", "ETestPhaseMode", "UTestBossAsset"])
        self.assertEqual(py_names, ["TestStatsConfig", "TestPhaseMode", "TestBossAsset"])

    def test_candidate_types_from_live_cpp(self):
        """Verify scanning Source/OneBossFight/Player headers discovers all required types."""
        candidates = extract_candidate_types_from_cpp(repo_root=REPO_ROOT)
        self.assertGreaterEqual(len(candidates), 20)

        cpp_names = set(c[1] for c in candidates)
        py_names = set(c[2] for c in candidates)

        # Check critical struct names from RPGEncounterBinding.h
        self.assertIn("FRPGBleedConfig", cpp_names)
        self.assertIn("RPGBleedConfig", py_names)
        self.assertIn("FRPGDeathConfig", cpp_names)
        self.assertIn("RPGDeathConfig", py_names)
        self.assertIn("FRPGBossStatsConfig", cpp_names)
        self.assertIn("RPGBossStatsConfig", py_names)
        self.assertIn("FRPGEncounterPolicyConfig", cpp_names)
        self.assertIn("RPGEncounterPolicyConfig", py_names)
        self.assertIn("URPGBossDefinition", cpp_names)
        self.assertIn("RPGBossDefinition", py_names)
        self.assertIn("ERPGBossDeathMode", cpp_names)
        self.assertIn("RPGBossDeathMode", py_names)

    def test_static_extraction_not_empty(self):
        """Verify AST extraction retrieves attribute chains across all three toolkit files."""
        chains = extract_static_chains(repo_root=REPO_ROOT)
        self.assertGreater(len(chains), 30, "Should extract more than 30 attribute citations")

        chain_names = set(c[0] for c in chains)
        # Check required core chains
        self.assertIn("unreal.EditorAssetLibrary", chain_names)
        self.assertIn("unreal.EditorAssetLibrary.does_asset_exist", chain_names)
        self.assertIn("unreal.SystemLibrary", chain_names)
        self.assertIn("unreal.SystemLibrary.is_editor", chain_names)
        self.assertIn("unreal.UnrealEditorSubsystem.get_game_world", chain_names)
        self.assertIn("unreal.AssetToolsHelpers.get_asset_tools", chain_names)
        self.assertIn("unreal.load_class", chain_names)
        self.assertIn("unreal.load_package", chain_names)

        for chain, fpath, lno in chains:
            self.assertTrue(fpath.endswith(".py"))
            self.assertGreater(lno, 0)

    def test_struct_property_extraction(self):
        """Verify pythonized property mappings are extracted for all 17 structs."""
        py_props = extract_python_property_names()
        self.assertEqual(len(py_props), 17, "Must extract properties for exactly 17 structs")

        self.assertIn("a1_montage", py_props["close_clip_swap"])
        self.assertIn("death_mode", py_props["death"])
        self.assertIn("initial_threshold", py_props["bleed"])
        self.assertIn("stagger_seconds", py_props["stagger_policy"])
        self.assertIn("field_path", py_props["fields"])

    def test_offline_probe_output_format(self):
        """Verify report format and offline notice when unreal is not importable."""
        lines, present, missing = run_probe(unreal_mod=None, instances=False)
        report_text = "\n".join(lines)

        self.assertIn("=== STATIC UNREAL API CHAINS & CITATIONS ===", report_text)
        self.assertIn("=== CANDIDATE TYPES DERIVED FROM C++ HEADERS", report_text)
        self.assertIn("=== PYTHONIZED STRUCT PROPERTY MAPPINGS (STRUCT_SPECS) ===", report_text)
        self.assertIn("[PROBE] unreal not importable: runtime part skipped", report_text)
        self.assertIn("[PROBE] NOTICE: An offline run proves nothing about the engine.", report_text)
        self.assertIn("[PROBE] SUMMARY missing=0 present=0", report_text)
        self.assertEqual(present, 0)
        self.assertEqual(missing, 0)

    def test_mock_unreal_probe_runtime(self):
        """Verify runtime probe execution, formatting, and counting with a mock unreal module."""
        mock_unreal = MockUnrealModule()
        lines, present, missing = run_probe(unreal_mod=mock_unreal, instances=False)
        report_text = "\n".join(lines)

        self.assertIn("=== RUNTIME PROBE EXECUTION (import unreal SUCCEEDED) ===", report_text)
        self.assertIn("[PROBE] unreal.EditorAssetLibrary.does_asset_exist exists=True callable=True", report_text)
        self.assertIn("[PROBE] unreal.SystemLibrary.is_editor exists=False callable=False", report_text)

        # C++ candidate check
        self.assertIn("[PROBE] type cpp=FRPGBleedConfig py=RPGBleedConfig exists_cpp=False exists_py=True", report_text)

        # Library member check
        self.assertIn("[PROBE] LIBRARY EditorAssetLibrary member_count=", report_text)
        self.assertIn("  [PROBE] EditorAssetLibrary.does_asset_exist", report_text)

        # Filtered unreal symbols check
        self.assertIn("[PROBE] UNREAL_MATCHED_SYMBOLS count=", report_text)
        self.assertIn("[PROBE] UNREAL_SYMBOL RPGCombatContextSubsystem", report_text)

        # Struct property comparison check
        self.assertIn("[PROBE] STRUCT RPGBleedConfig property_count=", report_text)
        self.assertIn("  [PROBE] STRUCT_PROP RPGBleedConfig prop=initial_threshold toolkit=initial_threshold status=MATCH", report_text)

        # Enum member comparison check
        self.assertIn("[PROBE] ENUM RPGBossDeathMode enumerator_count=2", report_text)
        self.assertIn("  [PROBE] ENUM_MEMBER RPGBossDeathMode member=PackMontage toolkit=PackMontage status=MATCH", report_text)
        self.assertIn("  [PROBE] ENUM_MEMBER RPGBossDeathMode member=OwnClip toolkit=OwnClip status=MATCH", report_text)

        # Summary line
        self.assertGreater(present, 0)
        self.assertGreater(missing, 0)
        self.assertIn(f"[PROBE] SUMMARY missing={missing} present={present}", report_text)

    def test_mock_unreal_stage2_instances(self):
        """Verify Stage 2 --instances mode queries get_editor_property on instances and CDO."""
        mock_unreal = MockUnrealModule()
        lines, present, missing = run_probe(unreal_mod=mock_unreal, instances=True)
        report_text = "\n".join(lines)

        self.assertIn("=== STAGE 2 INSTANCE PROBE EXECUTION (--instances) ===", report_text)
        self.assertIn("[PROBE] INSTANCE_CALL construct: unreal.RPGBleedConfig()", report_text)
        self.assertIn("[PROBE] INSTANCE RPGBleedConfig prop=initial_threshold get_editor_property=ok hasattr=True value=100", report_text)
        self.assertIn("[PROBE] INSTANCE_CALL get_default_object: unreal.RPGBossDefinition.get_default_object()", report_text)
        self.assertIn("[PROBE] CDO RPGBossDefinition prop=schema get_editor_property=ok type=int", report_text)
        self.assertIn("[PROBE] unreal.is_editor exists=True callable=True", report_text)
        self.assertIn("[PROBE] unreal.is_editor() result=True", report_text)

    def test_offline_stage2_instances_skipped(self):
        """Verify Stage 2 --instances mode cleanly handles offline environment."""
        lines, present, missing = run_probe(unreal_mod=None, instances=True)
        report_text = "\n".join(lines)
        self.assertIn("[PROBE] unreal not importable: stage 2 instance probe skipped", report_text)

    def test_resolve_unreal_chain_stepwise(self):
        """Verify resolve_unreal_chain accurately handles attribute walks."""
        mock_unreal = MockUnrealModule()
        exists, is_call, type_name = resolve_unreal_chain(mock_unreal, "unreal.EditorAssetLibrary.does_asset_exist")
        self.assertTrue(exists)
        self.assertTrue(is_call)

        exists_missing, is_call_missing, type_missing = resolve_unreal_chain(mock_unreal, "unreal.NonExistentService.action")
        self.assertFalse(exists_missing)
        self.assertFalse(is_call_missing)
        self.assertEqual(type_missing, "none")

if __name__ == "__main__":
    unittest.main()
