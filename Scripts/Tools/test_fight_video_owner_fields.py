"""Static guard that technical review edits preserve owner-only checklist fields."""
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKLIST = ROOT / "Documentation" / "Boss" / "FIGHT_VIDEO_REVIEW.md"


class FightVideoOwnerFieldTests(unittest.TestCase):
    def test_seven_owner_rows_remain_blank_and_no_verdict_is_filled(self):
        text = CHECKLIST.read_text(encoding="utf-8")
        rows = [line for line in text.splitlines() if re.match(r"\| \[.?\] \|", line)]
        self.assertEqual(len(rows), 7)
        self.assertTrue(all(re.match(r"\| \[ \] \|", row) for row in rows), rows)

    def test_combat_automation_does_not_write_owner_review_files(self):
        scripts = list((ROOT / "Scripts" / "Editor").glob("*.py"))
        writes = []
        for path in scripts:
            source = path.read_text(encoding="utf-8", errors="replace")
            if "FIGHT_VIDEO_REVIEW.md" in source and re.search(r"write_text|open\([^\n]*['\"]w", source):
                writes.append(path.name)
        self.assertEqual(writes, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
