"""Imports AG's V-09 textures and builds M_Boss01_Remains (log prefix [Remains]), the dissolve material of the boss's corpse statue.
Contract with RPGBossRemains (C++): scalar Dissolve (0 invisible .. 1 whole), vector Tint, scalar EmissiveBoost (default 1), scalar CoreGlow (default 0, steady Tint*CoreGlow emissive).
Masked material: pixel visible where noise < Dissolve; a 0.17 wide band at the cut edge reads the ember ramp (soot -> crimson -> amber -> white-hot) as emissive. UVs are world-space (the statue has no authored UV set to rely on). Idempotent: textures are re-imported in place; with REBUILD = True the graph of the existing material is cleared and built again in place."""
import os
import unreal

log = lambda m: unreal.log("[Remains] " + m)
proj = unreal.SystemLibrary.get_project_directory()
DEST = "/Game/OneBossFight/Boss01/Remains"
tools = unreal.AssetToolsHelpers.get_asset_tools()
L = unreal.MaterialEditingLibrary


def import_tex(name):
    t = unreal.AssetImportTask()
    t.filename = os.path.join(proj, "Import", "Boss01", "Effects", name + ".png").replace("/", os.sep)
    t.destination_path = DEST
    t.destination_name = name
    t.automated = True
    t.save = False
    t.replace_existing = True
    tools.import_asset_tasks([t])
    return unreal.load_asset(DEST + "/" + name)


noise = import_tex("T_Boss01_DissolveNoise")
ramp = import_tex("T_Boss01_DissolveRamp")
noise.set_editor_property("srgb", False)
noise.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
noise.set_editor_property("address_x", unreal.TextureAddress.TA_WRAP)
noise.set_editor_property("address_y", unreal.TextureAddress.TA_WRAP)
ramp.set_editor_property("address_x", unreal.TextureAddress.TA_CLAMP)
ramp.set_editor_property("address_y", unreal.TextureAddress.TA_CLAMP)
ramp.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
log("textures noise %s ramp %s" % (noise.get_name(), ramp.get_name()))

NAME = "M_Boss01_Remains"
REBUILD = False  # True: clear the graph of the existing asset and build it again in place (the asset keeps its identity, nothing that references it breaks)
exists = unreal.EditorAssetLibrary.does_asset_exist(DEST + "/" + NAME)
if exists and not REBUILD:
    log("%s exists: left as it is" % NAME)
else:
    if exists:
        mat = unreal.load_asset(DEST + "/" + NAME)
        L.delete_all_material_expressions(mat)
    else:
        mat = tools.create_asset(NAME, DEST, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    mat.set_editor_property("two_sided", True)

    def node(cls, x, y):
        return L.create_material_expression(mat, cls, x, y)

    def link(a, b, pin="", out=""):
        L.connect_material_expressions(a, out, b, pin)

    def const(v, x, y):
        n = node(unreal.MaterialExpressionConstant, x, y)
        n.set_editor_property("r", v)
        return n

    def scalar(name, v, x, y):
        n = node(unreal.MaterialExpressionScalarParameter, x, y)
        n.set_editor_property("parameter_name", name)
        n.set_editor_property("default_value", v)
        return n

    # world-space UV: two skewed projections so no axis of the statue stretches the noise
    wp = node(unreal.MaterialExpressionWorldPosition, -1700, 0)
    mask_x = node(unreal.MaterialExpressionComponentMask, -1500, -60)
    mask_x.set_editor_property("r", True); mask_x.set_editor_property("g", True); mask_x.set_editor_property("b", False); mask_x.set_editor_property("a", False)
    mask_z = node(unreal.MaterialExpressionComponentMask, -1500, 100)
    mask_z.set_editor_property("r", False); mask_z.set_editor_property("g", True); mask_z.set_editor_property("b", True); mask_z.set_editor_property("a", False)
    link(wp, mask_x); link(wp, mask_z)
    scale = const(1.0 / 350.0, -1500, 220)
    uv_a = node(unreal.MaterialExpressionMultiply, -1300, -60); link(mask_x, uv_a, "A"); link(scale, uv_a, "B")
    uv_b = node(unreal.MaterialExpressionMultiply, -1300, 100); link(mask_z, uv_b, "A"); link(scale, uv_b, "B")
    uv = node(unreal.MaterialExpressionAdd, -1100, 20); link(uv_a, uv, "A"); link(uv_b, uv, "B")

    tex = node(unreal.MaterialExpressionTextureSample, -900, 0)
    tex.set_editor_property("texture", noise)
    L.connect_material_expressions(uv, "", tex, "UVs")
    # a = noise * 0.8 + 0.1  (0.1 .. 0.9), so Dissolve 0 hides everything and Dissolve 1 shows everything
    a_mul = node(unreal.MaterialExpressionMultiply, -700, 0); link(tex, a_mul, "A", "R"); link(const(0.8, -900, 120), a_mul, "B")
    a = node(unreal.MaterialExpressionAdd, -520, 0); link(a_mul, a, "A"); link(const(0.1, -700, 120), a, "B")
    dissolve = scalar("Dissolve", 1.0, -700, -160)
    # the ember band is 0.17 wide and a tops out at 0.9: Dissolve 1 must put every pixel at least 0.17 past the cut, hence the 1.1 (no leftover glow on the whole statue)
    v_eff = node(unreal.MaterialExpressionMultiply, -520, -160); link(dissolve, v_eff, "A"); link(const(1.1, -700, -80), v_eff, "B")
    diff = node(unreal.MaterialExpressionSubtract, -340, -60); link(v_eff, diff, "A"); link(a, diff, "B")  # > 0 where the pixel is visible
    # opacity mask: clip at 0.5, so the cut sits exactly at diff = 0
    mask_mul = node(unreal.MaterialExpressionMultiply, -160, -60); link(diff, mask_mul, "A"); link(const(30.0, -340, 40), mask_mul, "B")
    mask_add = node(unreal.MaterialExpressionAdd, 20, -60); link(mask_mul, mask_add, "A"); link(const(0.5, -160, 40), mask_add, "B")
    mask_sat = node(unreal.MaterialExpressionSaturate, 200, -60); link(mask_add, mask_sat)
    L.connect_material_property(mask_sat, "", unreal.MaterialProperty.MP_OPACITY_MASK)

    # ember edge: U = 1 - saturate(diff / 0.17) reads the ramp (0 soot .. 1 burnout) in the 0.17 wide band behind the cut
    band = node(unreal.MaterialExpressionDivide, -160, 260); link(diff, band, "A"); link(const(0.17, -340, 330), band, "B")
    band_sat = node(unreal.MaterialExpressionSaturate, 20, 260); link(band, band_sat)
    u = node(unreal.MaterialExpressionOneMinus, 200, 260); link(band_sat, u)
    uv_ramp = node(unreal.MaterialExpressionAppendVector, 380, 260); link(u, uv_ramp, "A"); link(const(0.5, 200, 360), uv_ramp, "B")
    rtex = node(unreal.MaterialExpressionTextureSample, 560, 260)
    rtex.set_editor_property("texture", ramp)
    L.connect_material_expressions(uv_ramp, "", rtex, "UVs")
    in_band = node(unreal.MaterialExpressionMultiply, 380, 400); link(u, in_band, "A"); link(const(20.0, 200, 460), in_band, "B")
    in_band_sat = node(unreal.MaterialExpressionSaturate, 560, 440); link(in_band, in_band_sat)  # 0 outside the band: the soot end of the ramp must not light the whole statue
    ramp_rgb = node(unreal.MaterialExpressionMultiply, 640, 300); link(rtex, ramp_rgb, "A", "RGB"); link(in_band_sat, ramp_rgb, "B")
    edge_gain = node(unreal.MaterialExpressionMultiply, 760, 260); link(ramp_rgb, edge_gain, "A"); link(const(5.0, 560, 380), edge_gain, "B")
    boost = scalar("EmissiveBoost", 1.0, 760, 380)
    edge = node(unreal.MaterialExpressionMultiply, 940, 260); link(edge_gain, edge, "A"); link(boost, edge, "B")

    tint = node(unreal.MaterialExpressionVectorParameter, 200, -300)
    tint.set_editor_property("parameter_name", "Tint")
    tint.set_editor_property("default_value", unreal.LinearColor(0.1, 0.095, 0.09, 1.0))
    L.connect_material_property(tint, "", unreal.MaterialProperty.MP_BASE_COLOR)
    core = scalar("CoreGlow", 0.0, 200, -160)
    core_e = node(unreal.MaterialExpressionMultiply, 400, -230); link(tint, core_e, "A"); link(core, core_e, "B")
    total = node(unreal.MaterialExpressionAdd, 1120, 100); link(edge, total, "A"); link(core_e, total, "B")
    L.connect_material_property(total, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    rough = const(0.85, 200, -380)
    L.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    L.recompile_material(mat)
    log("built %s" % NAME)

for p in (DEST + "/T_Boss01_DissolveNoise", DEST + "/T_Boss01_DissolveRamp", DEST + "/" + NAME):
    log("save %s: %s" % (p, unreal.EditorAssetLibrary.save_asset(p, only_if_is_dirty=False)))
log("DONE")
