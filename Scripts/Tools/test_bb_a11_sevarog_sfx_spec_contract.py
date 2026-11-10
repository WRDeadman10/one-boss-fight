#!/usr/bin/env python3
"""Offline contract test for BB-A11..A13 Sevarog card SFX specification."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "Documentation" / "Boss" / "BB_A11_A13_SEVAROG_CARD_SFX_SPEC.md"

EXPECTED_CARDS = (
    "`S1` (`Move_Sevarog_Swing1_Medium`)",
    "`S2` (`Move_Sevarog_Swing2_Medium`)",
    "`S3` (`Move_Sevarog_Swing3_Slow`)",
    "`S4` (`Move_Sevarog_Speedburst`)",
    "`S5` (`Move_Sevarog_Swing1_FAST_v2`)",
    "`S6_Cand` (`Ultimate_Swing_120fps`)",
    "`S7_Cand` (`Subjugation`)",
    "`S8_Cand` (`Soul_Siphon`)",
)


class BbA11SevarogSfxSpecContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SPEC_PATH.read_text(encoding="utf-8")

    def test_all_sevarog_cards_and_candidates_are_mapped(self) -> None:
        for card_label in EXPECTED_CARDS:
            self.assertIn(card_label, self.text, f"Missing card mapping: {card_label}")

    def test_every_cited_game_sound_asset_exists_on_disk(self) -> None:
        game_paths = sorted(set(re.findall(r"`(/Game/[^`]+)`", self.text)))
        self.assertGreaterEqual(len(game_paths), 15)
        missing = []
        for asset_path in game_paths:
            rel = asset_path.removeprefix("/Game/")
            uasset = ROOT / "Content" / f"{rel}.uasset"
            if not uasset.is_file():
                missing.append((asset_path, str(uasset)))
        self.assertEqual(missing, [], f"Non-existent /Game cue assets cited: {missing}")

    def test_spec_maintains_opt_in_nullptr_default_and_honest_sevarog_scope(self) -> None:
        self.assertIn("nullptr", self.text)
        self.assertIn("FRPGBossCue", self.text)
        self.assertIn("vocal efforts and UI/lore cues only", self.text)
        self.assertIn("Zero pack assets modified", self.text)


if __name__ == "__main__":
    unittest.main()
