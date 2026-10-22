import os, sys
sys.path.insert(0, 'Scripts')
from blender_exec import execute_blender

code = """
import bpy, os, math
from mathutils import Vector, Euler

bpy.ops.wm.read_factory_settings(use_empty=True)
ref_path = os.path.abspath('Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx')
bpy.ops.import_scene.fbx(filepath=ref_path)

arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arm.name = 'root'

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.location = Vector((loc_cm[0] / 100.0, loc_cm[1] / 100.0, loc_cm[2] / 100.0))

def set_rot(pb_name, euler_deg):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()

def get_ue_bone_z(bname):
    pb = arm.pose.bones[bname]
    mw = arm.matrix_world @ pb.matrix
    return mw.translation.z * 100.0

set_loc('pelvis', (-48.0, 4.0, 0.0))
sp_slump = -26.0
set_rot('pelvis', (0.0, 0.0, sp_slump * 0.4))

t = 1.0
set_rot('thigh_l', (75.0 * t, 0.0, 5.0 + 5.0 * t))
set_rot('calf_l', (0.0, -120.0 * t, -60.0 * t))
set_rot('foot_l', (0.0, -25.0 * t, -25.0 * t))
set_rot('thigh_r', (85.0 * t, 0.0, -5.0 - 15.0 * t))
set_rot('calf_r', (0.0, 120.0 * t, -40.0 * t))
set_rot('foot_r', (0.0, 50.0 * t, 25.0 * t))

bpy.context.view_layer.update()
print('At t=1.0: ankle_l=%.2f, ankle_r=%.2f, ball_l=%.2f, ball_r=%.2f' % (get_ue_bone_z('foot_l'), get_ue_bone_z('foot_r'), get_ue_bone_z('ball_l'), get_ue_bone_z('ball_r')))

# Test what foot_r pitch / roll adjustments give:
for dp in [0, 10, 20, 30, 40]:
    for dr in [-20, -10, 0, 10, 20]:
        set_rot('foot_r', (0.0, 50.0 + dp, 25.0 + dr))
        bpy.context.view_layer.update()
        ar = get_ue_bone_z('foot_r')
        br = get_ue_bone_z('ball_r')
        if ar >= 3.0 and br >= 0.0:
            print('dp=%d, dr=%d -> ankle_r=%.2f, ball_r=%.2f' % (dp, dr, ar, br))
            break
"""
res = execute_blender(code)
print(res['result'])
