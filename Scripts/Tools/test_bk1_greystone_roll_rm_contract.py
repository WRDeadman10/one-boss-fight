"""Offline guard contract for the BK-1 Greystone quick/full roll retarget tool."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "Editor" / "retarget_greystone_pack_rolls_rm.py"
SOURCE = SCRIPT.read_text(encoding="utf-8")


class GreystoneRollRMContract(unittest.TestCase):
    def test_only_source_derived_quick_and_full_roll_pairs_are_selected(self):
        self.assertEqual(SOURCE.count('"kind": "quick"'), 1)
        self.assertEqual(SOURCE.count('"kind": "full"'), 1)
        self.assertIn("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll", SOURCE)
        self.assertIn("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle", SOURCE)
        self.assertIn("/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey", SOURCE)
        self.assertIn("/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage_Grey", SOURCE)

    def test_outputs_are_isolated_and_existing_destinations_fail_closed(self):
        self.assertIn('OUT_ROOT = "/Game/OneBossFight/Player/Greystone/RootMotion"', SOURCE)
        self.assertIn('SUFFIX = "_RM"', SOURCE)
        self.assertIn('require(not eal.does_asset_exist(path), "refusing to overwrite existing asset: " + path)', SOURCE)
        self.assertNotIn("delete_asset", SOURCE)
        self.assertNotIn("rename_asset(", SOURCE.split("def main():", 1)[0])

    def test_root_chain_and_manifest_proof_are_required(self):
        self.assertIn("RetargetTranslationMode.GLOBALLY_SCALED", SOURCE)
        self.assertIn('"source_root_xy_cm": source_root_xy', SOURCE)
        self.assertIn('"output_root_xy_cm": output_root_xy', SOURCE)
        self.assertIn('"root_xy_ratio": output_root_xy / source_root_xy', SOURCE)
        self.assertIn("require(output_root_xy > 0.5 * source_root_xy", SOURCE)

    def test_montage_copy_uses_cpp_wrapper_and_never_repoints_existing_child(self):
        self.assertIn("create_retarget_wrapper(source_montage, target_sequence, target_skeleton, montage_path)", SOURCE)
        self.assertIn("DescribeMontageNotifies", (ROOT / "Source" / "OneBossFightEditor" / "Public" / "RPGMontageWrapperLibrary.h").read_text(encoding="utf-8"))
        self.assertNotIn("set_editor_property(\"QuickMontage\"", SOURCE)
        self.assertNotIn("set_editor_property(\"FullMontage\"", SOURCE)

    def test_default_is_read_only_and_write_is_explicit(self):
        self.assertIn('return "--write" in unreal.SystemLibrary.get_command_line().split()', SOURCE)
        self.assertIn('log("RESULT=PASS dry_run=1 saves=0")', SOURCE)


if __name__ == "__main__":
    unittest.main()
