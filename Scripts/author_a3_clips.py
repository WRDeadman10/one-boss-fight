import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import os
import math
from mathutils import Vector, Quaternion, Euler

# Clean scene objects
scene = bpy.context.scene
for o in list(scene.objects):
    bpy.data.objects.remove(o, do_unlink=True)
dummy = bpy.data.objects.new("Dummy", None)
scene.collection.objects.link(dummy)
bpy.context.view_layer.objects.active = dummy

scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01

ref_path = r"c:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\ThirdParty\Reference\SKM_CombatMannequin_Simple.fbx"
bpy.ops.import_scene.fbx(filepath=ref_path)

bpy.data.objects.remove(dummy, do_unlink=True)

# MUST set scene FPS *AFTER* FBX import because import_scene.fbx resets scene FPS!
scene.render.fps = 30
scene.render.fps_base = 1.0

arm = [o for o in scene.objects if o.type == 'ARMATURE'][0]
arm.name = "root"
arm.data.name = "root"
arm.data.pose_position = 'POSE'
bpy.context.view_layer.objects.active = arm
arm.select_set(True)

# Remove any meshes imported with reference
for o in list(scene.objects):
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)

anim_dir = r"c:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Boss01\Animations"

# -------------------------------------------------------------------
# Create IK Targets for two-handed greatsword grip
# -------------------------------------------------------------------
target_r = bpy.data.objects.new("Temp_IK_R", None)
target_l = bpy.data.objects.new("Temp_IK_L", None)
scene.collection.objects.link(target_r)
scene.collection.objects.link(target_l)

def setup_ik():
    for pb in arm.pose.bones:
        for c in list(pb.constraints):
            pb.constraints.remove(c)
    cr = arm.pose.bones['hand_r'].constraints.new('IK')
    cr.target = target_r
    cr.chain_count = 3
    cl = arm.pose.bones['hand_l'].constraints.new('IK')
    cl.target = target_l
    cl.chain_count = 3

# ===================================================================
# 1. Author A3a: Combo Slash 1 (0.80 s = frames 0 to 24, 25 frames)
# ===================================================================
setup_ik()
act_a3a = bpy.data.actions.new("ACT_Boss01_A3a_Combo1")
arm.animation_data_create()
arm.animation_data.action = act_a3a
if hasattr(arm.animation_data, 'action_slot'):
    arm.animation_data.action_slot = act_a3a.slots[0] if act_a3a.slots else None

specs_a3a = [
    # (frame, pel_drop_x, spine_yaw, hr_pos, hl_pos)
    (0,   0.0,   0.0, Vector((-6.0, -18.0, 105.0)), Vector(( 6.0, -16.0, 102.0))),
    (6,  -6.0, -20.0, Vector((-18.0, -10.0, 125.0)), Vector((-8.0, -14.0, 118.0))),
    (12, -9.0, -30.0, Vector((-22.0,  -4.0, 138.0)), Vector((-10.0,  -8.0, 130.0))),
    (15,-11.0,   5.0, Vector((-2.0, -24.0,  95.0)), Vector((  8.0, -20.0,  96.0))),
    (18,-10.0,  25.0, Vector(( 16.0, -16.0,  80.0)), Vector(( 24.0,  -6.0,  84.0))),
    (24, -8.0,  20.0, Vector(( 14.0, -18.0,  82.0)), Vector(( 22.0, -10.0,  86.0)))
]

for frame, pel_drop_x, spine_yaw, hr_pos, hl_pos in specs_a3a:
    scene.frame_set(frame)
    pb_pel = arm.pose.bones['pelvis']
    pb_pel.location = (pel_drop_x, 0, 0)
    pb_pel.rotation_quaternion = Euler((math.radians(spine_yaw * 0.35), 0, math.radians(4.0))).to_quaternion()
    pb_pel.keyframe_insert("location", frame=frame)
    pb_pel.keyframe_insert("rotation_quaternion", frame=frame)
    
    s1_rot = Euler((math.radians(spine_yaw * 0.30), 0, math.radians(2.0))).to_quaternion()
    s3_rot = Euler((math.radians(spine_yaw * 0.35), 0, math.radians(3.0))).to_quaternion()
    s5_rot = Euler((math.radians(spine_yaw * 0.35), 0, math.radians(3.0))).to_quaternion()
    for sname, srot in [('spine_01', s1_rot), ('spine_03', s3_rot), ('spine_05', s5_rot)]:
        arm.pose.bones[sname].rotation_quaternion = srot
        arm.pose.bones[sname].keyframe_insert("rotation_quaternion", frame=frame)
        
    crouch_factor = abs(pel_drop_x) / 16.0
    thigh_angle = crouch_factor * 28.0
    calf_angle = -crouch_factor * 48.0
    foot_angle = crouch_factor * 20.0
    
    arm.pose.bones['thigh_l'].rotation_quaternion = Euler((math.radians(crouch_factor * 8), 0, math.radians(thigh_angle))).to_quaternion()
    arm.pose.bones['calf_l'].rotation_quaternion = Euler((0, 0, math.radians(calf_angle))).to_quaternion()
    arm.pose.bones['foot_l'].rotation_quaternion = Euler((0, 0, math.radians(foot_angle))).to_quaternion()
    arm.pose.bones['thigh_r'].rotation_quaternion = Euler((math.radians(-crouch_factor * 8), 0, math.radians(-thigh_angle))).to_quaternion()
    arm.pose.bones['calf_r'].rotation_quaternion = Euler((0, 0, math.radians(-calf_angle))).to_quaternion()
    arm.pose.bones['foot_r'].rotation_quaternion = Euler((0, 0, math.radians(-foot_angle))).to_quaternion()
    
    for bname in ['thigh_l', 'calf_l', 'foot_l', 'thigh_r', 'calf_r', 'foot_r']:
        arm.pose.bones[bname].keyframe_insert("rotation_quaternion", frame=frame)
        
    target_r.location = hr_pos
    target_r.keyframe_insert("location", frame=frame)
    target_l.location = hl_pos
    target_l.keyframe_insert("location", frame=frame)

# Bake visual transforms for A3a (frames 0 to 24)
scene.frame_start = 0
scene.frame_end = 24
bpy.ops.nla.bake(
    frame_start=0,
    frame_end=24,
    only_selected=False,
    visual_keying=True,
    clear_constraints=True,
    bake_types={'POSE'}
)

act_a3a.use_frame_range = True
act_a3a.frame_start = 0.0
act_a3a.frame_end = 24.0

# Export A3a FBX with exact scene frame range 0 to 24
scene.frame_start = 0
scene.frame_end = 24
fbx_a3a_path = os.path.join(anim_dir, "AN_Boss01_A3a_Combo1.fbx")
bpy.ops.export_scene.fbx(
    filepath=fbx_a3a_path,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',
    axis_forward='-Z',
    axis_up='Y',
    object_types={'ARMATURE'},
    add_leaf_bones=False,
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_actions=False,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=0.0
)

# ===================================================================
# 2. Author A3b: Combo Slash 2 (1.35 s = frames 0 to 40, 41 frames)
# ===================================================================
# Clear pose bones
for pb in arm.pose.bones:
    pb.location = (0, 0, 0)
    pb.rotation_quaternion = (1, 0, 0, 0)

setup_ik()
act_a3b = bpy.data.actions.new("ACT_Boss01_A3b_Combo2")
arm.animation_data.action = act_a3b
if hasattr(arm.animation_data, 'action_slot'):
    arm.animation_data.action_slot = act_a3b.slots[0] if act_a3b.slots else None

# Frame 0 of A3b matches Frame 24 of A3a:
# pel_drop_x = -8.0, spine_yaw = 20.0, hr = (14.0, -18.0, 82.0), hl = (22.0, -10.0, 86.0)
specs_a3b = [
    (0,  -8.0,  20.0, Vector(( 14.0, -18.0,  82.0)), Vector(( 22.0, -10.0,  86.0))),
    (4, -10.0,  28.0, Vector(( 18.0, -14.0,  80.0)), Vector(( 26.0,  -4.0,  82.0))),
    (8, -11.0, -10.0, Vector((-2.0, -26.0, 105.0)), Vector((  8.0, -22.0, 102.0))),
    (12, -9.0, -32.0, Vector((-22.0, -12.0, 115.0)), Vector((-12.0, -16.0, 110.0))),
    (24, -5.0, -15.0, Vector((-16.0, -16.0, 110.0)), Vector((-6.0, -18.0, 106.0))),
    (40,  0.0,   0.0, Vector((-6.0, -18.0, 105.0)), Vector(( 6.0, -16.0, 102.0)))
]

for frame, pel_drop_x, spine_yaw, hr_pos, hl_pos in specs_a3b:
    scene.frame_set(frame)
    pb_pel = arm.pose.bones['pelvis']
    pb_pel.location = (pel_drop_x, 0, 0)
    pb_pel.rotation_quaternion = Euler((math.radians(spine_yaw * 0.35), 0, math.radians(4.0))).to_quaternion()
    pb_pel.keyframe_insert("location", frame=frame)
    pb_pel.keyframe_insert("rotation_quaternion", frame=frame)
    
    s1_rot = Euler((math.radians(spine_yaw * 0.30), 0, math.radians(2.0))).to_quaternion()
    s3_rot = Euler((math.radians(spine_yaw * 0.35), 0, math.radians(3.0))).to_quaternion()
    s5_rot = Euler((math.radians(spine_yaw * 0.35), 0, math.radians(3.0))).to_quaternion()
    for sname, srot in [('spine_01', s1_rot), ('spine_03', s3_rot), ('spine_05', s5_rot)]:
        arm.pose.bones[sname].rotation_quaternion = srot
        arm.pose.bones[sname].keyframe_insert("rotation_quaternion", frame=frame)
        
    crouch_factor = abs(pel_drop_x) / 16.0
    thigh_angle = crouch_factor * 28.0
    calf_angle = -crouch_factor * 48.0
    foot_angle = crouch_factor * 20.0
    
    arm.pose.bones['thigh_l'].rotation_quaternion = Euler((math.radians(crouch_factor * 8), 0, math.radians(thigh_angle))).to_quaternion()
    arm.pose.bones['calf_l'].rotation_quaternion = Euler((0, 0, math.radians(calf_angle))).to_quaternion()
    arm.pose.bones['foot_l'].rotation_quaternion = Euler((0, 0, math.radians(foot_angle))).to_quaternion()
    arm.pose.bones['thigh_r'].rotation_quaternion = Euler((math.radians(-crouch_factor * 8), 0, math.radians(-thigh_angle))).to_quaternion()
    arm.pose.bones['calf_r'].rotation_quaternion = Euler((0, 0, math.radians(-calf_angle))).to_quaternion()
    arm.pose.bones['foot_r'].rotation_quaternion = Euler((0, 0, math.radians(-foot_angle))).to_quaternion()
    
    for bname in ['thigh_l', 'calf_l', 'foot_l', 'thigh_r', 'calf_r', 'foot_r']:
        arm.pose.bones[bname].keyframe_insert("rotation_quaternion", frame=frame)
        
    target_r.location = hr_pos
    target_r.keyframe_insert("location", frame=frame)
    target_l.location = hl_pos
    target_l.keyframe_insert("location", frame=frame)

# Bake visual transforms for A3b (frames 0 to 40)
scene.frame_start = 0
scene.frame_end = 40
bpy.ops.nla.bake(
    frame_start=0,
    frame_end=40,
    only_selected=False,
    visual_keying=True,
    clear_constraints=True,
    bake_types={'POSE'}
)

act_a3b.use_frame_range = True
act_a3b.frame_start = 0.0
act_a3b.frame_end = 40.0

# Export A3b FBX with exact scene frame range 0 to 40
scene.frame_start = 0
scene.frame_end = 40
fbx_a3b_path = os.path.join(anim_dir, "AN_Boss01_A3b_Combo2.fbx")
bpy.ops.export_scene.fbx(
    filepath=fbx_a3b_path,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',
    axis_forward='-Z',
    axis_up='Y',
    object_types={'ARMATURE'},
    add_leaf_bones=False,
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_actions=False,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=0.0
)

bpy.data.objects.remove(target_r, do_unlink=True)
bpy.data.objects.remove(target_l, do_unlink=True)

# -------------------------------------------------------------------
# Read back validation from the exported FBX files in clean scenes
# -------------------------------------------------------------------
def measure_clip_clean(filepath):
    s = bpy.data.scenes.new("Measure")
    bpy.context.window.scene = s
    bpy.ops.import_scene.fbx(filepath=filepath)
    a = [o for o in s.objects if o.type == 'ARMATURE'][0]
    act = a.animation_data.action
    curves = act.fcurves if hasattr(act, 'fcurves') else []
    # Find frame range of keyframes
    f_min = min(c.range()[0] for c in curves) if curves else 0
    f_max = max(c.range()[1] for c in curves) if curves else 0
    
    # Measure sample times
    samples = []
    times = [0.0, 0.20, 0.40, 0.60, 0.80] if "A3a" in filepath else [0.0, 0.13, 0.27, 0.40, 1.333]
    for t in times:
        f = round(t * 30.0)
        s.frame_set(f)
        bpy.context.view_layer.update()
        pel = a.matrix_world @ a.pose.bones['pelvis'].matrix.translation
        hr = a.matrix_world @ a.pose.bones['hand_r'].matrix.translation
        hl = a.matrix_world @ a.pose.bones['hand_l'].matrix.translation
        fl = a.matrix_world @ a.pose.bones['foot_l'].matrix.translation
        fr = a.matrix_world @ a.pose.bones['foot_r'].matrix.translation
        samples.append({
            "t": t,
            "f": f,
            "pelvis_z": round(pel.z * 100.0, 1),
            "wrist_dist": round((hr - hl).length * 100.0, 1),
            "lowest_foot_z": round(min(fl.z, fr.z) * 100.0, 1)
        })
    
    bpy.context.window.scene = scene
    for o in list(s.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.scenes.remove(s)
    
    return {
        "frame_min": f_min,
        "frame_max": f_max,
        "frames_count": int(f_max - f_min + 1),
        "duration_sec": round((f_max - f_min) / 30.0, 3),
        "samples": samples
    }

read_a3a = measure_clip_clean(fbx_a3a_path)
read_a3b = measure_clip_clean(fbx_a3b_path)

result = {
    "A3a_readback": read_a3a,
    "A3b_readback": read_a3b
}
"""

res = execute_blender(code)
print("Execution result:")
import json
print(json.dumps(res, indent=2))
