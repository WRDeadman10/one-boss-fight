"""Tunes MI_Arena_RomanFloor (wetness off, rougher, darker) and reports the switch states. Log prefix [Floor]."""
import unreal

ml = unreal.MaterialEditingLibrary
mi = unreal.EditorAssetLibrary.load_asset("/Game/OneBossFight/Environment/Materials/MI_Arena_RomanFloor")
for n in ("Enable Wetness", "Use Roughness MinMax", "RGB Blend - Disable"):
    try:
        unreal.log("[Floor] switch %s = %s" % (n, ml.get_material_instance_static_switch_parameter_value(mi, n)))
    except Exception as e:
        unreal.log("[Floor] switch %s read failed %s" % (n, e))
unreal.log("[Floor] tint now %s scale now %s" % (ml.get_material_instance_vector_parameter_value(mi, "Base - Albedo Tint"), ml.get_material_instance_scalar_parameter_value(mi, "UVs - Base  Scale")))
ml.set_material_instance_scalar_parameter_value(mi, "Base - Roughness Mult", 1.35)
ml.set_material_instance_scalar_parameter_value(mi, "Shore Wetness - Additional Spec", 0.0)
ml.set_material_instance_scalar_parameter_value(mi, "Specular Max", 0.3)
ml.set_material_instance_scalar_parameter_value(mi, "Gen - Final Roughness (Offset)", 0.28)
ml.set_material_instance_vector_parameter_value(mi, "Base - Albedo Tint", unreal.LinearColor(0.40, 0.40, 0.42, 1.0))
ml.set_material_instance_vector_parameter_value(mi, "RGB Noise - Tint", unreal.LinearColor(0.9, 0.85, 0.8, 1.0))
try:
    ml.set_material_instance_static_switch_parameter_value(mi, "Enable Wetness", False)
except Exception as e:
    unreal.log("[Floor] switch set failed %s" % e)
ml.update_material_instance(mi)
unreal.EditorAssetLibrary.save_loaded_asset(mi)
unreal.log("[Floor] tuned")
