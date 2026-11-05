#!/usr/bin/env python3
"""Offline fixtures for the G044 cooked package manifest comparator."""
import importlib.util
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

MODULE = Path(__file__).with_name("check_g044_cook_manifest.py")
SPEC = importlib.util.spec_from_file_location("check_g044_cook_manifest", MODULE)
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


def normalized_manifest():
    roots = {
        "selection": "/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter",
        "boss": "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft",
        "player": "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3",
    }
    return {"schema": CHECKER.NORMALIZED_SCHEMA, "build_id": "BUILD-222", "configuration": "Shipping",
            "root_packages": roots, "packages": list(roots.values()) + ["/Game/OneBossFight/Data/DA_Extra"],
            "source_manifest_sha256": "a" * 64}


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
            "/game/characters/mannequins/rigs/poses/quinn",
            "/game/characters/mannequins/rigs/poses/quinn/pose_a",
            "/game/characters/mannequins/rigs/poses/quinn/pose_b",
            "/game/characters/mannequins/rigs/poses/quinnplus/pose_c",
            "/game/data/required",
            "/game/unrelated/asset",
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
                "/game/characters/mannequins/rigs/poses/quinn",
                "/game/characters/mannequins/rigs/poses/quinn/pose_a",
                "/game/characters/mannequins/rigs/poses/quinn/pose_b",
            ],
        )
        self.assertEqual(
            missing,
            [
                "/game/characters/mannequins/rigs/poses/quinnplus/pose_c",
                "/game/unrelated/asset",
            ],
        )

    def test_normalized_manifest_requires_three_distinct_roots_and_valid_packages(self):
        value = normalized_manifest()
        required = {CHECKER.package_path(path) for path in value["root_packages"].values()}
        cooked, issues, roots = CHECKER.validate_normalized_manifest(value, required)
        self.assertEqual(issues, [])
        self.assertEqual(set(roots), {"selection", "boss", "player"})
        self.assertTrue(required <= cooked)

    def test_normalized_manifest_rejects_missing_root_identity_and_object_path(self):
        value = normalized_manifest()
        del value["root_packages"]["player"]
        value["packages"][0] = "/Game/Bad/DA_Asset.DA_Asset"
        _, issues, _ = CHECKER.validate_normalized_manifest(value)
        self.assertTrue(any("exactly selection, boss, and player" in issue for issue in issues))
        self.assertTrue(any("without an object suffix" in issue for issue in issues))

    def test_normalized_manifest_refuses_root_absent_from_inventory_and_duplicate_packages(self):
        value = normalized_manifest()
        value["packages"].remove(value["root_packages"]["boss"])
        value["packages"].append(value["packages"][0])
        _, issues, _ = CHECKER.validate_normalized_manifest(value)
        self.assertTrue(any("root boss is not present in packages" in issue for issue in issues))
        self.assertTrue(any("duplicate path" in issue for issue in issues))

    def test_json_summary_is_deterministic_and_carries_input_hashes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            required_file = root / "required.txt"
            manifest_file = root / "manifest.txt"
            required_file.write_text("/Game/Data/A\n", encoding="utf-8")
            manifest_file.write_text("/Game/Data/A\n", encoding="utf-8")
            required = CHECKER.read_required(required_file)
            cooked = CHECKER.read_cooked(manifest_file)
            first = CHECKER.build_summary(required, cooked, [], [], required_file, manifest_file)
            second = CHECKER.build_summary(required, cooked, [], [], required_file, manifest_file)
            self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
            self.assertEqual(first["verdict"], "PASS")
            self.assertEqual(set(first["input_sha256"]), {"required", "manifest"})

    def test_cli_json_emits_stable_hashed_summary(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            required = root / "required.txt"
            manifest = root / "cook.log"
            required.write_text("/Game/Data/A\n", encoding="utf-8")
            manifest.write_text("Cooked: /Game/Data/A.uasset\n", encoding="utf-8")
            stdout = io.StringIO()
            argv = ["check_g044_cook_manifest.py", "--required", str(required), "--manifest", str(manifest), "--json"]
            with contextlib.redirect_stdout(stdout), mock.patch.object(sys, "argv", argv):
                self.assertEqual(CHECKER.main(), 0)
            value = json.loads(stdout.getvalue())
            self.assertEqual(value["schema"], CHECKER.COMPARISON_SCHEMA)
            self.assertEqual(value["verdict"], "PASS")
            self.assertEqual(value["input_sha256"]["manifest"], CHECKER.sha256_file(manifest))

    def test_cli_validates_normalized_root_manifest_before_comparing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            value = normalized_manifest()
            required = root / "required.txt"
            manifest = root / "normalized.json"
            required.write_text("\n".join(value["root_packages"].values()) + "\n", encoding="utf-8")
            manifest.write_text(json.dumps(value), encoding="utf-8")
            stdout = io.StringIO()
            argv = ["check_g044_cook_manifest.py", "--required", str(required), "--normalized-manifest", str(manifest), "--json"]
            with contextlib.redirect_stdout(stdout), mock.patch.object(sys, "argv", argv):
                self.assertEqual(CHECKER.main(), 0)
            result = json.loads(stdout.getvalue())
            self.assertEqual(result["manifest_identity"]["configuration"], "Shipping")
            value["root_packages"].pop("player")
            manifest.write_text(json.dumps(value), encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr), mock.patch.object(sys, "argv", argv):
                self.assertEqual(CHECKER.main(), 2)
            self.assertIn("exactly selection, boss, and player", stderr.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
