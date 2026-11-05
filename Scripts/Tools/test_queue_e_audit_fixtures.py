"""Offline fixtures tying Queue E audit summaries to their source evidence."""
import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_project_file(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


class QueueEAuditFixtures(unittest.TestCase):
    def test_e66_editor_inventory_paths_and_parse_exception_are_preserved(self):
        index = ROOT / "Documentation/Boss/EDITOR_PYTHON_COMMAND_INDEX_D89.csv"
        with index.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertTrue(rows)
        paths = [row["script"] for row in rows]
        self.assertEqual(len(paths), len(set(paths)), "duplicate inventory rows")
        self.assertTrue(all((ROOT / path).is_file() for path in paths), "inventory contains a missing script")
        self.assertTrue(any(row["parse_status"] != "PARSES" for row in rows), "known parse exception disappeared")

    def test_e67_editor_dry_run_modes_remain_explicitly_default_off(self):
        paths = (
            "Scripts/Editor/retarget_pack_to_greystone.py",
            "Scripts/Editor/poise_data.py",
            "Scripts/Editor/repoint_player_refs.py",
        )
        for path in paths:
            with self.subTest(path=path):
                source = read_project_file(path)
                self.assertRegex(source, r"(?m)^DRY\s*=\s*False\s*$")
                self.assertIn("if DRY", source)

    def test_e68_finite_rule_fixes_and_remaining_witness_are_distinguished(self):
        leash = read_project_file("Source/OneBossFight/Player/RPGBossLeashRules.h")
        flask = read_project_file("Source/OneBossFight/UI/RPGFlaskHudRules.h")
        hud_tests = read_project_file("Source/OneBossFight/Tests/RPGFlaskHudTests.cpp")
        witnesses = read_project_file("Source/OneBossFight/Tests/RPGBossFiniteRuleOverflowWitnessTests.cpp")
        self.assertIn("FMath::IsFinite(RadiusCm)", leash)
        self.assertIn("static_cast<int64>(Count) * 3", flask)
        self.assertIn("large maximum does not overflow", hud_tests)
        self.assertIn("YawProbePositiveOverflowWitness", witnesses)
        self.assertIn("fail closed to neutral yaw", witnesses)

    def test_e69_scaler_reciprocal_boundaries_are_separate_from_nonfinite_cases(self):
        source = read_project_file("Source/OneBossFight/Player/RPGDamageScale.h")
        reciprocal = read_project_file("Source/OneBossFight/Tests/RPGDamageScalerReciprocalBoundaryTests.cpp")
        nonfinite = read_project_file("Source/OneBossFight/Tests/RPGBossDamageBleedFiniteInputTests.cpp")
        self.assertIn("<= Window", source)
        self.assertIn("one representable instant beyond", reciprocal)
        self.assertIn("NonfiniteLoss", nonfinite)
        self.assertIn("ApplyNonfiniteInputs", nonfinite)

    def test_e70_bleed_overflow_regression_is_distinct_from_ordinary_coverage(self):
        rules = read_project_file("Source/OneBossFight/Player/RPGBleedRules.h")
        saturation = read_project_file("Source/OneBossFight/Tests/RPGCodexTests.cpp")
        extreme = read_project_file("Source/OneBossFight/Tests/RPGBossDamageBleedFiniteInputTests.cpp")
        ordinary = read_project_file("Source/OneBossFight/Tests/RPGBleedRulesPropertyTests.cpp")
        self.assertIn("State.Procs < MAX_int32", rules)
        self.assertIn("Saturated.Procs = MAX_int32", saturation)
        self.assertIn("remains at MAX_int32", saturation)
        self.assertIn("ExtremeFiniteBuildup", extreme)
        self.assertIn("10000", ordinary)


if __name__ == "__main__":
    unittest.main()
