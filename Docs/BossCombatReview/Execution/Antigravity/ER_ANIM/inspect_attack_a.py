import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\Attack_PrimaryA_Anim.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
scene = bpy.context.scene

print(f"Total frames: {scene.frame_end - scene.frame_start + 1}")
hand = arm.pose.bones.get("hand_r")
pelvis = arm.pose.bones.get("pelvis")

for f in range(1, 45, 2):
    scene.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    hand_eval = arm_eval.pose.bones.get("hand_r")
    pelvis_eval = arm_eval.pose.bones.get("pelvis")
    # World or arm-relative position of hand_r
    h_loc = arm_eval.matrix_world @ hand_eval.matrix.translation
    p_loc = arm_eval.matrix_world @ pelvis_eval.matrix.translation
    print(f"F{f:02d}: hand_r=({h_loc.x:.2f}, {h_loc.y:.2f}, {h_loc.z:.2f}), pelvis_z={p_loc.z:.2f}")
