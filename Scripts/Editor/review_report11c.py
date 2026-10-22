"""Third part of the Report 11 engine review (log prefix [Review11c]): where the knees, ankles and toes of the kneeling poses are (component space, floor at z = 0), and the torso's lean (head minus pelvis) in the clips that should recoil or slump.
Needs the scratch clips of review_report11.py."""
import unreal

log = lambda m: unreal.log("[Review11c] " + m)
DEST = "/Game/OneBossFight/_Review11/"
POSE = unreal.AnimPoseExtensions
WORLD = unreal.AnimPoseSpaces.WORLD


def pose_at(anim, t):
    opts = unreal.AnimPoseEvaluationOptions()
    opts.set_editor_property("should_retarget", False)
    opts.set_editor_property("extract_root_motion", False)
    return POSE.get_anim_pose_at_time(anim, t, opts)


def v(p, b):
    return POSE.get_bone_pose(p, b, WORLD).translation


for clip, times in (("AN_Boss01_StaggerDown", (0.0,)), ("AN_Riposte_Boss_Reaction", (0.0, 0.8, 1.3)), ("AN_Boss01_DeathLegend", (0.0, 1.333, 2.5)), ("AN_Boss01_StaggerFall", (0.7,))):
    a = unreal.load_asset(DEST + clip)
    for t in times:
        p = pose_at(a, t)
        pel, head, neck = v(p, "pelvis"), v(p, "head"), v(p, "neck_01")
        row = []
        for b in ("thigh_l", "calf_l", "foot_l", "ball_l", "calf_r", "foot_r", "ball_r"):
            q = v(p, b)
            row.append("%s z %.1f" % (b, q.z))
        log("%s at %.3f s: head minus pelvis (%.1f %.1f %.1f), neck minus pelvis (%.1f %.1f %.1f); %s" % (clip, t, head.x - pel.x, head.y - pel.y, head.z - pel.z, neck.x - pel.x, neck.y - pel.y, neck.z - pel.z, ", ".join(row)))
log("done")
