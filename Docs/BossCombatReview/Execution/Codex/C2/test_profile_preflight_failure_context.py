"""Execute the selected-profile C2 action against a fake invalid profile."""
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
REVIEWS = ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews"
sys.path.insert(0, str(REVIEWS))
from test_validate_boss_config import get_sevarog_f10_valid_config


class FakePathAsset:
    def __init__(self, path):
        self.path = path

    def get_path_name(self):
        return self.path


class FakeSequence(FakePathAsset):
    def get_play_length(self):
        return 2.2


class FakeTransform:
    translation = types.SimpleNamespace(x=0.0, y=0.0, z=-165.0)
    scale3d = types.SimpleNamespace(x=1.0, y=1.0, z=1.0)


class FakeSpec:
    def __init__(self, spec):
        self.values = {
            "move_id": spec["MoveId"], "phase_id": spec["PhaseId"],
            "min_range_cm": spec["MinRangeCm"], "max_range_cm": spec["MaxRangeCm"],
            "active_start_seconds": spec["ActiveStartSeconds"], "recovery_end_seconds": spec["RecoveryEndSeconds"],
            "hp_damage": spec["HPDamage"], "max_vertical_delta_cm": spec.get("MaxVerticalDeltaCm", 0.0),
            "sequence": FakeSequence("/Game/Test/Sequence.Sequence"),
        }

    def get_editor_property(self, name):
        return self.values[name]


class FakeCard(FakePathAsset):
    def __init__(self, spec):
        super().__init__("/Game/Test/DA_Card.DA_Card")
        self.spec = FakeSpec(spec)

    def get_editor_property(self, name):
        if name == "spec":
            return self.spec
        raise AssertionError(name)


class FakeCardEntry:
    def __init__(self, item):
        self.card = FakeCard(item["spec"])
        self.item = item

    def get_editor_property(self, name):
        return self.card if name == "card" else self.item[name]


class FakeProfile:
    def __init__(self, config, invalid_band=True):
        self.config = dict(config)
        if invalid_band:
            self.config["band_min_cm"] = self.config["band_max_cm"]  # Invalid ordered band.
        self.values = {
            "fixture_label": self.config["fixture_label"], "damage_enabled": self.config["damage_enabled"],
            "mesh": FakePathAsset(self.config["mesh_path"]), "anim_class": FakePathAsset(self.config["anim_class_path"]),
            "target_pawn_class": FakePathAsset(self.config["target_pawn_class_path"]),
            "alignment_authored": self.config["alignment_authored"], "phase_two_id": self.config["phase_two_id"],
            "mesh_relative_transform": FakeTransform(), "card": None,
            "cards": [FakeCardEntry(item) for item in self.config["cards"]],
        }
        for key, value in self.config.items():
            self.values.setdefault(key, value)
        for key, value in list(self.values.items()):
            if key.endswith("_cm") or key.endswith("_seconds") or key in {
                "hit_max_substeps", "repeat_memory", "attack_count", "posture_max",
                "posture_regen_per_second", "posture_regen_delay_seconds", "bleed_buildup_per_hit",
                "bleed_initial_threshold", "bleed_threshold_increase", "bleed_threshold_max", "bleed_hp_fraction",
                "boss_max_health", "player_hit_damage", "phase_two_fraction", "repeat_penalty",
                "target_health", "band_min_cm", "band_max_cm", "walk_speed_cm_per_second",
                "acceptance_cm", "walk_timeout_seconds", "blend_in_seconds", "blend_out_seconds",
                "capsule_radius_cm", "capsule_half_height_cm",
            }:
                self.values.setdefault(key, value)

    def get_name(self):
        return "DA_Sevarog_Profile"

    def get_path_name(self):
        return "/Game/OneBossFight/FrameworkProof/DA_Sevarog_Profile.DA_Sevarog_Profile"

    def get_class(self):
        return types.SimpleNamespace(get_name=lambda: "RPGBossFrameworkProfile")

    def get_editor_property(self, name):
        mapping = {"band_min_cm": "band_min_cm", "band_max_cm": "band_max_cm"}
        return self.values[mapping.get(name, name)]


class ProfilePreflightFailureContextTests(unittest.TestCase):
    def test_selection_change_during_preflight_returns_stale_refusal(self):
        logged = []
        first = FakeProfile(get_sevarog_f10_valid_config(), invalid_band=False)
        replacement = FakeProfile(get_sevarog_f10_valid_config(), invalid_band=False)
        replacement.get_path_name = lambda: "/Game/Test/Other_Profile.Other_Profile"
        selection_reads = iter(([first], [replacement]))
        unreal_stub = types.SimpleNamespace(
            EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda: next(selection_reads)),
            EditorDialog=types.SimpleNamespace(show_message=lambda *args: None),
            AppMsgType=types.SimpleNamespace(OK="OK"), log=logged.append, log_warning=logged.append,
        )
        spec = importlib.util.spec_from_file_location("c2_profile_stale_selection", HERE / "validate_selected_boss_profile.py")
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": unreal_stub}):
            spec.loader.exec_module(module)
        receipt = json.loads(logged[0].split(" ", 1)[1])
        self.assertFalse(receipt["ok"])
        self.assertEqual(receipt["diagnostics"][0]["code"], "Selection.Stale")
        self.assertFalse(receipt["saved"])
        self.assertFalse(receipt["compiled"])

    def test_repeated_valid_preflight_is_idempotent(self):
        logged = []
        profile = FakeProfile(get_sevarog_f10_valid_config(), invalid_band=False)
        original = (profile.values["band_min_cm"], profile.values["band_max_cm"], len(profile.values["cards"]))
        unreal_stub = types.SimpleNamespace(
            EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda: [profile]),
            EditorDialog=types.SimpleNamespace(show_message=lambda *args: None),
            AppMsgType=types.SimpleNamespace(OK="OK"), log=logged.append, log_warning=logged.append,
        )
        for index in range(2):
            spec = importlib.util.spec_from_file_location(f"c2_profile_repeat_{index}", HERE / "validate_selected_boss_profile.py")
            module = importlib.util.module_from_spec(spec)
            with patch.dict(sys.modules, {"unreal": unreal_stub}):
                spec.loader.exec_module(module)
        self.assertEqual(len(logged), 2)
        self.assertEqual(logged[0], logged[1])
        receipts = [json.loads(line.split(" ", 1)[1]) for line in logged]
        self.assertTrue(all(receipt["ok"] and receipt["repeat_safe"] for receipt in receipts))
        self.assertEqual(original, (profile.values["band_min_cm"], profile.values["band_max_cm"], len(profile.values["cards"])))

    def test_valid_selected_profile_succeeds_without_mutating_asset_state(self):
        logged = []
        profile = FakeProfile(get_sevarog_f10_valid_config(), invalid_band=False)
        before = (profile.values["band_min_cm"], profile.values["band_max_cm"], len(profile.values["cards"]))
        unreal_stub = types.SimpleNamespace(
            EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda: [profile]),
            EditorDialog=types.SimpleNamespace(show_message=lambda *args: None),
            AppMsgType=types.SimpleNamespace(OK="OK"), log=logged.append, log_warning=logged.append,
        )
        spec = importlib.util.spec_from_file_location("c2_profile_success_integration", HERE / "validate_selected_boss_profile.py")
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": unreal_stub}):
            spec.loader.exec_module(module)
        after = (profile.values["band_min_cm"], profile.values["band_max_cm"], len(profile.values["cards"]))
        receipt = json.loads(logged[0].split(" ", 1)[1])
        self.assertTrue(receipt["ok"])
        self.assertFalse(receipt["saved"])
        self.assertFalse(receipt["compiled"])
        self.assertEqual(before, after)

    def test_invalid_selected_profile_receipt_preserves_field_and_read_only_flags(self):
        logged = []
        shown = []
        profile = FakeProfile(get_sevarog_f10_valid_config())
        before = (profile.values["band_min_cm"], profile.values["band_max_cm"], len(profile.values["cards"]))
        unreal_stub = types.SimpleNamespace(
            EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda: [profile]),
            EditorDialog=types.SimpleNamespace(show_message=lambda *args: shown.append(args)),
            AppMsgType=types.SimpleNamespace(OK="OK"),
            log=logged.append,
            log_warning=logged.append,
        )
        spec = importlib.util.spec_from_file_location("c2_profile_failure", HERE / "validate_selected_boss_profile.py")
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": unreal_stub}):
            spec.loader.exec_module(module)

        self.assertEqual(len(logged), 1)
        receipt = json.loads(logged[0].split(" ", 1)[1])
        after = (profile.values["band_min_cm"], profile.values["band_max_cm"], len(profile.values["cards"]))
        self.assertFalse(receipt["ok"])
        self.assertEqual(receipt["asset_path"], profile.get_path_name())
        self.assertEqual(receipt["diagnostics"][0]["code"], "Framework.Profile.Geometry")
        self.assertEqual(receipt["diagnostics"][0]["field"], "Profile")
        self.assertFalse(receipt["saved"])
        self.assertFalse(receipt["compiled"])
        self.assertTrue(receipt["repeat_safe"])
        self.assertEqual(before, after, "invalid preflight must not mutate selected asset data")
        self.assertEqual(len(shown), 1)


if __name__ == "__main__":
    unittest.main()
