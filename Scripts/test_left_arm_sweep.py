import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os, math
from mathutils import Vector, Euler, Matrix

ref_path = os.path.abspath("Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=ref_path)
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
arm.data.pose_position = 'POSE'
S = Matrix.Diagonal(Vector((1.0, -1.0, 1.0, 1.0)))

def get_ue(pb_name):
    pb = arm.pose.bones[pb_name]
    M_bl = arm.matrix_world @ pb.matrix
    scale_trans = 100.0 if abs(M_bl.translation.z) < 10.0 else 1.0
    M_ue = S @ M_bl @ S
    return Vector((M_ue[0][3] * scale_trans, M_ue[1][3] * scale_trans, M_ue[2][3] * scale_trans))

def set_rot(pb_name, euler_deg):
    pb = arm.pose.bones[pb_name]
    pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()

pb = arm.pose.bones['pelvis']
pb.location = Vector((-48.0, 4.0, 0.0))
pb.rotation_quaternion = Euler((0, 0, math.radians(-4.0))).to_quaternion()

# Set right arm
set_rot("upperarm_r", (0, 30, -45))
set_rot("lowerarm_r", (0, 0, -45))
bpy.context.view_layer.update()
p_hr = get_ue("hand_r")

# Now sweep left arm to find hand_l within 15 cm of p_hr
candidates = []
for uy in range(-60, 61, 15):
    for uz in range(-60, 61, 15):
        set_rot("upperarm_l", (0, uy, uz))
        for ly in range(-60, 61, 15):
            for lz in range(-60, 61, 15):
                set_rot("lowerarm_l", (0, ly, lz))
                bpy.context.view_layer.update()
                p_hl = get_ue("hand_l")
                dist = (p_hl - p_hr).length
                if dist < 20.0:
                    candidates.append((dist, (0, uy, uz), (0, ly, lz), list(p_hl)))

candidates.sort(key=lambda c: c[0])
result = {
    "hand_r": [round(x, 1) for x in p_hr],
    "best_matches": [
        {"dist": round(c[0], 1), "uarm_l": c[1], "larm_l": c[2], "hand_l": [round(x, 1) for x in c[3]]}
        for c in candidates[:10]
    ]
}
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
