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

v_grip_bone = Vector((-13.8996, 2.6063, 4.8925))
u_blade_bone = Vector((-0.49286, -0.12920, 0.86044))
v_tip_bone = v_grip_bone + 163.3 * u_blade_bone
S = Matrix.Diagonal(Vector((1.0, -1.0, 1.0, 1.0)))

def get_ue(pb):
    mw = arm.matrix_world @ pb.matrix
    M_ue = S @ mw @ S
    return M_ue.to_translation(), M_ue.to_quaternion()

def get_ue_sword():
    pb_r = arm.pose.bones['hand_r']
    pb_l = arm.pose.bones['hand_l']
    pos_r, rot_r = get_ue(pb_r)
    pos_l, _ = get_ue(pb_l)
    grip = pos_r + rot_r @ v_grip_bone
    tip = pos_r + rot_r @ v_tip_bone
    bdir = (tip - grip).normalized()
    return grip, tip, bdir, pos_r, pos_l

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

# Let's inspect shoulder position:
pos_clav, _ = get_ue(arm.pose.bones['clavicle_r'])
pos_uarm, _ = get_ue(arm.pose.bones['upperarm_r'])
print(f"clavicle_r UE pos: {pos_clav}")
print(f"upperarm_r UE pos: {pos_uarm}")

# Let's see what bone rotation axes do for upperarm_r:
# In rest pose:
print("Testing upperarm_r Euler axes...")
for axis, ang in [('X', (30,0,0)), ('Y', (0,30,0)), ('Z', (0,0,30))]:
    set_rot("upperarm_r", ang)
    bpy.context.view_layer.update()
    pos_larm, _ = get_ue(arm.pose.bones['lowerarm_r'])
    print(f"Rot {axis}+30 -> lowerarm_r UE pos: {pos_larm - pos_uarm}")

set_rot("upperarm_r", (0,0,0))
result = {"pos_clav": list(pos_clav), "pos_uarm": list(pos_uarm)}
"""

res = execute_blender(code)
print(res)
