"""BL-96..100 (C, implementer; X-2201): static closeout checks for the BL lane's native test files.

Source-only (nothing is compiled, run or written). The engine-lock acceptance build and automation run stay with the lead.
For every Source/OneBossFight/Tests/*.cpp whose header comment names "lane BL":
  - exactly one IMPLEMENT_SIMPLE_AUTOMATION_TEST, inside #if WITH_DEV_AUTOMATION_TESTS ... #endif;
  - its automation name and class name are unique across ALL test files;
  - every #include "Player/..." resolves to an existing header;
  - no trailing whitespace.
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TESTS = REPO / "Source" / "OneBossFight" / "Tests"
SOURCE = REPO / "Source" / "OneBossFight"
DECL = re.compile(r'IMPLEMENT_SIMPLE_AUTOMATION_TEST\(\s*(\w+)\s*,\s*"([^"]+)"', re.S)


def text(path):
    return path.read_text(encoding="utf-8-sig", errors="replace")


ALL = sorted(TESTS.glob("*.cpp"))
BL = [p for p in ALL if "lane BL" in text(p)[:1500]]


class BlLaneStaticChecks(unittest.TestCase):
    def test_lane_file_count(self):
        self.assertEqual(len(BL), 50, [p.name for p in BL])

    def test_one_guarded_automation_test_per_file(self):
        for path in BL:
            with self.subTest(file=path.name):
                body = text(path)
                self.assertEqual(len(DECL.findall(body)), 1)
                guard, decl, end = body.find("#if WITH_DEV_AUTOMATION_TESTS"), body.find("IMPLEMENT_SIMPLE_AUTOMATION_TEST"), body.rfind("#endif")
                self.assertTrue(0 <= guard < decl < end, "declaration must sit inside the dev-automation guard")

    def test_names_and_classes_unique_across_all_tests(self):
        names, classes = {}, {}
        for path in ALL:
            for cls, name in DECL.findall(text(path)):
                names.setdefault(name, []).append(path.name)
                classes.setdefault(cls, []).append(path.name)
        for path in BL:
            cls, name = DECL.findall(text(path))[0]
            with self.subTest(file=path.name):
                self.assertEqual(names[name], [path.name], f"automation name {name} reused")
                self.assertEqual(classes[cls], [path.name], f"class {cls} reused")

    def test_player_includes_exist(self):
        for path in BL:
            for inc in re.findall(r'#include "(Player/[^"]+)"', text(path)):
                with self.subTest(file=path.name, include=inc):
                    self.assertTrue((SOURCE / inc).is_file())

    def test_no_trailing_whitespace(self):
        for path in BL:
            with self.subTest(file=path.name):
                self.assertFalse(any(line.rstrip("\r") != line.rstrip("\r").rstrip() for line in text(path).splitlines()))


if __name__ == "__main__":
    unittest.main()
