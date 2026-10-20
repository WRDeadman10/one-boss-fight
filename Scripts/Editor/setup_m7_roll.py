"""
Retargets the Mage pack roll animations (UE4 mannequin skeleton) onto Greystone and builds the dodge montages.

Creates (all under /Game/OneBossFight/Characters/Greystone):
  IK_Greystone, RTG_UE4Mannequin_To_Greystone, AS_Roll_* retargeted copies, AM_Greystone_Dodge (forward roll),
  AM_Greystone_DodgeBack (backward roll). Assigns them to BP_PlayerCharacter.

Needs Slate (the batch retarget syncs the content browser), so run with a real editor, not the commandlet:
  UnrealEditor.exe OneBossFight.uproject -ExecutePythonScript=Scripts/Editor/setup_m7_roll.py -unattended
"""

import os
import sys

import unreal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rpg_content_lib as lib  # noqa: E402

GREY_DIR = "/Game/OneBossFight/Characters/Greystone"
ROLL_DIR = GREY_DIR + "/Roll"
PLAYER_BP = "/Game/OneBossFight/Characters/BP_PlayerCharacter"
GREY_MESH = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone"
UE4_MESH = "/Game/Mage/Demo/Mannequin_UE4/Character/Mesh/SK_Mannequin"
UE4_RIG = "/Game/Mage/Demo/Mannequin_UE4/Rigs/IK_UE4_Mannequin"
SOURCE_SEQ_DIR = "/Game/Mage/Animations/Sequence1/07_Roll/02_Roll_Combat/"
# Forward roll for any direction (the character turns to the dodge direction first); backward roll for a no-input step back.
SEQUENCES = ["AS_Roll_Combat_F_0_Seq", "AS_Roll_Combat_B_180_Seq"]


def log(msg):
    unreal.log("[M7Roll] " + msg)


def main():
    assets = unreal.AssetToolsHelpers.get_asset_tools()
    grey_mesh = unreal.load_asset(GREY_MESH)
    ue4_mesh = unreal.load_asset(UE4_MESH)
    ue4_rig = unreal.load_asset(UE4_RIG)

    # 1. IK rig for Greystone with chains generated from its bone names.
    unreal.EditorAssetLibrary.make_directory(GREY_DIR)
    rig = lib.recreate(GREY_DIR + "/IK_Greystone", unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
    rig_controller = unreal.IKRigController.get_controller(rig)
    rig_controller.set_skeletal_mesh(grey_mesh)
    ok = rig_controller.apply_auto_generated_retarget_definition()
    log("auto retarget definition: %s" % ok)
    for chain in rig_controller.get_retarget_chains_as_list() if hasattr(rig_controller, "get_retarget_chains_as_list") else []:
        log("  chain %s" % chain)
    log("retarget root: %s" % rig_controller.get_retarget_root())
    unreal.EditorAssetLibrary.save_loaded_asset(rig)

    # 2. Retargeter UE4 mannequin -> Greystone.
    rtg = lib.recreate(GREY_DIR + "/RTG_UE4Mannequin_To_Greystone", unreal.IKRetargeter, unreal.IKRetargetFactory())
    controller = unreal.IKRetargeterController.get_controller(rtg)
    controller.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, ue4_rig)
    controller.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, rig)
    controller.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, ue4_mesh)
    controller.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, grey_mesh)
    controller.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)
    unreal.EditorAssetLibrary.save_loaded_asset(rtg)

    # 3. Retarget the sequences.
    sources = [unreal.EditorAssetLibrary.find_asset_data(SOURCE_SEQ_DIR + name) for name in SEQUENCES]
    unreal.EditorAssetLibrary.make_directory(ROLL_DIR)
    batch = unreal.IKRetargetBatchOperation
    results = batch.duplicate_and_retarget(sources, ue4_mesh, grey_mesh, rtg, "", "", "", "_Greystone", True)
    log("retargeted: %s" % [str(r.package_name) for r in results])
    for result in results:
        # Duplicates land next to the source (/Game/Mage/...). Move them into our folder.
        new_path = ROLL_DIR + "/" + str(result.asset_name)
        if unreal.EditorAssetLibrary.does_asset_exist(new_path):
            unreal.EditorAssetLibrary.delete_asset(new_path)
        log("move %s -> %s: %s" % (result.package_name, new_path, unreal.EditorAssetLibrary.rename_asset(str(result.package_name), new_path)))
    unreal.EditorAssetLibrary.save_directory(ROLL_DIR)


try:
    main()
finally:
    lib.quit_editor_soon()
