#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_compare_runs.py

Unit and integration test suite for compare_runs.py:
1. Pure LF line endings check.
2. Synthetic test: Identical runs -> PASS.
3. Synthetic test: Missing hit -> FAIL.
4. Synthetic test: Damage discrepancy -> FAIL.
5. Synthetic test: Order swapped -> FAIL.
6. Real logs test: B_QA004 fixed30, fixed60, fixed120 -> PASS with diagnostic duplicate scaling.
"""

import unittest
import tempfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[5]
REVIEWS_DIR = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews"
sys.path.append(str(REVIEWS_DIR))

import compare_runs

SYNTHETIC_RUN_A = """[2026.10.31-22.00.00:000][1]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=MoveA score=0.900 range=150.0 phase=Phase_1 seq=1
[2026.10.31-22.00.01:000][2]LogTemp: Display: [FrameworkProof] hit instance=1 window=W1 key=Blade outcome=ERPGDamageOutcome::Accepted hpApplied=35 healthBefore=800 healthAfter=765
[2026.10.31-22.00.02:000][3]LogTemp: Display: [FrameworkProof] hit instance=1 window=W1 key=Blade outcome=ERPGDamageOutcome::RejectedDuplicate hpApplied=0 healthBefore=765 healthAfter=765
[2026.10.31-22.00.03:000][4]LogTemp: Display: [FrameworkProof] decision attack=2 chosen=MoveB score=0.850 range=150.0 phase=Phase_1 seq=2
[2026.10.31-22.00.04:000][5]LogTemp: Display: [FrameworkProof] hit instance=2 window=W2 key=Blade outcome=ERPGDamageOutcome::Accepted hpApplied=20 healthBefore=765 healthAfter=745
[2026.10.31-22.00.05:000][6]LogTemp: Display: [FrameworkProof] invariant targetHPBefore=800 targetHPAfter=745 expectedHP=745 acceptedHits=2 appliedDamage=55
[2026.10.31-22.00.05:000][7]LogTemp: Display: [FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=2 attacks=2
"""

SYNTHETIC_RUN_B_IDENTICAL = """[2026.10.31-22.01.00:000][10]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=MoveA score=0.900 range=150.0 phase=Phase_1 seq=101
[2026.10.31-22.01.01:000][11]LogTemp: Display: [FrameworkProof] hit instance=1 window=W1 key=Blade outcome=ERPGDamageOutcome::Accepted hpApplied=35 healthBefore=800 healthAfter=765
[2026.10.31-22.01.02:000][12]LogTemp: Display: [FrameworkProof] decision attack=2 chosen=MoveB score=0.850 range=150.0 phase=Phase_1 seq=102
[2026.10.31-22.01.03:000][13]LogTemp: Display: [FrameworkProof] hit instance=2 window=W2 key=Blade outcome=ERPGDamageOutcome::Accepted hpApplied=20 healthBefore=765 healthAfter=745
[2026.10.31-22.01.04:000][14]LogTemp: Display: [FrameworkProof] invariant targetHPBefore=800 targetHPAfter=745 expectedHP=745 acceptedHits=2 appliedDamage=55
[2026.10.31-22.01.04:000][15]LogTemp: Display: [FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=2 attacks=2
"""

SYNTHETIC_RUN_MISSING_HIT = """[2026.10.31-22.00.00:000][1]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=MoveA score=0.900 range=150.0 phase=Phase_1 seq=1
[2026.10.31-22.00.03:000][4]LogTemp: Display: [FrameworkProof] decision attack=2 chosen=MoveB score=0.850 range=150.0 phase=Phase_1 seq=2
[2026.10.31-22.00.04:000][5]LogTemp: Display: [FrameworkProof] hit instance=2 window=W2 key=Blade outcome=ERPGDamageOutcome::Accepted hpApplied=20 healthBefore=800 healthAfter=780
[2026.10.31-22.00.05:000][6]LogTemp: Display: [FrameworkProof] invariant targetHPBefore=800 targetHPAfter=780 expectedHP=780 acceptedHits=1 appliedDamage=20
[2026.10.31-22.00.05:000][7]LogTemp: Display: [FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=1 attacks=2
"""

SYNTHETIC_RUN_DAMAGE_DIFF = """[2026.10.31-22.00.00:000][1]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=MoveA score=0.900 range=150.0 phase=Phase_1 seq=1
[2026.10.31-22.00.01:000][2]LogTemp: Display: [FrameworkProof] hit instance=1 window=W1 key=Blade outcome=ERPGDamageOutcome::Accepted hpApplied=40 healthBefore=800 healthAfter=760
[2026.10.31-22.00.03:000][4]LogTemp: Display: [FrameworkProof] decision attack=2 chosen=MoveB score=0.850 range=150.0 phase=Phase_1 seq=2
[2026.10.31-22.00.04:000][5]LogTemp: Display: [FrameworkProof] hit instance=2 window=W2 key=Blade outcome=ERPGDamageOutcome::Accepted hpApplied=20 healthBefore=760 healthAfter=740
[2026.10.31-22.00.05:000][6]LogTemp: Display: [FrameworkProof] invariant targetHPBefore=800 targetHPAfter=740 expectedHP=740 acceptedHits=2 appliedDamage=60
[2026.10.31-22.00.05:000][7]LogTemp: Display: [FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=2 attacks=2
"""

SYNTHETIC_RUN_SWAPPED_ORDER = """[2026.10.31-22.00.00:000][1]LogTemp: Display: [FrameworkProof] decision attack=2 chosen=MoveB score=0.850 range=150.0 phase=Phase_1 seq=1
[2026.10.31-22.00.01:000][2]LogTemp: Display: [FrameworkProof] hit instance=2 window=W2 key=Blade outcome=ERPGDamageOutcome::Accepted hpApplied=20 healthBefore=800 healthAfter=780
[2026.10.31-22.00.03:000][4]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=MoveA score=0.900 range=150.0 phase=Phase_1 seq=2
[2026.10.31-22.00.04:000][5]LogTemp: Display: [FrameworkProof] hit instance=1 window=W1 key=Blade outcome=ERPGDamageOutcome::Accepted hpApplied=35 healthBefore=780 healthAfter=745
[2026.10.31-22.00.05:000][6]LogTemp: Display: [FrameworkProof] invariant targetHPBefore=800 targetHPAfter=745 expectedHP=745 acceptedHits=2 appliedDamage=55
[2026.10.31-22.00.05:000][7]LogTemp: Display: [FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=2 attacks=2
"""

class TestCompareRuns(unittest.TestCase):

    def test_pure_lf(self):
        script_path = REVIEWS_DIR / "compare_runs.py"
        self.assertTrue(script_path.exists())
        raw = script_path.read_bytes()
        self.assertNotIn(b"\r", raw, "compare_runs.py must be pure LF")

    def test_synthetic_identical_runs(self):
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as f1, \
             tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as f2:
            f1.write(SYNTHETIC_RUN_A)
            f2.write(SYNTHETIC_RUN_B_IDENTICAL)
            p1, p2 = Path(f1.name), Path(f2.name)

        try:
            r1 = compare_runs.parse_log_file(p1)
            r2 = compare_runs.parse_log_file(p2)
            ok, fails, diffs = compare_runs.compare_runs([r1, r2], damage_tol=0.0, score_tol=1e-3)
            self.assertTrue(ok, f"Expected identical runs to pass, got fails: {fails}")
            self.assertEqual(diffs["damage"], 0.0)
        finally:
            p1.unlink()
            p2.unlink()

    def test_synthetic_missing_hit(self):
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as f1, \
             tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as f2:
            f1.write(SYNTHETIC_RUN_A)
            f2.write(SYNTHETIC_RUN_MISSING_HIT)
            p1, p2 = Path(f1.name), Path(f2.name)

        try:
            r1 = compare_runs.parse_log_file(p1)
            r2 = compare_runs.parse_log_file(p2)
            ok, fails, diffs = compare_runs.compare_runs([r1, r2])
            self.assertFalse(ok, "Expected missing hit run to fail comparison")
            self.assertTrue(any("acceptedHits mismatch" in f for f in fails))
        finally:
            p1.unlink()
            p2.unlink()

    def test_synthetic_damage_diff(self):
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as f1, \
             tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as f2:
            f1.write(SYNTHETIC_RUN_A)
            f2.write(SYNTHETIC_RUN_DAMAGE_DIFF)
            p1, p2 = Path(f1.name), Path(f2.name)

        try:
            r1 = compare_runs.parse_log_file(p1)
            r2 = compare_runs.parse_log_file(p2)
            ok, fails, diffs = compare_runs.compare_runs([r1, r2], damage_tol=0.0)
            self.assertFalse(ok, "Expected damage difference to fail")
            self.assertTrue(any("total damage mismatch" in f or "hpApplied diff" in f for f in fails))
        finally:
            p1.unlink()
            p2.unlink()

    def test_synthetic_order_swapped(self):
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as f1, \
             tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as f2:
            f1.write(SYNTHETIC_RUN_A)
            f2.write(SYNTHETIC_RUN_SWAPPED_ORDER)
            p1, p2 = Path(f1.name), Path(f2.name)

        try:
            r1 = compare_runs.parse_log_file(p1)
            r2 = compare_runs.parse_log_file(p2)
            ok, fails, diffs = compare_runs.compare_runs([r1, r2])
            self.assertFalse(ok, "Expected swapped order to fail")
            self.assertTrue(any("mismatch" in f for f in fails))
        finally:
            p1.unlink()
            p2.unlink()

    def test_real_qa004_fps_parity_runs(self):
        """Integration test on Claude/B_QA004 fixed30, fixed60, fixed120."""
        b_qa004 = REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_QA004"
        logs = [
            b_qa004 / "fixed30/editor_raw.log",
            b_qa004 / "fixed60/editor_raw.log",
            b_qa004 / "fixed120/editor_raw.log",
        ]
        for l in logs:
            self.assertTrue(l.exists(), f"Log missing: {l}")

        runs = [compare_runs.parse_log_file(l, ignore_duplicate_hits=True) for l in logs]
        ok, fails, diffs = compare_runs.compare_runs(runs, damage_tol=0.0, score_tol=0.05, range_tol=10.0)
        self.assertTrue(ok, f"Expected fixed30/60/120 to pass FPS parity comparison, got: {fails}")
        self.assertEqual(diffs["damage"], 0.0)
        self.assertEqual(runs[0]["counts"]["accepted_hits"], 2)
        self.assertEqual(runs[1]["counts"]["accepted_hits"], 2)
        self.assertEqual(runs[2]["counts"]["accepted_hits"], 2)
        self.assertEqual(runs[0]["counts"]["total_damage"], 55.0)
        self.assertEqual(runs[1]["counts"]["total_damage"], 55.0)
        self.assertEqual(runs[2]["counts"]["total_damage"], 55.0)
        
        # Verify duplicate hits scale with frame rate
        self.assertEqual(runs[0]["counts"]["duplicate_hits"], 2)
        self.assertEqual(runs[1]["counts"]["duplicate_hits"], 4)
        self.assertEqual(runs[2]["counts"]["duplicate_hits"], 9)

if __name__ == "__main__":
    unittest.main()
