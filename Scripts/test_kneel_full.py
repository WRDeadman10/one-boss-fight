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

# Apply corrected kneel
set_loc('pelvis', (-48.0, 4.0, 0))
set_rot('thigh_l', (45.5, 0, 15.0))
set_rot('calf_l', (0, -100.0, -80.0))
set_rot('foot_l', (0, 30.0, -50.0))

set_rot('thigh_r', (84.0, 0, -10.0))
set_rot('calf_r', (0, 95.0, -80.0))
set_rot('foot_r', (0, -60.0, -15.0))

# Arms rested
set_rot('upperarm_r', (-45.0, -15.0, 10.0))
set_rot('lowerarm_r', (-60.0, 0, 0))
set_rot('hand_r', (10.0, 0, 0))
set_rot('upperarm_l', (-35.0, 15.0, -10.0))
set_rot('lowerarm_l', (-60.0, 0, 0))
set_rot('hand_l', (15.0, 0, 0))

bpy.context.view_layer.update()

def get_ue_pos(bname):
    pb = arm.pose.bones[bname]
    v = (arm.matrix_world @ pb.matrix).to_translation()
    return Vector((v.x * 100.0, -v.y * 100.0, v.z * 100.0))

print('Kneel check in UE coordinates:')
for b in ['pelvis', 'head', 'neck_01', 'calf_l', 'foot_l', 'ball_l', 'calf_r', 'foot_r', 'ball_r']:
    p = get_ue_pos(b)
    print(f'  {b:10s} : ({p.x:.1f}, {p.y:.1f}, {p.z:.1f}) cm')
"""

res = execute_blender(code)
print(res)
