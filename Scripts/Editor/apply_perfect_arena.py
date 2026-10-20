import unreal

DR = "/Game/Deadly_Ruins/"
MAT_DIR = "/Game/OneBossFight/Environment/Materials"

def main():
    eal = unreal.EditorAssetLibrary
    mel = unreal.MaterialEditingLibrary

    # 1. Configure MI_Arena_Floor with full PBR quality
    floor_mi = unreal.load_asset(MAT_DIR + "/MI_Arena_Floor")
    master = unreal.load_asset(DR + "Materials/MasterMaterial/MM_Prop_Detail")
    floor_mi.set_editor_property("parent", master)

    # Use 2K T_BrickFloor (or T_Brick_1)
    albedo = unreal.load_asset(DR + "Textures/TilingEnvironment/T_BrickFloor_Albedo")
    normal = unreal.load_asset(DR + "Textures/TilingEnvironment/T_BrickFloor_Normal")
    rma = unreal.load_asset(DR + "Textures/TilingEnvironment/T_BrickFloor_RMA")

    mel.set_material_instance_texture_parameter_value(floor_mi, "Input_Albedo", albedo)
    mel.set_material_instance_texture_parameter_value(floor_mi, "Input_Normal", normal)
    mel.set_material_instance_texture_parameter_value(floor_mi, "Input_RMA", rma)

    mel.set_material_instance_scalar_parameter_value(floor_mi, "Tiling", 18.0)
    mel.set_material_instance_scalar_parameter_value(floor_mi, "Roughness_Multiply", 0.70)
    mel.set_material_instance_scalar_parameter_value(floor_mi, "Strength_Normal", 2.2)
    mel.set_material_instance_scalar_parameter_value(floor_mi, "Albedo_Contrast", 0.35)
    mel.set_material_instance_scalar_parameter_value(floor_mi, "Metal_Multiply", 0.0)
    mel.update_material_instance(floor_mi)
    eal.save_loaded_asset(floor_mi, False)
    print("Configured MI_Arena_Floor with rich dark stone flagstones (tiling 18.0, normal 2.2, roughness 0.70)")

    # 2. Configure Arena Actor
    arenas = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a, unreal.RPGGreyboxArena)]
    if not arenas:
        print("No RPGGreyboxArena found!")
        return
    arena = arenas[0]

    pillar_clean = unreal.load_asset(DR + "Meshes/Architecture/SM_I_Pillar2")
    rubble = unreal.load_asset(DR + "Meshes/Prop/SM_brickrubble1")
    arch = unreal.load_asset(DR + "Meshes/Architecture/SM_archway_1")
    brazier = unreal.load_asset(DR + "Meshes/Prop/SM_Brazer")
    wall_mat = unreal.load_asset(DR + "Materials/Instances/MI_TIling_Brick")
    brazier_mat = unreal.load_asset(DR + "Materials/Instances/MI_TIling_Metal")

    # Use clean, uniform columns for all pillar slots
    arena.set_editor_property("PillarIntact", pillar_clean)
    arena.set_editor_property("PillarCracked", pillar_clean)
    arena.set_editor_property("PillarBroken", pillar_clean)

    # Clean meshes for arch, brazier, rubble
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
    print("Arena completely rebuilt with AAA modular Deadly Ruins assets and PBR materials!")

main()
