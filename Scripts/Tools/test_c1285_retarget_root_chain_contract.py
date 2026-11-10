#!/usr/bin/env python3
"""Offline TDD contract test (C-1285): Greystone retarget scripts must set Root chain GloballyScaled.

Per Claude directive [C-1285], this contract intentionally FAILS today until Lead updates
retarget_er_fit_candidate.py and retarget_pack_to_greystone.py to map Root->Root with
IKRetargeterController.set_retarget_chain_settings / GLOBALLY_SCALED translation mode.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ER_RETARGET = ROOT / "Scripts" / "Editor" / "retarget_er_fit_candidate.py"
PACK_RETARGET = ROOT / "Scripts" / "Editor" / "retarget_pack_to_greystone.py"
SWITCH_PLAN = ROOT / "Documentation" / "Boss" / "SWITCH_PLAN.md"
CHECKLIST = ROOT / "Documentation" / "Boss" / "C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md"


class C1285RetargetRootChainContractTests(unittest.TestCase):
    def test_retarget_er_fit_candidate_sets_root_chain_globally_scaled(self) -> None:
        source = ER_RETARGET.read_text(encoding="utf-8")
        self.assertIn("set_retarget_chain_settings", source)
        self.assertIn("GLOBALLY_SCALED", source)
        self.assertIn("translation_mode", source)

    def test_retarget_pack_to_greystone_sets_root_chain_globally_scaled(self) -> None:
        source = PACK_RETARGET.read_text(encoding="utf-8")
        self.assertIn("set_retarget_chain_settings", source)
        self.assertIn("GLOBALLY_SCALED", source)
        self.assertIn("translation_mode", source)

    def test_docs_record_c1284_baseline_and_c1285_retarget_contract(self) -> None:
        plan = SWITCH_PLAN.read_text(encoding="utf-8")
        checklist = CHECKLIST.read_text(encoding="utf-8")
        for token in ("GLOBALLY_SCALED", "set_retarget_chain_settings", "get_bone_pose_for_time"):
            self.assertIn(token, plan)
        for token in ("76.3 cm", "243.6", "GLOBALLY_SCALED", "KI-052"):
            self.assertIn(token, checklist)


if __name__ == "__main__":
    unittest.main()
