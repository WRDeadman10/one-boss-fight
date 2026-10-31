#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_validate_weapon_config.py
==============================
Offline unit test suite for validate_weapon_config.py with 25+ negative test cases,
exact failure token verification, enemy/boss style rejection, style collision checks,
update mode validation, catalog block validation, Blueprint _C class checks,
DirectoriesToAlwaysCook cooked root verification, and physical asset existence checking.
"""

import copy
import json
import os
import sys
import unittest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from validate_weapon_config import validate_weapon_config, DEFAULT_EXISTING_ROWS

BASE_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", "..", "..", ".."))


def _build_content_asset_set():
    """Builds a set of all .uasset paths under Content/ for offline path verification."""
    content_dir = os.path.join(BASE_DIR, "Content")
    assets = set()
    if not os.path.exists(content_dir):
        return assets
    for root, _dirs, files in os.walk(content_dir):
        for f in files:
            if f.endswith(".uasset"):
                rel = os.path.relpath(os.path.join(root, f), content_dir).replace(os.sep, "/")
                pkg = "/Game/" + rel[:-7]
                leaf = rel[:-7].split("/")[-1]
                assets.add(pkg)
                assets.add(f"{pkg}.{leaf}")
                assets.add(f"{pkg}.{leaf}_C")
    return assets


class TestValidateWeaponConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content_assets = _build_content_asset_set()

    def setUp(self):
        example_path = os.path.join(_THIS_DIR, "example_new_weapon.json")
        with open(example_path, "r", encoding="utf-8") as f:
            self.valid_cfg = json.load(f)

    def test_00_valid_example_offline(self):
        """Verify baseline valid example (Polearm on PolearmCombatStyle) passes with 0 errors offline."""
        errors = validate_weapon_config(self.valid_cfg)
        self.assertEqual(errors, [], f"Valid config produced unexpected errors: {errors}")

    def test_00b_valid_example_with_real_content_assets(self):
        """Verify baseline valid example passes with 0 errors against physical Content/ assets."""
        errors = validate_weapon_config(self.valid_cfg, asset_exists=self.content_assets)
        self.assertEqual(errors, [], f"Valid config failed physical asset check: {errors}")

    def test_00c_valid_update_existing_style(self):
        """Verify valid update mode on an existing style (Claymore) passes with 0 errors."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["mode"] = "update_existing_style"
        cfg["style_name"] = "ClaymoreCombatStyle"
        cfg["style_asset_path"] = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Claymore/ClaymoreCombatStyle.ClaymoreCombatStyle"
        cfg["actor_class"] = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Claymore/ClaymoreInstances/BP_KwangSword.BP_KwangSword_C"
        cfg["ability_class"] = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Claymore/GA_Claymore_Melee.GA_Claymore_Melee_C"
        errors = validate_weapon_config(cfg)
        self.assertEqual(errors, [], f"Valid update config produced unexpected errors: {errors}")

    def test_01_negative_structure_not_dict(self):
        """Negative 1: Config root is not a dict."""
        errors = validate_weapon_config(["not", "a", "dict"])
        self.assertTrue(any("[Weapon.Config.Structure]" in e for e in errors))

    def test_02_negative_missing_identity(self):
        """Negative 2: Missing or invalid weapon_id / style_name / hud_weapon_word."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["weapon_id"] = "None"
        cfg["style_name"] = "  "
        cfg["hud_weapon_word"] = ""
        errors = validate_weapon_config(cfg)
        identity_errors = [e for e in errors if "[Weapon.Config.Identity]" in e]
        self.assertGreaterEqual(len(identity_errors), 3)

    def test_03_negative_unknown_combat_style(self):
        """Negative 3: style_name points to an unknown non-pack style asset."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["style_name"] = "CustomImaginaryCombatStyle"
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.UnknownCombatStyle]" in e for e in errors))

    def test_04_negative_invalid_asset_path(self):
        """Negative 4: Asset path does not start with /Game/ or lacks package dot."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["item_path"] = "Relative/Path/NoPackageDot"
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.Path]" in e for e in errors))

    def test_05_negative_style_path_mismatch(self):
        """Negative 5: style_asset_path points to wrong pack asset for style_name."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["style_asset_path"] = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Sword/SwordCombatStyle.SwordCombatStyle"
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.Path]" in e for e in errors))

    def test_06_negative_build_block(self):
        """Negative 6: Invalid build block (whitespace in console_name, negative ui_order)."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["build"]["console_name"] = "invalid console name with spaces"
        cfg["build"]["ui_order"] = -5
        errors = validate_weapon_config(cfg)
        build_errors = [e for e in errors if "[Weapon.Config.Build]" in e]
        self.assertGreaterEqual(len(build_errors), 2)

    def test_07_negative_missing_required_attack_coverage(self):
        """Negative 7: Missing required attack kind in new_weapon mode (e.g. omitting JumpLight)."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["attack_rows"] = [r for r in cfg["attack_rows"] if r["kind"] != "JumpLight"]
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.AttackCoverage]" in e and "JumpLight" in e for e in errors))

    def test_08_negative_duplicate_attack_kind(self):
        """Negative 8: Duplicate attack kind in attack_rows."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["attack_rows"].append(copy.deepcopy(cfg["attack_rows"][0]))
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.AttackCoverage]" in e and "duplicate" in e for e in errors))

    def test_09_negative_invalid_attack_kind(self):
        """Negative 9: Unrecognized attack kind name (e.g. Running, Falling)."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["attack_rows"][0]["kind"] = "Running"
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.InvalidAttackKind]" in e and "Running" in e for e in errors))

    def test_10_negative_attack_domain_values(self):
        """Negative 10: Negative posture damage, zero stamina cost, negative bleed, non-positive health multiplier."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["attack_rows"][0]["posture_damage"] = -10.0
        cfg["attack_rows"][0]["stamina_cost"] = 0.0   # 0 is invalid; must be -1.0 or > 0.0
        cfg["attack_rows"][0]["bleed_buildup"] = -5.0
        cfg["attack_rows"][0]["health_damage_multiplier"] = 0.0  # strictly positive
        errors = validate_weapon_config(cfg)
        domain_errors = [e for e in errors if "[Weapon.Config.AttackDomain]" in e]
        self.assertGreaterEqual(len(domain_errors), 4)

    def test_11_negative_hyperarmor_window(self):
        """Negative 11: Invalid hyperarmor window (Start >= 0 but End <= Start)."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["attack_rows"][1]["hyperarmor_start"] = 0.5
        cfg["attack_rows"][1]["hyperarmor_end"] = 0.3  # End < Start
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.HyperArmor]" in e for e in errors))

    def test_12_negative_missing_asset_on_disk(self):
        """Negative 12: Asset path is well-formed but does not exist in asset_exists."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["item_path"] = "/Game/OneBossFight/Data/NonExistentItem_12345.NonExistentItem_12345"
        errors = validate_weapon_config(cfg, asset_exists=self.content_assets)
        self.assertTrue(any("Weapon.Config.PathMissing" in e for e in errors))

    def test_13_negative_enemy_combat_style(self):
        """Negative 13: Style name contains 'Enemy' (e.g. ExampleSwordEnemyCombatStyle)."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["style_name"] = "ExampleSwordEnemyCombatStyle"
        cfg["style_asset_path"] = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleSwordEnemy/ExampleSwordEnemyCombatStyle.ExampleSwordEnemyCombatStyle"
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.EnemyCombatStyle]" in e for e in errors))

    def test_14_negative_boss_combat_style(self):
        """Negative 14: Style name contains 'Boss' (e.g. SevarogBossCombatStyle)."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["style_name"] = "SevarogBossCombatStyle"
        cfg["style_asset_path"] = "/Game/OneBossFight/Boss01/SevarogBossCombatStyle.SevarogBossCombatStyle"
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.EnemyCombatStyle]" in e for e in errors))

    def test_15_negative_style_already_has_rows(self):
        """Negative 15: New weapon specifying a style that already has rows in DA_WeaponAttacks."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["mode"] = "new_weapon"
        cfg["style_name"] = "ClaymoreCombatStyle"
        cfg["style_asset_path"] = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Claymore/ClaymoreCombatStyle.ClaymoreCombatStyle"
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.StyleAlreadyHasRows[ClaymoreCombatStyle]]" in e for e in errors))

    def test_16_negative_update_mode_unknown_kind(self):
        """Negative 16: Update mode specifying a kind that has no existing row for that style."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["mode"] = "update_existing_style"
        cfg["style_name"] = "ClaymoreCombatStyle"
        cfg["style_asset_path"] = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Claymore/ClaymoreCombatStyle.ClaymoreCombatStyle"
        restricted_rows = {
            ("ClaymoreCombatStyle", "Light"),
            ("ClaymoreCombatStyle", "Strong"),
        }
        errors = validate_weapon_config(cfg, existing_rows=restricted_rows)
        self.assertTrue(any("[Weapon.Config.UnknownUpdateKind]" in e and "Charged" in e for e in errors))

    def test_17_negative_unknown_mode(self):
        """Negative 17: Config specifies an invalid or unrecognized mode."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["mode"] = "invalid_mode_name"
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.Mode]" in e for e in errors))

    def test_18_negative_catalog_legacy_slot(self):
        """Negative 18: Catalog legacy_slot is not -1 for a new build."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["catalog"]["legacy_slot"] = 1  # 0..2 are reserved for legacy compatibility builds
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.Catalog.LegacySlot]" in e for e in errors))

    def test_19_negative_catalog_reserved_name(self):
        """Negative 19: Build console name or alias uses reserved engine token 'none' or 'off'."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["build"]["console_name"] = "none"
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.Catalog.ReservedName]" in e for e in errors))

    def test_20_negative_catalog_legacy_collision(self):
        """Negative 20: Build console name or alias collides with shipped legacy build name/alias."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["build"]["aliases"].append("dexterity")
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.Catalog.AliasCollision[dexterity]]" in e for e in errors))

    def test_21_negative_catalog_path_not_in_catalog_folder(self):
        """Negative 21: Weapon definition path is outside /Game/OneBossFight/Data/Catalog/."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["catalog"]["weapon_asset_path"] = "/Game/OneBossFight/Data/WrongFolder/DA_Weapon_Bad.DA_Weapon_Bad"
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.Catalog.Path]" in e for e in errors))

    def test_22_negative_catalog_icon_missing(self):
        """Negative 22: Catalog icon asset path does not exist on disk."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["catalog"]["icon_path"] = "/Game/OneBossFight/UI/Art/NonExistentIcon_12345.NonExistentIcon_12345"
        errors = validate_weapon_config(cfg, asset_exists=self.content_assets)
        self.assertTrue(any("Weapon.Config.PathMissing" in e for e in errors))

    def test_23_negative_item_base_class_no_suffix_c(self):
        """Negative 23: item_base_class does not end in '_C'."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["item_base_class"] = "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/DataAssets/Items/WeaponItem.WeaponItem"
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.ItemBaseClassPath]" in e for e in errors))

    def test_24_negative_catalog_icon_outside_cook_root(self):
        """Negative 24: Catalog icon path is outside DirectoriesToAlwaysCook roots."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["catalog"]["icon_path"] = "/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/InventoryEquipmentUI/Icons/Icon_FengMao_Weapon.Icon_FengMao_Weapon"
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.Catalog.IconCookRoot]" in e for e in errors))

    def test_25_negative_asset_outside_cook_root(self):
        """Negative 25: An asset path resides outside DirectoriesToAlwaysCook roots."""
        cfg = copy.deepcopy(self.valid_cfg)
        cfg["item_path"] = "/Game/NonCookedFolder/SomeWeaponItem.SomeWeaponItem"
        errors = validate_weapon_config(cfg)
        self.assertTrue(any("[Weapon.Config.Path]" in e and "outside DirectoriesToAlwaysCook" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
