# Copyright One Boss Fight. All Rights Reserved.
"""
Offline validation test for Track C5 Weapon Data Audit.
Verifies all source file line citations, asset byte offsets, and pure CRLF compliance.
"""

import os
import struct
import sys
import unittest
from pathlib import Path

# Support isolated python -I invocation
sys.path.insert(0, str(Path(__file__).resolve().parent))


class TestC5WeaponDataAudit(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[5]

    def _read_lines(self, rel_path):
        full_path = self.repo_root / rel_path
        self.assertTrue(full_path.exists(), f"File not found: {rel_path}")
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()

    def _read_bytes(self, rel_path):
        full_path = self.repo_root / rel_path
        self.assertTrue(full_path.exists(), f"Asset not found: {rel_path}")
        return full_path.read_bytes()

    def test_cpp_citations_weapon_table(self):
        """Verify citations in RPGWeaponAttackTable.h and .cpp."""
        h_lines = self._read_lines("Source/OneBossFight/Player/RPGWeaponAttackTable.h")
        self.assertIn("struct ONEBOSSFIGHT_API FRPGWeaponAttackRow", h_lines[14])
        self.assertIn("class ONEBOSSFIGHT_API URPGWeaponAttackTable", h_lines[60])
        self.assertIn("AssetPath()", h_lines[83])
        self.assertIn("/Game/OneBossFight/Data/DA_WeaponAttacks.DA_WeaponAttacks", h_lines[83])

        cpp_lines = self._read_lines("Source/OneBossFight/Player/RPGWeaponAttackTable.cpp")
        self.assertIn("FillDefaults()", cpp_lines[36])
        self.assertIn("ClaymoreCombatStyle", cpp_lines[41])
        self.assertIn("SwordCombatStyle", cpp_lines[41])
        self.assertIn("Row.HealthDamageMultiplier = 0.39f;", cpp_lines[63])
        self.assertIn("DualSwordCombatStyle", cpp_lines[67])
        self.assertIn("TwinbladeCombatStyle", cpp_lines[67])

    def test_cpp_citations_combat_catalog(self):
        """Verify citations in RPGCombatCatalog.h."""
        lines = self._read_lines("Source/OneBossFight/Player/RPGCombatCatalog.h")
        self.assertIn("struct ONEBOSSFIGHT_API FRPGCatalogWeapon", lines[12])
        self.assertIn("FName WeaponId;", lines[15])
        self.assertIn("FName StyleName;", lines[16])
        self.assertIn("FSoftObjectPath StyleAsset;", lines[17])
        self.assertIn("FSoftObjectPath ItemPath;", lines[18])
        self.assertIn("FSoftObjectPath ItemBaseClass;", lines[19])
        self.assertIn("FSoftObjectPath ActorClass;", lines[20])
        self.assertIn("FSoftObjectPath AbilityClass;", lines[21])
        self.assertIn("FString HudWeaponWord;", lines[22])

    def test_cpp_citations_build_loadout_and_rules(self):
        """Verify citations in RPGBuildRules.h and RPGBuildLoadout.h/.cpp."""
        rules_lines = self._read_lines("Source/OneBossFight/Player/RPGBuildRules.h")
        self.assertIn("constexpr int32 WeaponSlotEnumerator = 11;", rules_lines[26])

        loadout_h = self._read_lines("Source/OneBossFight/Player/RPGBuildLoadout.h")
        self.assertIn("StartupDelaySeconds", loadout_h[39])

        loadout_cpp = self._read_lines("Source/OneBossFight/Player/RPGBuildLoadout.cpp")
        self.assertIn("ResolveWeaponSlotByte", loadout_cpp[122])

    def test_cpp_citations_hit_intake_and_swing_tracker(self):
        """Verify citations in RPGHitIntake.cpp and RPGSwingTracker.cpp."""
        intake_lines = self._read_lines("Source/OneBossFight/Player/RPGHitIntake.cpp")
        self.assertIn("URPGWeaponAttackTable::LoadOrDefault()", intake_lines[166])
        self.assertIn("ApplyPostureDamage", intake_lines[537])
        self.assertIn("AddBuildup", intake_lines[545])

        swing_lines = self._read_lines("Source/OneBossFight/Player/RPGSwingTracker.cpp")
        self.assertIn("Attribute.Stamina", swing_lines[21])
        self.assertIn("URPGWeaponAttackTable::LoadOrDefault()", swing_lines[58])
        self.assertIn("WindowOpen", swing_lines[281])

    def test_asset_byte_offsets_da_weapon_attacks(self):
        """Verify exact byte offsets in DA_WeaponAttacks.uasset."""
        data = self._read_bytes("Content/OneBossFight/Data/DA_WeaponAttacks.uasset")
        expected_strings = {
            0x1A5: b"BleedBuildup",
            0x1CF: b"ClaymoreCombatStyle",
            0x1EB: b"DualSwordCombatStyle",
            0x32C: b"HyperArmorEnd",
            0x342: b"HyperArmorStart",
            0x3BB: b"PostureDamage",
            0x3D1: b"Rows",
            0x3F9: b"StaminaCost",
            0x438: b"SwordCombatStyle",
            0x451: b"TwinbladeCombatStyle",
        }
        for offset, expected in expected_strings.items():
            actual = data[offset : offset + len(expected)]
            self.assertEqual(actual, expected, f"Mismatch at {hex(offset)} in DA_WeaponAttacks.uasset")

    def test_asset_byte_offsets_catalog_weapons(self):
        """Verify exact byte offsets in DA_Weapon_*.uasset (both path starts and short names)."""
        claymore_data = self._read_bytes("Content/OneBossFight/Data/Catalog/DA_Weapon_Claymore.uasset")
        self.assertEqual(claymore_data[0xD46 : 0xD46 + 8], b"Claymore")
        self.assertEqual(claymore_data[0x459 : 0x459 + 19], b"ClaymoreCombatStyle")
        self.assertEqual(claymore_data[0x1E2 : 0x1E2 + 20], b"/Game/AdvancedARPGCo")
        self.assertEqual(claymore_data[0x5DD : 0x5DD + 10], b"KwangSword")
        self.assertEqual(claymore_data[0x29C : 0x29C + 20], b"/Game/AdvancedARPGCo")
        self.assertEqual(claymore_data[0x42C : 0x42C + 15], b"BP_KwangSword_C")
        self.assertEqual(claymore_data[0x30B : 0x30B + 20], b"/Game/AdvancedARPGCo")
        self.assertEqual(claymore_data[0x577 : 0x577 + 19], b"GA_Claymore_Melee_C")

        sword_data = self._read_bytes("Content/OneBossFight/Data/Catalog/DA_Weapon_Sword.uasset")
        self.assertEqual(sword_data[0xD7A : 0xD7A + 5], b"Sword")
        self.assertEqual(sword_data[0x6E0 : 0x6E0 + 16], b"SwordCombatStyle")
        self.assertEqual(sword_data[0x1DF : 0x1DF + 20], b"/Game/AdvancedARPGCo")
        self.assertEqual(sword_data[0x717 : 0x717 + 10], b"ToughSword")
        self.assertEqual(sword_data[0x2EE : 0x2EE + 20], b"/Game/AdvancedARPGCo")
        self.assertEqual(sword_data[0x42C : 0x42C + 14], b"BP_ToughSword_")
        self.assertEqual(sword_data[0x236 : 0x236 + 20], b"/Game/AdvancedARPGCo")
        self.assertEqual(sword_data[0x55B : 0x55B + 16], b"GA_Sword_Melee_C")

        dual_data = self._read_bytes("Content/OneBossFight/Data/Catalog/DA_Weapon_DualSwords.uasset")
        self.assertEqual(dual_data[0xDC4 : 0xDC4 + 11], b"Dual Swords")
        self.assertEqual(dual_data[0x17E : 0x17E + 20], b"/Game/AdvancedARPGCo")
        self.assertEqual(dual_data[0x4DB : 0x4DB + 16], b"DualWeaponItem_C")
        self.assertEqual(dual_data[0x4BE : 0x4BE + 20], b"DualSwordCombatStyle")

    def test_asset_byte_offsets_pack_mechanics(self):
        """Verify pack stamina cost float and poise damage string offset."""
        ge_stamina_data = self._read_bytes(
            "Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_MeleeAttackCost.uasset"
        )
        val, = struct.unpack("<f", ge_stamina_data[0x1BC6 : 0x1BC6 + 4])
        self.assertAlmostEqual(val, -15.0, places=3, msg="Pack baseline stamina cost at 0x1bc6 must be -15.0f")

        attack_data = self._read_bytes(
            "Content/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/DataAssets/BP_AttackData.uasset"
        )
        self.assertEqual(attack_data[0x86C : 0x86C + 11], b"PoiseDamage")

    def test_pure_crlf_and_non_empty(self):
        """Verify deliverables exist, are non-empty, and maintain pure CRLF line endings."""
        docs_to_check = [
            "Docs/BossCombatReview/Execution/Antigravity/Reviews/C5_WEAPON_DATA_AUDIT.md",
            "Docs/BossCombatReview/Execution/Antigravity/Reviews/test_reopen_c5_weapon_data_audit.py",
        ]
        for rel in docs_to_check:
            raw = (self.repo_root / rel).read_bytes()
            self.assertGreater(len(raw), 500, f"{rel} is unexpectedly small")
            # Replace CRLF with empty; any remaining LF means mixed/Unix line endings
            without_crlf = raw.replace(b"\r\n", b"")
            self.assertNotIn(b"\n", without_crlf, f"{rel} contains LF without CR (not pure CRLF)")
            self.assertNotIn(b"\r", without_crlf, f"{rel} contains standalone CR (not pure CRLF)")


if __name__ == "__main__":
    unittest.main()
