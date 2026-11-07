import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\PrimaryAttack_A_Slow_Anim.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
scene = bpy.context.scene

print(f"PrimaryAttack_A_Slow Total frames: {scene.frame_end - scene.frame_start + 1}")
for f in range(1, 40, 2):
    scene.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    hand_eval = arm_eval.pose.bones.get("hand_r")
    pelvis_eval = arm_eval.pose.bones.get("pelvis")
    hr = arm_eval.matrix_world @ hand_eval.matrix.translation
    p = arm_eval.matrix_world @ pelvis_eval.matrix.translation
    print(f"F{f:02d}: hand_r=({hr.x:.2f}, {hr.y:.2f}, {hr.z:.2f}), pelvis_z={p.z:.2f}")
