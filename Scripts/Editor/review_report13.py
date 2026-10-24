"""Engine review of Antigravity's Brief 13/14 deliveries (log prefix [Review13]): imports the clips into the scratch folder /Game/OneBossFight/_Review13 (nothing that exists is touched) and prints, from the engine's own animation data in component space (floor z = 0,
root yaw 0 faces +Y), the numbers a review needs: length and frame rate, root travel, loop closures and seams, the lowest foot and ball height, and the sword (grip, tip, blade direction, hand distance) at the key times of each clip's timing card.
Clips: DormantIdle, Wake, DeathLegend (Report 13), A1_QuickSlash, A3a_Combo1, A3b_Combo2 (close attacks), A2_Raise, A2_ApexHold, A2_Slam. Run with Scripts/run_in_editor.py, read the log, then Scripts/Editor/cleanup_review12.py style cleanup of /Game/OneBossFight/_Review13 (own imports, unreferenced)."""
import os
import unreal

log = lambda m: unreal.log("[Review13] " + m)
proj = unreal.SystemLibrary.get_project_directory()
tools = unreal.AssetToolsHelpers.get_asset_tools()
DEST = "/Game/OneBossFight/_Review13"
body = unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body")
skel = unreal.load_asset("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin")
POSE = unreal.AnimPoseExtensions
WORLD = unreal.AnimPoseSpaces.WORLD

# clip, intended length, key times (seconds) for the sword table
CLIPS = [
    ("AN_Boss01_DormantIdle", 5.0, (0.0, 1.25, 2.5, 3.75, 4.97)),
    ("AN_Boss01_Wake", 3.5, (0.0, 1.0, 1.5, 2.0, 2.5, 3.5)),
    ("AN_Boss01_DeathLegend", 3.5, (0.0, 1.0, 2.0, 2.5, 3.5)),
    ("AN_Boss01_A1_QuickSlash", 1.2, (0.0, 0.33, 0.35, 0.50, 1.2)),
    ("AN_Boss01_A3a_Combo1", 0.8, (0.0, 0.38, 0.40, 0.60, 0.8)),
    ("AN_Boss01_A3b_Combo2", 1.3333, (0.0, 0.13, 0.15, 0.40, 1.3333)),
    ("AN_Boss01_A2_Raise", 0.6, (0.0, 0.3, 0.6)),
    ("AN_Boss01_A2_ApexHold", 1.1667, (0.0, 0.58, 1.1667)),
    ("AN_Boss01_A2_Slam", 1.3667, (0.0, 0.07, 0.17, 0.5, 1.3667)),
]


def options():
    o = unreal.FbxImportUI()
    o.set_editor_property("import_mesh", False)
    o.set_editor_property("import_as_skeletal", False)
    o.set_editor_property("import_animations", True)
    o.set_editor_property("skeleton", skel)
    o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
    return o


def import_clip(name):
    t = unreal.AssetImportTask()
    t.filename = os.path.join(proj, "Import", "Boss01", "Animations", name + ".fbx").replace("/", os.sep)
    t.destination_path = DEST
    t.destination_name = name
    t.automated = True
    t.save = False
    t.replace_existing = True
    t.replace_existing_settings = True
    t.options = options()
    tools.import_asset_tasks([t])
    return unreal.load_asset(DEST + "/" + name)


socket = None
for owner in (body, body.get_editor_property("skeleton") if body else None):
    if owner is None:
        continue
    try:
        socket = owner.find_socket("HeavySwordSocket_R")
    except Exception:
        socket = None
    if socket:
        break
sword = unreal.load_asset("/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword")
tip_local = unreal.Vector(0, 0, sword.get_bounding_box().max.z) if sword else None
rel = None
if socket:
    rel = unreal.Transform(socket.get_editor_property("relative_location"), socket.get_editor_property("relative_rotation"), socket.get_editor_property("relative_scale"))
    bone = str(socket.get_editor_property("bone_name"))
log("body %s, socket %s, sword %s" % (body.get_name() if body else None, bone if socket else None, sword.get_name() if sword else None))

anims = {}
for name, want, _t in CLIPS:
    a = import_clip(name)
    if not a:
        log("FAIL %s did not import" % name)
        continue
    anims[name] = a
    length = a.get_editor_property("sequence_length")
    frames = unreal.AnimationLibrary.get_num_frames(a)
    fps = (frames - 1) / length if length > 0 else 0
    log("%s %s length %.4f s (intended %.4f), %d frames, %.2f fps" % ("PASS" if abs(length - want) < 0.002 else "FAIL", name, length, want, frames, fps))
ALL = []
if anims:
    ALL = [str(n) for n in unreal.AnimationLibrary.get_animation_track_names(next(iter(anims.values())))]
log("tracks %d" % len(ALL))


def pose_at(name, t):
    opts = unreal.AnimPoseEvaluationOptions()
    opts.set_editor_property("should_retarget", False)
    opts.set_editor_property("extract_root_motion", False)
    return POSE.get_anim_pose_at_time(anims[name], min(t, anims[name].get_editor_property("sequence_length") - 0.0001), opts)


def P(p, b):
    return POSE.get_bone_pose(p, b, WORLD).translation


def local_diff(ca, ta, cb, tb):
    worst, wname = 0.0, ""
    for b in ALL:
        try:
            x = unreal.AnimationLibrary.get_bone_pose_for_time(anims[ca], b, ta, False)
            y = unreal.AnimationLibrary.get_bone_pose_for_time(anims[cb], b, tb, False)
        except Exception:
            continue
        ra, rb = x.rotation.rotator(), y.rotation.rotator()
        d = (x.translation - y.translation).length() + abs(ra.roll - rb.roll) + abs(ra.pitch - rb.pitch) + abs(ra.yaw - rb.yaw)
        if d > worst:
            worst, wname = d, b
    return worst, wname


def sword_at(name, t):
    p = pose_at(name, t)
    hr, hl = P(p, "hand_r"), P(p, "hand_l")
    root = P(p, "root")
    out = "t %.2f root (%.0f %.0f %.0f) pelvis z %.0f head z %.0f hand_r (%.0f %.0f %.0f) hands %.0f apart" % (t, root.x, root.y, root.z, P(p, "pelvis").z, P(p, "head").z, hr.x, hr.y, hr.z, (hl - hr).length())
    if rel is not None and tip_local is not None:
        comp = unreal.MathLibrary.compose_transforms(rel, POSE.get_bone_pose(p, bone, WORLD))
        grip = comp.translation
        tip = unreal.MathLibrary.transform_location(comp, tip_local)
        d = tip - grip
        d = d / d.length() if d.length() > 0 else d
        out += "; sword grip (%.0f %.0f %.0f) tip (%.0f %.0f %.0f) dir (%.2f %.2f %.2f)" % (grip.x, grip.y, grip.z, tip.x, tip.y, tip.z, d.x, d.y, d.z)
    return out


def feet(name, steps=12):
    length = anims[name].get_editor_property("sequence_length")
    low_ankle, low_ball = 9999.0, 9999.0
    for i in range(steps + 1):
        p = pose_at(name, length * i / steps)
        for b in ("foot_l", "foot_r"):
            low_ankle = min(low_ankle, P(p, b).z)
        for b in ("ball_l", "ball_r"):
            low_ball = min(low_ball, P(p, b).z)
    return low_ankle, low_ball


for name, want, times in CLIPS:
    if name not in anims:
        continue
    length = anims[name].get_editor_property("sequence_length")
    p0, p1 = pose_at(name, 0.0), pose_at(name, length)
    travel = (P(p1, "root") - P(p0, "root")).length()
    ank, ball = feet(name)
    closure, closure_bone = local_diff(name, 0.0, name, length - 0.0001)
    log("%s: root travel %.1f cm, lowest ankle %.1f cm, lowest ball %.1f cm, first-last local difference %.4f (%s)" % (name, travel, ank, ball, closure, closure_bone))
    for t in times:
        log("   %s %s" % (name, sword_at(name, t)))

# seams
if "AN_Boss01_DormantIdle" in anims and "AN_Boss01_Wake" in anims:
    d, b = local_diff("AN_Boss01_Wake", 0.0, "AN_Boss01_DormantIdle", 0.0)
    log("seam Wake first = DormantIdle first: %.4f (%s)" % (d, b))
roar = unreal.load_asset("/Game/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar")
if roar and "AN_Boss01_Wake" in anims:
    anims["_roar"] = roar
    d, b = local_diff("AN_Boss01_Wake", 3.4999, "_roar", 0.0)
    log("seam Wake last = PhaseRoar first: %.4f (%s)" % (d, b))
if "AN_Boss01_A3a_Combo1" in anims and "AN_Boss01_A3b_Combo2" in anims:
    d, b = local_diff("AN_Boss01_A3a_Combo1", 0.7999, "AN_Boss01_A3b_Combo2", 0.0)
    log("seam A3a last = A3b first: %.4f (%s)" % (d, b))
if "AN_Boss01_A2_Raise" in anims and "AN_Boss01_A2_ApexHold" in anims:
    d, b = local_diff("AN_Boss01_A2_Raise", 0.5999, "AN_Boss01_A2_ApexHold", 0.0)
    log("seam A2 Raise last = ApexHold first: %.4f (%s)" % (d, b))
    d, b = local_diff("AN_Boss01_A2_ApexHold", 0.0, "AN_Boss01_A2_ApexHold", 1.1666)
    log("A2 ApexHold loop closure: %.4f (%s)" % (d, b))
if "AN_Boss01_A2_ApexHold" in anims and "AN_Boss01_A2_Slam" in anims:
    d, b = local_diff("AN_Boss01_A2_ApexHold", 1.1666, "AN_Boss01_A2_Slam", 0.0)
    log("seam A2 ApexHold last = Slam first: %.4f (%s)" % (d, b))
log("DONE")
