"""Where does the retargeted roll travel? Component-space root and pelvis positions over time. Headless."""
import unreal
log = lambda m: unreal.log("[RollMotion] " + m)
lib = unreal.AnimationLibrary
for n in ("AS_Roll_Combat_F_0_Seq_Greystone", "AS_Roll_Combat_B_180_Seq_Greystone"):
    seq = unreal.load_asset("/Game/OneBossFight/Characters/Greystone/Roll/" + n)
    log("%s len=%.2f root_motion=%s root_lock=%s force_root_lock=%s" % (n, seq.get_play_length(), seq.get_editor_property("enable_root_motion"), seq.get_editor_property("root_motion_root_lock"), seq.get_editor_property("force_root_lock")))
    length = seq.get_play_length()
    for bone in ("root", "pelvis"):
        try:
            pts = []
            for f in (0.0, 0.25, 0.5, 0.75, 1.0):
                t = lib.get_bone_pose_for_time(seq, bone, length * f, False)
                pts.append("(%.0f,%.0f,%.0f)" % (t.translation.x, t.translation.y, t.translation.z))
            log("  %s local: %s" % (bone, " ".join(pts)))
        except Exception as e:
            log("  %s failed %s" % (bone, e))
    src = unreal.load_asset("/Game/Mage/Animations/Sequence1/07_Roll/02_Roll_Combat/" + n.replace("_Greystone", ""))
    for bone in ("root", "pelvis"):
        pts = []
        for f in (0.0, 0.25, 0.5, 0.75, 1.0):
            t = lib.get_bone_pose_for_time(src, bone, src.get_play_length() * f, False)
            pts.append("(%.0f,%.0f,%.0f)" % (t.translation.x, t.translation.y, t.translation.z))
        log("  SOURCE %s local: %s  root_motion=%s" % (bone, " ".join(pts), src.get_editor_property("enable_root_motion")))
