"""AGI-4: builds the Boss 01 materials from Antigravity's texture files (log prefix [BossMats]).
Imports Import/Boss01/Textures/<Set>/T_Boss01_<Set>_{BaseColor,Normal,ORM,Emissive}.png into /Game/OneBossFight/Boss01/Textures/<Set>,
builds the master material M_Boss01_Master and one instance M_Boss01_<Set> per set (the names are her FBX slot names).
Master parameters (scalar): PhaseGlow 0..1 (ember rim and emissive boost for phase two), Dissolve 0..1 (noise cut with a glowing edge, masked),
HitFlash 0..1 (white-hot flash), EmissiveStrength; vectors PhaseGlowColor, HitFlashColor, DissolveEdgeColor.
Then assigns the instances by slot name to the imported crown, mantle and gauntlet (unmatched slots are left alone; sword and javelin only get their slots logged).
Re-runnable: existing assets are reused, never deleted. Run with Scripts/run_in_editor.py."""
import os
import re
import unreal

log = lambda m: unreal.log("[BossMats] " + m)
ml = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
proj = unreal.SystemLibrary.get_project_directory()
SRC = os.path.join(proj, "Import", "Boss01", "Textures")
DEST = "/Game/OneBossFight/Boss01/Textures"
MAT = "/Game/OneBossFight/Boss01/Materials"
SETS = {  # name: (emissive map present, emissive strength, two sided)
    "BlackPlate": (False, 0.0, False), "Blade": (False, 0.0, False), "Blade_Glow": (True, 6.0, False),
    "CrimsonCloth": (False, 0.0, True), "EmberGlow": (True, 6.0, False), "GoldTrim": (False, 0.0, False),
    "Guard_Grip": (False, 0.0, False), "Javelin_Glow": (True, 6.0, False), "Javelin_Grip": (False, 0.0, False),
    "Javelin_Iron": (False, 0.0, False),
}


def import_texture(path, dest, name, kind):
    t = unreal.AssetImportTask()
    t.filename = path
    t.destination_path = dest
    t.destination_name = name
    t.automated = True
    t.save = False
    t.replace_existing = True
    t.replace_existing_settings = True
    tools.import_asset_tasks([t])
    tex = eal.load_asset(dest + "/" + name)
    if not tex:
        log("FAILED import %s" % path)
        return None
    if kind == "Normal":
        tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
        tex.set_editor_property("srgb", False)
    elif kind == "ORM":
        tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
        tex.set_editor_property("srgb", False)
    else:
        tex.set_editor_property("srgb", True)
    eal.save_loaded_asset(tex)
    return tex


def node(mat, cls, x, y):
    return ml.create_material_expression(mat, cls, x, y)


def link(a, b, out="", inp=""):
    ml.connect_material_expressions(a, out, b, inp)


def scalar(mat, name, default, x, y):
    n = node(mat, unreal.MaterialExpressionScalarParameter, x, y)
    n.set_editor_property("parameter_name", name)
    n.set_editor_property("default_value", default)
    return n


def vector(mat, name, color, x, y):
    n = node(mat, unreal.MaterialExpressionVectorParameter, x, y)
    n.set_editor_property("parameter_name", name)
    n.set_editor_property("default_value", color)
    return n


def texparam(mat, name, default_tex, sampler, x, y):
    n = node(mat, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
    n.set_editor_property("parameter_name", name)
    n.set_editor_property("texture", default_tex)
    n.set_editor_property("sampler_type", sampler)
    return n


def mul(mat, a, b, x, y, ao="", bo=""):
    m = node(mat, unreal.MaterialExpressionMultiply, x, y)
    link(a, m, ao, "A")
    link(b, m, bo, "B")
    return m


def add(mat, a, b, x, y, ao="", bo=""):
    m = node(mat, unreal.MaterialExpressionAdd, x, y)
    link(a, m, ao, "A")
    link(b, m, bo, "B")
    return m


def const(mat, v, x, y):
    c = node(mat, unreal.MaterialExpressionConstant, x, y)
    c.set_editor_property("r", v)
    return c


# ------------------------------------------------------------------ textures
for d in (DEST, MAT):
    if not eal.does_directory_exist(d):
        eal.make_directory(d)
imported = {}
for name, (has_em, _, _) in SETS.items():
    folder = os.path.join(SRC, name)
    for kind in ("BaseColor", "Normal", "ORM") + (("Emissive",) if has_em else ()):
        f = os.path.join(folder, "T_Boss01_%s_%s.png" % (name, kind))
        tn = "T_Boss01_%s_%s" % (name, kind)
        full = "%s/%s/%s" % (DEST, name, tn)
        if eal.does_asset_exist(full):
            imported[(name, kind)] = eal.load_asset(full)
        elif os.path.exists(f):
            imported[(name, kind)] = import_texture(f, "%s/%s" % (DEST, name), tn, kind)
        else:
            log("MISSING file %s" % f)
log("textures ready: %d" % len([v for v in imported.values() if v]))

# ------------------------------------------------------------------ master material
mpath = MAT + "/M_Boss01_Master"
if eal.does_asset_exist(mpath):
    master = eal.load_asset(mpath)
else:
    master = tools.create_asset("M_Boss01_Master", MAT, unreal.Material, unreal.MaterialFactoryNew())
ml.delete_all_material_expressions(master)
master.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
master.set_editor_property("opacity_mask_clip_value", 0.5)
master.set_editor_property("two_sided", False)
for flag in ("used_with_skeletal_mesh", "used_with_static_lighting"):
    try:
        master.set_editor_property(flag, flag == "used_with_skeletal_mesh")
    except Exception as e:
        log("flag %s: %s" % (flag, e))

# parameter defaults must match the sampler type (a mismatch fails the compile): use our own textures of the right kind
d_base = imported[("BlackPlate", "BaseColor")]
d_nrm = imported[("BlackPlate", "Normal")]
d_orm = imported[("BlackPlate", "ORM")]
S = unreal.MaterialSamplerType
base = texparam(master, "BaseColorMap", d_base, S.SAMPLERTYPE_COLOR, -1400, -400)
nrm = texparam(master, "NormalMap", d_nrm, S.SAMPLERTYPE_NORMAL, -1400, -150)
orm = texparam(master, "ORMMap", d_orm, S.SAMPLERTYPE_MASKS, -1400, 100)
ems = texparam(master, "EmissiveMap", d_base, S.SAMPLERTYPE_COLOR, -1400, 350)
ml.connect_material_property(base, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
ml.connect_material_property(nrm, "RGB", unreal.MaterialProperty.MP_NORMAL)
ml.connect_material_property(orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
ml.connect_material_property(orm, "G", unreal.MaterialProperty.MP_ROUGHNESS)
ml.connect_material_property(orm, "B", unreal.MaterialProperty.MP_METALLIC)

phase = scalar(master, "PhaseGlow", 0.0, -1400, 600)
dissolve = scalar(master, "Dissolve", 0.0, -1400, 700)
hitflash = scalar(master, "HitFlash", 0.0, -1400, 800)
em_str = scalar(master, "EmissiveStrength", 0.0, -1400, 900)
phase_col = vector(master, "PhaseGlowColor", unreal.LinearColor(1.0, 0.18, 0.02, 1.0), -1400, 1000)
flash_col = vector(master, "HitFlashColor", unreal.LinearColor(1.0, 0.85, 0.6, 1.0), -1400, 1100)
edge_col = vector(master, "DissolveEdgeColor", unreal.LinearColor(1.0, 0.35, 0.05, 1.0), -1400, 1200)

# emissive map * strength * (1 + 2 * PhaseGlow)
boost = add(master, const(master, 1.0, -1100, 600), mul(master, phase, const(master, 2.0, -1250, 640), -1100, 650), -900, 620)
em_map = mul(master, mul(master, ems, em_str, -900, 400, "RGB", ""), boost, -700, 420)
# ember rim: fresnel (pure rim) * PhaseGlowColor * PhaseGlow * 2 (every material glows at the edges in phase two)
fres = node(master, unreal.MaterialExpressionFresnel, -1100, 1000)
fres.set_editor_property("exponent", 4.0)
fres.set_editor_property("base_reflect_fraction", 0.0)
rim = mul(master, mul(master, phase_col, phase, -900, 1000, "", ""), mul(master, fres, const(master, 2.0, -1100, 1100), -900, 1100), -700, 1040)
# hit flash: HitFlashColor * HitFlash * 3
flash = mul(master, mul(master, flash_col, hitflash, -900, 1250), const(master, 3.0, -900, 1350), -700, 1280)

# dissolve: noise in object space (position minus object origin), masked at 0.5, glowing edge band 0.12 wide
wp = node(master, unreal.MaterialExpressionWorldPosition, -1700, 1500)
op = node(master, unreal.MaterialExpressionObjectPositionWS, -1700, 1600)
rel = node(master, unreal.MaterialExpressionSubtract, -1500, 1520)
link(wp, rel, "", "A")
link(op, rel, "", "B")
noise = node(master, unreal.MaterialExpressionNoise, -1300, 1520)
for prop, val in (("scale", 0.06), ("levels", 3), ("output_min", 0.0), ("output_max", 1.0), ("turbulence", False), ("level_scale", 2.0)):
    try:
        noise.set_editor_property(prop, val)
    except Exception as e:
        log("noise %s: %s" % (prop, e))
link(rel, noise, "", "Position")
# m = noise + 1 - 1.6 * Dissolve: >= 1 at Dissolve 0 (all visible), <= 0.4 at Dissolve 1 (all gone); clip 0.5
m = node(master, unreal.MaterialExpressionSubtract, -1000, 1560)
link(add(master, noise, const(master, 1.0, -1250, 1640), -1150, 1560), m, "", "A")
link(mul(master, dissolve, const(master, 1.6, -1250, 1700), -1150, 1700), m, "", "B")
ml.connect_material_property(m, "", unreal.MaterialProperty.MP_OPACITY_MASK)
# edge = saturate(1 - (m - 0.5) / 0.12)
sub = node(master, unreal.MaterialExpressionSubtract, -800, 1560)
link(m, sub, "", "A")
link(const(master, 0.5, -950, 1640), sub, "", "B")
div = mul(master, sub, const(master, 1.0 / 0.12, -950, 1700), -650, 1560)
edge = node(master, unreal.MaterialExpressionSaturate, -450, 1560)
one_minus = node(master, unreal.MaterialExpressionOneMinus, -550, 1560)
link(one_minus, edge)
link(div, one_minus)
edge_em = mul(master, mul(master, edge_col, edge, -300, 1560), const(master, 25.0, -300, 1660), -100, 1580)

total = add(master, add(master, em_map, rim, -300, 700), add(master, flash, edge_em, -300, 1000), -100, 800)
ml.connect_material_property(total, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
ml.recompile_material(master)
eal.save_loaded_asset(master)
log("master built: %s" % mpath)

# ------------------------------------------------------------------ one instance per set
instances = {}
for name, (has_em, strength, two_sided) in SETS.items():
    ipath = "%s/M_Boss01_%s" % (MAT, name)
    if eal.does_asset_exist(ipath):
        mi = eal.load_asset(ipath)
    else:
        mi = tools.create_asset("M_Boss01_" + name, MAT, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mi.set_editor_property("parent", master)
    for kind, param in (("BaseColor", "BaseColorMap"), ("Normal", "NormalMap"), ("ORM", "ORMMap"), ("Emissive", "EmissiveMap")):
        t = imported.get((name, kind))
        if t:
            ml.set_material_instance_texture_parameter_value(mi, param, t)
    ml.set_material_instance_scalar_parameter_value(mi, "EmissiveStrength", strength)
    if two_sided:
        mi.set_editor_property("override_two_sided", True) if hasattr(mi, "override_two_sided") else None
        try:
            ov = mi.get_editor_property("base_property_overrides")
            ov.set_editor_property("override_two_sided", True)
            ov.set_editor_property("two_sided", True)
            mi.set_editor_property("base_property_overrides", ov)
        except Exception as e:
            log("two sided override %s: %s" % (name, e))
    ml.update_material_instance(mi)
    eal.save_loaded_asset(mi)
    instances[name] = mi
log("instances: %s" % sorted(instances))

# ------------------------------------------------------------------ assign by slot name to what is imported
targets = {
    "/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown": True,
    "/Game/OneBossFight/Boss01/Body/SK_Boss01_Mantle": True,
    "/Game/OneBossFight/Boss01/Body/SK_Boss01_BrazierGauntlet": True,
}
# the in-game sword and javelin are Report 08 imports whose slots carry wrong names: they get the instances after the Report 10 import (Brief 11 G1)
for path in ("/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword", "/Game/OneBossFight/Boss01/Weapons/SM_Boss01_EmberJavelin"):
    a = eal.load_asset(path)
    if a:
        log("%s slots (not assigned): %s" % (path.split("/")[-1], [str(s.get_editor_property("material_slot_name")) for s in a.get_editor_property("static_materials")]))
for path, skeletal in targets.items():
    a = eal.load_asset(path)
    if not a:
        log("not imported: %s" % path)
        continue
    prop = "materials" if skeletal else "static_materials"
    slots = list(a.get_editor_property(prop))
    names = [str(s.get_editor_property("material_slot_name")) for s in slots]
    changed = 0
    for s in slots:
        key = re.sub(r"\.\d+$", "", str(s.get_editor_property("material_slot_name")))
        key = key[len("M_Boss01_"):] if key.startswith("M_Boss01_") else None
        if key in instances:
            s.set_editor_property("material_interface", instances[key])
            changed += 1
    a.set_editor_property(prop, slots)
    eal.save_loaded_asset(a)
    log("%s slots %s -> %d assigned" % (path.split("/")[-1], names, changed))
log("done")
