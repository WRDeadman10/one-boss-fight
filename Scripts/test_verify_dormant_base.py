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

pb = arm.pose.bones['pelvis']
pb.location = Vector((-48.0, 4.0, 0.0))
pb.rotation_quaternion = Euler((0, 0, math.radians(-4.0))).to_quaternion()

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

# Arm & Hand poses:
set_rot("upperarm_r", (0, 30, -50))
set_rot("lowerarm_r", (0, 0, -50))
set_rot("hand_r", (190, 5, 5))

set_rot("upperarm_l", (0, 30, -50))
set_rot("lowerarm_l", (0, 0, -50))
set_rot("hand_l", (190, -5, -5))

bpy.context.view_layer.update()

pb_r = arm.pose.bones['hand_r']
pb_l = arm.pose.bones['hand_l']

M_bl_r = arm.matrix_world @ pb_r.matrix
M_bl_l = arm.matrix_world @ pb_l.matrix

scale_trans = 100.0 if abs(M_bl_r.translation.z) < 10.0 else 1.0

M_ue_r = S @ M_bl_r @ S
pos_ue_r = Vector((M_ue_r[0][3] * scale_trans, M_ue_r[1][3] * scale_trans, M_ue_r[2][3] * scale_trans))
rot_ue_r = M_ue_r.to_quaternion()

M_ue_l = S @ M_bl_l @ S
pos_ue_l = Vector((M_ue_l[0][3] * scale_trans, M_ue_l[1][3] * scale_trans, M_ue_l[2][3] * scale_trans))

g_ue = pos_ue_r + rot_ue_r @ v_grip
t_ue = pos_ue_r + rot_ue_r @ v_tip
d_ue = (t_ue - g_ue).normalized()

# Check head minus pelvis
pb_pel = arm.pose.bones['pelvis']
pb_hd = arm.pose.bones['head']
M_pel = S @ (arm.matrix_world @ pb_pel.matrix) @ S
M_hd = S @ (arm.matrix_world @ pb_hd.matrix) @ S
pos_pel = Vector((M_pel[0][3] * scale_trans, M_pel[1][3] * scale_trans, M_pel[2][3] * scale_trans))
pos_hd = Vector((M_hd[0][3] * scale_trans, M_hd[1][3] * scale_trans, M_hd[2][3] * scale_trans))
hp = pos_hd - pos_pel

result = {
    "hand_r": [round(x, 2) for x in pos_ue_r],
    "hand_l": [round(x, 2) for x in pos_ue_l],
    "hands_dist": round((pos_ue_r - pos_ue_l).length, 2),
    "grip": [round(x, 2) for x in g_ue],
    "tip": [round(x, 2) for x in t_ue],
    "bdir": [round(x, 3) for x in d_ue],
    "head_minus_pelvis_y": round(hp.y, 2),
    "head_z": round(pos_hd.z, 2)
}
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
