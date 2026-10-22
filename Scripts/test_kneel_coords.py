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

def set_rot(pb_name, euler_deg):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.location = Vector(loc_cm)

set_loc('pelvis', (-48.0, 4.0, 0))

def get_ue_pos(bname):
    pb = arm.pose.bones[bname]
    mw = arm.matrix_world @ pb.matrix
    loc = mw.to_translation()
    return Vector((loc.x * 100.0, -loc.y * 100.0, loc.z * 100.0))

set_rot('thigh_l', (75, 0, 10))
set_rot('calf_l', (0, -120, -60))
set_rot('foot_l', (0, -30, -30))

set_rot('thigh_r', (85, 0, -20))
set_rot('calf_r', (0, 120, -40))
set_rot('foot_r', (0, 60, 30))

bpy.context.view_layer.update()

for b in ['pelvis', 'calf_l', 'foot_l', 'ball_l', 'calf_r', 'foot_r', 'ball_r']:
    p = get_ue_pos(b)
    print(f'  {b:10s} : ({p.x:.2f}, {p.y:.2f}, {p.z:.2f}) cm')
"""

res = execute_blender(code)
print(res)
