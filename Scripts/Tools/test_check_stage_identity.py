"""Fixture coverage for stage mix-up and missing-identity refusal."""
import tempfile
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_stage_identity import REQUIRED, validate


class StageIdentityTests(unittest.TestCase):
    def make_stage(self, root, configuration, stamp=None):
        for name in REQUIRED:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(stamp if name.endswith("BuildStamp.txt") else "present",
                            encoding="ascii")

    def test_distinct_valid_stages_and_rejections(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            ship, dev = base / "Shipping" / "Windows", base / "Development" / "Windows"
            self.make_stage(ship, "Shipping", "OBF-SHIPPING-20261108T010000Z-a1b2c3d4")
            self.make_stage(dev, "Development", "OBF-DEVELOPMENT-20261108T011000Z-b2c3d4e5")
            self.assertEqual(validate(ship, dev)["verdict"], "PASS")
            self.assertEqual(validate(ship, ship)["verdict"], "FAIL")
            (dev / "OneBossFight/Saved/BuildStamp.txt").write_text("OBF-SHIPPING-20261108T011000Z-b2c3d4e5")
            self.assertEqual(validate(ship, dev)["verdict"], "FAIL")
            (dev / "Manifest_UFSFiles_Win64.txt").unlink()
            self.assertIn("Manifest_UFSFiles_Win64.txt", str(validate(ship, dev)["issues"]))
            (ship / "Manifest_NonUFSFiles_Win64.txt").write_text("")
            self.assertIn("empty stage files", str(validate(ship, dev)["issues"]))


if __name__ == "__main__":
    unittest.main()
