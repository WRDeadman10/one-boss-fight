import unreal

DR = "/Game/Deadly_Ruins/"
MAT_DIR = "/Game/OneBossFight/Environment/Materials"

def tune_floor():
    floor_mi = unreal.load_asset(MAT_DIR + "/MI_Arena_Floor")
    mel = unreal.MaterialEditingLibrary
    eal = unreal.EditorAssetLibrary

    # Let's adjust Albedo Contrast and Tint to give an ancient, weathered grey-slate stone look
    # Tint_Albedo can darken the bright yellow brick to atmospheric ancient temple stone:
    mel.set_material_instance_vector_parameter_value(floor_mi, "Tint_Albedo", unreal.LinearColor(0.45, 0.45, 0.48, 1.0))
    mel.set_material_instance_scalar_parameter_value(floor_mi, "Tiling", 18.0)
    mel.set_material_instance_scalar_parameter_value(floor_mi, "Roughness_Multiply", 0.75)
    mel.set_material_instance_scalar_parameter_value(floor_mi, "Strength_Normal", 2.0)
    mel.set_material_instance_scalar_parameter_value(floor_mi, "Albedo_Contrast", 0.25)
    mel.update_material_instance(floor_mi)
    eal.save_loaded_asset(floor_mi, False)
    print("Tuned MI_Arena_Floor to ancient grey slate!")

def setup_clean_pillars():
    arenas = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a, unreal.RPGGreyboxArena)]
    if not arenas:
        return
    arena = arenas[0]

    pillar_clean = unreal.load_asset(DR + "Meshes/Architecture/SM_I_Pillar2")
    pillar_alt = unreal.load_asset(DR + "Meshes/Architecture/SM_I_Pillar3")
    
    # Use clean, properly unwrapped modular columns for all pillar slots
    arena.set_editor_property("PillarIntact", pillar_clean)
    arena.set_editor_property("PillarCracked", pillar_alt)
    arena.set_editor_property("PillarBroken", pillar_clean) # keep clean pillar geometry

    # Ensure material overrides are cleared on all pillar components
    for comp in arena.get_components_by_class(unreal.StaticMeshComponent):
        if "pillar" in comp.get_name().lower():
            comp.set_material(0, None)
            comp.set_material(1, None)

    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    print("Clean pillars applied!")

tune_floor()
setup_clean_pillars()
