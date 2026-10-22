import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os

bpy.ops.wm.read_factory_settings(use_empty=True)
fbx_path = os.path.abspath('Import/Boss01/Animations/AN_Boss01_PhaseRoar.fbx')
bpy.ops.import_scene.fbx(filepath=fbx_path)
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
act = arm.animation_data.action
strip = act.layers[0].strips[0]
cb = strip.channelbags[0]

for name in ['pelvis', 'spine_01', 'spine_03', 'spine_05', 'neck_01', 'head']:
    rot_fcs = [fc for fc in cb.fcurves if fc.data_path == f'pose.bones["{name}"].rotation_quaternion']
    print(f'Bone {name}:')
    for frame in [0, 6, 21, 54]:
        rot_val = [round(fc.evaluate(frame), 4) for fc in rot_fcs]
        print(f'  f={frame}: rot={rot_val}')
"""

res = execute_blender(code)
print(res)
