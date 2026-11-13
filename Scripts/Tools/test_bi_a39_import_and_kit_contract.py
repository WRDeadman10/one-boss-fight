import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IMPORT_DIR = REPO_ROOT / "Import"
KIT_DIR = REPO_ROOT / "Unreal_Boss_Combat_Engineering_Kit"
SAVED_REVIEW_DIR = REPO_ROOT / "Saved" / "BossCombatReview"


class BiA39ImportAndKitContractTest(unittest.TestCase):
    def test_import_tree_has_zero_empty_files(self) -> None:
        files = [p for p in IMPORT_DIR.rglob("*") if p.is_file()]
        self.assertGreaterEqual(len(files), 250)
        empty = [p.relative_to(REPO_ROOT).as_posix() for p in files if p.stat().st_size <= 0]
        self.assertEqual(empty, [], f"Zero-byte files under Import/: {empty}")

    def test_engineering_kit_markdowns_and_saved_caches_are_valid(self) -> None:
        mds = sorted(KIT_DIR.rglob("*.md"))
        self.assertGreaterEqual(len(mds), 25)
        for md in mds:
            md.read_text(encoding="utf-8")

        if SAVED_REVIEW_DIR.exists():
            for jf in sorted(SAVED_REVIEW_DIR.rglob("*.json")):
                json.loads(jf.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
