#!/usr/bin/env python3
"""Run C3's actual script with a mocked asset library to verify collision refusal ordering."""
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
REVIEWS = ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews"


class FakeTable:
    def __init__(self, rows=None):
        self.writes = 0
        self.rows = list(rows or [])

    def get_editor_property(self, name):
        if name == "rows":
            return self.rows
        raise AssertionError(name)

    def set_editor_property(self, name, value):
        self.writes += 1
        raise AssertionError("table mutation should not be reached")


class FakeAttackRow:
    def __init__(self, weapon, kind):
        self.values = {"weapon": weapon, "kind": kind}

    def get_editor_property(self, name):
        return self.values[name]


class FaultyWritableRow(FakeAttackRow):
    def __init__(self):
        self.values = {"weapon": "", "kind": "", "posture_damage": 0.0, "stamina_cost": 0.0,
                       "bleed_buildup": 0.0, "health_damage_multiplier": 0.0,
                       "hyper_armor_start": -1.0, "hyper_armor_end": -1.0, "note": ""}

    def set_editor_property(self, name, value):
        if name == "stamina_cost":
            return  # Simulate an Editor property write that did not stick.
        self.values[name] = value


class WritableTable(FakeTable):
    def __init__(self):
        super().__init__()

    def set_editor_property(self, name, value):
        self.writes += 1
        if name == "rows":
            self.rows = value


class FakeCatalogDefinition:
    def __init__(self, values):
        self.values = values

    def get_editor_property(self, name):
        return self.values[name]


class FakeSoftReference:
    def __init__(self, definition):
        self.asset = types.SimpleNamespace(get_editor_property=lambda name: definition if name == "definition" else None)

    def load_synchronous(self):
        return self.asset


class NewWeaponDestinationPreflightTests(unittest.TestCase):
    def test_dry_run_result_events_are_structured_json(self):
        config = json.loads((REVIEWS / "example_new_weapon.json").read_text(encoding="utf-8"))
        config["catalog"]["register"] = False
        logs, errors = [], []
        table = FakeTable()
        unreal_stub = types.SimpleNamespace(
            load_asset=lambda path: table if path == "/Game/OneBossFight/Data/DA_WeaponAttacks.DA_WeaponAttacks" else None,
            EditorAssetLibrary=types.SimpleNamespace(does_asset_exist=lambda path: True),
            log=logs.append, log_error=errors.append,
        )
        script = ROOT / "Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py"
        with tempfile.TemporaryDirectory() as temp:
            config_path = Path(temp) / "weapon.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            spec = importlib.util.spec_from_file_location("c3_dry_run_structured_result", script)
            module = importlib.util.module_from_spec(spec)
            with patch.dict(sys.modules, {"unreal": unreal_stub}), patch.object(sys, "argv", [str(script), str(config_path)]):
                with self.assertRaises(SystemExit) as exit_info:
                    spec.loader.exec_module(module)
        self.assertEqual(exit_info.exception.code, 0)
        self.assertEqual(errors, [])
        for tag_name in ("VALIDATION", "PLAN", "END"):
            line = next(item for item in logs if item.startswith(f"[NEWWEAPON_{tag_name}] "))
            payload = json.loads(line.split(" ", 1)[1])
            if tag_name == "VALIDATION":
                self.assertEqual(payload["errors"], [])
            elif tag_name == "PLAN":
                self.assertEqual(len(payload), len(config["attack_rows"]))
            else:
                self.assertEqual(payload, {"written": [], "dry_run": True})

    def test_dry_run_plan_is_deterministic_and_write_free(self):
        config = json.loads((REVIEWS / "example_new_weapon.json").read_text(encoding="utf-8"))
        config["catalog"]["register"] = False
        table = FakeTable()
        runs = []
        errors = []
        unreal_stub = types.SimpleNamespace(
            load_asset=lambda path: table if path == "/Game/OneBossFight/Data/DA_WeaponAttacks.DA_WeaponAttacks" else None,
            EditorAssetLibrary=types.SimpleNamespace(does_asset_exist=lambda path: True, save_loaded_asset=lambda asset: True),
            log=lambda message: runs[-1].append(message), log_error=errors.append,
        )
        script = ROOT / "Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py"
        with tempfile.TemporaryDirectory() as temp:
            config_path = Path(temp) / "weapon.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            for index in range(2):
                runs.append([])
                spec = importlib.util.spec_from_file_location(f"c3_dry_run_determinism_{index}", script)
                module = importlib.util.module_from_spec(spec)
                with patch.dict(sys.modules, {"unreal": unreal_stub}), patch.object(sys, "argv", [str(script), str(config_path)]):
                    with self.assertRaises(SystemExit) as exit_info:
                        spec.loader.exec_module(module)
                self.assertEqual(exit_info.exception.code, 0)
        self.assertEqual(errors, [])
        plans = [next(line for line in output if line.startswith("[NEWWEAPON_PLAN]")) for output in runs]
        self.assertEqual(plans[0], plans[1])
        self.assertEqual(table.writes, 0)

    def test_malformed_and_non_object_inputs_fail_before_asset_access(self):
        errors = []
        asset_access = []
        unreal_stub = types.SimpleNamespace(
            load_asset=lambda path: asset_access.append(path),
            EditorAssetLibrary=types.SimpleNamespace(does_asset_exist=lambda path: asset_access.append(path)),
            log_error=errors.append,
            log=lambda message: None,
        )
        script = ROOT / "Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py"
        with tempfile.TemporaryDirectory() as temp:
            for index, (payload, expected) in enumerate((("{invalid", "invalid weapon config input:"), ("[]", "root must be a JSON object"))):
                config_path = Path(temp) / f"invalid_{index}.json"
                config_path.write_text(payload, encoding="utf-8")
                spec = importlib.util.spec_from_file_location(f"c3_invalid_config_{index}", script)
                module = importlib.util.module_from_spec(spec)
                with patch.dict(sys.modules, {"unreal": unreal_stub}), patch.object(sys, "argv", [str(script), str(config_path), "--apply"]):
                    with self.assertRaises(SystemExit):
                        spec.loader.exec_module(module)
                self.assertIn(expected, errors[-1])
                self.assertEqual(asset_access, [], "invalid input must fail before loading assets")

    def test_property_readback_failure_aborts_before_save(self):
        config = json.loads((REVIEWS / "example_new_weapon.json").read_text(encoding="utf-8"))
        config["catalog"]["register"] = False
        config_path = HERE / "fixtures" / "readback_failure_config.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        table = WritableTable()
        errors = []
        saves = []
        enum_values = {}
        for row in config["attack_rows"]:
            enum_name = "".join("_" + char if char.isupper() and index else char for index, char in enumerate(row["kind"])).upper()
            enum_values[enum_name] = "RPGAttackKind." + enum_name
        unreal_stub = types.SimpleNamespace(
            load_asset=lambda path: table if path == "/Game/OneBossFight/Data/DA_WeaponAttacks.DA_WeaponAttacks" else None,
            EditorAssetLibrary=types.SimpleNamespace(does_asset_exist=lambda path: True, save_loaded_asset=lambda asset: saves.append(asset) or True),
            RPGWeaponAttackRow=FaultyWritableRow,
            RPGAttackKind=types.SimpleNamespace(**enum_values),
            log=lambda message: None,
            log_error=errors.append,
        )
        script = ROOT / "Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py"
        spec = importlib.util.spec_from_file_location("c3_new_weapon_readback_failure", script)
        module = importlib.util.module_from_spec(spec)
        try:
            with patch.dict(sys.modules, {"unreal": unreal_stub}), patch.object(sys, "argv", [str(script), str(config_path), "--apply"]):
                with self.assertRaises(SystemExit):
                    spec.loader.exec_module(module)
        finally:
            config_path.unlink(missing_ok=True)
        self.assertTrue(any("readback mismatch" in error for error in errors))
        self.assertEqual(len(table.rows), len(config["attack_rows"]))
        self.assertNotEqual(table.rows[0].get_editor_property("stamina_cost"), config["attack_rows"][0]["stamina_cost"])
        self.assertEqual(saves, [], "failed row readback must not save the table")
    def test_existing_attack_row_is_preserved_when_new_weapon_style_is_rejected(self):
        config = json.loads((REVIEWS / "example_new_weapon.json").read_text(encoding="utf-8"))
        existing_row = FakeAttackRow(config["style_name"], "Light")
        original = dict(existing_row.values)
        table = FakeTable([existing_row])
        errors = []
        logs = []
        unreal_stub = types.SimpleNamespace(
            load_asset=lambda path: table if path == "/Game/OneBossFight/Data/DA_WeaponAttacks.DA_WeaponAttacks" else None,
            EditorAssetLibrary=types.SimpleNamespace(does_asset_exist=lambda path: True),
            log=logs.append, log_error=errors.append,
        )
        script = ROOT / "Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py"
        spec = importlib.util.spec_from_file_location("c3_new_weapon_existing_row_preserved", script)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": unreal_stub}), patch.object(sys, "argv", [str(script), str(REVIEWS / "example_new_weapon.json"), "--apply"]):
            with self.assertRaises(SystemExit):
                spec.loader.exec_module(module)
        self.assertTrue(any("StyleAlreadyHasRows" in error for error in errors))
        validation = next(log for log in logs if log.startswith("[NEWWEAPON_VALIDATION] "))
        diagnostic = json.loads(validation.split(" ", 1)[1])["errors"]
        self.assertTrue(any("[Weapon.Config.StyleAlreadyHasRows[PolearmCombatStyle]]" in item for item in diagnostic))
        self.assertEqual(table.writes, 0)
        self.assertEqual(existing_row.values, original)

    def test_existing_catalog_destination_refuses_before_attack_table_write(self):
        config = json.loads((REVIEWS / "example_new_weapon.json").read_text(encoding="utf-8"))
        destination_package = config["catalog"]["weapon_asset_path"].split(".")[0]
        table = FakeTable()
        errors = []

        def does_asset_exist(path):
            return str(path) == destination_package or str(path).startswith("/Game/")

        unreal_stub = types.SimpleNamespace(
            load_asset=lambda path: table if path == "/Game/OneBossFight/Data/DA_WeaponAttacks.DA_WeaponAttacks" else None,
            EditorAssetLibrary=types.SimpleNamespace(does_asset_exist=does_asset_exist),
            log=lambda message: None,
            log_error=errors.append,
        )
        script = ROOT / "Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py"
        spec = importlib.util.spec_from_file_location("c3_new_weapon_destination_collision", script)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": unreal_stub}), patch.object(sys, "argv", [str(script), str(REVIEWS / "example_new_weapon.json"), "--apply"]):
            with self.assertRaises(SystemExit):
                spec.loader.exec_module(module)

        self.assertEqual(table.writes, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("catalog destination exists, refusing before table write", errors[0])
        self.assertIn(destination_package, errors[0])

    def test_duplicate_catalog_weapon_id_refuses_before_attack_table_write(self):
        config = json.loads((REVIEWS / "example_new_weapon.json").read_text(encoding="utf-8"))
        existing_weapon = FakeCatalogDefinition({
            "weapon_id": config["weapon_id"], "style_name": "UnrelatedStyle", "style_aliases": [],
        })
        root = types.SimpleNamespace(get_editor_property=lambda name: [FakeSoftReference(existing_weapon)] if name == "weapons" else [])
        table = FakeTable()
        errors = []
        destination_packages = {
            config["catalog"]["weapon_asset_path"].split(".")[0],
            config["catalog"]["build_asset_path"].split(".")[0],
        }

        def does_asset_exist(path):
            return str(path) not in destination_packages

        def load_asset(path):
            if path == "/Game/OneBossFight/Data/DA_WeaponAttacks.DA_WeaponAttacks":
                return table
            if path == config["catalog"]["catalog_root_path"]:
                return root
            return None

        unreal_stub = types.SimpleNamespace(
            load_asset=load_asset,
            EditorAssetLibrary=types.SimpleNamespace(does_asset_exist=does_asset_exist),
            log=lambda message: None,
            log_error=errors.append,
        )
        script = ROOT / "Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py"
        spec = importlib.util.spec_from_file_location("c3_new_weapon_duplicate_id", script)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": unreal_stub}), patch.object(sys, "argv", [str(script), str(REVIEWS / "example_new_weapon.json"), "--apply"]):
            with self.assertRaises(SystemExit):
                spec.loader.exec_module(module)

        self.assertEqual(table.writes, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("duplicate catalog WeaponId", errors[0])

    def test_duplicate_catalog_style_alias_refuses_before_attack_table_write(self):
        config = json.loads((REVIEWS / "example_new_weapon.json").read_text(encoding="utf-8"))
        existing_weapon = FakeCatalogDefinition({
            "weapon_id": "ExistingWeapon", "style_name": "DifferentCombatStyle",
            "style_aliases": [config["style_name"]],
        })
        root = types.SimpleNamespace(get_editor_property=lambda name: [FakeSoftReference(existing_weapon)] if name == "weapons" else [])
        table = FakeTable()
        errors = []
        destinations = {
            config["catalog"]["weapon_asset_path"].split(".")[0],
            config["catalog"]["build_asset_path"].split(".")[0],
        }
        unreal_stub = types.SimpleNamespace(
            load_asset=lambda path: table if path == "/Game/OneBossFight/Data/DA_WeaponAttacks.DA_WeaponAttacks" else root if path == config["catalog"]["catalog_root_path"] else None,
            EditorAssetLibrary=types.SimpleNamespace(does_asset_exist=lambda path: str(path) not in destinations),
            log=lambda message: None, log_error=errors.append,
        )
        script = ROOT / "Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py"
        spec = importlib.util.spec_from_file_location("c3_new_weapon_duplicate_style_alias", script)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": unreal_stub}), patch.object(sys, "argv", [str(script), str(REVIEWS / "example_new_weapon.json"), "--apply"]):
            with self.assertRaises(SystemExit):
                spec.loader.exec_module(module)
        self.assertEqual(table.writes, 0)
        self.assertTrue(any("duplicate catalog style/alias" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
