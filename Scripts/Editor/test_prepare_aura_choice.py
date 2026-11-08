"""Offline safety contracts for the aura owner-choice planner."""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import subprocess
import sys
import unittest

from Scripts.Editor import prepare_aura_choice as planner


class PrepareAuraChoiceContract(unittest.TestCase):
    def test_three_options_have_expected_asset_and_attachment(self):
        current = planner.build_plan("current")
        boosted = planner.build_plan("boosted")
        spine = planner.build_plan("boosted_on_spine")
        self.assertEqual(current["proposed_state"]["asset"], planner.SOURCE_ASSET)
        self.assertEqual(boosted["proposed_state"]["asset"], planner.BOOST_ASSET)
        self.assertEqual(spine["proposed_state"]["asset"], planner.BOOST_ASSET)
        self.assertEqual(current["proposed_state"]["attachment"]["socket"], "NAME_None")
        self.assertEqual(boosted["proposed_state"]["attachment"]["socket"], "NAME_None")
        self.assertEqual(spine["proposed_state"]["attachment"]["socket"], "spine_03")

    def test_default_is_read_only_and_manifest_requires_readback(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(planner.main([]), 0)
        plan = json.loads(output.getvalue())
        self.assertEqual(plan["mode"], "dry-run-only")
        self.assertFalse(plan["apply_manifest"]["executed"])
        self.assertTrue(plan["apply_manifest"]["requires_owner_choice"])
        self.assertTrue(plan["apply_manifest"]["requires_complete_readback"])
        self.assertFalse(plan["apply_manifest"]["asset_save_permitted"])
        self.assertIn("component asset", " ".join(plan["readback_required"]))
        self.assertIn("dirty state", " ".join(plan["readback_required"]))

    def test_apply_and_save_flags_are_refused(self):
        script = pathlib.Path(planner.__file__)
        for flag in ("--apply", "--save"):
            with self.subTest(flag=flag):
                result = subprocess.run(
                    [sys.executable, str(script), flag],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("are refused", result.stderr)

    def test_planner_is_offline_and_has_explicit_rollback(self):
        source = pathlib.Path(planner.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import unreal", source)
        self.assertNotIn("save_loaded_asset", source)
        self.assertNotIn("set_editor_property", source)
        rollback = planner.build_plan("boosted_on_spine")["rollback_manifest"]
        self.assertIn("restore_attachment", rollback)
        self.assertIn("restore_active_state", rollback)
        self.assertFalse(rollback["asset_save_permitted"])


if __name__ == "__main__":
    unittest.main()
