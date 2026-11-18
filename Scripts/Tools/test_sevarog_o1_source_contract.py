import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("sevarog_o1_inputs", ROOT / "Scripts/Editor/sevarog_o1_inputs.py")
o1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(o1)


class ApprovedO1SourceContract(unittest.TestCase):
    def test_float32_tolerance_is_bounded_and_nonfinite_fails_closed(self):
        self.assertTrue(o1.approved_float_matches(0.6000000238418579, 0.6))
        self.assertTrue(o1.approved_float_matches(13.00005, 13.0))
        self.assertFalse(o1.approved_float_matches(13.00011, 13.0))
        self.assertFalse(o1.approved_float_matches(float("nan"), 0.6))
        self.assertFalse(o1.approved_float_matches("not-a-number", 0.6))

    def test_owner_decision_excerpt_and_values_are_bound(self):
        values = o1.load_approved_values(ROOT)
        self.assertEqual(values, o1.EXPECTED_VALUES)

    def test_historical_pending_manifest_is_not_promoted(self):
        manifest = json.loads((ROOT / "Documentation/Boss/BK76_SEVAROG_DEFINITION_INPUTS_PENDING.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["manifest_state"], "PENDING")
        self.assertFalse(manifest["authoring_evidence"])
        self.assertFalse(manifest["executable"])
        self.assertIn("sevarog_o1_inputs.json", manifest["warning"])

    def test_authoring_scripts_use_separate_o1_source(self):
        phase = (ROOT / "Scripts/Editor/ensure_bk56_60_sevarog_initial_phase.py").read_text(encoding="utf-8")
        encounter = (ROOT / "Scripts/Editor/author_framework_encounter_definition.py").read_text(encoding="utf-8")
        self.assertIn("load_approved_values", phase)
        self.assertIn("load_approved_values", encounter)
        self.assertIn("approved_float_matches(current_stats[key], value)", phase)
        self.assertIn("approved_float_matches(current_phase[key], value)", phase)
        self.assertIn("RESULT ALREADY_CURRENT", phase)
        self.assertIn("approved_float_matches(actual, expected)", encounter)
        self.assertIn("O1_AUTHORED", phase)
        self.assertIn("existing target has wrong class", encounter)
        self.assertIn("field_manifest.json", encounter)

    def test_locked_runner_is_full_editor_and_staged(self):
        runner = (ROOT / "Scripts/Editor/run_BK_SEVAROG_O1_locked.ps1").read_text(encoding="utf-8")
        for value in ("C-1155", "CreateNew", "owner_token", "-nosound", "phase_dry", "phase_write",
                      "encounter_dry", "encounter_write", "encounter_readback"):
            self.assertIn(value, runner)
        self.assertNotIn("UnrealEditor-Cmd", runner)
        self.assertNotIn("Automation RunTests", runner)


if __name__ == "__main__":
    unittest.main()
