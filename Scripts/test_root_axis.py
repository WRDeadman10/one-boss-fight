import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os
from mathutils import Vector, Euler, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
ref_path = os.path.abspath('Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx')
bpy.ops.import_scene.fbx(filepath=ref_path)

arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
pb_root = arm.pose.bones.get('root')
print('Root matrix_local:\n', arm.data.bones['root'].matrix_local)

# When root bone moves:
# What local axis moves forward in world space?
for axis in [Vector((1,0,0)), Vector((0,1,0)), Vector((0,0,1)), Vector((0,-1,0))]:
    pb_root.location = axis * 90.0 # in cm
    bpy.context.view_layer.update()
    mw = arm.matrix_world @ pb_root.matrix
    v = mw.to_translation()
    print(f'Root loc {axis * 90.0} -> world pos ({v.x:.1f}, {v.y:.1f}, {v.z:.1f})')
"""

res = execute_blender(code)
print(res)
