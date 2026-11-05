#!/usr/bin/env python3
"""Fixtures for benchmark-kit copy manifest validation."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("check_bench_kit_manifest.py")
SPEC = importlib.util.spec_from_file_location("check_bench_kit_manifest", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
ROOT = Path(__file__).resolve().parents[2]


class BenchKitManifestTests(unittest.TestCase):
    def test_existing_manifest_is_unique_and_resolves(self):
        text = (ROOT / "Scripts/MakeBenchKit.ps1").read_text(encoding="utf-8")
        names = MODULE.manifest_names(text)
        self.assertEqual(MODULE.validate(names, ROOT / "Scripts"), [])

    def test_duplicate_windows_destination_fails_case_insensitively(self):
        with tempfile.TemporaryDirectory() as temp:
            scripts = Path(temp)
            (scripts / "One.ps1").write_text("", encoding="utf-8")
            issues = MODULE.validate(["One.ps1", "one.PS1"], scripts)
            self.assertTrue(any("DUPLICATE destination" in issue for issue in issues))

    def test_missing_manifest_source_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertIn("MISSING source Scripts/Missing.ps1", MODULE.validate(["Missing.ps1"], Path(temp)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
