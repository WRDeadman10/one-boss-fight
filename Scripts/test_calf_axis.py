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

# Check calf_l rotation axis
for axis in ['X', 'Y', 'Z']:
    for angle in [-90, -45, 45, 90]:
        e = [0, 0, 0]
        idx = {'X':0, 'Y':1, 'Z':2}[axis]
        e[idx] = math.radians(angle)
        arm.pose.bones['calf_l'].rotation_quaternion = Euler(e).to_quaternion()
        bpy.context.view_layer.update()
        fz = get_pos('foot_l').z
        print(f'calf_l rot {axis}={angle:3d} -> foot_l Z={fz:.1f}')
"""

res = execute_blender(code)
print(res)
