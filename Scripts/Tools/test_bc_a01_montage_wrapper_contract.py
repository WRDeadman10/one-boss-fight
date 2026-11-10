#!/usr/bin/env python3
"""Offline contract test (BC-A01..A02) for URPGMontageWrapperLibrary."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEADER_PATH = ROOT / "Source" / "OneBossFightEditor" / "Public" / "RPGMontageWrapperLibrary.h"
CPP_PATH = ROOT / "Source" / "OneBossFightEditor" / "Private" / "RPGMontageWrapperLibrary.cpp"
TEST_CPP_PATH = ROOT / "Source" / "OneBossFightEditor" / "Private" / "Tests" / "RPGMontageWrapperLibraryTests.cpp"
SWITCH_PLAN_PATH = ROOT / "Documentation" / "Boss" / "SWITCH_PLAN.md"


class BcA01MontageWrapperContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.header = HEADER_PATH.read_text(encoding="utf-8")
        self.cpp = CPP_PATH.read_text(encoding="utf-8")
        self.test_cpp = TEST_CPP_PATH.read_text(encoding="utf-8")
        self.switch_plan = SWITCH_PLAN_PATH.read_text(encoding="utf-8")

    def test_editor_only_api_and_strict_greystone_allowlist(self) -> None:
        self.assertIn("ONEBOSSFIGHTEDITOR_API URPGMontageWrapperLibrary", self.header)
        self.assertIn("static UAnimMontage* CreateRetargetWrapper(", self.header)
        self.assertIn('GreystoneRoot[] = TEXT("/Game/OneBossFight/Player/Greystone/")', self.cpp)
        self.assertIn("PackagePath.StartsWith(GreystoneRoot, ESearchCase::CaseSensitive)", self.cpp)
        self.assertIn("FPackageName::IsValidLongPackageName(PackagePath)", self.cpp)

    def test_all_fail_closed_refusal_guards_present(self) -> None:
        required_tokens = (
            "MontageWrapper.NotGameThread",
            "MontageWrapper.RequiredObject",
            "MontageWrapper.PackagePathOutsideGreystoneAllowlist",
            "MontageWrapper.TargetSkeletonMismatch",
            "MontageWrapper.SourceHasNoSlotTracks",
            "MontageWrapper.TargetShorterThanLastNotify",
            "MontageWrapper.DestinationAlreadyExists",
            "MontageWrapper.SourceHasNoSegments",
        )
        for token in required_tokens:
            self.assertIn(token, self.cpp, f"Missing guard token: {token}")
        self.assertIn("DuplicateObject<UAnimMontage>(Source, Outer, AssetName", self.cpp)
        self.assertIn("Segment.SetAnimReference(TargetSequence, false)", self.cpp)
        # Ensure wrapper library never saves or mutates source/pack assets
        self.assertNotIn("SavePackage", self.cpp)
        self.assertIn("OneBossFight.Editor.MontageWrapper.SyntheticCopyAndGuards", self.test_cpp)

    def test_switch_plan_reflects_corrected_backstep_source_timings(self) -> None:
        self.assertIn("0.091–0.414 s", self.switch_plan)
        self.assertIn("duration 0.323", self.switch_plan)
        self.assertIn("0.198–0.567 s", self.switch_plan)


if __name__ == "__main__":
    unittest.main()
