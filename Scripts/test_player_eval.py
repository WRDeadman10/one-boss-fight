import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os, math
from mathutils import Vector, Euler, Matrix, Quaternion

bpy.ops.wm.read_factory_settings(use_empty=True)
ref_path = os.path.abspath('Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx')
bpy.ops.import_scene.fbx(filepath=ref_path)

arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arm.name = 'root'
arm.data.name = 'root'
arm.data.pose_position = 'POSE'

for o in list(bpy.context.scene.objects):
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)

scene = bpy.context.scene
scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01

arm.animation_data_create()
act = bpy.data.actions.new('ACT_Riposte_Player_Front')
arm.animation_data.action = act
if act.slots:
    arm.animation_data.action_slot = act.slots[0]

def set_rot(pb_name, euler_deg):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()
        pb.keyframe_insert('rotation_quaternion')

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.location = Vector(loc_cm)
        pb.keyframe_insert('location')

def clear_pose():
    arm.location = Vector((0, 0, 0))
    arm.rotation_euler = Euler((0, 0, 0))
    for pb in arm.pose.bones:
        pb.location = Vector((0, 0, 0))
        pb.rotation_quaternion = Quaternion((1, 0, 0, 0))

# Keyframes: 0..48
# Root travels along +Y in Unreal from (0,0,0) to (0,90,0) reached by frame 21 (0.7s)
player_kfs = [
    # (frame, root_y, pel_drop, lunge_step, thrust_ext, torso_twist, arm_windup)
    ( 0,  0.0,   0.0, 0.0,  0.0,   0.0,   0.0), # Combat ready
    ( 6, 15.0,  -3.0, 0.2,  0.0,  15.0,  30.0), # Coiling, right arm draws back
    (14, 55.0,  -6.0, 0.6, -0.2,  25.0,  60.0), # Heavy windup, lunging forward
    (21, 90.0,  -8.0, 1.0,  0.5,  10.0,  30.0), # Forward plant, thrust beginning
    (24, 90.0, -10.0, 1.0,  1.0,  -5.0,   0.0), # IMPACT (0.80s): maximum extension thrust!
    (30, 90.0,  -9.0, 1.0,  0.9,  -4.0,   5.0), # Embedded thrust hold
    (36, 90.0,  -6.0, 0.8,  0.5,   5.0,  20.0), # Wrenching blade free
    (42, 90.0,  -3.0, 0.4,  0.2,   2.0,  10.0), # Recovery stance
    (48, 90.0,   0.0, 0.0,  0.0,   0.0,   0.0), # Settled combat ready (same relative pose as frame 0!)
]

for f, ry, p_drop, step, thrust, twist, windup in player_kfs:
    scene.frame_set(f)
    # Root motion: advance in Unreal +Y means -ry in Blender
    arm.location = Vector((0, -ry / 100.0, 0))
    arm.rotation_euler = Euler((0, 0, 0))
    arm.keyframe_insert('location')
    arm.keyframe_insert('rotation_euler')
    
    set_loc('pelvis', (p_drop, 0, 0))
    # Torso lunges forward and twists:
    # Forward pitch is negative Z in Blender local
    set_rot('pelvis', (0, twist * 0.2, -thrust * 15.0))
    set_rot('spine_01', (0, twist * 0.25, -thrust * 12.0))
    set_rot('spine_03', (0, twist * 0.35, -thrust * 10.0))
    set_rot('spine_05', (0, twist * 0.40, -thrust * 8.0))
    set_rot('neck_01', (0, 0, thrust * 8.0)) # look at target
    set_rot('head', (0, 0, thrust * 12.0))
    
    # Right arm: windup -> powerful forward thrust
    # At impact (thrust=1.0): upperarm rotated forward (-80 deg pitch)
    r_pitch = -15.0 - windup * 0.5 + thrust * 85.0
    r_yaw = 20.0 + twist * 0.5
    set_rot('clavicle_r', (0, -thrust * 15.0, 0))
    set_rot('upperarm_r', (-r_pitch, -r_yaw, 15.0))
    set_rot('lowerarm_r', (-15.0 - windup * 0.4 + thrust * 45.0, 0, 0))
    set_rot('hand_r', (10.0, 0, 0))
    
    # Left arm: guard balance
    set_rot('clavicle_l', (0, thrust * 10.0, 0))
    set_rot('upperarm_l', (-20.0, 25.0 - twist * 0.3, -20.0))
    set_rot('lowerarm_l', (-50.0 + windup * 0.3, 0, 0))
    set_rot('hand_l', (15.0, 0, 0))
    
    # Legs stride and plant
    set_rot('thigh_r', (step * 35.0, 0, -8.0))
    set_rot('calf_r', (-step * 45.0, 0, 0))
    set_rot('foot_r', (step * 15.0, 0, 0))
    set_rot('thigh_l', (-step * 25.0, 0, 8.0))
    set_rot('calf_l', (-step * 20.0, 0, 0))
    set_rot('foot_l', (step * 10.0, 0, 0))

# Measure relative to root:
def get_ue_bone_world(bname):
    pb = arm.pose.bones[bname]
    mw = arm.matrix_world @ pb.matrix
    loc = mw.to_translation()
    return Vector((loc.x * 100.0, -loc.y * 100.0, loc.z * 100.0))

def get_ue_root():
    loc = arm.matrix_world.to_translation()
    return Vector((loc.x * 100.0, -loc.y * 100.0, loc.z * 100.0))

# 1. Check hand_r at frame 24 relative to root
scene.frame_set(24)
bpy.context.view_layer.update()
r24 = get_ue_root()
hr24 = get_ue_bone_world('hand_r')
rel_hr = hr24 - r24
print(f'Frame 24 hand_r rel root: X={rel_hr.x:.1f}, Y={rel_hr.y:.1f} (need >= 45), Z={hr24.z:.1f} (need 105..140)')

# 2. Check bone movement sum between frame 14 and frame 24
all_bones = [b.name for b in arm.data.bones]
scene.frame_set(14)
bpy.context.view_layer.update()
r14 = get_ue_root()
b14 = {b: get_ue_bone_world(b) - r14 for b in all_bones}

scene.frame_set(24)
bpy.context.view_layer.update()
r24 = get_ue_root()
b24 = {b: get_ue_bone_world(b) - r24 for b in all_bones}

total_move = sum((b24[b] - b14[b]).length for b in all_bones)
print(f'Bone movements inside root frame (f14 to f24): {total_move:.1f} cm (need >= 400)')

# 3. Check recovery at frame 48 vs frame 0 relative to root
scene.frame_set(0)
bpy.context.view_layer.update()
r0 = get_ue_root()
b0 = {b: get_ue_bone_world(b) - r0 for b in ['hand_r', 'hand_l', 'head']}

scene.frame_set(48)
bpy.context.view_layer.update()
r48 = get_ue_root()
b48 = {b: get_ue_bone_world(b) - r48 for b in ['hand_r', 'hand_l', 'head']}

for b in ['hand_r', 'hand_l', 'head']:
    d = (b48[b] - b0[b]).length
    print(f'Frame 48 recovery of {b}: {d:.2f} cm (need <= 15)')
"""

res = execute_blender(code)
print(res)
