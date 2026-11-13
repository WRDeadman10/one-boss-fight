#!/usr/bin/env python3
"""Offline contract test (BF-A02) verifying fix_greystone_fit_root_motion.py safety & root XY gates."""

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROOTFIX_PATH = ROOT / "Scripts" / "Editor" / "fix_greystone_fit_root_motion.py"
DOC_PATH = ROOT / "Documentation" / "Boss" / "BF_A01_A05_BATCH1_RETARGET_SOURCE_AUDIT.md"


class BfA02RetargetRootfixSourceContractTests(unittest.TestCase):
    def test_rootfix_script_enforces_globally_scaled_root_probe_and_rollback(self) -> None:
        source = ROOTFIX_PATH.read_text(encoding="utf-8")
        ast.parse(source, filename=str(ROOTFIX_PATH))
        for token in (
            'OUT_ROOT = "/Game/OneBossFight/Player/FitTest/Greystone"',
            'SUFFIX = "_Fit_GreystoneRM"',
            "RetargetTranslationMode.GLOBALLY_SCALED",
            "set_retarget_chain_settings",
            'AnimationLibrary.get_bone_pose_for_time(seq, bone',
            'backstep["output_root_xy_cm"] > 0.5 * backstep["source_root_xy_cm"]',
            "ROLLBACK_DELETED=",
            "refusing overwrite:",
        ):
            self.assertIn(token, source)
        self.assertNotIn("SaveDirectory", source)
        doc = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("BLOCKED", doc)
        self.assertIn("ERFitRM_", doc)


if __name__ == "__main__":
    unittest.main()
