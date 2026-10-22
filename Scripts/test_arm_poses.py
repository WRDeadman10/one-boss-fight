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
u_blade = Vector((-0.49286, -0.12920, 0.86044))
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

# Apply base kneel
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

bpy.context.view_layer.update()

# Let's inspect where clavicle_r and clavicle_l are in UE space
pb_cr = arm.pose.bones['clavicle_r']
pb_cl = arm.pose.bones['clavicle_l']
pb_ur = arm.pose.bones['upperarm_r']
pb_ul = arm.pose.bones['upperarm_l']

# To bring the arms forward and towards the center:
# In rest pose, upperarm_r points out to -X and down.
# Let's see what happens when we rotate upperarm_r by Euler angles:
# Let's print the UE position of hand_r for a set of plausible arm poses:
test_poses = [
    # (uarm_r, larm_r)
    ((-30, 0, 45), (-60, 0, 0)),
    ((-45, 0, 60), (-60, 0, 0)),
    ((-20, 20, 45), (-70, 0, 0)),
    ((-30, 30, 30), (-60, 0, 0)),
    ((-40, 20, 40), (-70, 0, 0)),
    ((-30, -30, 60), (-60, 0, 0)),
    ((0, 30, 45), (-80, 0, 0)),
    ((10, 40, 30), (-80, 0, 0)),
    ((-20, 40, 30), (-60, 0, 0)),
    ((-15, -45, 15), (-60, 0, 0)),
]

results = []
for ur, lr in test_poses:
    set_rot("upperarm_r", ur)
    set_rot("lowerarm_r", lr)
    set_rot("hand_r", (0, 0, 0))
    bpy.context.view_layer.update()
    
    pb_hr = arm.pose.bones['hand_r']
    M_bl = arm.matrix_world @ pb_hr.matrix
    scale_trans = 100.0 if abs(M_bl.translation.z) < 10.0 else 1.0
    M_ue = S @ M_bl @ S
    pos_hr = Vector((M_ue[0][3] * scale_trans, M_ue[1][3] * scale_trans, M_ue[2][3] * scale_trans))
    
    results.append({
        "ur": ur, "lr": lr,
        "pos_hr": [round(x, 1) for x in pos_hr]
    })

result = results
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
