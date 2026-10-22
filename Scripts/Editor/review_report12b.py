"""Second part of the Report 12 engine review (log prefix [Review12b]); needs the scratch clips of review_report12.py in /Game/OneBossFight/_Review12.
 - the death clip's legs frame by frame (pelvis, knee, ankle, ball heights): when do the shins reach the floor and do the feet stay above it;
 - the dormant idle: how far any bone ever moves from frame 0 (the brief asks for slow breathing, a few millimetres), sampled over the whole loop;
 - the wake clip: the hand and pelvis heights and how far the right hand travels between 1.0 and 2.0 s."""
import unreal

log = lambda m: unreal.log("[Review12b] " + m)
DEST = "/Game/OneBossFight/_Review12/"
POSE = unreal.AnimPoseExtensions
WORLD = unreal.AnimPoseSpaces.WORLD


def pose_at(anim, t):
    opts = unreal.AnimPoseEvaluationOptions()
    opts.set_editor_property("should_retarget", False)
    opts.set_editor_property("extract_root_motion", False)
    return POSE.get_anim_pose_at_time(anim, t, opts)


def P(p, bone):
    return POSE.get_bone_pose(p, bone, WORLD).translation


death = unreal.load_asset(DEST + "AN_Boss01_DeathLegend")
log("death legs, per 0.1 s: time, pelvis z, knee l/r z (calf bone), ankle l/r z (foot bone), ball l/r z")
t = 0.0
while t <= 3.5001:
    p = pose_at(death, min(t, 3.5))
    log("   %.1f s: pelvis %.1f  knee %.1f %.1f  ankle %.1f %.1f  ball %.1f %.1f" % (t, P(p, "pelvis").z, P(p, "calf_l").z, P(p, "calf_r").z, P(p, "foot_l").z, P(p, "foot_r").z, P(p, "ball_l").z, P(p, "ball_r").z))
    t += 0.1

dormant = unreal.load_asset(DEST + "AN_Boss01_DormantIdle")
names = [str(n) for n in unreal.AnimationLibrary.get_animation_track_names(dormant)]
p0 = pose_at(dormant, 0.0)
worst, worst_bone, worst_t = 0.0, "", 0.0
per_time = []
t = 0.0
while t <= 5.0001:
    p = pose_at(dormant, min(t, 5.0))
    biggest, bone_name = 0.0, ""
    for b in names:
        try:
            d = (P(p, b) - P(p0, b)).length()
        except Exception:
            continue
        if d > biggest:
            biggest, bone_name = d, b
    per_time.append((t, biggest, bone_name))
    if biggest > worst:
        worst, worst_bone, worst_t = biggest, bone_name, t
    t += 0.25
log("dormant idle: the largest distance of any bone from its frame 0 position over the whole loop is %.4f cm (bone %s at %.2f s)" % (worst, worst_bone, worst_t))
for t, d, b in per_time:
    log("   %.2f s: largest bone distance from frame 0 %.4f cm (%s)" % (t, d, b))
# the spine and the head over the loop
for t in (0.0, 1.25, 2.5, 3.75):
    p = pose_at(dormant, t)
    log("   dormant at %.2f s: spine_03 %s head %s hand_r %s" % (t, P(p, "spine_03"), P(p, "head"), P(p, "hand_r")))

wake = unreal.load_asset(DEST + "AN_Boss01_Wake")
log("wake, per 0.25 s: pelvis z, hand_r and hand_l positions, head z")
t = 0.0
while t <= 3.5001:
    p = pose_at(wake, min(t, 3.5))
    hr, hl = P(p, "hand_r"), P(p, "hand_l")
    log("   %.2f s: pelvis z %.1f  hand_r (%.1f %.1f %.1f)  hand_l (%.1f %.1f %.1f)  head z %.1f" % (t, P(p, "pelvis").z, hr.x, hr.y, hr.z, hl.x, hl.y, hl.z, P(p, "head").z))
    t += 0.25
log("done")
