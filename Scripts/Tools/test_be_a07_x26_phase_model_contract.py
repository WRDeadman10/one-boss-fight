#!/usr/bin/env python3
"""Offline contract test (BE-A07) verifying X26 C++ AdditionalPhaseIds & C1278 acceptance alignment."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARD_H = ROOT / "Source" / "OneBossFight" / "Player" / "RPGBossMoveCard.h"
MODEL_CPP = ROOT / "Source" / "OneBossFight" / "Player" / "RPGBossMoveModel.cpp"
PROFILE_CPP = ROOT / "Source" / "OneBossFight" / "Player" / "RPGBossFrameworkProfile.cpp"
ACCEPTANCE_DOC = ROOT / "Documentation" / "Boss" / "C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md"


class BeA07X26PhaseModelContractTests(unittest.TestCase):
    def test_cpp_additional_phase_ids_and_pool_sharing_present(self) -> None:
        card_h = CARD_H.read_text(encoding="utf-8")
        model_cpp = MODEL_CPP.read_text(encoding="utf-8")
        profile_cpp = PROFILE_CPP.read_text(encoding="utf-8")
        acceptance = ACCEPTANCE_DOC.read_text(encoding="utf-8")

        self.assertIn("TArray<FName> AdditionalPhaseIds;", card_h)
        self.assertIn(
            'if (!RPGBossMoveCards::IsEligibleInPhase(Card->Spec(),S.PhaseId)) return Refuse(Error,TEXT("MoveModel.Phase"));',
            model_cpp,
        )
        self.assertIn("AddCandidateCooldownToPhasePools(C.Card->Spec(),C.CooldownSeconds,One,P->PhaseTwoId,PoolOne,PoolTwo);", profile_cpp)
        self.assertIn("PhasePoolCannotStarve(PoolTwo,P->AttackCount)", profile_cpp)
        for token in ("X26-P1", "X26-P2", "X26-S6", "X26-S7a", "X26-S7b", "X26-S8a", "X26-S8b"):
            self.assertIn(token, acceptance)


if __name__ == "__main__":
    unittest.main()
