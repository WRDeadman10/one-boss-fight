import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\Dodge_Small_Forward_Roll.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
scene = bpy.context.scene

print(f"Dodge_Roll Total frames: {scene.frame_end - scene.frame_start + 1}")
for f in range(1, 23):
    scene.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    pelvis_eval = arm_eval.pose.bones.get("pelvis")
    p = arm_eval.matrix_world @ pelvis_eval.matrix.translation
    # Also check root bone translation
    root_eval = arm_eval.pose.bones.get("root")
    r_loc = root_eval.location if root_eval else (0,0,0)
    print(f"F{f:02d}: pelvis=({p.x:.2f}, {p.y:.2f}, {p.z:.2f}), root_loc=({r_loc[0]:.2f}, {r_loc[1]:.2f}, {r_loc[2]:.2f})")
