"""Guard direct local PowerShell dependencies in the staged benchmark kit."""
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAKE_KIT = ROOT / "Scripts" / "MakeBenchKit.ps1"
SCRIPTS_DIR = ROOT / "Scripts"

MANIFEST_PATTERN = re.compile(r"foreach\s*\(\s*\$f\s+in\s+([^)]*)\)", re.IGNORECASE | re.DOTALL)
STRING_PATTERN = re.compile(r"'([^']+)'|\"([^\"]+)\"")
SCRIPTROOT_PATTERN = re.compile(r"Join-Path\s+\$PSScriptRoot\s+(['\"])([^'\"]+)\1", re.IGNORECASE)
IMPORT_PATTERN = re.compile(r"Import-Module\s+(?:-Name\s+)?(['\"])([^'\"]+)\1", re.IGNORECASE)
DOT_SOURCE_PATTERN = re.compile(r"(?m)^\s*\.\s+['\"]?\$PSScriptRoot[\\/]([^\s'\"]+\.ps1)['\"]?\b", re.IGNORECASE)


def _manifest_names(text: str) -> set[str]:
    match = MANIFEST_PATTERN.search(text)
    if not match:
        raise AssertionError("MakeBenchKit.ps1 has no literal foreach ($f in ...) copy manifest")
    return {single or double for single, double in STRING_PATTERN.findall(match.group(1))}


def _local_targets(script_text: str) -> set[str]:
    targets = {match.group(2).replace("/", "\\").rsplit("\\", 1)[-1]
               for match in SCRIPTROOT_PATTERN.finditer(script_text)}
    for match in IMPORT_PATTERN.finditer(script_text):
        value = match.group(2).replace("/", "\\")
        leaf = value.rsplit("\\", 1)[-1]
        if leaf.lower().endswith((".psm1", ".psd1")):
            targets.add(leaf)
    targets.update(match.group(1).replace("/", "\\").rsplit("\\", 1)[-1]
                   for match in DOT_SOURCE_PATTERN.finditer(script_text))
    return targets


def _missing_dependencies(script_text: str, manifest: set[str]) -> set[str]:
    return _local_targets(script_text) - manifest


class MakeBenchKitDependencyTests(unittest.TestCase):
    def test_every_kit_script_local_target_is_staged(self) -> None:
        manifest = _manifest_names(MAKE_KIT.read_text(encoding="utf-8"))
        self.assertIn("round5_experiments.json", manifest)
        self.assertIn("RunPerfExperiments.ps1", manifest)
        missing_files = sorted(name for name in manifest if not (SCRIPTS_DIR / name).is_file())
        self.assertEqual(missing_files, [], f"manifest names absent files: {missing_files}")

        missing = {}
        for name in sorted(manifest):
            path = SCRIPTS_DIR / name
            if path.suffix.lower() not in {".ps1", ".psm1"}:
                continue
            targets = _missing_dependencies(path.read_text(encoding="utf-8"), manifest)
            if targets:
                missing[name] = sorted(targets)
        self.assertEqual(missing, {}, f"kit scripts reference unstaged local files: {missing}")

    def test_fixture_detects_missing_import_and_scriptroot_targets(self) -> None:
        source = """
Import-Module (Join-Path $PSScriptRoot 'LocalModule.psm1') -Force
$child = Join-Path $PSScriptRoot 'Child.ps1'
"""
        self.assertEqual(
            _missing_dependencies(source, {"Tool.ps1"}),
            {"LocalModule.psm1", "Child.ps1"},
        )

    def test_fixture_detects_missing_dot_sourced_scriptroot_target(self) -> None:
        source = '. "$PSScriptRoot\\MissingSetup.ps1"\n'
        self.assertEqual(_missing_dependencies(source, {"Tool.ps1"}), {"MissingSetup.ps1"})


if __name__ == "__main__":
    unittest.main()
