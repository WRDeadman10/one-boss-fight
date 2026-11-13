"""Pure preflight contracts for authored MoveCard numeric and phase inputs."""
import importlib.util
import math
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "Editor" / "author_sevarog_draft_cards.py"
SPEC = importlib.util.spec_from_file_location("author_sevarog_draft_cards", SCRIPT)
AUTHOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUTHOR)


class MoveCardPreflightContract(unittest.TestCase):
    def test_authored_candidate_rows_have_exact_ids_and_clear_static_preflight(self):
        cards = AUTHOR.read_f5_cards(ROOT)
        rows = AUTHOR.build_candidate_specs(cards)
        AUTHOR.apply_approved_s1_s2_ranges(rows)
        self.assertEqual(
            [row["move_id"] for row in rows],
            [
                "Move_Sevarog_Swing1_Medium",
                "Move_Sevarog_Swing2_Medium",
                "Move_Sevarog_Swing3_Slow",
                "Move_Sevarog_Speedburst",
                "Move_Sevarog_Swing1_FAST_v2",
                "Move_Sevarog_Ultimate_Swing_120fps_C1277",
                "Move_Sevarog_Subjugation_C1277",
                "Move_Sevarog_Soul_Siphon_C1277",
            ],
        )
        self.assertEqual(AUTHOR.unresolved_gates(rows), [])
        for row in rows:
            self.assertIsNone(AUTHOR.phase_membership_error(row), row["move_id"])
            for name, value in row.items():
                if name.endswith(("_seconds", "_cm", "_degrees")) and value is not None:
                    AUTHOR.is_finite_nonnegative(value, row["move_id"] + "." + name)
            for addon in (row["area_effect"], row["channel_drain"]):
                if addon:
                    for name, value in addon.items():
                        if name != "track_facing_each_tick":
                            AUTHOR.is_finite_nonnegative(value, row["move_id"] + "." + name)

    def test_numeric_ceiling_matches_cpp_and_refuses_nonfinite_or_unrepresentable(self):
        for value in (0, 1, 1_000_000):
            AUTHOR.is_finite_nonnegative(value, "fixture")
        for value in (-1, 1_000_001, math.nan, math.inf, -math.inf, 10**1000, True, "1"):
            with self.subTest(value=repr(value)):
                with self.assertRaises(AUTHOR.Refusal):
                    AUTHOR.is_finite_nonnegative(value, "fixture")

    def test_phase_membership_rejects_mixed_invalid_sets(self):
        valid = {"phase_id": "Phase_1", "additional_phase_ids": ["Phase_2"]}
        self.assertIsNone(AUTHOR.phase_membership_error(valid))
        invalid = (
            {"phase_id": "Phase_1", "additional_phase_ids": ["Phase_1"]},
            {"phase_id": "Phase_1", "additional_phase_ids": ["Phase_2", ""]},
            {"phase_id": "Phase_1", "additional_phase_ids": ["Phase_2", "Phase_2"]},
            {"phase_id": "Phase_1", "additional_phase_ids": ["A", "B", "C", "D", "E"]},
            {"phase_id": "", "additional_phase_ids": []},
            {"phase_id": "Phase_1", "additional_phase_ids": "Phase_2"},
        )
        for row in invalid:
            with self.subTest(row=row):
                self.assertTrue(AUTHOR.phase_membership_error(row))


if __name__ == "__main__":
    unittest.main()
