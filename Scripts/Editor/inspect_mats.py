"""
Prints the parent and parameters of material instances (paths in PATHS) and the existing arena floor material. Log prefix [Mats].
Run with Scripts/run_in_editor.py.
"""
import unreal

PATHS = [
    "/Game/Materials/FogCards/MI_FogCard_02",
    "/Game/Materials/FogCards/MI_FogCard__Green_01",
    "/Game/Materials/FogCards/M_FogCard",
]
ml = unreal.MaterialEditingLibrary
for path in PATHS:
    mi = unreal.EditorAssetLibrary.load_asset(path)
    if not mi:
        unreal.log("[Mats] MISSING " + path)
        continue
    parent = mi.get_editor_property("parent") if hasattr(mi, "get_editor_property") and isinstance(mi, unreal.MaterialInstanceConstant) else None
    unreal.log("[Mats] %s class=%s parent=%s" % (path.split("/")[-1], mi.get_class().get_name(), parent.get_path_name() if parent else None))
    if isinstance(mi, unreal.MaterialInstanceConstant):
        for n in ml.get_scalar_parameter_names(mi):
            unreal.log("[Mats]    scalar %s = %s" % (n, ml.get_material_instance_scalar_parameter_value(mi, n)))
        for n in ml.get_vector_parameter_names(mi):
            unreal.log("[Mats]    vector %s = %s" % (n, ml.get_material_instance_vector_parameter_value(mi, n)))
        for n in ml.get_static_switch_parameter_names(mi) if hasattr(ml, "get_static_switch_parameter_names") else []:
            unreal.log("[Mats]    switch %s" % n)
