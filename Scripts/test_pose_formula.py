import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os, math
from mathutils import Vector, Euler, Matrix, Quaternion

ref_path = os.path.abspath("Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=ref_path)
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
arm.data.pose_position = 'POSE'

pb_r = arm.pose.bones['hand_r']
pb_p = pb_r.parent

b = arm.data.bones['hand_r']
b_p = b.parent

# Test if formula matches Blender's pb.matrix
# rest relative transform:
M_rest_rel = b_p.matrix_local.inverted() @ b.matrix_local

pb_r.rotation_quaternion = Euler((math.radians(30), math.radians(45), math.radians(60))).to_quaternion()
bpy.context.view_layer.update()

M_actual = pb_r.matrix.copy()

M_calc = pb_p.matrix @ M_rest_rel @ Matrix.LocRotScale(pb_r.location, pb_r.rotation_quaternion, pb_r.scale)

diff = max(abs(M_actual[i][j] - M_calc[i][j]) for i in range(4) for j in range(4))
result = {"diff": diff, "match": diff < 1e-4}
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
