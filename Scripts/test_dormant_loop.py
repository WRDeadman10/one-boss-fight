import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os, math
from mathutils import Vector, Euler, Matrix, Quaternion

ref_path = os.path.abspath("Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=ref_path)
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
arm.data.pose_position = 'POSE'

v_grip = Vector((-13.8996, 2.6063, 4.8925))
v_tip = Vector((-94.39, -18.50, 145.39))
S = Matrix.Diagonal(Vector((1.0, -1.0, 1.0, 1.0)))

def set_rot(pb_name, euler_deg):
    pb = arm.pose.bones.get(pb_name)
    pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones.get(pb_name)
    pb.location = Vector(loc_cm)

def get_sword():
    pb_r = arm.pose.bones['hand_r']
    pb_l = arm.pose.bones['hand_l']
    M_bl_r = arm.matrix_world @ pb_r.matrix
    M_bl_l = arm.matrix_world @ pb_l.matrix
    scale_trans = 100.0 if abs(M_bl_r.translation.z) < 10.0 else 1.0
    M_ue_r = S @ M_bl_r @ S
    pos_r = Vector((M_ue_r[0][3] * scale_trans, M_ue_r[1][3] * scale_trans, M_ue_r[2][3] * scale_trans))
    rot_r = M_ue_r.to_quaternion()
    M_ue_l = S @ M_bl_l @ S
    pos_l = Vector((M_ue_l[0][3] * scale_trans, M_ue_l[1][3] * scale_trans, M_ue_l[2][3] * scale_trans))
    grip = pos_r + rot_r @ v_grip
    tip = pos_r + rot_r @ v_tip
    bdir = (tip - grip).normalized()
    return pos_r, pos_l, grip, tip, bdir

def get_bone_ue(bname):
    pb = arm.pose.bones[bname]
    M_bl = arm.matrix_world @ pb.matrix
    scale_trans = 100.0 if abs(M_bl.translation.z) < 10.0 else 1.0
    M_ue = S @ M_bl @ S
    return Vector((M_ue[0][3] * scale_trans, M_ue[1][3] * scale_trans, M_ue[2][3] * scale_trans))

# Let's test a breathing loop across 151 frames
# We want:
# - loop closure 0.0000 (f=0 == f=150)
# - tip Z in [0.0, 3.0] cm in EVERY frame
# - tip motion in X, Y <= 1.0 cm over the whole loop
# - breathing visible (largest bone movement >= 1.5 cm, spine/head heave)

# If breathing moves spine_01, spine_03, neck_01, head:
# To keep hand_r pinned:
# We can counter-rotate clavicle_r / upperarm_r / hand_r smoothly with breath!
# Let's test!
frames_data = []
min_tz, max_tz = 999.0, -999.0
min_tx, max_tx = 999.0, -999.0
min_ty, max_ty = 999.0, -999.0

# Base pose at f=0:
set_loc("pelvis", (-48.0, 4.0, 0.0))
set_rot("pelvis", (0.0, 0.0, -4.0))
set_rot("spine_01", (0.0, 0.0, -5.0))
set_rot("spine_03", (0.0, 0.0, -6.0))
set_rot("spine_05", (0.0, 0.0, -7.0))
set_rot("neck_01", (0.0, 0.0, -8.0))
set_rot("head", (0.0, 0.0, -10.0))

set_rot("thigh_l", (85.0, 0.0, 10.0))
set_rot("calf_l", (0.0, -120.0, -60.0))
set_rot("foot_l", (0.0, -30.0, -30.0))
set_rot("thigh_r", (95.0, 0.0, -20.0))
set_rot("calf_r", (0.0, 120.0, -40.0))
set_rot("foot_r", (0.0, 60.0, 30.0))

set_rot("upperarm_r", (0, 30, -50))
set_rot("lowerarm_r", (0, 0, -50))
set_rot("hand_r", (190, 5, 5))

set_rot("upperarm_l", (0, 30, -50))
set_rot("lowerarm_l", (0, 0, -50))
set_rot("hand_l", (190, -5, -5))

bpy.context.view_layer.update()
p0_r, p0_l, g0, t0, d0 = get_sword()
f0_bones = {b.name: get_bone_ue(b.name) for b in arm.pose.bones}

# Test with counter-compensated arms during breath:
for f in [0, 38, 75, 113, 150]:
    # Breath wave (0 to 1 to 0):
    breath = math.sin(math.pi * f / 150.0)
    
    # Breathing motion on pelvis, spine, head:
    set_loc("pelvis", (-48.0 + breath * 0.3, 4.0, 0.0))
    set_rot("spine_01", (0.0, 0.0, -5.0 - breath * 0.8))
    set_rot("spine_03", (0.0, 0.0, -6.0 - breath * 1.2))
    set_rot("spine_05", (0.0, 0.0, -7.0 - breath * 1.0))
    set_rot("neck_01", (0.0, 0.0, -8.0 + breath * 0.8))
    set_rot("head", (0.0, 0.0, -10.0 + breath * 1.2))
    
    # Counter-rotate upperarm and lowerarm so hands stay pinned:
    # Spine_05 rotated by -1.0 deg around Z. We counter-rotate upperarm_r by +1.0 deg!
    set_rot("upperarm_r", (0, 30 + breath * 0.2, -50 + breath * 1.5))
    set_rot("lowerarm_r", (0, 0, -50 - breath * 0.8))
    set_rot("hand_r", (190, 5, 5 - breath * 0.5))
    
    set_rot("upperarm_l", (0, 30 + breath * 0.2, -50 + breath * 1.5))
    set_rot("lowerarm_l", (0, 0, -50 - breath * 0.8))
    set_rot("hand_l", (190, -5, -5 - breath * 0.5))
    
    bpy.context.view_layer.update()
    pos_r, pos_l, grip, tip, bdir = get_sword()
    
    min_tz = min(min_tz, tip.z)
    max_tz = max(max_tz, tip.z)
    min_tx = min(min_tx, tip.x)
    max_tx = max(max_tx, tip.x)
    min_ty = min(min_ty, tip.y)
    max_ty = max(max_ty, tip.y)
    
    frames_data.append({
        "f": f,
        "tip": [round(x, 2) for x in tip],
        "grip": [round(x, 2) for x in grip],
        "bdir": [round(x, 2) for x in bdir],
        "hand_r": [round(x, 2) for x in pos_r],
        "hand_l": [round(x, 2) for x in pos_l],
        "hands_dist": round((pos_r - pos_l).length, 2)
    })

# Check breath displacement at f=75
f75_bones = {b.name: get_bone_ue(b.name) for b in arm.pose.bones}
max_d, max_b = 0.0, ""
for b in f0_bones:
    d = (f75_bones[b] - f0_bones[b]).length
    if d > max_d:
        max_d, max_b = d, b

result = {
    "frames": frames_data,
    "tip_z_range": [round(min_tz, 2), round(max_tz, 2)],
    "tip_xy_drift": round(math.sqrt((max_tx - min_tx)**2 + (max_ty - min_ty)**2), 2),
    "max_breath_disp": round(max_d, 2),
    "max_breath_bone": max_b,
    "head_breath_disp": round((f75_bones['head'] - f0_bones['head']).length, 2)
}
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
