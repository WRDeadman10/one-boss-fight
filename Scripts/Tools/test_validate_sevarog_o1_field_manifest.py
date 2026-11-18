"""Unit tests for validate_sevarog_o1_field_manifest and Sevarog BossCore requirements."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "Scripts" / "Tools"

import sys
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import sevarog_boss_core_required_fields as extractor
import validate_sevarog_o1_field_manifest as validator


class ValidateSevarogO1FieldManifestTests(unittest.TestCase):
    def test_extracted_paths_count_is_exactly_115(self):
        paths = extractor.extract_required_paths(ROOT)
        self.assertEqual(len(paths), 115)

    def test_owner_o1_paths_are_eight(self):
        self.assertEqual(len(validator.OWNER_PATHS), 8)
        paths = extractor.extract_required_paths(ROOT)
        self.assertTrue(validator.OWNER_PATHS.issubset(paths))

    def test_draft_preimage_paths_are_107(self):
        paths = extractor.extract_required_paths(ROOT)
        preimage = paths - validator.OWNER_PATHS
        self.assertEqual(len(preimage), 107)

    def test_validation_passes_cleanly(self):
        result = validator.validate(ROOT)
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["required_path_count"], 115)
        self.assertEqual(result["owner_o1_path_count"], 8)
        self.assertEqual(result["draft_preimage_path_count"], 107)
        self.assertEqual(len(result["owner_o1_paths"]), 8)
        self.assertEqual(len(result["draft_preimage_paths"]), 107)

    def test_all_metadata_required_fields_present(self):
        result = validator.validate(ROOT)
        required_meta = {"FieldPath", "Type", "SourcePath", "SourceSHA256", "SourceSite",
                         "Origin", "Precedence", "Destination", "FirstRead", "Witness"}
        self.assertEqual(set(result["field_metadata_required"]), required_meta)

    def test_fail_closed_on_altered_owner_paths(self):
        original = set(validator.OWNER_PATHS)
        try:
            validator.OWNER_PATHS = original | {"Stats.NonExistentField"}
            with self.assertRaises(ValueError):
                validator.validate(ROOT)
        finally:
            validator.OWNER_PATHS = original

    def test_evidence_context_and_verified_preimage_hash_containment(self):
        phase_source = (ROOT / "Scripts" / "Editor" / "ensure_bk56_60_sevarog_initial_phase.py").read_text(encoding="utf-8")
        self.assertIn("base_evidence_dir = (REPO / \"Saved\" / \"B_SEVAROG_O1\").resolve()", phase_source)
        self.assertIn("require(run_dir.parent == base_evidence_dir", phase_source)
        self.assertIn("require(witness_dir.parent == base_evidence_dir", phase_source)
        self.assertIn("require(re.fullmatch(r\"Run_[A-Za-z0-9_-]+\", run_dir.name) is not None", phase_source)
        self.assertIn("require(manifest_path.is_file() and manifest_path.parent == run_dir", phase_source)
        self.assertIn("require(manifest_path.is_file() and manifest_path.parent == witness_dir", phase_source)
        self.assertIn("expected_backup_dir = (run_dir / \"rollback_files\").resolve()", phase_source)
        self.assertIn("src == expected_source and bak == expected_backup and bak.is_relative_to(expected_backup_dir)", phase_source)

    def test_reflected_boolean_and_struct_property_resolution(self):
        import unittest.mock as mock
        import importlib.util
        sys.modules.setdefault("unreal", mock.MagicMock())
        spec = importlib.util.spec_from_file_location("ensure_bk56", ROOT / "Scripts/Editor/ensure_bk56_60_sevarog_initial_phase.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        class MockBossDefinition:
            def __init__(self):
                self.attack_tracker = "TrackerObj"
            def get_editor_property(self, name):
                if name in ("attack_tracker", "AttackTracker"):
                    return self.attack_tracker
                raise RuntimeError(f"Property {name} not found")

        boss = MockBossDefinition()
        self.assertEqual(mod.resolve_reflected_property_name(boss, "AttackTracker"), "attack_tracker")
        self.assertEqual(mod.get_reflected_property(boss, "AttackTracker"), "TrackerObj")

        class MockAttackTrackerConfig:
            def __init__(self):
                self.enabled = True
                self.veto_illegal_starts = True
                self.branch_range = 400.0
                self.branch_cone_degrees = 120.0
                self.attacks = []
            def get_editor_property(self, name):
                if hasattr(self, name):
                    return getattr(self, name)
                raise RuntimeError(f"RPGAttackTrackerConfig: Failed to find property '{name}' for attribute '{name}'")

        cfg = MockAttackTrackerConfig()
        self.assertEqual(mod.resolve_reflected_property_name(cfg, "bEnabled"), "enabled")
        self.assertEqual(mod.resolve_reflected_property_name(cfg, "bVetoIllegalStarts"), "veto_illegal_starts")
        self.assertEqual(mod.resolve_reflected_property_name(cfg, "BranchRange"), "branch_range")
        self.assertEqual(mod.resolve_reflected_property_name(cfg, "Attacks"), "attacks")
        self.assertTrue(mod.get_reflected_property(cfg, "bEnabled"))
        self.assertTrue(mod.get_reflected_property(cfg, "bVetoIllegalStarts"))
        self.assertEqual(mod.get_reflected_property(cfg, "BranchRange"), 400.0)

    def test_reflected_property_canonical_preference_and_missing_fails_closed(self):
        import unittest.mock as mock
        import importlib.util
        sys.modules.setdefault("unreal", mock.MagicMock())
        spec = importlib.util.spec_from_file_location("ensure_bk56", ROOT / "Scripts/Editor/ensure_bk56_60_sevarog_initial_phase.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        class MultiAliasConfig:
            def __init__(self):
                self.enabled = True
                self.b_enabled = False
            def get_editor_property(self, name):
                if hasattr(self, name):
                    return getattr(self, name)
                raise RuntimeError("missing")

        cfg = MultiAliasConfig()
        # Canonical preference picks stripped snake_case 'enabled' first
        self.assertEqual(mod.resolve_reflected_property_name(cfg, "bEnabled"), "enabled")

        class MissingConfig:
            def get_editor_property(self, name):
                raise RuntimeError(f"Failed to find property '{name}'")

        with self.assertRaises(RuntimeError):
            mod.resolve_reflected_property_name(MissingConfig(), "bEnabled")
        with self.assertRaises(RuntimeError):
            mod.resolve_reflected_property_name(MissingConfig(), "NonExistentField")

    def test_stable_value_uobject_and_struct_address_independence(self):
        import unittest.mock as mock
        import importlib.util
        sys.modules.setdefault("unreal", mock.MagicMock())
        spec = importlib.util.spec_from_file_location("ensure_bk56", ROOT / "Scripts/Editor/ensure_bk56_60_sevarog_initial_phase.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        class MockAnimSequence:
            def __init__(self, path, addr):
                self.path = path
                self.addr = addr
            def get_path_name(self):
                return self.path
            def __str__(self):
                return f"<Object '{self.path}' ({self.addr}) Class 'AnimSequence'>"

        class MockVector2D:
            def __init__(self, x, y, addr):
                self.x = x
                self.y = y
                self.addr = addr
            def __str__(self):
                return f"<Struct 'Vector2D' ({self.addr}) {{x: {self.x:.6f}, y: {self.y:.6f}}}>"

        down_clip_run1 = MockAnimSequence("/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown.AN_Boss01_StaggerDown", "0x00000AEF412CB400")
        down_clip_run2 = MockAnimSequence("/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown.AN_Boss01_StaggerDown", "0x00000B1A7C3D8200")
        # stable_value must return canonical path without pointer address
        self.assertEqual(mod.stable_value(down_clip_run1), "/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown.AN_Boss01_StaggerDown")
        self.assertEqual(mod.stable_value(down_clip_run1), mod.stable_value(down_clip_run2))

        vec_run1 = MockVector2D(6.0, 10.0, "0x00000AEEFE5F5168")
        vec_run2 = MockVector2D(6.0, 10.0, "0x00000B99AA123456")
        self.assertEqual(mod.stable_value(vec_run1), "<Struct 'Vector2D' {x: 6.000000, y: 10.000000}>")
        self.assertEqual(mod.stable_value(vec_run1), mod.stable_value(vec_run2))



if __name__ == "__main__":
    unittest.main()
