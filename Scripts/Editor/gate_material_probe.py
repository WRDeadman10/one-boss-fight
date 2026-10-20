"""Lists the parameters of MI_Arena_FogGate and its parent. Log prefix [GateMat]."""
import unreal

MATS = "/Game/OneBossFight/Materials/"
mi = None
for base in ("/Game/OneBossFight/Environment/Materials/",):
    mi = unreal.EditorAssetLibrary.load_asset(base + "MI_Arena_FogGate")
    if mi:
        break
unreal.log("[GateMat] asset: %s" % (mi.get_path_name() if mi else None))
if mi:
    unreal.log("[GateMat] parent: %s" % mi.get_editor_property("parent").get_path_name())
    for n in unreal.MaterialEditingLibrary.get_scalar_parameter_names(mi):
        unreal.log("[GateMat] scalar %s = %s" % (n, unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(mi, n)))
    for n in unreal.MaterialEditingLibrary.get_vector_parameter_names(mi):
        unreal.log("[GateMat] vector %s = %s" % (n, unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(mi, n)))
    for p in mi.get_editor_property("scalar_parameter_values"):
        unreal.log("[GateMat] override scalar %s = %s" % (p.parameter_info.name, p.parameter_value))
    for p in mi.get_editor_property("vector_parameter_values"):
        unreal.log("[GateMat] override vector %s = %s" % (p.parameter_info.name, p.parameter_value))
