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

def get_z(bname):
    pb = arm.pose.bones[bname]
    mw = arm.matrix_world @ pb.matrix
    return mw.to_translation().z * 100.0

# Print pelvis translation axis effect
pb_pel = arm.pose.bones['pelvis']
for axis in [Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)), Vector((-1, 0, 0)), Vector((0, -1, 0)), Vector((0, 0, -1))]:
    pb_pel.location = axis * 0.48
    bpy.context.view_layer.update()
    pz = get_z('pelvis')
    print(f'Pelvis loc {axis * 0.48} -> Z={pz:.1f}')
"""

res = execute_blender(code)
print(res)
