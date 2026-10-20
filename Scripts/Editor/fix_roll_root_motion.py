"""
The IK retargeter put the roll's travel in the pelvis (the source animation moves its root bone, which is not retargeted),
so the mesh left the capsule and snapped back when the montage ended. This moves the pelvis's horizontal travel into the
root bone and enables root motion, so the capsule travels with the animation. Run after setup_m7_roll.py, before
setup_m7_content.py. Idempotent (a second run finds no pelvis travel left).

  UnrealEditor-Cmd.exe OneBossFight.uproject -run=pythonscript -script=Scripts/Editor/fix_roll_root_motion.py -unattended -nullrhi
"""
import unreal

ROLL_DIR = "/Game/OneBossFight/Characters/Greystone/Roll/"
SEQUENCES = ["AS_Roll_Combat_F_0_Seq_Greystone", "AS_Roll_Combat_B_180_Seq_Greystone"]
TARGET_TRAVEL_CM = 320.0  # the animation travels about 4.9 m, more than the camera can follow; a Souls-style roll is about 3 m
log = lambda m: unreal.log("[RollRoot] " + m)

for name in SEQUENCES:
    seq = unreal.load_asset(ROLL_DIR + name)
    model = seq.get_editor_property("data_model_interface") or seq.get_editor_property("data_model")
    controller = seq.get_editor_property("controller")
    log("model=%s controller=%s" % (model, controller))
    keys = model.get_number_of_keys()
    lib = unreal.AnimationLibrary
    pelvis = [lib.get_bone_pose_for_frame(seq, "pelvis", i, False) for i in range(keys)]
    root = [lib.get_bone_pose_for_frame(seq, "root", i, False) for i in range(keys)]
    first = pelvis[0].translation
    travel = max(abs(p.translation.x - first.x) + abs(p.translation.y - first.y) for p in pelvis)
    if travel < 20.0:
        log("%s: pelvis travel already %.0f cm, nothing to do" % (name, travel))
    else:
        root_pos, pelvis_pos = [], []
        for r, p in zip(root, pelvis):
            dx, dy = p.translation.x - first.x, p.translation.y - first.y
            root_pos.append(unreal.Vector(r.translation.x + dx, r.translation.y + dy, r.translation.z))
            pelvis_pos.append(unreal.Vector(first.x, first.y, p.translation.z))
        root_rot = [r.rotation for r in root]
        pelvis_rot = [p.rotation for p in pelvis]
        root_scale = [r.scale3d for r in root]
        pelvis_scale = [p.scale3d for p in pelvis]
        controller.open_bracket("move roll travel into the root", True)
        controller.set_bone_track_keys("root", root_pos, root_rot, root_scale, True)
        controller.set_bone_track_keys("pelvis", pelvis_pos, pelvis_rot, pelvis_scale, True)
        controller.close_bracket(True)
        log("%s: moved %.0f cm of pelvis travel into the root (%d keys)" % (name, travel, len(pelvis)))
    # Scale the root travel to the target distance (idempotent: measures the travel now in the root track).
    keys = model.get_number_of_keys()
    root = [lib.get_bone_pose_for_frame(seq, "root", i, False) for i in range(keys)]
    current = (root[-1].translation - root[0].translation)
    current_len = (current.x ** 2 + current.y ** 2) ** 0.5
    if current_len > 1.0 and abs(current_len - TARGET_TRAVEL_CM) > 5.0:
        k = TARGET_TRAVEL_CM / current_len
        positions = [unreal.Vector(r.translation.x * k, r.translation.y * k, r.translation.z) for r in root]
        controller.open_bracket("scale roll travel", True)
        controller.set_bone_track_keys("root", positions, [r.rotation for r in root], [r.scale3d for r in root], True)
        controller.close_bracket(True)
        log("%s: root travel %.0f cm -> %.0f cm" % (name, current_len, TARGET_TRAVEL_CM))
    seq.set_editor_property("force_root_lock", False)
    seq.set_editor_property("enable_root_motion", True)
    unreal.EditorAssetLibrary.save_loaded_asset(seq, False)
