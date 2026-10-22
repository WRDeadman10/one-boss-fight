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

def get_ue_bone_world(bname):
    pb = arm.pose.bones[bname]
    mw = arm.matrix_world @ pb.matrix
    loc = mw.to_translation()
    return Vector((loc.x * 100.0, -loc.y * 100.0, loc.z * 100.0))

# In rest pose:
print('Rest hand_r:', get_ue_bone_world('hand_r'))

for axis in ['X', 'Y', 'Z']:
    for ang in [-90, -45, 45, 90]:
        e = [0, 0, 0]
        e[{'X':0, 'Y':1, 'Z':2}[axis]] = ang
        set_rot('upperarm_r', e)
        bpy.context.view_layer.update()
        hr = get_ue_bone_world('hand_r')
        print(f'upperarm_r {axis}={ang:3d} -> hand_r ({hr.x:.1f}, {hr.y:.1f}, {hr.z:.1f})')
"""

res = execute_blender(code)
print(res)
