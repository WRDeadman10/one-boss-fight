"""Creates M_Gate_Rune (log prefix [GateRune]): the dim ember glow for the rune slot of the M-08 fog gate frame (M_Ember is far too bright for a big lintel panel: it blooms to white). Dark base, emissive ember orange with a slow pulse. New asset only; run once (skips when it exists)."""
import unreal

log = lambda m: unreal.log("[GateRune] " + m)
PATH = "/Game/OneBossFight/Environment/Materials"
NAME = "M_Gate_Rune"
if unreal.EditorAssetLibrary.does_asset_exist(PATH + "/" + NAME):
    log("exists, nothing to do")
else:
    L = unreal.MaterialEditingLibrary
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(NAME, PATH, unreal.Material, unreal.MaterialFactoryNew())
    base = L.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -700, -200)
    base.set_editor_property("constant", unreal.LinearColor(0.02, 0.012, 0.01, 1.0))
    L.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    ember = L.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -700, 100)
    ember.set_editor_property("constant", unreal.LinearColor(1.0, 0.28, 0.04, 1.0))
    time = L.create_material_expression(mat, unreal.MaterialExpressionTime, -1100, 300)
    sine = L.create_material_expression(mat, unreal.MaterialExpressionSine, -900, 300)
    mul_t = L.create_material_expression(mat, unreal.MaterialExpressionMultiply, -1000, 300)
    speed = L.create_material_expression(mat, unreal.MaterialExpressionConstant, -1100, 400)
    speed.set_editor_property("r", 0.8)
    L.connect_material_expressions(time, "", mul_t, "A")
    L.connect_material_expressions(speed, "", mul_t, "B")
    L.connect_material_expressions(mul_t, "", sine, "")
    # pulse = 0.55 + 0.25 * sin(t): between 0.3 and 0.8 of the base ember strength
    amp = L.create_material_expression(mat, unreal.MaterialExpressionConstant, -800, 400)
    amp.set_editor_property("r", 0.25)
    mul_a = L.create_material_expression(mat, unreal.MaterialExpressionMultiply, -700, 330)
    L.connect_material_expressions(sine, "", mul_a, "A")
    L.connect_material_expressions(amp, "", mul_a, "B")
    off = L.create_material_expression(mat, unreal.MaterialExpressionConstant, -700, 430)
    off.set_editor_property("r", 0.55)
    add = L.create_material_expression(mat, unreal.MaterialExpressionAdd, -550, 350)
    L.connect_material_expressions(mul_a, "", add, "A")
    L.connect_material_expressions(off, "", add, "B")
    gain = L.create_material_expression(mat, unreal.MaterialExpressionConstant, -550, 450)
    gain.set_editor_property("r", 2.2)
    mul_g = L.create_material_expression(mat, unreal.MaterialExpressionMultiply, -400, 380)
    L.connect_material_expressions(add, "", mul_g, "A")
    L.connect_material_expressions(gain, "", mul_g, "B")
    mul_e = L.create_material_expression(mat, unreal.MaterialExpressionMultiply, -250, 200)
    L.connect_material_expressions(ember, "", mul_e, "A")
    L.connect_material_expressions(mul_g, "", mul_e, "B")
    L.connect_material_property(mul_e, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    L.recompile_material(mat)
    log("created %s/%s" % (PATH, NAME))
log("DONE")
