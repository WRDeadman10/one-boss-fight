import unreal

LEVEL = "/Game/OneBossFight/Levels/L_SevarogArena"
DR = "/Game/Deadly_Ruins/"
MAT_DIR = "/Game/OneBossFight/Environment/Materials"

def setup_materials():
    mel = unreal.MaterialEditingLibrary
    eal = unreal.EditorAssetLibrary

    # 1. Build a stunning PBR floor material instance
    floor_mi_path = MAT_DIR + "/MI_Arena_Floor"
    if eal.does_asset_exist(floor_mi_path):
        floor_mi = unreal.load_asset(floor_mi_path)
    else:
        floor_mi = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "MI_Arena_Floor", MAT_DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    
    # Use MM_Prop_Detail as parent
    master = unreal.load_asset(DR + "Materials/MasterMaterial/MM_Prop_Detail")
    floor_mi.set_editor_property("parent", master)

    # Let's use T_Brick_1 (or T_Rock_1) for dark ancient temple stone
    albedo = unreal.load_asset(DR + "Textures/TilingEnvironment/T_Brick_1_Albedo")
    normal = unreal.load_asset(DR + "Textures/TilingEnvironment/T_Brick_1_Normal")
    rma = unreal.load_asset(DR + "Textures/TilingEnvironment/T_Brick_1_RMA")
    
    mel.set_material_instance_texture_parameter_value(floor_mi, "Input_Albedo", albedo)
    mel.set_material_instance_texture_parameter_value(floor_mi, "Input_Normal", normal)
    mel.set_material_instance_texture_parameter_value(floor_mi, "Input_RMA", rma)
    
    # 20 repeats across 60m = 3 meters per tile repeat, realistic cobblestone scale
    mel.set_material_instance_scalar_parameter_value(floor_mi, "Tiling", 20.0)
    mel.set_material_instance_scalar_parameter_value(floor_mi, "Roughness_Multiply", 0.65)
    mel.set_material_instance_scalar_parameter_value(floor_mi, "Strength_Normal", 1.8)
    mel.set_material_instance_scalar_parameter_value(floor_mi, "Albedo_Contrast", 0.15)
    mel.set_material_instance_scalar_parameter_value(floor_mi, "Metal_Multiply", 0.0)
    mel.update_material_instance(floor_mi)
    eal.save_loaded_asset(floor_mi, False)
    print("Updated MI_Arena_Floor with dark ancient cobblestone PBR!")
    return floor_mi

def main():
    floor_mi = setup_materials()
    
    arenas = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a, unreal.RPGGreyboxArena)]
    if not arenas:
        print("No RPGGreyboxArena found!")
        return
    arena = arenas[0]

    # Assign floor
    arena.set_editor_property("FloorMaterial", floor_mi)

    # Let's test SM_I_Pillar2 (single clean stone column) vs SM__Pillar5
    pillar = unreal.load_asset(DR + "Meshes/Architecture/SM_I_Pillar2")
    pillar_broken = unreal.load_asset(DR + "Meshes/Architecture/SM__pillar2")
    pillar_cracked = unreal.load_asset(DR + "Meshes/Architecture/SM__pillar3")
    
    arena.set_editor_property("PillarIntact", pillar)
    arena.set_editor_property("PillarCracked", pillar_cracked)
    arena.set_editor_property("PillarBroken", pillar_broken)
    arena.set_editor_property("PillarMaterial", None) # Native materials!

    # Rubble
    rubble = unreal.load_asset(DR + "Meshes/Prop/SM_brickrubble1")
    arena.set_editor_property("Rubble", rubble)
    arena.set_editor_property("RubbleMaterial", None) # Native MI_Brick_Debris!

    # Curved Wall
    wall_mat = unreal.load_asset(DR + "Materials/Instances/MI_TIling_Brick")
    arena.set_editor_property("WallMaterial", wall_mat)

    # Arch & Brazier
    arch = unreal.load_asset(DR + "Meshes/Architecture/SM_archway_1")
    arena.set_editor_property("EntranceArch", arch)
    arena.set_editor_property("ArchMaterial", None)
    
    brazier = unreal.load_asset(DR + "Meshes/Prop/SM_Brazer")
    arena.set_editor_property("Brazier", brazier)
    arena.set_editor_property("BrazierMaterial", unreal.load_asset(DR + "Materials/Instances/MI_TIling_Metal"))

    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    print("Arena updated with new floor and pillar setup!")

main()
