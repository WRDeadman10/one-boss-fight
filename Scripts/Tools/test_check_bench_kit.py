#!/usr/bin/env python3
"""Offline fixtures for the bench-kit pre-transfer checklist."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import tempfile
import unittest
import re
import subprocess

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

    def test_package_stamp_output_passes_bench_kit_intake_for_shipping_and_development(self):
        project = Path(__file__).resolve().parents[2]
        package_source = (project / "Scripts/Package.ps1").read_text(encoding="utf-8-sig")
        self.assertIn(
            "$BuildId = 'OBF-' + $Configuration.ToUpperInvariant() + '-' + (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8)",
            package_source,
        )

        evidence = project / "Docs/BossCombatReview/Execution/Claude/B_C947_R6KIT"
        shipping_info = (evidence / "BUILD_INFO.txt").read_text(encoding="utf-8-sig")
        shipping_id = re.search(r"(?m)^Package build ID: (.+)$", shipping_info).group(1)
        self.assertRegex(shipping_id, r"^OBF-SHIPPING-\d{8}T\d{6}Z-[0-9a-f]{8}$")
        stage_lines = (evidence / "stamps.txt").read_text(encoding="utf-8-sig").splitlines()
        development_id = next(line.split()[1] for line in stage_lines if line.startswith("DEVELOPMENT "))
        self.assertRegex(development_id, r"^OBF-DEVELOPMENT-\d{8}T\d{6}Z-[0-9a-f]{8}$")

        checker = project / "Scripts/Tools/check_bench_kit.py"
        for build_id, configuration, development_only in (
            (shipping_id, "Shipping", False),
            (development_id, "Development", True),
        ):
            with self.subTest(configuration=configuration), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                create_kit(root, development=True)
                info = shipping_info.replace(shipping_id, build_id).replace(
                    "Package configuration: Shipping", f"Package configuration: {configuration}"
                )
                (root / "BUILD_INFO.txt").write_text(info, encoding="utf-8")
                command = [sys.executable, str(checker), "--kit-root", str(root)]
                if development_only:
                    command.append("--development-only")
                else:
                    command.append("--include-development")
                result = subprocess.run(command, capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('"verdict": "PASS"', result.stdout)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_kit(root)
            obsolete_info = shipping_info.replace(
                shipping_id, development_id.replace("OBF-DEVELOPMENT-", "OBF-DEV-")
            ).replace("Package configuration: Shipping", "Package configuration: Development")
            (root / "BUILD_INFO.txt").write_text(obsolete_info, encoding="utf-8")
            rejected = subprocess.run(
                [sys.executable, str(checker), "--kit-root", str(root)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("must include a generated package build ID", rejected.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
