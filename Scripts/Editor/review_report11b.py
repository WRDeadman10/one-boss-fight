"""Second part of the Report 11 engine review (log prefix [Review11b]); needs the scratch clips of review_report11.py in /Game/OneBossFight/_Review11.
 - which way each clip's character faces (foot to ball of foot, component space) and which way the root travels;
 - the pose relative to the root over time: how far the body moves inside the root's frame (the strike), as the largest joint movement after the root's own travel is taken out;
 - the player's hand_r relative to the root at the Impact time, and its distance to the boss's chest (the boss at the origin, 60 cm from the player's final root)."""
import unreal

log = lambda m: unreal.log("[Review11b] " + m)
DEST = "/Game/OneBossFight/_Review11/"
POSE = unreal.AnimPoseExtensions
WORLD = unreal.AnimPoseSpaces.WORLD


def pose_at(anim, t):
    opts = unreal.AnimPoseEvaluationOptions()
    opts.set_editor_property("should_retarget", False)
    opts.set_editor_property("extract_root_motion", False)
    return POSE.get_anim_pose_at_time(anim, t, opts)


def pos(p, bone):
    return POSE.get_bone_pose(p, bone, WORLD).translation


def rot(p, bone):
    r = POSE.get_bone_pose(p, bone, WORLD).rotation.rotator()
    return "roll %.0f pitch %.0f yaw %.0f" % (r.roll, r.pitch, r.yaw)


def facing(clip, t):
    a = unreal.load_asset(DEST + clip)
    p = pose_at(a, t)
    f = pos(p, "ball_l") - pos(p, "foot_l")
    f.z = 0
    g = pos(p, "ball_r") - pos(p, "foot_r")
    g.z = 0
    log("%s at %.2f s: foot to ball (left) (%.1f %.1f), (right) (%.1f %.1f); root rotation %s; pelvis rotation %s" % (clip, t, f.x, f.y, g.x, g.y, rot(p, "root"), rot(p, "pelvis")))


for clip in ("AN_Boss01_StaggerDown", "AN_Riposte_Player_Front", "AN_Riposte_Boss_Reaction", "AN_Boss01_PhaseRoar"):
    facing(clip, 0.0)
facing("AN_Riposte_Player_Front", 1.6)

# the body in the root's frame: subtract the root position, then the largest movement of any bone between two times
a = unreal.load_asset(DEST + "AN_Riposte_Player_Front")
names = [str(n) for n in unreal.AnimationLibrary.get_animation_track_names(a)]
for t0, t1 in ((0.0, 0.4667), (0.4667, 0.8), (0.8, 1.6), (0.0, 1.6)):
    p0, p1 = pose_at(a, t0), pose_at(a, t1)
    r0, r1 = pos(p0, "root"), pos(p1, "root")
    worst, name, total = 0.0, "", 0.0
    for b in names:
        try:
            d = ((pos(p1, b) - r1) - (pos(p0, b) - r0)).length()
        except Exception:
            continue
        total += d
        if d > worst:
            worst, name = d, b
    log("player clip, body inside the root frame between %.3f s and %.3f s: sum %.1f cm, largest %.1f cm (bone %s)" % (t0, t1, total, worst, name))
for t in (0.0, 0.4667, 0.8, 1.6):
    p = pose_at(a, t)
    r = pos(p, "root")
    log("player at %.3f s: hand_r relative to root (%.1f %.1f %.1f), hand_l (%.1f %.1f %.1f), head (%.1f %.1f %.1f)" % (
        t, *(lambda v: (v.x, v.y, v.z))(pos(p, "hand_r") - r), *(lambda v: (v.x, v.y, v.z))(pos(p, "hand_l") - r), *(lambda v: (v.x, v.y, v.z))(pos(p, "head") - r)))
log("done")
