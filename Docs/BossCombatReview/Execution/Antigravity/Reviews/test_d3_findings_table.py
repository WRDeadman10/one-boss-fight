"""test_d3_findings_table.py - Unit tests for D3 findings table generator.

Verifies:
- Structure and column headers of generated Markdown table (including 'Ledger priority').
- Hand-calculated frame counts and seconds for Clip 1 (REF_MaceSlam_Sweep, medium confidence).
- Hand-calculated frame counts and seconds for Clip 2 (REF_HolySwordRain_Setup, low confidence).
- Hand-calculated frame counts and seconds for Clip 3 (REF_GapPounce_Close, low confidence).
- Ledger priority values in table cells match the ledger's 'priority' fields (6, 9, 10).
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
        self.assertEqual(metrics["priority"], 9)

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
        self.assertEqual(metrics["priority"], 6)

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

    def test_hand_calculated_metrics_gap_pounce(self):
        """Tests hand-calculated numbers for Clip 3: REF_GapPounce_Close."""
        entry = next(e for e in self.ledger["entries"] if e["ref_id"] == "REF_GapPounce_Close")
        metrics = compute_entry_metrics(entry, fps=FPS)

        self.assertEqual(metrics["orig_id"], "Move_EmberWarden_GapPounce")
        self.assertEqual(metrics["confidence"], "low")
        self.assertEqual(metrics["priority"], 10)

        # Frames: W=3951, C=3981, A=4005, E=4023, R=4047, RE=4065
        self.assertEqual(metrics["windup_f"], 54)       # 4005 - 3951
        self.assertEqual(metrics["active_f"], 18)       # 4023 - 4005
        self.assertEqual(metrics["recovery_f"], 42)     # 4065 - 4023 (RE - E)
        self.assertEqual(metrics["tail_f"], 18)         # 4065 - 4047 (RE - R)
        self.assertEqual(metrics["total_f"], 114)       # 4065 - 3951

        # Seconds: deltas / 59.9401
        self.assertAlmostEqual(metrics["windup_s"], 0.9009, places=4)
        self.assertAlmostEqual(metrics["active_s"], 0.3003, places=4)
        self.assertAlmostEqual(metrics["recovery_s"], 0.7007, places=4)
        self.assertAlmostEqual(metrics["tail_s"], 0.3003, places=4)
        self.assertAlmostEqual(metrics["total_s"], 1.9019, places=4)

    def test_generate_markdown_table_structure(self):
        """Tests that generated Markdown table contains expected header and exactly 3 populated rows."""
        table_md = generate_markdown_table(self.ledger, fps=FPS)
        self.assertIn("| Ledger priority | Reference ID | Original Move ID |", table_md)
        self.assertIn("REF_MaceSlam_Sweep", table_md)
        self.assertIn("REF_HolySwordRain_Setup", table_md)
        self.assertIn("REF_GapPounce_Close", table_md)
        self.assertIn("Move_EmberWarden_MaceSlam", table_md)
        self.assertIn("Move_EmberWarden_SwordRain", table_md)
        self.assertIn("Move_EmberWarden_GapPounce", table_md)

        lines = [line for line in table_md.strip().split("\n") if line.startswith("|")]
        # Header + separator + 3 data rows = 5 lines
        self.assertEqual(len(lines), 5)

    def test_table_ledger_priority_matches_entry_priority(self):
        """Tests that generated table prints the actual ledger priority values (6, 9, 10)."""
        table_md = generate_markdown_table(self.ledger, fps=FPS)
        lines = [line for line in table_md.strip().split("\n") if line.startswith("|")]
        # Data rows are lines[2:]
        data_rows = lines[2:]
        self.assertEqual(len(data_rows), 3)

        # Row 1 is REF_HolySwordRain_Setup with priority 6
        cells_row1 = [c.strip() for c in data_rows[0].split("|") if c.strip()]
        self.assertEqual(cells_row1[0], "6")
        self.assertIn("REF_HolySwordRain_Setup", cells_row1[1])

        # Row 2 is REF_MaceSlam_Sweep with priority 9
        cells_row2 = [c.strip() for c in data_rows[1].split("|") if c.strip()]
        self.assertEqual(cells_row2[0], "9")
        self.assertIn("REF_MaceSlam_Sweep", cells_row2[1])

        # Row 3 is REF_GapPounce_Close with priority 10
        cells_row3 = [c.strip() for c in data_rows[2].split("|") if c.strip()]
        self.assertEqual(cells_row3[0], "10")
        self.assertIn("REF_GapPounce_Close", cells_row3[1])

    def test_cli_execution(self):
        """Tests CLI execution of D3_findings_table.py exits with code 0 and prints table."""
        script = os.path.join(os.path.dirname(__file__), "D3_findings_table.py")
        res = subprocess.run([sys.executable, "-I", script, DEFAULT_LEDGER], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("| Ledger priority |", res.stdout)
        self.assertIn("REF_MaceSlam_Sweep", res.stdout)
        self.assertIn("REF_HolySwordRain_Setup", res.stdout)
        self.assertIn("REF_GapPounce_Close", res.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
