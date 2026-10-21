"""Reads bone transforms of imported Boss01 clips at several times to see whether they really move. Log prefix [AnimProbe]."""
import unreal

log = lambda m: unreal.log("[AnimProbe] " + m)
CLIPS = ["AN_Boss01_A1_QuickSlash", "AN_Boss01_A3a_Combo1", "AN_Boss01_A3b_Combo2", "AN_Boss01_A4_LowSweep", "AN_Boss01_A5_JavelinThrow"]
BONES = ["root", "pelvis", "spine_01", "thigh_l", "calf_l", "upperarm_l", "lowerarm_l", "hand_l", "upperarm_r", "hand_r", "head"]
for name in CLIPS:
    a = unreal.load_asset("/Game/OneBossFight/Boss01/Animations/" + name)
    if not a:
        log("%s missing" % name)
        continue
    L = a.get_editor_property("sequence_length")
    tracks = unreal.AnimationLibrary.get_animation_track_names(a)
    log("%s: length %.3f, %d tracks, frames %d" % (name, L, len(tracks), unreal.AnimationLibrary.get_num_frames(a)))
    for b in BONES:
        row = []
        for f in (0.0, 0.25, 0.5, 0.75, 1.0):
            t = L * f
            try:
                tr = unreal.AnimationLibrary.get_bone_pose_for_time(a, b, t, False)
                row.append("(%.0f %.0f %.0f | rot %.0f %.0f %.0f)" % (tr.translation.x, tr.translation.y, tr.translation.z, tr.rotation.rotator().roll, tr.rotation.rotator().pitch, tr.rotation.rotator().yaw))
            except Exception as e:
                row.append("ERR " + str(e)[:40])
        log("   %-11s %s" % (b, "  ".join(row)))
