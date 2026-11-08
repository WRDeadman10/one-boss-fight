"""Offline synthetic contracts for dual-configuration stage identity checks."""
from pathlib import Path
import importlib.util
import tempfile
import unittest

MODULE = Path(__file__).with_name("check_stage_identity.py")
SPEC = importlib.util.spec_from_file_location("check_stage_identity_test_module", MODULE)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(CHECK)


class StageIdentityTests(unittest.TestCase):
    def make_stage(self, root: Path, configuration: str, suffix: str) -> None:
        for name in ("OneBossFight.exe", "Manifest_UFSFiles_Win64.txt", "Manifest_NonUFSFiles_Win64.txt"):
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_bytes((name + suffix).encode("ascii"))
        stamp = f"OBF-{configuration.upper()}-20261108T000000Z-{suffix:0<8}"
        stamp_path = root / "OneBossFight/Saved/BuildStamp.txt"
        stamp_path.parent.mkdir(parents=True, exist_ok=True)
        stamp_path.write_text(stamp, encoding="ascii")

    def test_distinct_valid_build_stamps_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ship, dev = root / "ship", root / "dev"
            self.make_stage(ship, "Shipping", "a")
            self.make_stage(dev, "Development", "b")
            result = CHECK.validate(ship, dev)
            self.assertEqual("PASS", result["verdict"])
            self.assertEqual("OBF-SHIPPING-20261108T000000Z-a0000000", result["shipping"]["build_id"])

    def test_shared_root_and_configuration_mismatch_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "stage"
            self.make_stage(root, "Shipping", "a")
            result = CHECK.validate(root, root)
            self.assertEqual("FAIL", result["verdict"])
            self.assertTrue(any("same directory" in item for item in result["issues"]))
            self.assertTrue(any("configuration or format mismatch" in item for item in result["development"]["issues"]))

    def test_resolved_alias_roots_are_a_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ship = root / "ship"
            self.make_stage(ship, "Shipping", "a")
            alias = root / "other" / ".." / "ship"
            result = CHECK.validate(ship, alias)
            self.assertEqual("FAIL", result["verdict"])
            self.assertTrue(any("same directory" in item for item in result["issues"]))

    def test_empty_required_artifact_fails_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ship, dev = root / "ship", root / "dev"
            self.make_stage(ship, "Shipping", "a")
            self.make_stage(dev, "Development", "b")
            target = ship / "Manifest_NonUFSFiles_Win64.txt"
            target.write_bytes(b"")
            before = target.read_bytes()
            result = CHECK.validate(ship, dev)
            self.assertEqual("FAIL", result["verdict"])
            self.assertIn("Manifest_NonUFSFiles_Win64.txt", result["shipping"]["empty"])
            self.assertEqual(before, target.read_bytes())

    def test_missing_stage_artifact_fails_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ship, dev = root / "ship", root / "dev"
            self.make_stage(ship, "Shipping", "a")
            self.make_stage(dev, "Development", "b")
            (ship / "Manifest_UFSFiles_Win64.txt").unlink()
            result = CHECK.validate(ship, dev)
            self.assertEqual("FAIL", result["verdict"])
            self.assertIn("Manifest_UFSFiles_Win64.txt", result["shipping"]["missing"])
            self.assertFalse((ship / "Manifest_UFSFiles_Win64.txt").exists())


if __name__ == "__main__":
    unittest.main()
