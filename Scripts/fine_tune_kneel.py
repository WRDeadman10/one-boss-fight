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

# Left leg fine tune
for t_x in range(65, 80, 2):
    for c_y in range(-125, -110, 3):
        for c_z in range(-65, -50, 3):
            set_rot('thigh_l', (t_x, 0, 10))
            set_rot('calf_l', (0, c_y, c_z))
            set_rot('foot_l', (0, -30, -30))
            bpy.context.view_layer.update()
            kz = get_ue_pos('calf_l').z
            az = get_ue_pos('foot_l').z
            bz = get_ue_pos('ball_l').z
            if 3.4 <= kz <= 3.8 and 6.0 <= az <= 8.5 and 0.5 <= bz <= 2.5:
                print(f'Fine Left: t_x={t_x}, c_y={c_y}, c_z={c_z} -> knee={kz:.2f}, ankle={az:.2f}, ball={bz:.2f}')
                break

# Right leg fine tune
for t_x in range(75, 90, 2):
    for c_y in range(110, 125, 3):
        for c_z in range(-50, -35, 3):
            set_rot('thigh_r', (t_x, 0, -20))
            set_rot('calf_r', (0, c_y, c_z))
            set_rot('foot_r', (0, 60, 30))
            bpy.context.view_layer.update()
            kz = get_ue_pos('calf_r').z
            az = get_ue_pos('foot_r').z
            bz = get_ue_pos('ball_r').z
            if 3.0 <= kz <= 4.0 and 6.0 <= az <= 8.5 and 0.5 <= bz <= 2.5:
                print(f'Fine Right: t_x={t_x}, c_y={c_y}, c_z={c_z} -> knee={kz:.2f}, ankle={az:.2f}, ball={bz:.2f}')
                break
"""

res = execute_blender(code)
print(res)
