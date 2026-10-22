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

for bname in ['pelvis', 'spine_01', 'spine_03', 'spine_05', 'neck_01', 'head', 'thigh_l', 'calf_l', 'foot_l']:
    b = arm.data.bones[bname]
    print(f'Bone {bname}:')
    print(f'  head: {b.head}, tail: {b.tail}, vector: {b.vector}')
    print(f'  matrix_local:\n{b.matrix_local}')
"""

res = execute_blender(code)
print(res)
