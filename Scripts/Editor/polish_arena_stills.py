import unreal

# 1. Slightly tune floor roughness to 0.82 for balanced ancient dry-wet stone
MAT_DIR = "/Game/OneBossFight/Environment/Materials"
eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary

floor_mi = unreal.load_asset(MAT_DIR + "/MI_Arena_Floor")
mel.set_material_instance_scalar_parameter_value(floor_mi, "Roughness_Multiply", 0.82)
mel.set_material_instance_scalar_parameter_value(floor_mi, "Strength_Normal", 2.0)
mel.update_material_instance(floor_mi)
eal.save_loaded_asset(floor_mi, False)

# 2. Deselect all actors in the editor level so there's no orange selection wireframe
unreal.EditorLevelLibrary.select_nothing()
print("Deselected all actors and adjusted floor roughness to 0.82!")
