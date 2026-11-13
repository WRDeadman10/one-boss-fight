#!/usr/bin/env python3
"""Fixtures for A5 receipt directory pair-ID validation."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("validate_a5_receipt_directory.py")
SPEC = importlib.util.spec_from_file_location("validate_a5_receipt_directory", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_arm(path: Path, driver: str | None, route: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"identity": {"driver": driver}, "route": route}), encoding="utf-8")


class A5ReceiptDirectoryTests(unittest.TestCase):
    def test_complete_expected_pair_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_arm(root / "pie_one/receipt_legacy.json", "pie_one", "legacy")
            write_arm(root / "pie_one/receipt_data.json", "pie_one", "data")
            self.assertEqual(MODULE.validate(root, ["pie_one"]), [])

    def test_missing_pair_and_missing_arm_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_arm(root / "pie_one/receipt_legacy.json", "pie_one", "legacy")
            issues = MODULE.validate(root, ["pie_one", "pie_two"])
            self.assertTrue(any("MISSING data arm" in issue for issue in issues))
            self.assertTrue(any("MISSING pair ID pie_two" in issue for issue in issues))

    def test_data_only_directory_reports_missing_legacy_arm(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_arm(root / "pie_one/receipt_data.json", "pie_one", "data")
            self.assertTrue(any("MISSING legacy arm" in issue for issue in MODULE.validate(root, ["pie_one"])))

    def test_duplicate_pair_id_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for folder in ("first", "second"):
                write_arm(root / folder / "receipt_legacy.json", "pie_one", "legacy")
                write_arm(root / folder / "receipt_data.json", "pie_one", "data")
            self.assertTrue(any("DUPLICATE pair ID pie_one" in issue for issue in MODULE.validate(root, ["pie_one"])))

    def test_arm_driver_or_route_disagreement_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_arm(root / "pie_one/receipt_legacy.json", "pie_other", "data")
            write_arm(root / "pie_one/receipt_data.json", "pie_one", "legacy")
            issues = MODULE.validate(root, ["pie_one"])
            self.assertTrue(any("CONTRADICTORY pair IDs" in issue for issue in issues))
            self.assertTrue(any("CONTRADICTORY legacy arm route" in issue for issue in issues))

    def test_malformed_json_shapes_are_reported_without_crashing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pair = root / "pie_one"
            pair.mkdir()
            (pair / "receipt_legacy.json").write_text("[]", encoding="utf-8")
            (pair / "receipt_data.json").write_text(json.dumps({"identity": []}), encoding="utf-8")
            issues = MODULE.validate(root, ["pie_one"])
            self.assertTrue(any("INVALID receipt object" in issue for issue in issues))

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pair = root / "pie_one"
            write_arm(pair / "receipt_legacy.json", "pie_one", "legacy")
            (pair / "receipt_data.json").write_text(json.dumps({"identity": []}), encoding="utf-8")
            issues = MODULE.validate(root, ["pie_one"])
            self.assertTrue(any("MISSING pair ID" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main(verbosity=2)
