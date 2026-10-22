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

best_l = None
min_err_l = 999.0

for cy in range(-130, -50, 10):
    for cz in range(-120, 120, 20):
        for fy in range(-90, 90, 20):
            for fz in range(-90, 90, 20):
                arm.pose.bones['calf_l'].rotation_quaternion = Euler((0, math.radians(cy), math.radians(cz))).to_quaternion()
                arm.pose.bones['foot_l'].rotation_quaternion = Euler((0, math.radians(fy), math.radians(fz))).to_quaternion()
                bpy.context.view_layer.update()
                
                kz = get_pos('calf_l').z
                az = get_pos('foot_l').z
                bz = get_pos('ball_l').z
                
                if 2.0 <= kz <= 6.0 and az >= 3.0 and bz >= -1.0:
                    err = abs(az - 7.5) + abs(bz - 1.5)
                    if err < min_err_l:
                        min_err_l = err
                        best_l = (cy, cz, fy, fz, kz, az, bz)

print('Best Left Leg:', best_l)
"""

res = execute_blender(code)
print(res)
