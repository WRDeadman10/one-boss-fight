import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os, math
from mathutils import Vector, Euler, Matrix, Quaternion

anim_dir = os.path.abspath("Import/Boss01/Animations")
v_grip = Vector((-13.8996, 2.6063, 4.8925))
v_tip = Vector((-94.39, -18.50, 145.39))
S = Matrix.Diagonal(Vector((1.0, -1.0, 1.0, 1.0)))

fbx_p = os.path.join(anim_dir, "AN_Boss01_DormantIdle.fbx")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fbx_p)
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')

bpy.context.scene.frame_set(1)
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

result = {
    "hand_r": [round(x, 1) for x in pos_ue_r],
    "hand_l": [round(x, 1) for x in pos_ue_l],
    "hands_dist": round((pos_ue_r - pos_ue_l).length, 1),
    "grip": [round(x, 1) for x in g_ue],
    "tip": [round(x, 1) for x in t_ue],
    "blade_dir": [round(x, 2) for x in d_ue]
}
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
