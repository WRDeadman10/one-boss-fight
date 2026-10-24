"""Imports AG's three effect flipbook sheets and builds their materials (log prefix [Flipbook]).
Sheets (Import/Boss01/Effects, 2048 x 2048, 8 x 8 cells, 64 frames, row-major from the top left): FB_Boss01_BloodBurst, FB_Boss01_DodgeDust (straight alpha), FB_Boss01_HitSpark (additive, RGB on black).
Assets in /Game/OneBossFight/Effects/Flipbook: textures T_FB_*, parents M_Boss01_Flipbook_Alpha (translucent, unlit) and M_Boss01_Flipbook_Additive (additive, unlit), and the three instances the code uses: MI_Boss01_FB_BloodBurst, MI_Boss01_FB_DodgeDust, MI_Boss01_FB_HitSpark.
Parameters (all of them, on the instances): scalar Frame (0..63, floored in the material), Columns (8), Rows (8), vector Tint (rgb colour multiplier, a = opacity or additive strength).
Idempotent: textures are re-imported in place, the parents are rebuilt in place (graph cleared), the instances are created when missing and their parameters set again."""
import os
import unreal

log = lambda m: unreal.log("[Flipbook] " + m)
proj = unreal.SystemLibrary.get_project_directory()
DEST = "/Game/OneBossFight/Effects/Flipbook"
tools = unreal.AssetToolsHelpers.get_asset_tools()
L = unreal.MaterialEditingLibrary
SHEETS = {"BloodBurst": "FB_Boss01_BloodBurst", "DodgeDust": "FB_Boss01_DodgeDust", "HitSpark": "FB_Boss01_HitSpark"}


def import_sheet(key, src):
    t = unreal.AssetImportTask()
    t.filename = os.path.join(proj, "Import", "Boss01", "Effects", src + ".png").replace("/", os.sep)
    t.destination_path, t.destination_name = DEST, "T_FB_" + key
    t.automated, t.save, t.replace_existing = True, False, True
    tools.import_asset_tasks([t])
    tex = unreal.load_asset(DEST + "/T_FB_" + key)
    tex.set_editor_property("srgb", True)
    tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    tex.set_editor_property("address_x", unreal.TextureAddress.TA_CLAMP)
    tex.set_editor_property("address_y", unreal.TextureAddress.TA_CLAMP)
    tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_BC7)
    return tex


def build_parent(name, additive):
    path = DEST + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mat = unreal.load_asset(path)
        L.delete_all_material_expressions(mat)
    else:
        mat = tools.create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE if additive else unreal.BlendMode.BLEND_TRANSLUCENT)
    mat.set_editor_property("two_sided", True)

    def node(cls, x, y):
        return L.create_material_expression(mat, cls, x, y)

    def link(a, b, pin="", out=""):
        L.connect_material_expressions(a, out, b, pin)

    def scalar(pname, v, x, y):
        n = node(unreal.MaterialExpressionScalarParameter, x, y)
        n.set_editor_property("parameter_name", pname)
        n.set_editor_property("default_value", v)
        return n

    frame = scalar("Frame", 0.0, -1400, -100)
    cols = scalar("Columns", 8.0, -1400, 40)
    rows = scalar("Rows", 8.0, -1400, 180)
    f_floor = node(unreal.MaterialExpressionFloor, -1220, -100); link(frame, f_floor)
    col = node(unreal.MaterialExpressionFmod, -1040, -60); link(f_floor, col, "A"); link(cols, col, "B")
    f_div = node(unreal.MaterialExpressionDivide, -1220, 60); link(f_floor, f_div, "A"); link(cols, f_div, "B")
    row = node(unreal.MaterialExpressionFloor, -1040, 60); link(f_div, row)
    offset = node(unreal.MaterialExpressionAppendVector, -860, 0); link(col, offset, "A"); link(row, offset, "B")
    size = node(unreal.MaterialExpressionAppendVector, -860, 160); link(cols, size, "A"); link(rows, size, "B")
    tc = node(unreal.MaterialExpressionTextureCoordinate, -860, -120)
    add = node(unreal.MaterialExpressionAdd, -660, -60); link(tc, add, "A"); link(offset, add, "B")
    uv = node(unreal.MaterialExpressionDivide, -480, -40); link(add, uv, "A"); link(size, uv, "B")
    sheet = node(unreal.MaterialExpressionTextureSampleParameter2D, -300, -40)
    sheet.set_editor_property("parameter_name", "Sheet")
    L.connect_material_expressions(uv, "", sheet, "UVs")
    tint = node(unreal.MaterialExpressionVectorParameter, -300, 160)
    tint.set_editor_property("parameter_name", "Tint")
    tint.set_editor_property("default_value", unreal.LinearColor(1.0, 1.0, 1.0, 1.0))
    color = node(unreal.MaterialExpressionMultiply, -100, 0); link(sheet, color, "A", "RGB"); link(tint, color, "B", "RGB")
    if additive:
        # additive: the tint alpha is the strength; the sheet alpha is 1 everywhere (RGB on black)
        strength = node(unreal.MaterialExpressionMultiply, 100, 0); link(color, strength, "A"); link(tint, strength, "B", "A")
        L.connect_material_property(strength, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    else:
        L.connect_material_property(color, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        opacity = node(unreal.MaterialExpressionMultiply, 100, 120); link(sheet, opacity, "A", "A"); link(tint, opacity, "B", "A")
        L.connect_material_property(opacity, "", unreal.MaterialProperty.MP_OPACITY)
    L.recompile_material(mat)
    log("built %s (%s)" % (name, "additive" if additive else "translucent"))
    return mat


def make_instance(name, parent, tex, tint):
    path = DEST + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mi = unreal.load_asset(path)
    else:
        mi = tools.create_asset(name, DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mi.set_editor_property("parent", parent)
    L.set_material_instance_texture_parameter_value(mi, "Sheet", tex)
    L.set_material_instance_scalar_parameter_value(mi, "Columns", 8.0)
    L.set_material_instance_scalar_parameter_value(mi, "Rows", 8.0)
    L.set_material_instance_scalar_parameter_value(mi, "Frame", 0.0)
    L.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(*tint))
    L.update_material_instance(mi)
    log("instance %s -> %s, sheet %s" % (name, parent.get_name(), tex.get_name()))
    return mi


tex = {k: import_sheet(k, v) for k, v in SHEETS.items()}
alpha = build_parent("M_Boss01_Flipbook_Alpha", False)
add = build_parent("M_Boss01_Flipbook_Additive", True)
instances = [
    make_instance("MI_Boss01_FB_BloodBurst", alpha, tex["BloodBurst"], (1.0, 1.0, 1.0, 1.0)),
    make_instance("MI_Boss01_FB_DodgeDust", alpha, tex["DodgeDust"], (1.0, 1.0, 1.0, 0.85)),
    make_instance("MI_Boss01_FB_HitSpark", add, tex["HitSpark"], (1.6, 1.3, 1.0, 1.0)),
]
for asset in list(tex.values()) + [alpha, add] + instances:
    p = asset.get_path_name().split(".")[0]
    log("save %s: %s" % (p, unreal.EditorAssetLibrary.save_asset(p, only_if_is_dirty=False)))
log("DONE")
