"""test_d3_findings_table.py - Unit tests for D3 findings table generator.

Verifies:
- Structure and column headers of generated Markdown table.
- Hand-calculated frame counts and seconds for Clip 1 (REF_MaceSlam_Sweep, medium confidence).
- Hand-calculated frame counts and seconds for Clip 2 (REF_HolySwordRain_Setup, low confidence).
- CLI execution returns returncode 0 on D3_MEASURED_LEDGER.json.

Run: python -I test_d3_findings_table.py
"""

import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from D3_findings_table import (
    FPS,
    DEFAULT_LEDGER,
    compute_entry_metrics,
    generate_markdown_table
)


class TestD3FindingsTable(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(DEFAULT_LEDGER), f"Ledger file not found: {DEFAULT_LEDGER}")
        with open(DEFAULT_LEDGER, "r", encoding="utf-8") as f:
            self.ledger = json.load(f)

    def test_hand_calculated_metrics_mace_slam(self):
        """Tests hand-calculated numbers for Clip 1: REF_MaceSlam_Sweep."""
        entry = next(e for e in self.ledger["entries"] if e["ref_id"] == "REF_MaceSlam_Sweep")
        metrics = compute_entry_metrics(entry, fps=FPS)

        self.assertEqual(metrics["orig_id"], "Move_EmberWarden_MaceSlam")
        self.assertEqual(metrics["confidence"], "medium")

        # Frames: W=1703, C=1787, A=1796, E=1801, R=1835, RE=1871
        self.assertEqual(metrics["windup_f"], 93)       # 1796 - 1703
        self.assertEqual(metrics["active_f"], 5)        # 1801 - 1796
        self.assertEqual(metrics["recovery_f"], 70)     # 1871 - 1801 (RE - E)
        self.assertEqual(metrics["tail_f"], 36)         # 1871 - 1835 (RE - R)
        self.assertEqual(metrics["total_f"], 168)       # 1871 - 1703

        # Seconds: deltas / 59.9401
        self.assertAlmostEqual(metrics["windup_s"], 1.5515, places=4)
        self.assertAlmostEqual(metrics["active_s"], 0.0834, places=4)
        self.assertAlmostEqual(metrics["recovery_s"], 1.1678, places=4)
        self.assertAlmostEqual(metrics["tail_s"], 0.6006, places=4)
        self.assertAlmostEqual(metrics["total_s"], 2.8028, places=4)

    def test_hand_calculated_metrics_holy_sword_rain(self):
        """Tests hand-calculated numbers for Clip 2: REF_HolySwordRain_Setup."""
        entry = next(e for e in self.ledger["entries"] if e["ref_id"] == "REF_HolySwordRain_Setup")
        metrics = compute_entry_metrics(entry, fps=FPS)

        self.assertEqual(metrics["orig_id"], "Move_EmberWarden_SwordRain")
        self.assertEqual(metrics["confidence"], "low")

        # Frames: W=2381, C=2423, A=2566, E=2602, R=2620, RE=2818
        self.assertEqual(metrics["windup_f"], 185)      # 2566 - 2381
        self.assertEqual(metrics["active_f"], 36)       # 2602 - 2566
        self.assertEqual(metrics["recovery_f"], 216)    # 2818 - 2602 (RE - E)
        self.assertEqual(metrics["tail_f"], 198)        # 2818 - 2620 (RE - R)
        self.assertEqual(metrics["total_f"], 437)       # 2818 - 2381

        # Seconds: deltas / 59.9401
        self.assertAlmostEqual(metrics["windup_s"], 3.0864, places=4)
        self.assertAlmostEqual(metrics["active_s"], 0.6006, places=4)
        self.assertAlmostEqual(metrics["recovery_s"], 3.6036, places=4)
        self.assertAlmostEqual(metrics["tail_s"], 3.3033, places=4)
        self.assertAlmostEqual(metrics["total_s"], 7.2906, places=4)

    def test_generate_markdown_table_structure(self):
        """Tests that generated Markdown table contains expected header and exactly 2 populated rows."""
        table_md = generate_markdown_table(self.ledger, fps=FPS)
        self.assertIn("| Reference ID | Original Move ID |", table_md)
        self.assertIn("REF_MaceSlam_Sweep", table_md)
        self.assertIn("REF_HolySwordRain_Setup", table_md)
        self.assertIn("Move_EmberWarden_MaceSlam", table_md)
        self.assertIn("Move_EmberWarden_SwordRain", table_md)

        lines = [line for line in table_md.strip().split("\n") if line.startswith("|")]
        # Header + separator + 2 data rows = 4 lines
        self.assertEqual(len(lines), 4)

    def test_cli_execution(self):
        """Tests CLI execution of D3_findings_table.py exits with code 0 and prints table."""
        script = os.path.join(os.path.dirname(__file__), "D3_findings_table.py")
        res = subprocess.run([sys.executable, "-I", script, DEFAULT_LEDGER], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("REF_MaceSlam_Sweep", res.stdout)
        self.assertIn("REF_HolySwordRain_Setup", res.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
