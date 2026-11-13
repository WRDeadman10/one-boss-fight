import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "scan_pie_driver_safety", ROOT / "Scripts" / "Tools" / "scan_pie_driver_safety.py")
SCANNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCANNER)


class ScanPieDriverSafetyTests(unittest.TestCase):
    def test_finds_missing_result_and_unguarded_release(self):
        source = "register_slate_post_tick_callback(tick)\nset_key_down(pc, key, False)\n"
        row = SCANNER.scan_text("unsafe.py", source)
        self.assertEqual(row["findings"], ["missing_final_result", "key_release_without_readiness_gate"])

    def test_accepts_result_and_mapping_gate(self):
        source = ("editor_request_begin_play()\nFinalResult(log, 'x')\n"
                  "MappingReadinessGate(2)\nset_key_down(pc, key, False)\n")
        self.assertEqual(SCANNER.scan_text("safe.py", source)["findings"], [])

    def test_ignores_non_driver_scripts_and_scans_tree(self):
        self.assertIsNone(SCANNER.scan_text("utility.py", "set_key_down(pc, key, False)"))
        with tempfile.TemporaryDirectory() as temp:
            Path(temp, "pie_one.py").write_text("register_slate_post_tick_callback(tick)", encoding="utf-8")
            Path(temp, "other.py").write_text("editor_request_begin_play()", encoding="utf-8")
            self.assertEqual(len(SCANNER.scan(temp)), 1)


if __name__ == "__main__":
    unittest.main()
