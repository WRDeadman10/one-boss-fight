"""
M7 arena art pass: configures authentic Deadly Ruins modular meshes and PBR materials
for the arena actor. Idempotent; preserves the gameplay footprint.

Run inside editor via:
  python -I Scripts/run_in_editor.py Scripts/Editor/setup_m7_arena.py
Or in headless batch via:
  powershell -File Scripts/RunEditorScript.ps1 -Script Scripts/Editor/setup_m7_arena.py -Tag M7Arena
"""

import os
import sys

import unreal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import rpg_content_lib as lib
except ImportError:
    lib = None

LEVELS = ["/Game/OneBossFight/Levels/L_SevarogArena", "/Game/OneBossFight/Levels/L_Greybox"]
RUINS = "/Game/Deadly_Ruins/"
MATERIAL_DIR = "/Game/OneBossFight/Environment/Materials"
FLOOR_REPEATS = 18.0
FLOOR_ROUGHNESS = 0.82
FLOOR_NORMAL_STRENGTH = 2.0


def log(msg):
    unreal.log("[M7Arena] " + msg)


def build_floor_material():
    """Builds a rich ancient cobblestone/slate PBR material instance."""
    path = MATERIAL_DIR + "/MI_Arena_Floor"
    unreal.EditorAssetLibrary.make_directory(MATERIAL_DIR)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mi = unreal.load_asset(path)
    else:
        mi = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "MI_Arena_Floor", MATERIAL_DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    
    mi.set_editor_property("parent", unreal.load_asset(RUINS + "Materials/MasterMaterial/MM_Prop_Detail"))
    mel = unreal.MaterialEditingLibrary
    mel.set_material_instance_texture_parameter_value(
        mi, "Input_Albedo", unreal.load_asset(RUINS + "Textures/TilingEnvironment/T_BrickFloor_Albedo"))
    mel.set_material_instance_texture_parameter_value(
        mi, "Input_Normal", unreal.load_asset(RUINS + "Textures/TilingEnvironment/T_BrickFloor_Normal"))
    mel.set_material_instance_texture_parameter_value(
        mi, "Input_RMA", unreal.load_asset(RUINS + "Textures/TilingEnvironment/T_BrickFloor_RMA"))
    
    mel.set_material_instance_scalar_parameter_value(mi, "Tiling", FLOOR_REPEATS)
    mel.set_material_instance_scalar_parameter_value(mi, "Roughness_Multiply", FLOOR_ROUGHNESS)
    mel.set_material_instance_scalar_parameter_value(mi, "Strength_Normal", FLOOR_NORMAL_STRENGTH)
    mel.set_material_instance_scalar_parameter_value(mi, "Albedo_Contrast", 0.35)
    mel.set_material_instance_scalar_parameter_value(mi, "Metal_Multiply", 0.0)
    mel.update_material_instance(mi)
    unreal.EditorAssetLibrary.save_loaded_asset(mi, False)
    log("MI_Arena_Floor updated successfully")
    return mi


def configure_level_arena(level_path, floor_mi):
    if not unreal.EditorAssetLibrary.does_asset_exist(level_path):
        log("Level does not exist: " + level_path)
        return
    unreal.EditorLevelLibrary.load_level(level_path)
    arenas = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a, unreal.RPGGreyboxArena)]
    if not arenas:
        log("No RPGGreyboxArena found in " + level_path)
        return
    arena = arenas[0]

    pillar_clean = unreal.load_asset(RUINS + "Meshes/Architecture/SM_I_Pillar2")
    rubble = unreal.load_asset(RUINS + "Meshes/Prop/SM_brickrubble1")
    arch = unreal.load_asset(RUINS + "Meshes/Architecture/SM_archway_1")
    brazier = unreal.load_asset(RUINS + "Meshes/Prop/SM_Brazer")
    wall_mat = unreal.load_asset(RUINS + "Materials/Instances/MI_TIling_Brick")
    brazier_mat = unreal.load_asset(RUINS + "Materials/Instances/MI_TIling_Metal")

    # Meshes
    arena.set_editor_property("PillarIntact", pillar_clean)
    arena.set_editor_property("PillarCracked", pillar_clean)
    arena.set_editor_property("PillarBroken", pillar_clean)
    arena.set_editor_property("EntranceArch", arch)
    arena.set_editor_property("Brazier", brazier)
    arena.set_editor_property("Rubble", rubble)
    arena.set_editor_property("RubbleCount", 20)

    # Materials
    arena.set_editor_property("FloorMaterial", floor_mi)
    arena.set_editor_property("WallMaterial", wall_mat)
    arena.set_editor_property("BrazierMaterial", brazier_mat)
    arena.set_editor_property("PillarMaterial", None)
    arena.set_editor_property("ArchMaterial", None)
    arena.set_editor_property("RubbleMaterial", None)

    # Clear component-level overrides so native materials shine
    for comp in arena.get_components_by_class(unreal.StaticMeshComponent):
        name = comp.get_name()
        if name in ("Pillars", "PillarsCracked", "PillarsBroken", "Debris", "Arch"):
            comp.set_material(0, None)
            comp.set_material(1, None)
        elif name == "Floor":
            comp.set_material(0, floor_mi)
        elif name in ("Walls", "WallsDamaged"):
            comp.set_material(0, wall_mat)
        elif name == "Braziers":
            comp.set_material(0, brazier_mat)

    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("Arena configured and saved in " + level_path)


def main():
    floor_mi = build_floor_material()
    for lvl in LEVELS:
        configure_level_arena(lvl, floor_mi)


try:
    main()
except Exception:
    import traceback
    log("FAILED: " + traceback.format_exc())
finally:
    if lib and not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world():
        lib.quit_editor_soon()
