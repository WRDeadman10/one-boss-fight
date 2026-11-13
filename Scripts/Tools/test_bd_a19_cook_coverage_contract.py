#!/usr/bin/env python3
"""Offline contract test (BD-A19) verifying DefaultGame.ini cook coverage for Sevarog & Greystone assets."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GAME_INI = ROOT / "Config" / "DefaultGame.ini"
AUTHOR_SEVAROG = ROOT / "Scripts" / "Editor" / "author_sevarog_draft_cards.py"


class BdA19CookCoverageContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ini = DEFAULT_GAME_INI.read_text(encoding="utf-8")
        self.cook_roots = re.findall(r'\+DirectoriesToAlwaysCook=\(Path="([^"]+)"\)', self.ini)

    def _is_cooked(self, game_path: str) -> bool:
        return any(game_path == root or game_path.startswith(root + "/") for root in self.cook_roots)

    def test_authored_greystone_and_sevarog_assets_covered_by_cook_roots(self) -> None:
        greystone_dir = ROOT / "Content" / "OneBossFight" / "Player" / "Greystone"
        for uasset in greystone_dir.glob("*.uasset"):
            game_path = f"/Game/OneBossFight/Player/Greystone/{uasset.stem}"
            self.assertTrue(self._is_cooked(game_path), f"Uncooked Greystone asset: {game_path}")

        sevarog_dir = ROOT / "Content" / "OneBossFight" / "Data" / "Sevarog"
        for uasset in sevarog_dir.glob("*.uasset"):
            game_path = f"/Game/OneBossFight/Data/Sevarog/{uasset.stem}"
            self.assertTrue(self._is_cooked(game_path), f"Uncooked Sevarog data asset: {game_path}")

        # Planned S6-S8 cards & S1-S8 Sevarog animations
        author_text = AUTHOR_SEVAROG.read_text(encoding="utf-8")
        for planned_card in (
            "DA_Move_Sevarog_Ultimate_Swing_120fps_C1277",
            "DA_Move_Sevarog_Subjugation_C1277",
            "DA_Move_Sevarog_Soul_Siphon_C1277",
        ):
            self.assertIn(planned_card, author_text)
            self.assertTrue(self._is_cooked(f"/Game/OneBossFight/Data/Sevarog/{planned_card}"))
        self.assertTrue(self._is_cooked("/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Soul_Siphon"))


if __name__ == "__main__":
    unittest.main()
