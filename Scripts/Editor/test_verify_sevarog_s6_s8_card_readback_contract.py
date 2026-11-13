"""BQ-41..44 static contract for verify_sevarog_s6_s8_card_readback.py (no Unreal, no editor, no asset access).

1. Read-only: the readback never calls a setter, save, delete, duplicate, rename or create API.
2. Drift: every EXPECTED value equals what author_sevarog_draft_cards.build_candidate_specs authors, so the readback and the
   author script cannot silently disagree.
3. The pure values_match comparison (names, bools, float32 tolerance, non-finite refusal).
"""
import ast
import importlib.util
import math
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
READBACK = HERE / "verify_sevarog_s6_s8_card_readback.py"
AUTHOR = HERE / "author_sevarog_draft_cards.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReadbackContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = READBACK.read_text(encoding="utf-8")
        cls.readback = load(READBACK, "sevarog_s6_s8_readback")  # module import must not need Unreal
        author = load(AUTHOR, "sevarog_author_for_readback")
        rows = author.build_candidate_specs(author.read_f5_cards(ROOT))
        cls.by_id = {row["move_id"]: row for row in rows}

    def test_read_only_calls(self):
        tree = ast.parse(self.source)
        called = {node.func.attr for node in ast.walk(tree)
                  if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        forbidden = {"set_editor_property", "save_asset", "save_loaded_asset", "save_package", "delete_asset",
                     "duplicate_asset", "rename_asset", "create_asset", "save_directory", "modify"}
        self.assertEqual(called & forbidden, set())
        self.assertIn("get_editor_property", called)
        self.assertIn("load_asset", called)

    def test_unreal_import_is_inside_main_only(self):
        tree = ast.parse(self.source)
        top_level = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.assertFalse(any(a.name == "unreal" for n in top_level for a in getattr(n, "names", [])))

    def test_expected_values_match_the_author_script(self):
        for asset_name, expected in self.readback.EXPECTED.items():
            row = self.by_id[expected["spec"]["move_id"]]
            self.assertEqual(row["asset_name"], asset_name)
            for field, want in expected["spec"].items():
                self.assertEqual(row[field], want, "%s.%s" % (asset_name, field))
            self.assertEqual(len(row["windows"]), expected["window_count"], asset_name)
            for index, window in enumerate(expected.get("windows", [])):
                for field, want in window.items():
                    self.assertEqual(row["windows"][index][field], want,
                                     "%s.windows[%d].%s" % (asset_name, index, field))
            if "additional_phase_ids" in expected:
                self.assertEqual(row["additional_phase_ids"], expected["additional_phase_ids"])
            for struct in ("area_effect", "channel_drain"):
                want = dict(expected[struct])
                enabled = want.pop("enabled")
                self.assertEqual(row[struct] is not None, enabled, "%s.%s enabled" % (asset_name, struct))
                if enabled:
                    self.assertEqual(row[struct], want, "%s.%s values" % (asset_name, struct))

    def test_covers_exactly_s6_s7_s8(self):
        self.assertEqual(sorted(e["spec"]["move_id"] for e in self.readback.EXPECTED.values()),
                         sorted(["Move_Sevarog_Ultimate_Swing_120fps_C1277", "Move_Sevarog_Subjugation_C1277",
                                 "Move_Sevarog_Soul_Siphon_C1277"]))

    def test_values_match(self):
        match = self.readback.values_match
        self.assertTrue(match(0.6669999957084656, 0.667))   # float32 round trip
        self.assertFalse(match(0.668, 0.667))
        self.assertTrue(match(True, True))
        self.assertFalse(match(1, True))                    # an int is not a bool
        self.assertFalse(match(math.nan, 0.5))
        self.assertFalse(match("x", 1.0))
        self.assertTrue(match([], []))
        self.assertFalse(match(["unexpected"], []))
        self.assertTrue(match("Phase_2", "Phase_2"))

    def test_terminal_markers(self):
        for marker in ("RESULT=PASS cards=%d saves=0", "RESULT=FAIL", "CARD %s move=%s"):
            self.assertIn(marker, self.source)


if __name__ == "__main__":
    unittest.main()
