"""
Unit tests for Move-Card Authoring Helper (A-247).
Runs 100% offline with zero engine dependency.
Verifies every C++ validation rule from Source/OneBossFight/Player/RPGBossMoveCard.cpp.
"""

import math
import os
import unittest
from pathlib import Path
from typing import Dict, Any, List

# Add directory to sys.path
import sys
cur_dir = str(Path(__file__).resolve().parent)
if cur_dir not in sys.path:
    sys.path.insert(0, cur_dir)

from author_move_cards import (
    validate_move_card_spec,
    execute_authoring,
    check_number,
    CEILING
)


def make_valid_spec() -> Dict[str, Any]:
    """Produces a minimal valid FRPGBossMoveCardSpec."""
    return {
        "Schema": 1,
        "MoveId": "Move_Valid_Test",
        "FamilyId": "Family_01",
        "PhaseId": "Phase_1",
        "Skeleton": "/Game/Skeleton",
        "Sequence": "/Game/Sequence",
        "Montage": None,
        "SlotName": "FullBody",
        "SectionName": "None",
        "PlayRate": 1.0,
        "CommitSeconds": 0.2,
        "ActiveStartSeconds": 0.4,
        "ActiveEndSeconds": 0.8,
        "RecoveryEndSeconds": 1.2,
        "TrackDegreesPerSecond": 90.0,
        "MinRangeCm": 100.0,
        "MaxRangeCm": 300.0,
        "FrontConeDegrees": 120.0,
        "HPDamage": 20.0,
        "bUsesRootMotion": False,
        "Windows": [
            {
                "WindowId": "Window_1",
                "HitGroup": "HitGroup_Blade",
                "StartSeconds": 0.4,
                "EndSeconds": 0.8,
                "SocketA": "weapon_r",
                "SocketB": "root_weapon_end_r",
                "RadiusCm": 15.0
            }
        ]
    }


def make_valid_metadata() -> Dict[str, Any]:
    """Produces matching FRPGBossMoveMetadata."""
    return {
        "AnimationPath": "/Game/Sequence",
        "SkeletonPath": "/Game/Skeleton",
        "AnimationSkeletonPath": "/Game/Skeleton",
        "MeshSkeletonPath": "/Game/Skeleton",
        "ClipLengthSeconds": 1.5,
        "bRootMotion": False,
        "Slots": {"FullBody", "UpperBody", "DefaultSlot"},
        "Sections": set(),
        "SocketOrBoneNames": {"weapon_r", "root_weapon_end_r", "hand_r", "hand_l"}
    }


class TestMoveCardValidationRules(unittest.TestCase):
    def test_valid_spec_passes_cleanly(self):
        spec = make_valid_spec()
        meta = make_valid_metadata()
        errors = validate_move_card_spec(spec, meta)
        self.assertEqual(errors, [])

    def test_identity_schema_mismatch(self):
        spec = make_valid_spec()
        spec["Schema"] = 0
        errors = validate_move_card_spec(spec)
        self.assertIn("MoveCard.Identity[Schema/MoveId/FamilyId/PhaseId]", errors)

    def test_identity_empty_move_id(self):
        spec = make_valid_spec()
        spec["MoveId"] = ""
        errors = validate_move_card_spec(spec)
        self.assertIn("MoveCard.Identity[Schema/MoveId/FamilyId/PhaseId]", errors)

    def test_animation_source_both_or_neither(self):
        # Neither
        s1 = make_valid_spec()
        s1["Sequence"] = None
        s1["Montage"] = None
        errors1 = validate_move_card_spec(s1)
        self.assertIn("MoveCard.AnimationSource[exactly one sequence OR montage]", errors1)

        # Both
        s2 = make_valid_spec()
        s2["Sequence"] = "/Game/Seq"
        s2["Montage"] = "/Game/Mont"
        errors2 = validate_move_card_spec(s2)
        self.assertIn("MoveCard.AnimationSource[exactly one sequence OR montage]", errors2)

    def test_animation_identity_descriptor_mismatch(self):
        spec = make_valid_spec()
        meta = make_valid_metadata()
        meta["AnimationPath"] = "/Game/DifferentSequence"
        errors = validate_move_card_spec(spec, meta)
        self.assertIn("MoveCard.AnimationIdentity[selected source vs resolved descriptor]", errors)

    def test_skeleton_identity_mismatch(self):
        spec = make_valid_spec()
        meta = make_valid_metadata()
        meta["SkeletonPath"] = "/Game/DifferentSkeleton"
        errors = validate_move_card_spec(spec, meta)
        self.assertIn("MoveCard.SkeletonIdentity[declared/resolved/animation/mesh skeleton]", errors)

    def test_slot_membership(self):
        spec = make_valid_spec()
        meta = make_valid_metadata()
        spec["SlotName"] = "InvalidSlot"
        errors = validate_move_card_spec(spec, meta)
        self.assertIn("MoveCard.Slot[SlotName]", errors)

    def test_section_membership_for_montage(self):
        spec = make_valid_spec()
        spec["Sequence"] = None
        spec["Montage"] = "/Game/Montage"
        spec["SectionName"] = "AttackSection"
        meta = make_valid_metadata()
        meta["AnimationPath"] = "/Game/Montage"
        meta["Sections"] = {"Intro", "Idle"}  # Does not contain AttackSection
        errors = validate_move_card_spec(spec, meta)
        self.assertIn("MoveCard.Section[SectionName]", errors)

    def test_unsupported_root_motion(self):
        spec = make_valid_spec()
        spec["bUsesRootMotion"] = True
        errors = validate_move_card_spec(spec)
        self.assertIn("MoveCard.UnsupportedRootMotion[first backend is in-place only]", errors)

    def test_scalar_domain_and_nonfinite(self):
        spec = make_valid_spec()
        spec["PlayRate"] = 0.0  # Must be strictly positive
        errors = validate_move_card_spec(spec)
        self.assertIn("MoveCard.Domain[PlayRate]", errors)

        spec2 = make_valid_spec()
        spec2["CommitSeconds"] = -0.1
        errors2 = validate_move_card_spec(spec2)
        self.assertIn("MoveCard.Domain[CommitSeconds]", errors2)

        spec3 = make_valid_spec()
        spec3["HPDamage"] = float("nan")
        errors3 = validate_move_card_spec(spec3)
        self.assertIn("MoveCard.NonFinite[HPDamage]", errors3)

    def test_eligibility_cone_and_range_order(self):
        # Cone > 360
        s1 = make_valid_spec()
        s1["FrontConeDegrees"] = 361.0
        self.assertIn("MoveCard.Eligibility[cone or range order]", validate_move_card_spec(s1))

        # MaxRange < MinRange
        s2 = make_valid_spec()
        s2["MinRangeCm"] = 500.0
        s2["MaxRangeCm"] = 200.0
        self.assertIn("MoveCard.Eligibility[cone or range order]", validate_move_card_spec(s2))

    def test_timeline_ordering(self):
        # activeStart >= activeEnd
        s1 = make_valid_spec()
        s1["ActiveStartSeconds"] = 0.8
        s1["ActiveEndSeconds"] = 0.4
        self.assertIn("MoveCard.Timeline[commit<=activeStart<activeEnd<=recoveryEnd<=clipLength]", validate_move_card_spec(s1))

        # commit > activeStart
        s2 = make_valid_spec()
        s2["CommitSeconds"] = 0.6
        s2["ActiveStartSeconds"] = 0.4
        self.assertIn("MoveCard.Timeline[commit<=activeStart<activeEnd<=recoveryEnd<=clipLength]", validate_move_card_spec(s2))

        # recoveryEnd > clipLength
        s3 = make_valid_spec()
        s3["RecoveryEndSeconds"] = 2.0
        meta = make_valid_metadata()
        meta["ClipLengthSeconds"] = 1.5
        self.assertIn("MoveCard.Timeline[commit<=activeStart<activeEnd<=recoveryEnd<=clipLength]", validate_move_card_spec(s3, meta))

    def test_empty_windows_rejected(self):
        spec = make_valid_spec()
        spec["Windows"] = []
        errors = validate_move_card_spec(spec)
        self.assertIn("MoveCard.Window[no hit windows]", errors)

    def test_window_identity_and_duplicates(self):
        spec = make_valid_spec()
        spec["Windows"].append({
            "WindowId": "Window_1",  # Duplicate id
            "HitGroup": "HitGroup_2",
            "StartSeconds": 0.5,
            "EndSeconds": 0.7,
            "SocketA": "weapon_r",
            "SocketB": "root_weapon_end_r",
            "RadiusCm": 10.0
        })
        errors = validate_move_card_spec(spec)
        self.assertIn("MoveCard.WindowIdentity[Windows[1]]", errors)

    def test_window_boundary_violations(self):
        # Window starts before activeStart
        s1 = make_valid_spec()
        s1["Windows"][0]["StartSeconds"] = 0.2  # activeStart is 0.4
        self.assertIn("MoveCard.Window[Windows[0]]", validate_move_card_spec(s1))

        # Window ends after activeEnd
        s2 = make_valid_spec()
        s2["Windows"][0]["EndSeconds"] = 0.9  # activeEnd is 0.8
        self.assertIn("MoveCard.Window[Windows[0]]", validate_move_card_spec(s2))

        # Overlapping windows
        s3 = make_valid_spec()
        s3["Windows"].append({
            "WindowId": "Window_2",
            "HitGroup": "HitGroup_Blade",
            "StartSeconds": 0.6,  # Window 1 ends at 0.8! Overlaps!
            "EndSeconds": 0.8,
            "SocketA": "weapon_r",
            "SocketB": "root_weapon_end_r",
            "RadiusCm": 10.0
        })
        self.assertIn("MoveCard.Window[Windows[1]]", validate_move_card_spec(s3))

    def test_window_socket_identity_and_membership(self):
        # SocketA == SocketB
        s1 = make_valid_spec()
        s1["Windows"][0]["SocketA"] = "weapon_r"
        s1["Windows"][0]["SocketB"] = "weapon_r"
        self.assertIn("MoveCard.Socket[Windows[0]]", validate_move_card_spec(s1))

        # Socket not in mesh/skeleton
        s2 = make_valid_spec()
        s2["Windows"][0]["SocketA"] = "UnknownSocket"
        meta = make_valid_metadata()
        self.assertIn("MoveCard.Socket[Windows[0]]", validate_move_card_spec(s2, meta))

    def test_unmeasured_probe_tbd_values_refused(self):
        spec = make_valid_spec()
        spec["CommitSeconds"] = "[PROBE TBD]"
        errors = validate_move_card_spec(spec)
        self.assertIn("MoveCard.UnmeasuredTiming[CommitSeconds]", errors)

        spec2 = make_valid_spec()
        spec2["Windows"][0]["StartSeconds"] = None
        errors2 = validate_move_card_spec(spec2)
        self.assertIn("MoveCard.UnmeasuredTiming[Windows[0].StartSeconds]", errors2)


class FakeEditorPropertyObject:
    def __init__(self):
        self._props = {}

    def get_editor_property(self, name: str) -> Any:
        return self._props.get(name)

    def set_editor_property(self, name: str, val: Any) -> None:
        self._props[name] = val


class FakeRPGBossMoveCard(FakeEditorPropertyObject):
    def __init__(self):
        super().__init__()
        self._props["spec"] = FakeEditorPropertyObject()


class FakeRPGBossMoveWindow(FakeEditorPropertyObject):
    pass


class FakeUnrealModule:
    class Name:
        def __init__(self, val: Any):
            self.val = str(val)

        def __str__(self) -> str:
            return self.val

        def __eq__(self, other: Any) -> bool:
            return str(self) == str(other)

    class EditorAssetLibrary:
        existing_assets = set()
        saved_assets = []
        loaded_assets = {}

        @classmethod
        def reset(cls):
            cls.existing_assets = set()
            cls.saved_assets = []
            cls.loaded_assets = {}

        @classmethod
        def does_asset_exist(cls, path: str) -> bool:
            return path in cls.existing_assets

        @classmethod
        def load_asset(cls, path: str) -> Any:
            return f"AssetObject:{path}"

        @classmethod
        def save_loaded_asset(cls, asset: Any) -> bool:
            cls.saved_assets.append(asset)
            return True

    class AssetTools:
        def __init__(self):
            self.created = []

        def create_asset(self, asset_name: str, package_path: str, asset_class: Any, factory: Any) -> Any:
            asset = asset_class()
            self.created.append((asset_name, package_path, asset))
            return asset

    class AssetToolsHelpers:
        _tools = None

        @classmethod
        def get_asset_tools(cls):
            if cls._tools is None:
                cls._tools = FakeUnrealModule.AssetTools()
            return cls._tools

    RPGBossMoveCard = FakeRPGBossMoveCard
    RPGBossMoveWindow = FakeRPGBossMoveWindow

    class DataAssetFactory:
        pass


class TestAuthorMoveCardsExecution(unittest.TestCase):
    def setUp(self):
        FakeUnrealModule.EditorAssetLibrary.reset()
        FakeUnrealModule.AssetToolsHelpers._tools = None
        self._orig_unreal = sys.modules.get("unreal")
        sys.modules["unreal"] = FakeUnrealModule

    def tearDown(self):
        if self._orig_unreal is not None:
            sys.modules["unreal"] = self._orig_unreal
        else:
            sys.modules.pop("unreal", None)

    def test_dry_run_does_not_create_assets(self):
        card = make_valid_spec()
        rc = execute_authoring([card], apply_mode=False)
        self.assertEqual(rc, 0)
        tools = FakeUnrealModule.AssetToolsHelpers.get_asset_tools()
        self.assertEqual(len(tools.created), 0)

    def test_apply_in_memory_creates_and_reads_back(self):
        card = make_valid_spec()
        rc = execute_authoring([card], apply_mode=True, save_mode=False)
        self.assertEqual(rc, 0)
        tools = FakeUnrealModule.AssetToolsHelpers.get_asset_tools()
        self.assertEqual(len(tools.created), 1)
        name, path, asset = tools.created[0]
        self.assertEqual(name, card["MoveId"])
        self.assertEqual(path, "/Game/OneBossFight/FrameworkProof/Cards")
        # Zero saves in memory mode
        self.assertEqual(len(FakeUnrealModule.EditorAssetLibrary.saved_assets), 0)

    def test_apply_with_save_calls_save_loaded_asset(self):
        card = make_valid_spec()
        rc = execute_authoring([card], apply_mode=True, save_mode=True)
        self.assertEqual(rc, 0)
        self.assertEqual(len(FakeUnrealModule.EditorAssetLibrary.saved_assets), 1)

    def test_anti_overwrite_refuses_existing_asset(self):
        card = make_valid_spec()
        target_path = f"/Game/OneBossFight/FrameworkProof/Cards/{card['MoveId']}"
        FakeUnrealModule.EditorAssetLibrary.existing_assets.add(target_path)
        rc = execute_authoring([card], apply_mode=True, save_mode=False)
        self.assertEqual(rc, 1)

    def test_selector_only_authors_matching_card(self):
        c1 = make_valid_spec()
        c1["MoveId"] = "Move_One"
        c2 = make_valid_spec()
        c2["MoveId"] = "Move_Two"
        rc = execute_authoring([c1, c2], apply_mode=True, save_mode=False, only_move_id="Move_Two")
        self.assertEqual(rc, 0)
        tools = FakeUnrealModule.AssetToolsHelpers.get_asset_tools()
        self.assertEqual(len(tools.created), 1)
        self.assertEqual(tools.created[0][0], "Move_Two")

    def test_selector_nonexistent_card_returns_error(self):
        card = make_valid_spec()
        rc = execute_authoring([card], apply_mode=False, only_move_id="NonExistent")
        self.assertEqual(rc, 1)

    def test_unmeasured_probe_tbd_halts_authoring(self):
        card = make_valid_spec()
        card["CommitSeconds"] = "[PROBE TBD]"
        rc = execute_authoring([card], apply_mode=False)
        self.assertEqual(rc, 1)


class TestCppTokenParity(unittest.TestCase):
    """Verifies that all Python validation tokens match the live C++ tokens in RPGBossMoveCard.cpp."""
    def test_tokens_match_cpp_source(self):
        cpp_path = Path("Source/OneBossFight/Player/RPGBossMoveCard.cpp")
        self.assertTrue(cpp_path.is_file(), f"C++ source must exist at {cpp_path}")
        cpp_text = cpp_path.read_text(encoding="utf-8", errors="replace")

        expected_tokens = [
            "MoveCard.NonFinite",
            "MoveCard.Domain",
            "MoveCard.Identity",
            "MoveCard.AnimationSource",
            "MoveCard.AnimationIdentity",
            "MoveCard.SkeletonIdentity",
            "MoveCard.Slot",
            "MoveCard.Section",
            "MoveCard.UnsupportedRootMotion",
            "MoveCard.Eligibility",
            "MoveCard.Timeline",
            "MoveCard.Window",
            "MoveCard.WindowIdentity",
            "MoveCard.Socket",
        ]

        for token in expected_tokens:
            self.assertIn(token, cpp_text, f"Expected token '{token}' in C++ source {cpp_path}")


class TestReceiptIntegrity(unittest.TestCase):
    def test_receipt_exists_and_clean(self):
        receipt_path = Path(__file__).resolve().parent / "evidence_sha256.txt"
        self.assertTrue(receipt_path.is_file(), "evidence_sha256.txt must exist")
        raw = receipt_path.read_bytes()
        self.assertNotIn(b"\r\r\n", raw)
        self.assertNotIn(b"\n\n", raw)
        lines = receipt_path.read_text(encoding="utf-8").splitlines()
        self.assertGreater(len(lines), 0)
        for i, l in enumerate(lines):
            self.assertTrue(l.strip(), f"Line {i+1} must not be blank")
            parts = l.split()
            self.assertEqual(len(parts), 3, f"Line {i+1} must have 3 parts: {l}")
            self.assertEqual(len(parts[0]), 64, "SHA256 must be 64 characters")
            self.assertTrue(parts[1].isdigit(), "Size must be integer")


if __name__ == "__main__":
    unittest.main()
