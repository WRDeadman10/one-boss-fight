"""No-write contracts for the owner-gated camera-default migration planner."""
import ast
from pathlib import Path
import unittest

from Scripts.Tools import plan_camera_default as planner


class CameraDefaultPlanTests(unittest.TestCase):
    def test_missing_or_invalid_owner_choice_cannot_produce_a_migration_plan(self):
        missing = planner.build_plan(None, None)
        self.assertEqual(missing["status"], "WAITING_FOR_OWNER")
        self.assertNotIn("proposed_config", missing)
        invalid = planner.build_plan("A", "C-1051")
        self.assertEqual(invalid["status"], "INVALID_CHOICE")
        self.assertNotIn("proposed_config", invalid)
        no_reference = planner.build_plan("B", " ")
        self.assertEqual(no_reference["status"], "WAITING_FOR_OWNER")
        self.assertNotIn("proposed_config", no_reference)

    def test_current_owner_brief_choices_produce_plan_only_with_record_reference(self):
        result = planner.build_plan("BC", "TEST-ONLY-REF")
        self.assertEqual(result["status"], "READY_FOR_REVIEW")
        self.assertFalse(result["apply_available"])
        self.assertFalse(result["save_available"])
        self.assertFalse(result["source_mutation"])
        self.assertFalse(result["config_mutation"])
        self.assertFalse(result["decision_reference_is_verified"])
        self.assertFalse(result["owner_approval_authenticated"])
        config = result["proposed_config"]
        self.assertEqual(config["file"], "Config/DefaultGame.ini")
        self.assertEqual(config["applies_to"], ["Development", "Shipping"])
        self.assertEqual(config["section_proposal"], "[/Script/OneBossFight.RPGCameraRig]")
        self.assertEqual(config["keys_proposal"], {
            "bDefaultHideBossInside": "true",
            "bDefaultLockOnFraming": "true",
        })
        self.assertIn("two bool UPROPERTY(Config)", config["runtime_type_proposal"])
        self.assertEqual(config["missing_or_invalid_fallback"], "false/false (all behavior disabled)")
        self.assertEqual(result["runtime_plan"]["enabled_behaviors"], ["HideBossInside", "LockOnFraming"])
        self.assertIn("outside !UE_BUILD_SHIPPING", result["runtime_plan"]["production_path"])
        self.assertIn("Development-only test CVar", result["runtime_plan"]["cvar_and_config_rule"])
        self.assertTrue(any("same-run activation witness" in gate for gate in result["gates"]))
        self.assertFalse(any("legacy" in gate.lower() for gate in result["gates"]))
        self.assertIn("C-1090 and C-1105 cover bounded B+C", result["evidence_gap"])
        self.assertIn("C-1105", result["evidence_gap"])

    def test_planner_has_no_file_write_apply_or_save_api(self):
        tree = ast.parse(Path(planner.__file__).read_text(encoding="utf-8"))
        calls = {
            node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
            for node in ast.walk(tree) if isinstance(node, ast.Call)
        }
        forbidden = {"write_text", "write_bytes", "unlink", "remove", "replace", "mkdir", "rmdir", "save", "apply"}
        self.assertFalse(calls & forbidden, sorted(calls & forbidden))
        self.assertFalse(any(arg in {"--output", "--apply", "--save"} for arg in planner.main.__code__.co_consts))


if __name__ == "__main__":
    unittest.main(verbosity=2)
