#!/usr/bin/env python3
"""Offline disk existence contract test for active SFX & voice-bark specs (BC-A26..A28)."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ACTIVE_CLEAN_SFX_SPECS = (
    "Documentation/Boss/SFX_05_BATCH3_CANDIDATE_SPEC.md",
    "Documentation/Boss/SFX_07_BATCH4_CANDIDATE_SPEC.md",
    "Documentation/Boss/SFX_08_BATCH5_CANDIDATE_SPEC.md",
    "Documentation/Boss/SFX_09_BATCH6_CANDIDATE_SPEC.md",
    "Documentation/Boss/SFX_10_BATCH7_CANDIDATE_SPEC.md",
    "Documentation/Boss/SFX_11_BATCH8_CANDIDATE_SPEC.md",
    "Documentation/Boss/SFX_12_BATCH9_CANDIDATE_SPEC.md",
    "Documentation/Boss/BB_A11_A13_SEVAROG_CARD_SFX_SPEC.md",
    "Documentation/Boss/BB_A14_SEVAROG_VOICE_BARKS_SPEC.md",
)


class BcA26SfxSpecsDiskContractTests(unittest.TestCase):
    def test_all_active_sfx_and_bark_specs_resolve_100_percent_on_disk(self) -> None:
        missing = []
        total_paths = 0
        for rel in ACTIVE_CLEAN_SFX_SPECS:
            text = (ROOT / rel).read_text(encoding="utf-8")
            paths = sorted(set(re.findall(r"(/Game/[A-Za-z0-9_./-]+)", text)))
            for gp in paths:
                if "*" in gp or ".." in gp or gp.endswith("/"):
                    continue
                total_paths += 1
                asset = gp.split(".", 1)[0].removeprefix("/Game/")
                uasset = ROOT / "Content" / f"{asset}.uasset"
                if not uasset.is_file() and not (ROOT / "Content" / asset).is_dir():
                    missing.append((rel, gp))
        self.assertGreaterEqual(total_paths, 100)
        self.assertEqual(missing, [], f"Missing /Game assets in SFX specs: {missing}")


if __name__ == "__main__":
    unittest.main()
