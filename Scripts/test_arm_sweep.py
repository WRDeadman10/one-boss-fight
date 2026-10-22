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
    if pb:
        pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.location = Vector(loc_cm)

def get_ue_state():
    bpy.context.view_layer.update()
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

# Base kneel body
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

# Now let's explore upperarm_r and lowerarm_r to bring hand_r to:
# X in [-15, 15], Y in [30, 50], Z in [80, 100]
print("Baseline upperarm_r/lowerarm_r...")
# Let's test sweeping upperarm_r angles
candidates = []
for p in range(-90, 91, 15):
    for r in range(-90, 91, 15):
        for y in range(-90, 91, 15):
            set_rot("upperarm_r", (p, r, y))
            for lp in range(-120, 1, 15):
                set_rot("lowerarm_r", (lp, 0, 0))
                set_rot("hand_r", (0, 0, 0))
                pos_r, _, _, _, _ = get_ue_state()
                if -15 <= pos_r.x <= 15 and 25 <= pos_r.y <= 55 and 80 <= pos_r.z <= 105:
                    candidates.append(((p, r, y), lp, list(pos_r)))

print(f"Arm positions found: {len(candidates)}")
result = candidates[:15]
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
