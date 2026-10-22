import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os
from mathutils import Vector, Euler, Matrix

ref_path = os.path.abspath("Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=ref_path)
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')

bones = ['clavicle_r', 'upperarm_r', 'lowerarm_r', 'hand_r', 'clavicle_l', 'upperarm_l', 'lowerarm_l', 'hand_l']
data = {}
for bname in bones:
    b = arm.data.bones[bname]
    data[bname] = {
        "head": [round(x*100, 2) for x in b.head_local],
        "tail": [round(x*100, 2) for x in b.tail_local],
        "length": round(b.length * 100, 2)
    }

result = data
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
