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

def get_world_pos(pb_name):
    pb = arm.pose.bones[pb_name]
    return (arm.matrix_world @ pb.matrix).to_translation()

# In rest pose:
p0 = get_world_pos("pelvis")
h0 = get_world_pos("head")
n0 = get_world_pos("neck_01")
print(f'Rest pose head - pelvis: ({h0.x - p0.x:.2f}, {h0.y - p0.y:.2f}, {h0.z - p0.z:.2f})')
print(f'Rest pose neck - pelvis: ({n0.x - p0.x:.2f}, {n0.y - p0.y:.2f}, {n0.z - p0.z:.2f})')

# Test 1: rotate around local Z
for angle_deg in [-30, 0, 30]:
    for sname in ['spine_01', 'spine_03', 'spine_05', 'neck_01', 'head']:
        arm.pose.bones[sname].rotation_quaternion = Euler((0, 0, math.radians(angle_deg / 5.0))).to_quaternion()
    bpy.context.view_layer.update()
    p = get_world_pos("pelvis")
    h = get_world_pos("head")
    n = get_world_pos("neck_01")
    print(f'Angle {angle_deg:+3d} deg around local Z: head - pelvis = ({h.x - p.x:.2f}, {h.y - p.y:.2f}, {h.z - p.z:.2f})')
"""

res = execute_blender(code)
print(res)
