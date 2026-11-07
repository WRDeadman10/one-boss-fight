import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\BlockLoop.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
scene = bpy.context.scene

print(f"BlockLoop Total frames: {scene.frame_end - scene.frame_start + 1}")
for f in range(1, 10):
    scene.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    hand_eval = arm_eval.pose.bones.get("hand_r")
    hand_l_eval = arm_eval.pose.bones.get("hand_l")
    pelvis_eval = arm_eval.pose.bones.get("pelvis")
    hr = arm_eval.matrix_world @ hand_eval.matrix.translation
    hl = arm_eval.matrix_world @ hand_l_eval.matrix.translation
    print(f"F{f}: hand_r=({hr.x:.2f}, {hr.y:.2f}, {hr.z:.2f}), hand_l=({hl.x:.2f}, {hl.y:.2f}, {hl.z:.2f})")
