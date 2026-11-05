"""Pure contract test for a successful selected-profile preflight receipt."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
REVIEWS = ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews"
sys.path.insert(0, str(REVIEWS))
from validate_boss_config import validate_boss_config

spec = importlib.util.spec_from_file_location("c2_receipt_schema", HERE / "receipt_schema.py")
receipt_schema = importlib.util.module_from_spec(spec)
spec.loader.exec_module(receipt_schema)
sys.path.insert(0, str(REVIEWS))
from test_validate_boss_config import get_sevarog_f10_valid_config


class ProfileSuccessContractTests(unittest.TestCase):
    def test_valid_profile_produces_successful_read_only_preflight_receipt(self):
        config = get_sevarog_f10_valid_config()
        self.assertEqual(validate_boss_config(config), [])
        receipt = receipt_schema.normalize_receipt({
            "ok": True,
            "summary": "Profile preflight passed; no assets were compiled or saved.",
            "asset_path": "/Game/OneBossFight/FrameworkProof/DA_Sevarog_Profile.DA_Sevarog_Profile",
            "fields": {"fixture_label": config["fixture_label"], "cards": len(config["cards"])},
            "diagnostics": [], "saved": False, "compiled": False, "repeat_safe": True,
        }, "preflight_selected_boss_profile")
        decoded = json.loads(receipt_schema.serialize_receipt(receipt, "preflight_selected_boss_profile"))
        self.assertTrue(decoded["ok"])
        self.assertEqual(decoded["diagnostics"], [])
        self.assertFalse(decoded["saved"])
        self.assertFalse(decoded["compiled"])
        self.assertTrue(decoded["repeat_safe"])
        self.assertEqual(decoded["action"], "preflight_selected_boss_profile")

    def test_invalid_profile_surfaces_stable_field_diagnostic_without_mutation(self):
        config = get_sevarog_f10_valid_config()
        config["band_min_cm"] = config["band_max_cm"]
        tokens = validate_boss_config(config)
        self.assertTrue(tokens)
        token = "Framework.Profile.Geometry"
        self.assertIn(token, tokens)
        diagnostic = {"code": token, "field": "Profile", "message": "Offline preflight rejected this profile value."}
        receipt = json.loads(receipt_schema.serialize_receipt({
            "ok": False, "summary": "Profile preflight blocked.", "diagnostics": [diagnostic],
            "saved": False, "compiled": False, "repeat_safe": True,
        }, "preflight_selected_boss_profile"))
        self.assertFalse(receipt["ok"])
        self.assertEqual(receipt["diagnostics"][0]["code"], token)
        self.assertEqual(receipt["diagnostics"][0]["field"], "Profile")
        self.assertFalse(receipt["saved"])
        self.assertFalse(receipt["compiled"])


if __name__ == "__main__":
    unittest.main()
