#!/usr/bin/env python3
"""Offline contract test (BC-A14) for Sevarog signature cards S6..S8 draft spec."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = ROOT / "Documentation" / "Boss" / "BC_A11_A15_SEVAROG_SIGNATURE_CARDS_DRAFT.md"
SFX_SPEC_PATH = ROOT / "Documentation" / "Boss" / "BB_A11_A13_SEVAROG_CARD_SFX_SPEC.md"

CARDS = (
    {
        "move_id": "Move_Sevarog_Ultimate_Swing",
        "sequence": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Ultimate_Swing_120fps",
        "commit": 0.600,
        "active_start": 0.667,
        "active_end": 0.867,
        "recovery_end": 2.633,
        "clip_len": 2.633,
        "min_range": 100.0,
        "max_range": 320.0,
        "cone": 360.0,
    },
    {
        "move_id": "Move_Sevarog_Subjugation",
        "sequence": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Subjugation",
        "commit": 0.733,
        "active_start": 0.800,
        "active_end": 0.867,
        "recovery_end": 2.867,
        "clip_len": 2.867,
        "min_range": 300.0,
        "max_range": 900.0,
        "cone": 140.0,
    },
    {
        "move_id": "Move_Sevarog_Soul_Siphon",
        "sequence": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Soul_Siphon",
        "commit": 0.200,
        "active_start": 0.267,
        "active_end": 1.267,
        "recovery_end": 1.833,
        "clip_len": 1.833,
        "min_range": 250.0,
        "max_range": 750.0,
        "cone": 90.0,
    },
)


class BcA14SevarogSignatureCardsContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = DOC_PATH.read_text(encoding="utf-8")

    def test_timeline_and_eligibility_bounds_match_rpg_boss_move_card_rules(self) -> None:
        for card in CARDS:
            self.assertIn(card["move_id"], self.text)
            self.assertLessEqual(card["commit"], card["active_start"])
            self.assertLess(card["active_start"], card["active_end"])
            self.assertLessEqual(card["active_end"], card["recovery_end"])
            self.assertLessEqual(card["recovery_end"], card["clip_len"])
            self.assertGreaterEqual(card["min_range"], 0.0)
            self.assertGreaterEqual(card["max_range"], card["min_range"])
            self.assertGreater(card["cone"], 0.0)
            self.assertLessEqual(card["cone"], 360.0)

    def test_all_cited_game_assets_exist_on_disk(self) -> None:
        game_paths = sorted(set(re.findall(r"`(/Game/[^`]+)`", self.text)))
        self.assertGreaterEqual(len(game_paths), 4)
        missing = []
        for asset_path in game_paths:
            rel = asset_path.removeprefix("/Game/")
            uasset = ROOT / "Content" / f"{rel}.uasset"
            if not uasset.is_file():
                missing.append((asset_path, str(uasset)))
        self.assertEqual(missing, [], f"Missing /Game assets on disk: {missing}")

    def test_cues_default_empty_opt_in_and_module_gaps_documented(self) -> None:
        self.assertIn("`[]` (empty by default)", self.text)
        self.assertIn("RPGBossCue::DistinctChannels", self.text)
        self.assertIn("Target-Positioned AoE Spawn", self.text)
        self.assertIn("Continuous Channel Ticks", self.text)
        self.assertIn("never repurpose `RPGBossBleed`", self.text)
        # Confirm alignment with BB-A11..A13 SFX spec
        sfx_text = SFX_SPEC_PATH.read_text(encoding="utf-8")
        for clip_name in ("Ultimate_Swing_120fps", "Subjugation", "Soul_Siphon"):
            self.assertIn(clip_name, sfx_text)


if __name__ == "__main__":
    unittest.main()
