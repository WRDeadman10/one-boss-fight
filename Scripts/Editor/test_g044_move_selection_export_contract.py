"""Read-only source contract for Lead-run G044 attack-selection export."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/Editor/export_g044_move_selection_readonly.py"


class G044MoveSelectionExportContract(unittest.TestCase):
    def test_script_identifies_g044_and_follows_boss_definition(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("DA_Sevarog_G044_Encounter", source)
        self.assertIn("boss_definition", source)
        self.assertIn("attack_tracker", source)
        self.assertIn("low_sweep", source)
        self.assertIn("phase_records", source)
        self.assertIn("a4_records", source)
        self.assertIn("a4_phase_range_fields", source)

    def test_export_includes_a4_phase_range_and_tracker_fields_without_inference(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for field in ("move_id", "montage_name", "fallback_montage_name", "clip_path", "active_start_time", "active_end_time",
                      "branch_range_cm", "phase_id", "low_sweep", "b_enabled"):
            self.assertIn(field, source)
        self.assertIn("not evidence of runtime selection", source.lower())

    def test_script_is_read_only_and_refuses_ambiguous_missing_data(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("set_editor_property(", "save_loaded_asset(", "save_asset(", "duplicate_asset(", "delete_asset("):
            self.assertNotIn(forbidden, source)
        self.assertIn("raise RuntimeError", source)
        self.assertIn('open("x"', source)
        self.assertIn("output_path", source)


if __name__ == "__main__":
    unittest.main()
