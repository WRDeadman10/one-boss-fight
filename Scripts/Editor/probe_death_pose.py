"""Measures the last frame of the boss death clip in component space (log prefix [DeathPose]): head, pelvis, feet, hands, sword tip, overall bounds. Read-only. Compare with the corpse statue (SM_Boss01_CorpseStatue, bounds min -55 -190 -2, max 64 32 101)."""
import unreal

log = lambda m: unreal.log("[DeathPose] " + m)
clip = unreal.load_asset("/Game/OneBossFight/Boss01/Animations/AN_Boss01_DeathLegend")
POSE, WORLD = unreal.AnimPoseExtensions, unreal.AnimPoseSpaces.WORLD
o = unreal.AnimPoseEvaluationOptions()
o.set_editor_property("should_retarget", False)
o.set_editor_property("extract_root_motion", False)
L = clip.get_editor_property("sequence_length")
log("length %.3f" % L)
for t in (0.0, L * 0.5, L - 0.0001):
    p = POSE.get_anim_pose_at_time(clip, t, o)
    pts = {b: POSE.get_bone_pose(p, b, WORLD).translation for b in ("root", "pelvis", "head", "foot_l", "foot_r", "hand_l", "hand_r", "spine_03")}
    xs = [v.x for v in pts.values()]; ys = [v.y for v in pts.values()]; zs = [v.z for v in pts.values()]
    log("t %.2f " % t + " ".join("%s(%.0f %.0f %.0f)" % (k, v.x, v.y, v.z) for k, v in pts.items()))
    log("   bone bounds x %.0f..%.0f y %.0f..%.0f z %.0f..%.0f (skeleton space, boss mesh scale 1.5)" % (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
log("DONE")
