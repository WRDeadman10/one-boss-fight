#!/usr/bin/env python3
"""Offline contract test for C-1278 X26 acceptance table & C-1279 BC-A10 Death_front notes."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE_DOC = ROOT / "Documentation" / "Boss" / "C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md"
BC_A10_DOC = ROOT / "Documentation" / "Boss" / "BC_A10_SEVAROG_STUN_INTRO_FRAME_NOTES.md"
MOVE_EXECUTOR_CPP = ROOT / "Source" / "OneBossFight" / "Boss" / "RPGFrameworkMoveExecutor.cpp"
BOSS_CHAR_CPP = ROOT / "Source" / "OneBossFight" / "Boss" / "RPGFrameworkBossCharacter.cpp"


class C1278X26AcceptanceAndDeathContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.acceptance = ACCEPTANCE_DOC.read_text(encoding="utf-8")
        self.bc_a10 = BC_A10_DOC.read_text(encoding="utf-8")
        self.executor_cpp = MOVE_EXECUTOR_CPP.read_text(encoding="utf-8")
        self.boss_cpp = BOSS_CHAR_CPP.read_text(encoding="utf-8")

    def test_x26_acceptance_log_tokens_match_cpp_exactly(self) -> None:
        log_tokens = (
            "[FrameworkProof] area_effect state=Released",
            "[FrameworkProof] area_effect state=Resolve",
            "[FrameworkProof] area_effect_damage",
            "[FrameworkProof] area_effect_snare state=Started",
            "[FrameworkProof] area_effect_snare state=Ended",
            "[FrameworkProof] channel state=Started",
            "[FrameworkProof] channel_tick",
            "[FrameworkProof] channel state=Ended",
            "[FrameworkProof] phase_transition",
        )
        for token in log_tokens:
            self.assertIn(token, self.acceptance)
            self.assertTrue(
                token in self.executor_cpp or token in self.boss_cpp,
                f"Expected verbatim C++ log token: {token}",
            )
        for ref in ("MoveModel.Phase", "90–150 cm", "radius=225", "scale=0.55", "seconds=2.5"):
            self.assertIn(ref, self.acceptance)

    def test_bc_a10_death_front_frame_citations_present(self) -> None:
        self.assertIn("Death_front_sheet.png", self.bc_a10)
        self.assertIn("Claude/P_C1278_SEVAROGDEATH", self.bc_a10)
        for span in ("002–009", "010–012", "013–015", "0.967"):
            self.assertIn(span, self.bc_a10)


if __name__ == "__main__":
    unittest.main()
