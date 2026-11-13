#!/usr/bin/env python3
"""Offline contract for C-1289 Decision 1 skeleton-scaled Greystone root-motion pairing."""

from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "Saved" / "ERFitRM_20261111_023747.json"
GREYSTONE_RM4_LINES = ROOT / "Docs" / "BossCombatReview" / "Execution" / "Claude" / "P_C1282_GREYSTONE_RM4_GREYSTONE" / "data_lines.txt"
MANNEQUIN_RM4_LINES = ROOT / "Docs" / "BossCombatReview" / "Execution" / "Claude" / "P_C1282_GREYSTONE_RM4_MANNEQUIN" / "data_lines.txt"

BACKSTEP_BASE_BAND = (84.0, 98.0)
QUICK_ROLL_BASE_BAND = (215.0, 290.0)
PAIRING_TOLERANCE = 0.10


def load_backstep_root_ratio(manifest_path: Path = MANIFEST_PATH) -> float:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    for clip in data.get("clips", []):
        if "Backstep" in clip.get("source", "") and clip.get("enable_root_motion"):
            ratio = clip.get("root_ratio")
            if not isinstance(ratio, (int, float)) or not math.isfinite(ratio) or ratio <= 0.0:
                raise AssertionError(f"Invalid backstep root_ratio in {manifest_path}: {ratio!r}")
            return float(ratio)
    raise AssertionError(f"No root-motion-enabled backstep clip found in {manifest_path}")


def scaled_band(base_band: tuple[float, float], ratio: float) -> tuple[float, float]:
    return (base_band[0] * ratio, base_band[1] * ratio)


def parse_trial_distances(lines_path: Path, move: str) -> list[float]:
    pattern = re.compile(rf"TRIAL\b.*\bmove={re.escape(move)}\b.*\bdistance_cm=(\d+(?:\.\d+)?)")
    return [float(m.group(1)) for m in pattern.finditer(lines_path.read_text(encoding="utf-8"))]


def evaluate_pairing(mannequin_mean: float, greystone_mean: float, ratio: float) -> tuple[float, bool]:
    normalized = greystone_mean / ratio
    delta_frac = abs(normalized - mannequin_mean) / mannequin_mean
    return delta_frac, delta_frac <= PAIRING_TOLERANCE


class C1289GreystonePairingContractTest(unittest.TestCase):
    def test_root_ratio_read_from_manifest_and_scales_bands(self) -> None:
        ratio = load_backstep_root_ratio()
        self.assertGreater(ratio, 1.0)
        back_lo, back_hi = scaled_band(BACKSTEP_BASE_BAND, ratio)
        roll_lo, roll_hi = scaled_band(QUICK_ROLL_BASE_BAND, ratio)
        self.assertAlmostEqual(back_lo, BACKSTEP_BASE_BAND[0] * ratio, places=9)
        self.assertAlmostEqual(back_hi, BACKSTEP_BASE_BAND[1] * ratio, places=9)
        self.assertAlmostEqual(roll_lo, QUICK_ROLL_BASE_BAND[0] * ratio, places=9)
        self.assertAlmostEqual(roll_hi, QUICK_ROLL_BASE_BAND[1] * ratio, places=9)

    def test_rm4_backstep_passes_scaled_band_and_10pct_pairing(self) -> None:
        ratio = load_backstep_root_ratio()
        man_trials = parse_trial_distances(MANNEQUIN_RM4_LINES, "backstep")
        grey_trials = parse_trial_distances(GREYSTONE_RM4_LINES, "backstep")
        self.assertEqual(len(man_trials), 5)
        self.assertEqual(len(grey_trials), 5)

        back_lo, back_hi = scaled_band(BACKSTEP_BASE_BAND, ratio)
        self.assertTrue(all(math.floor(back_lo) <= d <= math.ceil(back_hi) for d in grey_trials), grey_trials)

        man_mean = sum(man_trials) / len(man_trials)
        grey_mean = sum(grey_trials) / len(grey_trials)
        delta_frac, ok = evaluate_pairing(man_mean, grey_mean, ratio)
        self.assertTrue(ok, f"Pairing delta {delta_frac:.4f} exceeded 10%")

    def test_rm4_grey_quick_roll_remains_fail_closed_until_bk1(self) -> None:
        ratio = load_backstep_root_ratio()
        man_roll_trials = parse_trial_distances(MANNEQUIN_RM4_LINES, "quick_roll")
        grey_roll_trials = parse_trial_distances(GREYSTONE_RM4_LINES, "quick_roll")
        self.assertEqual(len(man_roll_trials), 5)
        self.assertEqual(len(grey_roll_trials), 4)
        self.assertTrue(all(d == 0.0 for d in grey_roll_trials))
        man_roll_mean = sum(man_roll_trials) / len(man_roll_trials)
        grey_roll_mean = sum(grey_roll_trials) / len(grey_roll_trials)
        _, ok = evaluate_pairing(man_roll_mean, grey_roll_mean, ratio)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
