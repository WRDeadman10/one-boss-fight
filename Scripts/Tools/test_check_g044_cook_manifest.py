#!/usr/bin/env python3
"""Offline fixtures for the G044 cooked package manifest comparator."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

MODULE = Path(__file__).with_name("check_g044_cook_manifest.py")
SPEC = importlib.util.spec_from_file_location("check_g044_cook_manifest", MODULE)
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


class CookManifestTests(unittest.TestCase):
    def test_all_required_paths_are_present(self):
        self.assertEqual(CHECKER.compare({"/game/data/a", "/game/data/b"}, {"/game/data/a", "/game/data/b", "/game/extra"}), [])

    def test_missing_path_is_reported(self):
        self.assertEqual(CHECKER.compare({"/game/data/a", "/game/data/b"}, {"/game/data/a"}), ["/game/data/b"])

    def test_extensions_and_case_normalize(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            required = root / "required.txt"
            manifest = root / "manifest.txt"
            required.write_text("/Game/OneBossFight/Data/DA_Test.DA_Test\n", encoding="utf-8")
            manifest.write_text("Cooked package: /game/onebossfight/data/da_test.uasset\n", encoding="utf-8")
            self.assertEqual(CHECKER.compare(CHECKER.read_required(required), CHECKER.read_cooked(manifest)), [])

    def test_editor_only_folder_excludes_only_component_bounded_missing_paths(self):
        required = {
            "/game/characters/mannequins/rigs/poses/quinn/pose_a",
            "/game/characters/mannequins/rigs/poses/quinn/pose_b",
            "/game/characters/mannequins/rigs/poses/quinnplus/pose_c",
            "/game/data/required",
        }
        cooked = {"/game/data/required"}
        missing, excluded = CHECKER.compare_with_editor_only_folders(
            required,
            cooked,
            ["/Game/Characters/Mannequins/Rigs/Poses/Quinn/"],
        )
        self.assertEqual(
            excluded,
            [
                "/game/characters/mannequins/rigs/poses/quinn/pose_a",
                "/game/characters/mannequins/rigs/poses/quinn/pose_b",
            ],
        )
        self.assertEqual(
            missing,
            [
                "/game/characters/mannequins/rigs/poses/quinnplus/pose_c",
            ],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
