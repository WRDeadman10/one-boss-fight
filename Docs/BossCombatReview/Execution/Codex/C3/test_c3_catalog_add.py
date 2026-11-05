#!/usr/bin/env python3
"""Exercise the C3 catalog-add path with a mocked Unreal asset API."""
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
REVIEWS = ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews"


class DataObject:
    def __init__(self, path):
        self.path = path
        self.values = {}

    def get_editor_property(self, name):
        return self.values.get(name)

    def set_editor_property(self, name, value):
        self.values[name] = value

    def get_path_name(self):
        return self.path

    def get_name(self):
        return self.path.rsplit("/", 1)[-1].split(".")[0]


class AttackRow(DataObject):
    def __init__(self):
        super().__init__("")
        self.values = {"weapon": "", "kind": "", "posture_damage": 0.0, "stamina_cost": 0.0,
                       "bleed_buildup": 0.0, "health_damage_multiplier": 0.0,
                       "hyper_armor_start": -1.0, "hyper_armor_end": -1.0, "note": ""}


class AttackTable(DataObject):
    def __init__(self):
        super().__init__("/Game/OneBossFight/Data/DA_WeaponAttacks.DA_WeaponAttacks")
        self.values = {"rows": []}


class CatalogRoot(DataObject):
    def __init__(self):
        super().__init__("/Game/OneBossFight/Data/Catalog/DA_CombatCatalog.DA_CombatCatalog")
        self.values = {"weapons": [], "builds": []}


class AssetTools:
    def __init__(self):
        self.created = []

    def create_asset(self, name, package, _asset_class, _factory):
        asset = DataObject(package + "/" + name + "." + name)
        asset.values["definition"] = DataObject(asset.path + ":Definition")
        self.created.append(asset)
        return asset


class CatalogAddTests(unittest.TestCase):
    def test_apply_adds_and_reads_back_weapon_build_and_root_entries(self):
        config = json.loads((REVIEWS / "example_new_weapon.json").read_text(encoding="utf-8"))
        table, root, tools = AttackTable(), CatalogRoot(), AssetTools()
        saves, logs, errors = [], [], []
        destinations = {
            config["catalog"]["weapon_asset_path"].split(".")[0],
            config["catalog"]["build_asset_path"].split(".")[0],
        }
        enum_values = {}
        for row in config["attack_rows"]:
            enum_name = "".join("_" + char if char.isupper() and index else char for index, char in enumerate(row["kind"])).upper()
            enum_values[enum_name] = "RPGAttackKind." + enum_name

        def load_asset(path):
            if path == "/Game/OneBossFight/Data/DA_WeaponAttacks.DA_WeaponAttacks":
                return table
            if path == config["catalog"]["catalog_root_path"]:
                return root
            return None

        def does_asset_exist(path):
            return str(path) not in destinations

        unreal_stub = types.SimpleNamespace(
            load_asset=load_asset,
            EditorAssetLibrary=types.SimpleNamespace(
                does_asset_exist=does_asset_exist,
                save_loaded_asset=lambda asset: saves.append(asset) or True,
            ),
            AssetToolsHelpers=types.SimpleNamespace(get_asset_tools=lambda: tools),
            DataAssetFactory=lambda: object(),
            RPGWeaponAttackRow=AttackRow,
            RPGWeaponDefinition=type("RPGWeaponDefinition", (), {}),
            RPGBuildDefinition=type("RPGBuildDefinition", (), {}),
            RPGAttackKind=types.SimpleNamespace(**enum_values),
            SoftObjectPath=lambda value: value,
            Name=lambda value: value,
            log=logs.append,
            log_error=errors.append,
        )
        script = ROOT / "Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py"
        spec = importlib.util.spec_from_file_location("c3_catalog_add_action", script)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": unreal_stub}), patch.object(sys, "argv", [str(script), str(REVIEWS / "example_new_weapon.json"), "--apply"]):
            spec.loader.exec_module(module)

        self.assertEqual(errors, [])
        self.assertEqual(len(tools.created), 2)
        weapon_asset, build_asset = tools.created
        self.assertEqual(weapon_asset.values["definition"].values["weapon_id"], config["weapon_id"])
        self.assertEqual(build_asset.values["definition"].values["build_id"], config["build"]["build_id"])
        self.assertEqual(root.values["weapons"], [weapon_asset])
        self.assertEqual(root.values["builds"], [build_asset])
        self.assertEqual(len(table.values["rows"]), len(config["attack_rows"]))
        self.assertEqual(len(saves), 4)  # attack table, weapon definition, build definition, root catalog
        self.assertTrue(any("CATALOG_READBACK_OK" in log for log in logs))
        pending = next(log for log in logs if "[NEWWEAPON_CATALOG_COMPILE_PENDING]" in log)
        state = json.loads(pending.split(" ", 1)[1])
        self.assertEqual(state["surface"], "URPGCombatCatalogSubsystem startup initialization")
        self.assertTrue(state["restart_required"])
        self.assertFalse(state["native_compile_run"])


if __name__ == "__main__":
    unittest.main()
