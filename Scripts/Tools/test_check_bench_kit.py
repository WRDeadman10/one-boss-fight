#!/usr/bin/env python3
"""Offline fixtures for the bench-kit pre-transfer checklist."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("check_bench_kit.py")
SPEC = spec_from_file_location("check_bench_kit", MODULE_PATH)
CHECK = module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


def create_kit(root: Path, development: bool = False) -> None:
    names = list(CHECK.BASE_FILES)
    if development:
        names.extend(CHECK.DEVELOPMENT_FILES)
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if name == "BUILD_INFO.txt":
            path.write_text("Package build ID: OBF-SHIPPING-20261106T010000Z-deadbeef\nExecutable SHA-256: " + "a" * 64 + "\n", encoding="utf-8")
        else:
            path.write_text("fixture\n", encoding="utf-8")


class BenchKitCheckTests(unittest.TestCase):
    def test_shipping_kit_passes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_kit(root)
            self.assertEqual(CHECK.validate(root)["verdict"], "PASS")

    def test_missing_dependency_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_kit(root)
            (root / "Scripts/PackagedRunLog.psm1").unlink()
            self.assertIn("Scripts/PackagedRunLog.psm1", CHECK.validate(root)["missing"])

    def test_pdb_is_excluded_from_transfer_kit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_kit(root)
            pdb = root / "Saved/StagedBuilds/Windows/debug.pdb"
            pdb.parent.mkdir(parents=True, exist_ok=True)
            pdb.write_bytes(b"symbols")
            self.assertEqual(CHECK.validate(root)["verdict"], "FAIL")

    def test_development_stage_is_required_when_requested(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_kit(root)
            self.assertTrue(CHECK.validate(root, include_development=True)["missing"])
            create_kit(root, development=True)
            self.assertEqual(CHECK.validate(root, include_development=True)["verdict"], "PASS")

    def test_make_kit_runs_checker_after_manifest_copy(self):
        project = Path(__file__).resolve().parents[2]
        source = (project / "Scripts/MakeBenchKit.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("check_bench_kit.py", source)
        self.assertIn("check_bench_kit.py') @KitCheckArgs", source)
        self.assertLess(source.index("check_bench_kit.py"), source.index("if ($Zip)"))
        self.assertIn("PackagedRunLog.psm1", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
