"""C-1284 Lead read-only probe: does root-bone translation survive the Greystone retargets?

For each sequence: skeleton name, bone 0 name, root bone translation at t=0 and t=end with
AnimationLibrary.get_bone_pose_for_time (extract_root_motion False = component space, True = root extracted),
and the pelvis translation as a control. Never writes. Log prefix [GreystoneRootBone]; ends with "finished".
"""
import unreal

PREFIX = "[GreystoneRootBone] "
SEQUENCES = [
    "/Game/OneBossFight/Player/Animations/AN_ER_Backstep_Mixamo_V2",
    "/Game/OneBossFight/Player/FitTest/Greystone/AN_ER_Backstep_Mixamo_V2_Fit_Greystone",
    "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll",
    "/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Grey",
    "/Game/OneBossFight/Player/FitTest/Greystone/AN_ER_Attack_Air_Light_Fit_Greystone",
]


def log(m):
    unreal.log(PREFIX + m)


def bone_names(skeleton):
    names = []
    try:
        count = unreal.AnimationLibrary.get_bone_count(skeleton) if hasattr(unreal.AnimationLibrary, "get_bone_count") else 0
    except Exception:
        count = 0
    ref = None
    try:
        ref = skeleton.get_editor_property("reference_skeleton") if hasattr(skeleton, "get_editor_property") else None
    except Exception:
        ref = None
    return names, count, ref


def pose(seq, bone, t, extract):
    try:
        tf = unreal.AnimationLibrary.get_bone_pose_for_time(seq, bone, t, extract)
        v = tf.translation
        return "(%.2f,%.2f,%.2f)" % (v.x, v.y, v.z), v
    except Exception as exc:
        return "ERR(%r)" % exc, None


for path in SEQUENCES:
    seq = unreal.load_asset(path)
    if seq is None:
        log("SEQ %s missing" % path)
        continue
    skel = seq.get_editor_property("skeleton")
    length = seq.get_play_length()
    rm = seq.get_editor_property("enable_root_motion")
    lock = seq.get_editor_property("root_motion_root_lock")
    try:
        track_names = list(unreal.AnimationLibrary.get_animation_track_names(seq))
    except Exception as exc:
        track_names = ["ERR(%r)" % exc]
    bone0 = track_names[0] if track_names else None
    log("SEQ %s skeleton=%s length=%.4f enable_root_motion=%s lock=%s tracks=%d first_tracks=%s" %
        (seq.get_name(), skel.get_name() if skel else None, length, rm, lock, len(track_names), [str(n) for n in track_names[:4]]))
    for bone in ("root", "pelvis", "Pelvis", "Hips"):
        if str(bone) not in [str(n) for n in track_names] and bone != "root":
            continue
        s0, v0 = pose(seq, bone, 0.0, False)
        s1, v1 = pose(seq, bone, length, False)
        dist = ((v1.x - v0.x) ** 2 + (v1.y - v0.y) ** 2) ** 0.5 if (v0 is not None and v1 is not None) else -1.0
        e0, _ = pose(seq, bone, 0.0, True)
        e1, _ = pose(seq, bone, length, True)
        log("BONE %s bone=%s component_space start=%s end=%s xy_distance_cm=%.2f | root_extracted start=%s end=%s" %
            (seq.get_name(), bone, s0, s1, dist, e0, e1))
log("finished")
