#!/usr/bin/env python3
"""Behavior tests for C3 catalog registration validation boundaries."""
import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
REVIEWS = ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews"
sys.path.insert(0, str(REVIEWS))
from validate_weapon_config import validate_weapon_config


class C3RegistrationValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example = json.loads((REVIEWS / "example_new_weapon.json").read_text(encoding="utf-8"))

    def errors(self, config):
        return validate_weapon_config(config)

    def test_complete_registered_catalog_config_is_valid(self):
        self.assertEqual(self.errors(copy.deepcopy(self.example)), [])

    def test_register_flag_requires_boolean(self):
        config = copy.deepcopy(self.example)
        config["catalog"]["register"] = "true"
        self.assertTrue(any("[Weapon.Config.Catalog.Structure] catalog.register must be a boolean" in e for e in self.errors(config)))

    def test_registration_requires_all_three_distinct_destinations(self):
        for key in ("weapon_asset_path", "build_asset_path", "catalog_root_path"):
            with self.subTest(missing=key):
                config = copy.deepcopy(self.example)
                config["catalog"][key] = ""
                self.assertTrue(any(f"catalog.{key} is required" in e for e in self.errors(config)))
        config = copy.deepcopy(self.example)
        config["catalog"]["build_asset_path"] = config["catalog"]["weapon_asset_path"]
        self.assertTrue(any("[Weapon.Config.Catalog.DestinationCollision]" in e for e in self.errors(config)))

    def test_unregistered_config_does_not_require_new_destinations(self):
        config = copy.deepcopy(self.example)
        config["catalog"]["register"] = False
        for key in ("weapon_asset_path", "build_asset_path", "catalog_root_path"):
            config["catalog"][key] = None
        errors = self.errors(config)
        self.assertFalse(any("required when catalog.register is true" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
