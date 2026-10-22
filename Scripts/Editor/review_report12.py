"""Review of Antigravity's Report 12 inside the engine (log prefix [Review12]): imports the delivered clips into the scratch folder /Game/OneBossFight/_Review12 (nothing that exists is touched or deleted) and checks, from the
engine's own animation data in component space (floor z = 0, root yaw 0 faces +Y), every number BRIEF_12 asks for. Each check prints PASS or FAIL with the measured values; a summary line ends the run.
 - lengths and frame counts; the root's travel and yaw in the player clip; the strike (hand_r ahead of the root, body movement inside the root frame, the recovery);
 - the spine: head minus pelvis and neck_01 minus pelvis at the named times (the brief's absolute head heights are absolute, the report's relative numbers are printed beside them);
 - the kneel feet: the lowest ankle and ball height over the kneeling frames of each clip;
 - the seams between clips (largest local difference over all bones) and the loop closures.
Run with Scripts/run_in_editor.py, read the log, then run Scripts/Editor/cleanup_review12.py (deletes the scratch folder)."""
import os
import unreal

log = lambda m: unreal.log("[Review12] " + m)
proj = unreal.SystemLibrary.get_project_directory()
tools = unreal.AssetToolsHelpers.get_asset_tools()
SKEL = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin"
DEST = "/Game/OneBossFight/_Review12"
skel = unreal.load_asset(SKEL)
POSE = unreal.AnimPoseExtensions
WORLD = unreal.AnimPoseSpaces.WORLD
results = []


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


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


CLIPS = ["AN_Boss01_PhaseRoar", "AN_Boss01_StaggerFall", "AN_Boss01_StaggerDown", "AN_Riposte_Player_Front", "AN_Riposte_Boss_Reaction", "AN_Boss01_DeathLegend", "AN_Boss01_DormantIdle", "AN_Boss01_Wake"]
anims = {}
for clip in CLIPS:
    a = task("Animations/%s.fbx" % clip, clip, anim_options())
    if not a:
        check("%s imports" % clip, False)
        continue
    anims[clip] = a
    log("%s: engine length %.4f s, %d frames" % (clip, a.get_editor_property("sequence_length"), unreal.AnimationLibrary.get_num_frames(a)))
LENGTHS = {"AN_Boss01_PhaseRoar": 1.8, "AN_Boss01_StaggerFall": 0.7, "AN_Boss01_StaggerDown": 1.0, "AN_Riposte_Player_Front": 1.6, "AN_Riposte_Boss_Reaction": 2.0, "AN_Boss01_DeathLegend": 3.5, "AN_Boss01_DormantIdle": 5.0, "AN_Boss01_Wake": 3.5}
for clip, want in LENGTHS.items():
    if clip in anims:
        check("%s length %.1f s" % (clip, want), abs(anims[clip].get_editor_property("sequence_length") - want) < 0.001, "%.4f" % anims[clip].get_editor_property("sequence_length"))
ALL = [str(n) for n in unreal.AnimationLibrary.get_animation_track_names(anims["AN_Boss01_StaggerDown"])]
log("tracks: %d" % len(ALL))


def pose_at(name, t):
    opts = unreal.AnimPoseEvaluationOptions()
    opts.set_editor_property("should_retarget", False)
    opts.set_editor_property("extract_root_motion", False)
    return POSE.get_anim_pose_at_time(anims[name], t, opts)


def P(p, bone):
    return POSE.get_bone_pose(p, bone, WORLD).translation


def R(p, bone):
    return POSE.get_bone_pose(p, bone, WORLD).rotation.rotator()


def rel(p, a, b):
    v = P(p, a) - P(p, b)
    return v


def local_diff(ca, ta, cb, tb):
    worst, name = 0.0, ""
    for bone in ALL:
        try:
            x = unreal.AnimationLibrary.get_bone_pose_for_time(anims[ca], bone, ta, False)
            y = unreal.AnimationLibrary.get_bone_pose_for_time(anims[cb], bone, tb, False)
        except Exception:
            continue
        ra, rb = x.rotation.rotator(), y.rotation.rotator()
        d = (x.translation - y.translation).length() + abs(ra.roll - rb.roll) + abs(ra.pitch - rb.pitch) + abs(ra.yaw - rb.yaw)
        if d > worst:
            worst, name = d, bone
    return worst, name


def movement(name, t0, t1):
    """Sum and largest of the movement of every bone in the ROOT's frame between two times (the root's own travel taken out)."""
    p0, p1 = pose_at(name, t0), pose_at(name, t1)
    r0, r1 = P(p0, "root"), P(p1, "root")
    total, worst, bone_name = 0.0, 0.0, ""
    for b in ALL:
        try:
            d = ((P(p1, b) - r1) - (P(p0, b) - r0)).length()
        except Exception:
            continue
        total += d
        if d > worst:
            worst, bone_name = d, b
    return total, worst, bone_name


def kneel_feet(name, times):
    """Lowest ankle (foot_l, foot_r) and lowest ball (ball_l, ball_r) height and the lowest knee (calf) over the given times."""
    lo_ankle, lo_ball, hi_knee = 1e9, 1e9, -1e9
    for t in times:
        p = pose_at(name, t)
        lo_ankle = min(lo_ankle, P(p, "foot_l").z, P(p, "foot_r").z)
        lo_ball = min(lo_ball, P(p, "ball_l").z, P(p, "ball_r").z)
        hi_knee = max(hi_knee, P(p, "calf_l").z, P(p, "calf_r").z)
    return lo_ankle, lo_ball, hi_knee


def frames(name, a=0.0, b=None, step=1.0 / 30.0):
    L = anims[name].get_editor_property("sequence_length")
    b = L if b is None else b
    out, t = [], a
    while t <= b + 1e-6:
        out.append(min(t, L))
        t += step
    return out


# ============================================================ player riposte
n = "AN_Riposte_Player_Front"
yaws = [R(pose_at(n, t), "root").yaw for t in frames(n)]
check("player riposte: root yaw 0 on every frame (%d frames)" % len(yaws), all(abs(((y + 180.0) % 360.0) - 180.0) < 0.5 for y in yaws), "min %.2f max %.2f" % (min(yaws), max(yaws)))
r0, r7, r16 = P(pose_at(n, 0.0), "root"), P(pose_at(n, 0.7), "root"), P(pose_at(n, 1.6), "root")
check("player riposte: the root travels from (0, 0, 0) to (0, 90, 0) by 0.7 s and holds", r0.length() < 0.2 and abs(r7.y - 90.0) < 0.5 and abs(r7.x) < 0.5 and abs(r16.y - 90.0) < 0.5, "t0 %s, 0.7 s %s, 1.6 s %s" % (r0, r7, r16))
p8 = pose_at(n, 0.8)
hand = P(p8, "hand_r") - P(p8, "root")
check("player riposte: hand_r at 0.8 s is at least 45 cm ahead (+Y) of the root and 105 to 140 cm high", hand.y >= 45.0 and 105.0 <= hand.z <= 140.0, "relative to the root (%.1f %.1f %.1f)" % (hand.x, hand.y, hand.z))
tot, worst, bn = movement(n, 0.4667, 0.8)
check("player riposte: bone movement inside the root frame between 0.467 and 0.8 s is at least 400 cm", tot >= 400.0, "sum %.1f cm, largest %.1f cm (%s)" % (tot, worst, bn))
tot0, worst0, bn0 = movement(n, 0.0, 0.8)
log("player riposte: movement 0 to 0.8 s sum %.1f largest %.1f (%s); 0.8 to 1.6 s %s" % (tot0, worst0, bn0, movement(n, 0.8, 1.6)))
p0, p16 = pose_at(n, 0.0), pose_at(n, 1.6)
d = {b: ((P(p16, b) - P(p16, "root")) - (P(p0, b) - P(p0, "root"))).length() for b in ("hand_r", "hand_l", "head")}
check("player riposte: at 1.6 s hand_r, hand_l and head are back within 15 cm of frame 0 relative to the root", all(v <= 15.0 for v in d.values()), "%s" % {k: round(v, 2) for k, v in d.items()})
for t in (0.0, 0.4667, 0.8, 1.2, 1.6):
    p = pose_at(n, t)
    h = P(p, "hand_r") - P(p, "root")
    log("   player riposte at %.3f s: root %s hand_r rel (%.1f %.1f %.1f) head rel %s pelvis z %.1f" % (t, P(p, "root"), h.x, h.y, h.z, P(p, "head") - P(p, "root"), P(p, "pelvis").z))

# ============================================================ boss reaction
n = "AN_Riposte_Boss_Reaction"
p0, p8, p13 = pose_at(n, 0.0), pose_at(n, 0.8), pose_at(n, 1.3)
hp0, hp8, hp13 = rel(p0, "head", "pelvis"), rel(p8, "head", "pelvis"), rel(p13, "head", "pelvis")
np8, np0 = rel(p8, "neck_01", "pelvis"), rel(p0, "neck_01", "pelvis")
check("boss reaction at 0.8 s: head minus pelvis y <= -15 and z <= 64", hp8.y <= -15.0 and hp8.z <= 64.0, "(%.1f %.1f %.1f), frame 0 (%.1f %.1f %.1f)" % (hp8.x, hp8.y, hp8.z, hp0.x, hp0.y, hp0.z))
check("boss reaction at 0.8 s: neck_01 minus pelvis y <= -8", np8.y <= -8.0, "(%.1f %.1f %.1f), frame 0 (%.1f %.1f %.1f)" % (np8.x, np8.y, np8.z, np0.x, np0.y, np0.z))
check("boss reaction at 1.3 s: head minus pelvis within 5 cm of frame 0", (hp13 - hp0).length() <= 5.0, "difference %.2f cm" % (hp13 - hp0).length())
a, b = local_diff(n, 0.0, "AN_Boss01_StaggerDown", 1.0)
check("boss reaction first frame = StaggerDown last frame (<= 0.01)", a <= 0.01, "%.4f (%s)" % (a, b))
a, b = local_diff(n, 2.0, "AN_Boss01_StaggerDown", 0.0)
check("boss reaction last frame = StaggerDown first frame (<= 0.01)", a <= 0.01, "%.4f (%s)" % (a, b))
ank, ball, knee = kneel_feet(n, frames(n))
check("boss reaction: ankles >= 3 and balls >= -1 in every frame", ank >= 3.0 and ball >= -1.0, "lowest ankle %.2f lowest ball %.2f highest knee %.2f" % (ank, ball, knee))

# ============================================================ death
n = "AN_Boss01_DeathLegend"
p0, p75 = pose_at(n, 0.0), pose_at(n, 2.5)
hp75 = rel(p75, "head", "pelvis")
head_abs = P(p75, "head").z
check("death at 2.5 s: head minus pelvis y >= +30", hp75.y >= 30.0, "(%.1f %.1f %.1f)" % (hp75.x, hp75.y, hp75.z))
check("death at 2.5 s: the head is at most 90 cm HIGH (absolute z)", head_abs <= 90.0, "head z %.1f, pelvis z %.1f; the report's 'head height 89.80' is head minus pelvis z" % (head_abs, P(p75, "pelvis").z))
a, b = local_diff(n, 2.5, n, 3.5)
check("death: held pose exact between 2.5 s and 3.5 s", a <= 0.001, "%.5f (%s)" % (a, b))
check("death starts standing (pelvis z about 96)", abs(P(p0, "pelvis").z - 95.9) < 1.0, "pelvis z %.1f, head minus pelvis %s" % (P(p0, "pelvis").z, rel(p0, "head", "pelvis")))
ank, ball, knee = kneel_feet(n, frames(n, 1.4, 3.5))
check("death: ankles >= 3 and balls >= -1 in the kneeling frames (1.4 s to 3.5 s)", ank >= 3.0 and ball >= -1.0, "lowest ankle %.2f lowest ball %.2f highest knee %.2f" % (ank, ball, knee))
for t in (0.0, 0.8, 1.333, 2.0, 2.5, 3.5):
    p = pose_at(n, t)
    log("   death at %.3f s: pelvis z %.1f head (%.1f %.1f %.1f) head minus pelvis %s" % (t, P(p, "pelvis").z, P(p, "head").x, P(p, "head").y, P(p, "head").z, rel(p, "head", "pelvis")))

# ============================================================ roar
n = "AN_Boss01_PhaseRoar"
p7 = pose_at(n, 0.7)
hp7 = rel(p7, "head", "pelvis")
check("roar at 0.7 s: head minus pelvis y <= -12", hp7.y <= -12.0, "(%.1f %.1f %.1f)" % (hp7.x, hp7.y, hp7.z))
check("roar at 0.7 s: the head is at least 150 cm high", P(p7, "head").z >= 150.0, "head z %.1f" % P(p7, "head").z)
a, b = local_diff(n, 0.0, n, 1.8)
check("roar: first and last frame equal (<= 0.01)", a <= 0.01, "%.4f (%s)" % (a, b))
tot, worst, bn = movement(n, 0.0, 0.7)
log("roar: movement 0 to 0.7 s sum %.1f cm, largest %.1f cm (%s)" % (tot, worst, bn))

# ============================================================ stagger fall and down
n = "AN_Boss01_StaggerFall"
p35 = pose_at(n, 0.35)
hf = rel(p35, "head", "pelvis")
check("stagger fall at 0.35 s: head minus pelvis y >= +10", hf.y >= 10.0, "(%.1f %.1f %.1f)" % (hf.x, hf.y, hf.z))
a, b = local_diff(n, 0.7, "AN_Boss01_StaggerDown", 0.0)
check("stagger fall last frame = StaggerDown first frame (<= 0.01)", a <= 0.01, "%.4f (%s)" % (a, b))
ank, ball, knee = kneel_feet(n, frames(n, 0.5, 0.7))
check("stagger fall: ankles >= 3 and balls >= -1 in the last frames (0.5 s to 0.7 s)", ank >= 3.0 and ball >= -1.0, "lowest ankle %.2f lowest ball %.2f highest knee %.2f" % (ank, ball, knee))
n = "AN_Boss01_StaggerDown"
a, b = local_diff(n, 0.0, n, 1.0)
check("stagger down loop closes (<= 0.0001)", a <= 0.0001, "%.5f (%s)" % (a, b))
ank, ball, knee = kneel_feet(n, frames(n))
check("stagger down: ankles >= 3 and balls >= -1 in every frame", ank >= 3.0 and ball >= -1.0, "lowest ankle %.2f lowest ball %.2f highest knee %.2f" % (ank, ball, knee))
hd = [rel(pose_at(n, t), "head", "pelvis") for t in frames(n)]
log("stagger down: head minus pelvis over the loop from (%.1f %.1f %.1f) to (%.1f %.1f %.1f)" % (hd[0].x, hd[0].y, hd[0].z, hd[15].x, hd[15].y, hd[15].z))

# ============================================================ dormant and wake
n = "AN_Boss01_DormantIdle"
a, b = local_diff(n, 0.0, n, 5.0)
check("dormant idle loop closes (<= 0.0001)", a <= 0.0001, "%.5f (%s)" % (a, b))
ank, ball, knee = kneel_feet(n, frames(n, 0.0, 5.0, 0.2))
check("dormant idle: kneel feet (ankles >= 3, balls >= -1)", ank >= 3.0 and ball >= -1.0, "lowest ankle %.2f lowest ball %.2f highest knee %.2f" % (ank, ball, knee))
tot, worst, bn = movement(n, 0.0, 2.5)
check("dormant idle breathes (some bone moves by more than 0.1 cm and less than 6 cm over 2.5 s)", 0.1 < worst < 6.0, "largest %.2f cm (%s), sum %.1f" % (worst, bn, tot))
n = "AN_Boss01_Wake"
a, b = local_diff(n, 0.0, "AN_Boss01_DormantIdle", 0.0)
check("wake first frame = dormant idle first frame (<= 0.01)", a <= 0.01, "%.4f (%s)" % (a, b))
a, b = local_diff(n, 3.5, "AN_Boss01_PhaseRoar", 0.0)
check("wake last frame = roar first frame, the combat idle (<= 0.01)", a <= 0.01, "%.4f (%s)" % (a, b))
for t in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5):
    p = pose_at(n, t)
    log("   wake at %.2f s: pelvis z %.1f head z %.1f hand_r (%.1f %.1f %.1f) spine head minus pelvis %s" % (t, P(p, "pelvis").z, P(p, "head").z, P(p, "hand_r").x, P(p, "hand_r").y, P(p, "hand_r").z, rel(p, "head", "pelvis")))

log("SUMMARY %d checks, %d failed" % (len(results), sum(1 for r in results if not r)))
