#!/usr/bin/env python3
"""Offline contract test (BE-A02) verifying A_C1285_GREYSTONE_ROOTFIX dry-run metrics & source root XY."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRYRUN_LOG = ROOT / "Docs" / "BossCombatReview" / "Execution" / "Claude" / "A_C1285_GREYSTONE_ROOTFIX" / "fix_dryrun.log"
DRYRUN_STATUS = ROOT / "Docs" / "BossCombatReview" / "Execution" / "Claude" / "A_C1285_GREYSTONE_ROOTFIX" / "fix_dryrun_status.txt"
DOC_PATH = ROOT / "Documentation" / "Boss" / "BE_A01_A05_BATCH1_RM_DRYRUN_AUDIT.md"


class BeA02RootfixDryrunContractTests(unittest.TestCase):
    def test_dryrun_log_confirms_backstep_source_root_and_none_mode(self) -> None:
        self.assertIn("FIX_dryrun exit=0", DRYRUN_STATUS.read_text(encoding="utf-8"))
        log = DRYRUN_LOG.read_text(encoding="utf-8", errors="ignore")
        for token in (
            "MODE=DRY_RUN",
            "SOURCE AN_ER_Backstep_Mixamo_V2 skeleton=SK_CombatMannequin enable_root_motion=True root_xy_cm=156.75 pelvis_xy_cm=1.36",
            "RIG IK_CombatMannequin root chain present: Root",
            "RIG IK_Fit_Greystone root chain present: Root",
            "fk_translation_mode=<RetargetTranslationMode.NONE: 0>",
            "RESULT=PASS dry_run=1 saves=0",
        ):
            self.assertIn(token, log)
        doc = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("156.75", doc)
        self.assertIn("BLOCKED", doc)


if __name__ == "__main__":
    unittest.main()
