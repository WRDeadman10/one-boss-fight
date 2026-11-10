#!/usr/bin/env python3
"""Offline contract test (BD-A03..A04) reconciling refreshed bb_a15 28 resolved textures."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROBE_JSON = ROOT / "Saved" / "BossCombatReview" / "bb_a15_greystone_materials_probe.json"
DOC_PATH = ROOT / "Documentation" / "Boss" / "BD_A03_A04_GREYSTONE_TEXTURES_RECONCILE.md"


class BdA03GreystoneTexturesContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads(PROBE_JSON.read_text(encoding="utf-8"))
        self.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_probe_json_and_reconcile_match_28_textures_zero_foreign_leaks(self) -> None:
        child_tex = self.data["child_bp"]["unique_textures"]
        parent_tex = self.data["parent_bp"]["unique_textures"]
        self.assertEqual(len(child_tex), 28)
        self.assertEqual(child_tex, parent_tex)
        for path in child_tex:
            self.assertTrue(
                path.startswith("/Game/ParagonGreystone/Characters/Global/")
                or path.startswith("/Engine/"),
                f"Unexpected foreign texture outside ParagonGreystone/Global or Engine: {path}",
            )
        self.assertIn("`28` unique textures", self.doc)
        self.assertIn("`26` Shared Paragon Greystone Global Textures", self.doc)


if __name__ == "__main__":
    unittest.main()
