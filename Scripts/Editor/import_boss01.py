"""Imports Antigravity's Boss 01 deliveries into /Game/OneBossFight/Boss01 (log prefix [Import]): body on SK_CombatMannequin, sword, A2 clips, dormant idle and wake clips. Then reattaches the original Paragon Sevarog materials by slot name.
Run with Scripts/run_in_editor.py. Own content (Antigravity's work), tracked by git; the Paragon materials stay referenced from the ignored Paragon folder."""
import os
import unreal

log = lambda m: unreal.log("[Import] " + m)
proj = unreal.SystemLibrary.get_project_directory()
SKEL = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin"
tools = unreal.AssetToolsHelpers.get_asset_tools()


def run(task):
    tools.import_asset_tasks([task])
    return [str(p) for p in task.imported_object_paths]


def base_task(fbx, dest, name):
    t = unreal.AssetImportTask()
    t.filename = os.path.join(proj, "Import", "Boss01", fbx).replace("/", os.sep)
    t.destination_path = dest
    t.destination_name = name
    t.automated = True
    t.save = False
    t.replace_existing = True
    t.replace_existing_settings = True
    return t


skel = unreal.load_asset(SKEL)
# body
t = base_task("SK_Boss01_Body.fbx", "/Game/OneBossFight/Boss01/Body", "SK_Boss01_Body")
o = unreal.FbxImportUI()
o.set_editor_property("import_mesh", True)
o.set_editor_property("import_as_skeletal", True)
o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
o.set_editor_property("skeleton", skel)
o.set_editor_property("import_materials", False)
o.set_editor_property("import_textures", False)
o.set_editor_property("import_animations", False)
o.skeletal_mesh_import_data.set_editor_property("import_morph_targets", False)
t.options = o
log("body -> %s" % run(t))

# sword
t = base_task("Weapons/SM_Boss01_Greatsword.fbx", "/Game/OneBossFight/Boss01/Weapons", "SM_Boss01_Greatsword")
o = unreal.FbxImportUI()
o.set_editor_property("import_mesh", True)
o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
o.set_editor_property("import_materials", False)
o.set_editor_property("import_textures", False)
o.set_editor_property("import_animations", False)
t.options = o
log("sword -> %s" % run(t))

# animations
for clip in ("AN_Boss01_A2_Raise", "AN_Boss01_A2_ApexHold", "AN_Boss01_A2_Slam", "AN_Boss01_DormantIdle", "AN_Boss01_Wake", "AN_Boss01_A4_LowSweep", "AN_Boss01_A5_JavelinThrow", "AN_Boss01_A1_QuickSlash", "AN_Boss01_A3a_Combo1", "AN_Boss01_A3b_Combo2"):
    old = "/Game/OneBossFight/Boss01/Animations/" + clip
    if unreal.EditorAssetLibrary.does_asset_exist(old):
        unreal.EditorAssetLibrary.delete_asset(old)  # a replaced clip with another frame rate cannot be imported over the old one
    t = base_task("Animations/%s.fbx" % clip, "/Game/OneBossFight/Boss01/Animations", clip)
    o = unreal.FbxImportUI()
    o.set_editor_property("import_mesh", False)
    o.set_editor_property("import_as_skeletal", False)
    o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
    o.set_editor_property("skeleton", skel)
    o.set_editor_property("import_animations", True)
    o.set_editor_property("import_materials", False)
    o.set_editor_property("import_textures", False)
    t.options = o
    paths = run(t)
    log("%s -> %s" % (clip, paths))
    for p in paths:
        a = unreal.load_asset(p.split(".")[0])
        if a:
            unreal.EditorAssetLibrary.save_loaded_asset(a)  # an unsaved clip is gone after an editor restart
            try:
                log("   length %.3f s, rate %.1f, frames %d" % (a.get_editor_property("sequence_length"), a.get_editor_property("rate_scale") if False else 1.0, a.get_editor_property("number_of_sampled_frames") if hasattr(a, "number_of_sampled_frames") else -1))
            except Exception as e:
                log("   info ERR %s" % e)

# materials by slot name
ar = unreal.AssetRegistryHelpers.get_asset_registry()
want = {"M00_Torso_skin00": "M_Sevarog_Torso", "M01_Shoulders_skin01": "M_Sevarog_ArmourRuins", "M02_Arms_skin02": "M_Sevarog_Back_01", "M03_Dress_skin03": "M_Sevarog_Chainmail", "M06_Black": "M_invis"}
mats = {}
for ad in ar.get_assets_by_path("/Game/ParagonSevarog", recursive=True):
    n = str(ad.asset_name)
    if n in want.values() and str(ad.asset_class_path.asset_name) in ("Material", "MaterialInstanceConstant") and n not in mats and "Skins" not in str(ad.package_path):
        mats[n] = ad.get_asset()
log("found materials %s" % list(mats))
body = unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body")
if body:
    slots = body.get_editor_property("materials")
    log("body slots %s" % [str(s.get_editor_property("material_slot_name")) for s in slots])
    new = []
    for s in slots:
        nm = str(s.get_editor_property("material_slot_name"))
        mat = mats.get(want.get(nm))
        if mat:
            s.set_editor_property("material_interface", mat)
        new.append(s)
    body.set_editor_property("materials", new)
    b = body.get_bounds()
    log("body size %.0f x %.0f x %.0f cm" % (b.box_extent.x * 2, b.box_extent.y * 2, b.box_extent.z * 2))
    unreal.EditorAssetLibrary.save_loaded_asset(body)
log("done")

# the FBX importer turns spaces in socket names into underscores: the pack's trace names them with a space
sword = unreal.load_asset("/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword")
if sword:
    for sock in sword.get_sockets_by_tag(""):
        n = str(sock.get_editor_property("socket_name"))
        if n in ("Weapon_Start", "Weapon_End"):
            sock.set_editor_property("socket_name", n.replace("_", " "))
    unreal.EditorAssetLibrary.save_loaded_asset(sword)
    log("sword sockets now %s" % [str(s.get_editor_property("socket_name")) for s in sword.get_sockets_by_tag("")])

if sword:
    log("sword material slots: %s" % [str(m.get_editor_property("material_slot_name")) for m in sword.get_editor_property("static_materials")])
    sb = sword.get_bounds()
    log("sword size %.1f x %.1f x %.1f cm" % (sb.box_extent.x * 2, sb.box_extent.y * 2, sb.box_extent.z * 2))

# modular customisation pieces (skeletal meshes on the same skeleton)
for piece in ("SK_Boss01_Crown", "SK_Boss01_Mantle", "SK_Boss01_BrazierGauntlet"):
    t = base_task(piece + ".fbx", "/Game/OneBossFight/Boss01/Body", piece)
    o = unreal.FbxImportUI()
    o.set_editor_property("import_mesh", True)
    o.set_editor_property("import_as_skeletal", True)
    o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    o.set_editor_property("skeleton", skel)
    o.set_editor_property("import_materials", False)
    o.set_editor_property("import_textures", False)
    o.set_editor_property("import_animations", False)
    t.options = o
    log("%s -> %s" % (piece, run(t)))
    m = unreal.load_asset("/Game/OneBossFight/Boss01/Body/" + piece)
    if m:
        b = m.get_bounds()
        log("   %s size %.1f x %.1f x %.1f cm, centre z %.0f, slots %s, skeleton %s" % (piece, b.box_extent.x * 2, b.box_extent.y * 2, b.box_extent.z * 2, b.origin.z, [str(x.get_editor_property("material_slot_name")) for x in m.get_editor_property("materials")], m.get_editor_property("skeleton").get_name() if m.get_editor_property("skeleton") else None))
        unreal.EditorAssetLibrary.save_loaded_asset(m)

# the thrown javelin of A5 (static mesh, origin at the tail, points along +X)
t = base_task("Weapons/SM_Boss01_EmberJavelin.fbx", "/Game/OneBossFight/Boss01/Weapons", "SM_Boss01_EmberJavelin")
o = unreal.FbxImportUI()
o.set_editor_property("import_mesh", True)
o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
o.set_editor_property("import_materials", False)
o.set_editor_property("import_textures", False)
o.set_editor_property("import_animations", False)
t.options = o
log("javelin -> %s" % run(t))
jav = unreal.load_asset("/Game/OneBossFight/Boss01/Weapons/SM_Boss01_EmberJavelin")
if jav:
    jb = jav.get_bounds()
    log("javelin size %.1f x %.1f x %.1f cm, origin offset x %.1f, slots %s" % (jb.box_extent.x * 2, jb.box_extent.y * 2, jb.box_extent.z * 2, jb.origin.x - jb.box_extent.x, [str(m.get_editor_property("material_slot_name")) for m in jav.get_editor_property("static_materials")]))
    unreal.EditorAssetLibrary.save_loaded_asset(jav)
