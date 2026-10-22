import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os, math
from mathutils import Vector, Euler, Matrix, Quaternion

bpy.ops.wm.read_factory_settings(use_empty=True)
fbx_path = os.path.abspath('Import/Boss01/Animations/AN_Boss01_StaggerDown.fbx')
bpy.ops.import_scene.fbx(filepath=fbx_path)

arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
scene = bpy.context.scene
scene.frame_set(0)
act = arm.animation_data.action
if act and act.slots:
    arm.animation_data.action_slot = act.slots[0]
bpy.context.view_layer.update()

def get_pos(bname):
    pb = arm.pose.bones[bname]
    v = (arm.matrix_world @ pb.matrix).to_translation()
    return Vector((v.x * 100.0, v.y * 100.0, v.z * 100.0))

print('Current calf_l:', get_pos('calf_l'))
print('Current foot_l:', get_pos('foot_l'))
print('Current ball_l:', get_pos('ball_l'))

# Sweep calf_l rotation
for c_rot in [-90, -110, -120, -130, -140, -150]:
    for ft_rot in [-30, 0, 30, 45, 60, 90]:
        arm.pose.bones['calf_l'].rotation_quaternion = Euler((math.radians(c_rot), 0, 0)).to_quaternion()
        arm.pose.bones['foot_l'].rotation_quaternion = Euler((math.radians(ft_rot), 0, 0)).to_quaternion()
        bpy.context.view_layer.update()
        kz = get_pos('calf_l').z
        az = get_pos('foot_l').z
        bz = get_pos('ball_l').z
        if az >= 3.0 and bz >= -1.0:
            print(f'calf={c_rot:4d}, foot={ft_rot:3d} -> Knee Z={kz:.1f}, Ankle Z={az:.1f}, Ball Z={bz:.1f}')
"""

res = execute_blender(code)
print(res)
