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

set_loc('pelvis', (-46.5, 0, 0)) # drop pelvis so knee is ~ 3.6 cm
set_rot('thigh_l', (0, 0, 0))

def get_ue_pos(bname):
    pb = arm.pose.bones[bname]
    v = (arm.matrix_world @ pb.matrix).to_translation()
    return Vector((v.x * 100.0, -v.y * 100.0, v.z * 100.0))

print('Knee at rest with pel=-46.5:', get_ue_pos('calf_l'))

for axis in ['Y', 'Z']:
    for ang in [-120, -105, -90, -75, 75, 90, 105, 120]:
        e = [0, 0, 0]
        e[{'X':0, 'Y':1, 'Z':2}[axis]] = ang
        set_rot('calf_l', e)
        set_rot('foot_l', [0, 0, 0])
        bpy.context.view_layer.update()
        p_foot = get_ue_pos('foot_l')
        p_ball = get_ue_pos('ball_l')
        if p_foot.z >= 2.0 and p_ball.z >= -2.0:
            print(f'calf_l {axis}={ang:4d}: foot=({p_foot.x:.1f}, {p_foot.y:.1f}, {p_foot.z:.1f}), ball=({p_ball.x:.1f}, {p_ball.y:.1f}, {p_ball.z:.1f})')
"""

res = execute_blender(code)
print(res)
