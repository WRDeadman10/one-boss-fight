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

def get_ue_z(bname):
    pb = arm.pose.bones[bname]
    v = (arm.matrix_world @ pb.matrix).to_translation()
    return v.z * 100.0

for axis in ['X', 'Y', 'Z']:
    for ang in [30, 60, 90]:
        e = [0, 0, 0]
        e[{'X':0, 'Y':1, 'Z':2}[axis]] = ang
        set_rot('thigh_l', e)
        set_rot('calf_l', [0, 0, 0])
        set_rot('foot_l', [0, 0, 0])
        bpy.context.view_layer.update()
        kz = get_ue_z('calf_l')
        fz = get_ue_z('foot_l')
        print(f'thigh_l {axis}={ang:2d}: knee Z={kz:.1f}, foot Z={fz:.1f}')
"""

res = execute_blender(code)
print(res)
