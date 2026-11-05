#!/usr/bin/env python3
"""Offline fixtures for the opt-in Package.ps1 G044/VFX manifest check."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("check_packaged_g044_cook.py")
SPEC = importlib.util.spec_from_file_location("check_packaged_g044_cook", MODULE_PATH)
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class PackagedG044CookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.content = self.root / "Content"
        vfx = self.content / "OneBossFight" / "VFX"
        vfx.mkdir(parents=True)
        (vfx / "NS_One.uasset").write_bytes(b"fixture")
        (vfx / "Nested").mkdir()
        (vfx / "Nested" / "NS_Two.umap").write_bytes(b"fixture")
        self.required = self.root / "required.txt"
        self.required.write_text("\n".join([
            "/Game/OneBossFight/Data/Selection",
            "/Game/OneBossFight/Data/Boss",
            "/Game/OneBossFight/Data/Player",
        ]) + "\n", encoding="utf-8")
        self.manifest = self.root / "manifest.json"
        self.value = {
            "schema": "onebossfight.g044-cook-manifest/v1",
            "build_id": "BUILD-FIXTURE",
            "configuration": "Development",
            "root_packages": {
                "selection": "/Game/OneBossFight/Data/Selection",
                "boss": "/Game/OneBossFight/Data/Boss",
                "player": "/Game/OneBossFight/Data/Player",
            },
            "packages": [
                "/Game/OneBossFight/Data/Selection",
                "/Game/OneBossFight/Data/Boss",
                "/Game/OneBossFight/Data/Player",
                "/Game/OneBossFight/VFX/NS_One",
                "/Game/OneBossFight/VFX/Nested/NS_Two",
            ],
            "source_manifest_sha256": "a" * 64,
        }

    def tearDown(self):
        self.temp.cleanup()

    def save_manifest(self):
        self.manifest.write_text(json.dumps(self.value), encoding="utf-8")

    def test_passes_when_closure_and_nested_vfx_are_cooked(self):
        self.save_manifest()
        result = CHECK.compare(self.required, self.manifest, "Development", self.content)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["vfx_package_count"], 2)

    def test_fails_when_vfx_package_is_missing(self):
        self.value["packages"].remove("/Game/OneBossFight/VFX/Nested/NS_Two")
        self.save_manifest()
        result = CHECK.compare(self.required, self.manifest, "Development", self.content)
        self.assertEqual(result["missing_vfx"], ["/game/onebossfight/vfx/nested/ns_two"])

    def test_fails_when_required_closure_package_is_missing(self):
        self.value["packages"].remove("/Game/OneBossFight/Data/Boss")
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "root boss is not present"):
            CHECK.compare(self.required, self.manifest, "Development", self.content)

    def test_rejects_manifest_for_different_configuration(self):
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "does not match package Shipping"):
            CHECK.compare(self.required, self.manifest, "Shipping", self.content)

    def test_package_script_wires_optional_check_after_successful_cook(self):
        project = Path(__file__).resolve().parents[2]
        package_script = (project / "Scripts" / "Package.ps1").read_text(encoding="utf-8-sig")
        default_game = (project / "Config" / "DefaultGame.ini").read_text(encoding="utf-8-sig")
        self.assertIn("$G044RequiredFile", package_script)
        self.assertIn("$G044CookManifest", package_script)
        self.assertIn("check_packaged_g044_cook.py", package_script)
        self.assertIn("G044/VFX cook-manifest verification failed", package_script)
        self.assertIn('+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/VFX")', default_game)
        self.assertLess(package_script.index("if ($LASTEXITCODE -ne 0) { throw \"BuildCookRun"),
                        package_script.index("check_packaged_g044_cook.py"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
