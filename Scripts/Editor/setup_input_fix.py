"""
Rebuilds the movement and look mappings in IMC_Default with real modifiers, and adds block/parry input.

Why: the mappings made through the editor MCP kept their modifier slots empty after save (null modifiers), so
W/S/A all moved the character right and the gamepad sticks had no dead zone (camera drift). Idempotent.

Run headless from the project root (editor closed):
  UnrealEditor-Cmd.exe OneBossFight.uproject -run=pythonscript -script=Scripts/Editor/setup_input_fix.py -unattended -nullrhi
"""

import os
import sys

import unreal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rpg_content_lib as lib  # noqa: E402

INPUT_DIR = "/Game/OneBossFight/Input/"
PLAYER_BP = "/Game/OneBossFight/Characters/BP_PlayerCharacter"
GREY_DIR = "/Game/OneBossFight/Characters/Greystone"
PACK = "/Game/ParagonGreystone"
FEEDBACK = "/Game/OneBossFight/Feedback/DA_Feedback_Greystone"

STICK_DEAD_ZONE = 0.25
LOOK_DEGREES_PER_SECOND = 150.0


def log(msg):
    unreal.log("[InputFix] " + msg)


def key(name):
    k = unreal.Key()
    k.set_editor_property("key_name", name)
    return k


def main():
    imc = unreal.load_asset(INPUT_DIR + "IMC_Default")
    imc.modify()
    move = unreal.load_asset(INPUT_DIR + "IA_Move")
    look = unreal.load_asset(INPUT_DIR + "IA_Look")

    # Block / parry action.
    block_path = INPUT_DIR + "IA_Block"
    if unreal.EditorAssetLibrary.does_asset_exist(block_path):
        block = unreal.load_asset(block_path)
    else:
        block = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "IA_Block", INPUT_DIR.rstrip("/"), unreal.InputAction, unreal.InputAction_Factory())
        block.set_editor_property("value_type", unreal.InputActionValueType.BOOLEAN)
        unreal.EditorAssetLibrary.save_loaded_asset(block)

    # Move and Look are rebuilt natively (Python cannot create editable modifiers).
    unreal.RPGInputAuthoring.configure_move_and_look(imc, move, look, STICK_DEAD_ZONE, LOOK_DEGREES_PER_SECOND)
    imc.unmap_all_keys_from_action(block)
    for k in ("LeftControl", "Gamepad_LeftShoulder"):
        imc.map_key(block, key(k))
    unreal.EditorAssetLibrary.save_loaded_asset(imc, False)
    log("IMC_Default rebuilt: WASD swizzle/negate, stick dead zones, stick look in degrees per second, block on LCtrl / LB.")

    # Player: block input and the guard animation (Greystone raises its shield with Deflect_InPlace).
    guard = lib.make_plain_montage(GREY_DIR, "AM_Greystone_Guard", PACK, "Deflect_InPlace", "UpperBody")
    log("AM_Greystone_Guard length %.2fs" % guard.get_play_length())
    bp = unreal.load_asset(PLAYER_BP)
    cdo = unreal.get_default_object(bp.generated_class())
    cdo.set_editor_property("block_action", block)
    cdo.set_editor_property("guard_montage", guard)

    feedback = unreal.load_asset(FEEDBACK)
    if feedback:
        parry_sound = unreal.load_asset(PACK + "/Audio/Cues/Greystone_Effort_Block")
        parry_fx = unreal.load_asset(PACK + "/FX/Particles/Greystone/Abilities/Primary/FX/P_Greystone_Primary_Impact")
        if parry_sound:
            feedback.set_editor_property("parry_sound", parry_sound)
        if parry_fx:
            feedback.set_editor_property("parry_effect", parry_fx)
        unreal.EditorAssetLibrary.save_loaded_asset(feedback, False)

    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
    log("BP_PlayerCharacter has block input and guard montage.")


main()
