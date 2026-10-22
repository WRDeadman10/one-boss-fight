"""Review of Antigravity's Report 11 inside the engine (log prefix [Review11]): imports the delivered clips and the sword and javelin into the scratch folder /Game/OneBossFight/_Review11
(nothing that exists is touched or deleted) and prints, from the engine's own animation data:
 - length and frame count of every clip;
 - world (component space) height of pelvis, head, hands, feet and the root position at several times (AnimPose in world space, root motion included);
 - how far the whole body moves between two times (the sum and the largest of the joint position differences over all bones, in cm), which is the test of "does the clip move";
 - the paired riposte: the player's root travel, the boss reaction's first frame against the last frame of StaggerDown and its last frame against the first frame of StaggerDown (largest bone difference), the recoil at 0.8 s;
 - the death clip: pelvis height over time and the largest bone difference between 2.5 s and 3.5 s (the held pose);
 - sword sockets, bounds, slots; javelin bounds and slots.
Run with Scripts/run_in_editor.py, read the log, then run Scripts/Editor/cleanup_review11.py to delete the scratch folder (nothing references it)."""
import os
import unreal

log = lambda m: unreal.log("[Review11] " + m)
proj = unreal.SystemLibrary.get_project_directory()
tools = unreal.AssetToolsHelpers.get_asset_tools()
SKEL = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin"
DEST = "/Game/OneBossFight/_Review11"
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


CLIPS = ["AN_Boss01_PhaseRoar", "AN_Boss01_StaggerFall", "AN_Boss01_StaggerDown", "AN_Riposte_Player_Front", "AN_Riposte_Boss_Reaction", "AN_Boss01_DeathLegend"]
anims = {}
for clip in CLIPS:
    a = task("Animations/%s.fbx" % clip, clip, anim_options())
    if not a:
        log("%s: import failed" % clip)
        continue
    anims[clip] = a
    log("%s: engine length %.4f s, %d frames" % (clip, a.get_editor_property("sequence_length"), unreal.AnimationLibrary.get_num_frames(a)))

POSE = unreal.AnimPoseExtensions
WORLD = unreal.AnimPoseSpaces.WORLD
ALL = [str(n) for n in unreal.AnimationLibrary.get_animation_track_names(anims["AN_Boss01_StaggerDown"])] if "AN_Boss01_StaggerDown" in anims else []
log("tracks in StaggerDown: %d" % len(ALL))


def pose_at(anim, t):
    opts = unreal.AnimPoseEvaluationOptions()
    opts.set_editor_property("evaluation_type", unreal.AnimDataEvalType.RAW) if hasattr(unreal, "AnimDataEvalType") else None
    opts.set_editor_property("should_retarget", False)
    opts.set_editor_property("extract_root_motion", False)  # the root's own track is read as animated data, not as extracted motion
    return POSE.get_anim_pose_at_time(anim, t, opts)


def world(anim, bone, t):
    return POSE.get_bone_pose(pose_at(anim, t), bone, WORLD)


def height(anim, bone, t):
    return world(anim, bone, t).translation.z


def table(clip, bones, times):
    a = anims.get(clip)
    if not a:
        return
    for b in bones:
        row = []
        for t in times:
            try:
                tr = world(a, b, t)
                row.append("(%.1f %.1f %.1f)" % (tr.translation.x, tr.translation.y, tr.translation.z))
            except Exception as e:
                row.append("ERR " + str(e)[:50])
        log("   %-12s world x y z at %s: %s" % (clip.replace("AN_", "")[:20], b, "  ".join(row)))


def moved(clip, t0, t1, bones=None):
    """Sum and largest of the world position differences of all bones between two times, in cm."""
    a = anims.get(clip)
    if not a:
        return
    p0, p1 = pose_at(a, t0), pose_at(a, t1)
    total, worst, name = 0.0, 0.0, ""
    for b in (bones or ALL):
        try:
            d = (POSE.get_bone_pose(p0, b, WORLD).translation - POSE.get_bone_pose(p1, b, WORLD).translation).length()
        except Exception:
            continue
        total += d
        if d > worst:
            worst, name = d, b
    log("%s: bodies moves between %.2f s and %.2f s: sum of joint position differences %.1f cm, largest %.1f cm (bone %s)" % (clip, t0, t1, total, worst, name))


def local_diff(clip_a, t_a, clip_b, t_b):
    """Largest difference of the local transforms (translation in cm plus the rotation angles in degrees) of any bone between two clips at two times."""
    a, b = anims.get(clip_a), anims.get(clip_b)
    if not a or not b:
        return
    worst, name = 0.0, ""
    for bone in ALL:
        try:
            x = unreal.AnimationLibrary.get_bone_pose_for_time(a, bone, t_a, False)
            y = unreal.AnimationLibrary.get_bone_pose_for_time(b, bone, t_b, False)
        except Exception:
            continue
        ra, rb = x.rotation.rotator(), y.rotation.rotator()
        d = (x.translation - y.translation).length() + abs(ra.roll - rb.roll) + abs(ra.pitch - rb.pitch) + abs(ra.yaw - rb.yaw)
        if d > worst:
            worst, name = d, bone
    log("%s at %.3f s against %s at %.3f s: largest local difference over %d bones %.4f (bone %s)" % (clip_a, t_a, clip_b, t_b, len(ALL), worst, name))


KEY = ["pelvis", "head", "hand_l", "hand_r", "foot_l", "foot_r", "root"]
for clip, times in (("AN_Boss01_PhaseRoar", (0.0, 0.7, 1.8)), ("AN_Boss01_StaggerFall", (0.0, 0.35, 0.7)), ("AN_Boss01_StaggerDown", (0.0, 0.5, 1.0)),
                    ("AN_Riposte_Player_Front", (0.0, 0.4667, 0.8, 1.6)), ("AN_Riposte_Boss_Reaction", (0.0, 0.8, 1.3, 2.0)), ("AN_Boss01_DeathLegend", (0.0, 0.8, 1.333, 2.5, 3.5))):
    log("--- %s" % clip)
    table(clip, KEY, times)

log("--- does it move")
moved("AN_Boss01_PhaseRoar", 0.0, 0.7)
moved("AN_Boss01_StaggerFall", 0.0, 0.7)
moved("AN_Riposte_Player_Front", 0.0, 0.8)
moved("AN_Riposte_Boss_Reaction", 0.0, 0.8)
moved("AN_Boss01_DeathLegend", 0.0, 2.5)
moved("AN_Boss01_DeathLegend", 2.5, 3.5)
moved("AN_Boss01_DeathLegend", 2.5, 2.9)

log("--- paired riposte seams")
local_diff("AN_Riposte_Boss_Reaction", 0.0, "AN_Boss01_StaggerDown", 1.0)
local_diff("AN_Riposte_Boss_Reaction", 2.0, "AN_Boss01_StaggerDown", 0.0)
local_diff("AN_Boss01_StaggerFall", 0.7, "AN_Boss01_StaggerDown", 0.0)
log("--- death held pose")
local_diff("AN_Boss01_DeathLegend", 2.5, "AN_Boss01_DeathLegend", 3.5)
local_diff("AN_Boss01_DeathLegend", 2.5, "AN_Boss01_DeathLegend", 3.0)

# sword and javelin
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
    for name in ("BladeStart", "MiddleSocket", "BladeEnd", "Weapon_Start", "Weapon_End", "Weapon Start", "Weapon End", "TrailStartSocket", "TrailEndSocket"):
        s = sw.find_socket(name)
        if s:
            loc = s.get_editor_property("relative_location")
            found.append("%s (%.1f, %.1f, %.1f)" % (name, loc.x, loc.y, loc.z))
    log("sword sockets found by name: %d: %s" % (len(found), found))
    log("sword: size %.1f x %.1f x %.1f cm, min %s max %s, slots %s" % (box.max.x - box.min.x, box.max.y - box.min.y, box.max.z - box.min.z, box.min, box.max,
        [str(m.get_editor_property("material_slot_name")) for m in sw.get_editor_property("static_materials")]))
jv = task("Weapons/SM_Boss01_EmberJavelin.fbx", "SM_Boss01_EmberJavelin", sm_opt)
if jv:
    box = jv.get_bounding_box()
    log("javelin: size %.1f x %.1f x %.1f cm, slots %s" % (box.max.x - box.min.x, box.max.y - box.min.y, box.max.z - box.min.z,
        [str(m.get_editor_property("material_slot_name")) for m in jv.get_editor_property("static_materials")]))
log("done")
