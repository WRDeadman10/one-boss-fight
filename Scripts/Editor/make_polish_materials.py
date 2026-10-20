"""
Creates the materials the arena polish needs (all under /Game/OneBossFight/Environment/Materials, recreated in place so references stay valid):
  M_Ember        unlit emissive orange, brightness varies per instance (the ember field)
  M_Banner       dark crimson cloth with gold trim bands at both ends, two sided
  MI_Arena_Mist  the sample's fog card material turned down: dim cool emissive, animated flow, low opacity
  MI_Arena_Pillar  Roman stone for the greybox pillars, three tiles around
Run with Scripts/run_in_editor.py. Log prefix [PolishMats].
"""
import unreal

log = lambda m: unreal.log("[PolishMats] " + m)
PATH = "/Game/OneBossFight/Environment/Materials"
ml = unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()


def ensure(name, cls, factory):
    full = PATH + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    return tools.create_asset(name, PATH, cls, factory)


def node(mat, cls, x, y):
    return ml.create_material_expression(mat, cls, x, y)


def link(a, b, out="", inp=""):
    ml.connect_material_expressions(a, out, b, inp)


def clear(mat):
    ml.delete_all_material_expressions(mat)


# ---------------------------------------------------------------- embers
ember = ensure("M_Ember", unreal.Material, unreal.MaterialFactoryNew())
clear(ember)
ember.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
color = node(ember, unreal.MaterialExpressionConstant3Vector, -700, 0)
color.set_editor_property("constant", unreal.LinearColor(1.0, 0.30, 0.05, 1.0))
gain = node(ember, unreal.MaterialExpressionConstant, -700, 160)
gain.set_editor_property("r", 140.0)
rnd = node(ember, unreal.MaterialExpressionPerInstanceRandom, -700, 300)
lerp = node(ember, unreal.MaterialExpressionLinearInterpolate, -450, 280)
lo = node(ember, unreal.MaterialExpressionConstant, -700, 400)
lo.set_editor_property("r", 0.3)
hi = node(ember, unreal.MaterialExpressionConstant, -700, 480)
hi.set_editor_property("r", 1.0)
link(lo, lerp, "", "A")
link(hi, lerp, "", "B")
link(rnd, lerp, "", "Alpha")
m1 = node(ember, unreal.MaterialExpressionMultiply, -450, 40)
link(color, m1, "", "A")
link(gain, m1, "", "B")
m2 = node(ember, unreal.MaterialExpressionMultiply, -220, 120)
link(m1, m2, "", "A")
link(lerp, m2, "", "B")
ml.connect_material_property(m2, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
ml.recompile_material(ember)
unreal.EditorAssetLibrary.save_loaded_asset(ember)
log("M_Ember done")

# ---------------------------------------------------------------- banner (the sway is done by the dressing actor: Python cannot reach world position offset)
banner = ensure("M_Banner", unreal.Material, unreal.MaterialFactoryNew())
clear(banner)
banner.set_editor_property("two_sided", True)
crimson = node(banner, unreal.MaterialExpressionConstant3Vector, -900, -300)
crimson.set_editor_property("constant", unreal.LinearColor(0.16, 0.012, 0.016, 1.0))
gold = node(banner, unreal.MaterialExpressionConstant3Vector, -900, -150)
gold.set_editor_property("constant", unreal.LinearColor(0.55, 0.38, 0.08, 1.0))
uv = node(banner, unreal.MaterialExpressionTextureCoordinate, -1300, 150)
v = node(banner, unreal.MaterialExpressionComponentMask, -1100, 150)
v.set_editor_property("g", True)
v.set_editor_property("r", False)
link(uv, v)
# trim bands at both ends: saturate((v - 0.93) * 60) and saturate((0.07 - v) * 60)
sub_hi = node(banner, unreal.MaterialExpressionSubtract, -900, 100)
link(v, sub_hi, "", "A")
k_hi = node(banner, unreal.MaterialExpressionConstant, -1100, 260)
k_hi.set_editor_property("r", 0.93)
link(k_hi, sub_hi, "", "B")
mul_hi = node(banner, unreal.MaterialExpressionMultiply, -700, 100)
link(sub_hi, mul_hi, "", "A")
gain = node(banner, unreal.MaterialExpressionConstant, -900, 260)
gain.set_editor_property("r", 60.0)
link(gain, mul_hi, "", "B")
sat_hi = node(banner, unreal.MaterialExpressionSaturate, -520, 100)
link(mul_hi, sat_hi)
sub_lo = node(banner, unreal.MaterialExpressionSubtract, -900, 380)
k_lo = node(banner, unreal.MaterialExpressionConstant, -1100, 380)
k_lo.set_editor_property("r", 0.07)
link(k_lo, sub_lo, "", "A")
link(v, sub_lo, "", "B")
mul_lo = node(banner, unreal.MaterialExpressionMultiply, -700, 380)
link(sub_lo, mul_lo, "", "A")
link(gain, mul_lo, "", "B")
sat_lo = node(banner, unreal.MaterialExpressionSaturate, -520, 380)
link(mul_lo, sat_lo)
band = node(banner, unreal.MaterialExpressionAdd, -340, 240)
link(sat_hi, band, "", "A")
link(sat_lo, band, "", "B")
sat_band = node(banner, unreal.MaterialExpressionSaturate, -200, 240)
link(band, sat_band)
mix = node(banner, unreal.MaterialExpressionLinearInterpolate, -60, -200)
link(crimson, mix, "", "A")
link(gold, mix, "", "B")
link(sat_band, mix, "", "Alpha")
ml.connect_material_property(mix, "", unreal.MaterialProperty.MP_BASE_COLOR)
rough = node(banner, unreal.MaterialExpressionConstant, -60, -40)
rough.set_editor_property("r", 0.88)
ml.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
ml.recompile_material(banner)
unreal.EditorAssetLibrary.save_loaded_asset(banner)
log("M_Banner done")

# ---------------------------------------------------------------- mist cards
parent_fog = unreal.EditorAssetLibrary.load_asset("/Game/Materials/FogCards/M_FogCard")
mist = ensure("MI_Arena_Mist", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
mist.set_editor_property("parent", parent_fog)
for name, value in (("Emissive intensity", 110.0), ("Base Opacity - Intensity", 1.1), ("Base Opacity - Contrast", 1.2), ("FlowMap Intensity", 1.0), ("FlowSpeed", 0.04), ("Normal Intensity", 0.5)):
    ml.set_material_instance_scalar_parameter_value(mist, name, value)
ml.set_material_instance_vector_parameter_value(mist, "Base Color", unreal.LinearColor(0.28, 0.34, 0.50, 1.0))
ml.update_material_instance(mist)
unreal.EditorAssetLibrary.save_loaded_asset(mist)
log("MI_Arena_Mist done")

gate = ensure("MI_Arena_FogGate", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
gate.set_editor_property("parent", parent_fog)
for name, value in (("Emissive intensity", 700.0), ("Base Opacity - Intensity", 2.2), ("Base Opacity - Contrast", 1.0), ("FlowMap Intensity", 1.0), ("FlowSpeed", 0.08), ("Normal Intensity", 0.3)):
    ml.set_material_instance_scalar_parameter_value(gate, name, value)
ml.set_material_instance_vector_parameter_value(gate, "Base Color", unreal.LinearColor(0.55, 0.65, 0.9, 1.0))
ml.update_material_instance(gate)
unreal.EditorAssetLibrary.save_loaded_asset(gate)
log("MI_Arena_FogGate done")

# ---------------------------------------------------------------- pillar stone
pillar = ensure("MI_Arena_Pillar", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
pillar.set_editor_property("parent", unreal.EditorAssetLibrary.load_asset("/Game/MS/Surfaces/Roman_Stone_Floor_thsjdfxq/MI_Roman_Stone_Floor_thsjdfxq_1"))
ml.set_material_instance_scalar_parameter_value(pillar, "UVs - Base  Scale", 3.0)
ml.set_material_instance_scalar_parameter_value(pillar, "Gen - Final Roughness (Offset)", 0.25)
ml.set_material_instance_vector_parameter_value(pillar, "Base - Albedo Tint", unreal.LinearColor(0.45, 0.43, 0.41, 1.0))
ml.update_material_instance(pillar)
unreal.EditorAssetLibrary.save_loaded_asset(pillar)
log("MI_Arena_Pillar done")

# ---------------------------------------------------------------- ground outside the arena wall (no more bright void under the ruins)
outside = ensure("MI_Arena_Outside", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
outside.set_editor_property("parent", unreal.EditorAssetLibrary.load_asset("/Game/MS/Surfaces/Gravel_Ground_vi0maebg/MI_Gravel_Ground_vi0maebg"))
ml.set_material_instance_scalar_parameter_value(outside, "UVs - Base  Scale", 70.0)
ml.set_material_instance_scalar_parameter_value(outside, "Gen - Final Roughness (Offset)", 0.6)
ml.set_material_instance_scalar_parameter_value(outside, "Specular Max", 0.2)
ml.set_material_instance_scalar_parameter_value(outside, "Shore Wetness - Additional Spec", 0.0)
ml.set_material_instance_vector_parameter_value(outside, "Base - Albedo Tint", unreal.LinearColor(0.16, 0.15, 0.14, 1.0))
ml.set_material_instance_static_switch_parameter_value(outside, "Enable Wetness", False)
ml.update_material_instance(outside)
unreal.EditorAssetLibrary.save_loaded_asset(outside)
log("MI_Arena_Outside done")
