"""Review of Antigravity's Report 10 inside the engine (log prefix [Review10]): imports the delivered files into the scratch folder /Game/OneBossFight/_Review10 (nothing that exists is touched or deleted), then prints
engine lengths and frame counts of the new clips, the pelvis height over time, the closure of the StaggerDown loop (every bone at the first and the last frame), the sword's sockets, triangles, bounds and material slots, the javelin's slots,
and the bounds of the crown next to the bounds of the existing body. Run with Scripts/run_in_editor.py, read the log. The scratch folder can be deleted afterwards (nothing references it)."""
import os
import unreal

log = lambda m: unreal.log("[Review10] " + m)
proj = unreal.SystemLibrary.get_project_directory()
tools = unreal.AssetToolsHelpers.get_asset_tools()
SKEL = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin"
DEST = "/Game/OneBossFight/_Review10"
skel = unreal.load_asset(SKEL)


def task(rel, name, options):
    t = unreal.AssetImportTask()
    t.filename = os.path.join(proj, "Import", "Boss01", rel).replace("/", os.sep)
    t.destination_path = DEST
    t.destination_name = name
    t.automated = True
    t.save = False
    t.replace_existing = True
    t.replace_existing_settings = True
    t.options = options
    tools.import_asset_tasks([t])
    return unreal.load_asset(DEST + "/" + name)


def anim_options():
    o = unreal.FbxImportUI()
    o.set_editor_property("import_mesh", False)
    o.set_editor_property("import_as_skeletal", False)
    o.set_editor_property("import_animations", True)
    o.set_editor_property("skeleton", skel)
    o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
    return o


BONES = ["pelvis", "spine_01", "spine_03", "head", "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r", "upperarm_l", "hand_l", "upperarm_r", "hand_r"]
for clip in ("AN_Boss01_A3a_Combo1", "AN_Boss01_A3b_Combo2", "AN_Boss01_PhaseRoar", "AN_Boss01_StaggerFall", "AN_Boss01_StaggerDown", "AN_Boss01_StaggerGetUp"):
    a = task("Animations/%s.fbx" % clip, clip, anim_options())
    if not a:
        log("%s: import failed" % clip)
        continue
    length = a.get_editor_property("sequence_length")
    frames = unreal.AnimationLibrary.get_num_frames(a)
    log("%s: engine length %.4f s, %d frames" % (clip, length, frames))
    for b in ("pelvis", "foot_l", "foot_r"):
        row = []
        for f in (0.0, 0.25, 0.5, 0.75, 1.0):
            tr = unreal.AnimationLibrary.get_bone_pose_for_time(a, b, length * f, False)
            row.append("%.1f" % tr.translation.z)
        log("   %-8s local z at 0, 25, 50, 75, 100 percent: %s" % (b, " ".join(row)))
    if clip == "AN_Boss01_StaggerDown":
        worst = (0.0, "")
        for b in BONES:
            t0 = unreal.AnimationLibrary.get_bone_pose_for_time(a, b, 0.0, False)
            t1 = unreal.AnimationLibrary.get_bone_pose_for_time(a, b, length, False)
            d = (t0.translation - t1.translation).length() + abs(t0.rotation.rotator().pitch - t1.rotation.rotator().pitch) + abs(t0.rotation.rotator().yaw - t1.rotation.rotator().yaw) + abs(t0.rotation.rotator().roll - t1.rotation.rotator().roll)
            if d > worst[0]:
                worst = (d, b)
        log("   loop closure: the largest difference between the first and the last frame over %d bones is %.4f (bone %s)" % (len(BONES), worst[0], worst[1]))

# sword
sm_opt = unreal.FbxImportUI()
sm_opt.set_editor_property("import_mesh", True)
sm_opt.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
sm_opt.set_editor_property("import_materials", False)
sm_opt.set_editor_property("import_textures", False)
sm_opt.set_editor_property("import_animations", False)
sw = task("Weapons/SM_Boss01_Greatsword.fbx", "SM_Boss01_Greatsword", sm_opt)
if sw:
    box = sw.get_bounding_box()
    found = []
    for name in ("BladeStart", "MiddleSocket", "BladeEnd", "Weapon_Start", "Weapon_End", "Weapon Start", "Weapon End", "TrailStartSocket", "TrailEndSocket", "SOCKET_BladeStart"):
        s = sw.find_socket(name)
        if s:
            loc = s.get_editor_property("relative_location")
            found.append("%s (%.1f, %.1f, %.1f)" % (name, loc.x, loc.y, loc.z))
    log("sword sockets found by name: %d: %s" % (len(found), found))
    log("sword: triangles %d, size %.1f x %.1f x %.1f cm, min %s max %s, slots %s" % (-1, box.max.x - box.min.x, box.max.y - box.min.y, box.max.z - box.min.z, box.min, box.max,
        [str(m.get_editor_property("material_slot_name")) for m in sw.get_editor_property("static_materials")]))
jv = task("Weapons/SM_Boss01_EmberJavelin.fbx", "SM_Boss01_EmberJavelin", sm_opt)
if jv:
    box = jv.get_bounding_box()
    log("javelin: triangles %d, size %.1f x %.1f x %.1f cm, slots %s" % (-1, box.max.x - box.min.x, box.max.y - box.min.y, box.max.z - box.min.z,
        [str(m.get_editor_property("material_slot_name")) for m in jv.get_editor_property("static_materials")]))

# crown next to the body (component space of the skeletal meshes)
sk_opt = unreal.FbxImportUI()
sk_opt.set_editor_property("import_mesh", True)
sk_opt.set_editor_property("import_as_skeletal", True)
sk_opt.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
sk_opt.set_editor_property("skeleton", skel)
sk_opt.set_editor_property("import_materials", False)
sk_opt.set_editor_property("import_textures", False)
sk_opt.set_editor_property("import_animations", False)
crown = task("SK_Boss01_Crown.fbx", "SK_Boss01_Crown", sk_opt)
body = unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body")
for label, m in (("crown", crown), ("body", body)):
    if m:
        b = m.get_bounds()
        log("%s (engine, component space): z %.2f to %.2f, x %.1f to %.1f, y %.1f to %.1f" % (label, b.origin.z - b.box_extent.z, b.origin.z + b.box_extent.z, b.origin.x - b.box_extent.x, b.origin.x + b.box_extent.x, b.origin.y - b.box_extent.y, b.origin.y + b.box_extent.y))
log("done")
