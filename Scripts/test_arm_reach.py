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
arm.name = 'root'
arm.data.name = 'root'

def set_rot(pb_name, euler_deg):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()

def get_ue_bone_world(bname):
    pb = arm.pose.bones[bname]
    mw = arm.matrix_world @ pb.matrix
    loc = mw.to_translation()
    return Vector((loc.x * 100.0, -loc.y * 100.0, loc.z * 100.0))

def get_ue_root():
    loc = arm.matrix_world.to_translation()
    return Vector((loc.x * 100.0, -loc.y * 100.0, loc.z * 100.0))

# Test extending right arm forward in UE +Y
for c_y in [0, 20, 40]:
    for u_x in [-110, -90, -70]:
        for u_y in [-60, -30, 0, 30]:
            for u_z in [-30, 0, 30]:
                for l_x in [-20, 0, 20]:
                    set_rot('clavicle_r', (0, c_y, 0))
                    set_rot('upperarm_r', (u_x, u_y, u_z))
                    set_rot('lowerarm_r', (l_x, 0, 0))
                    bpy.context.view_layer.update()
                    hr = get_ue_bone_world('hand_r') - get_ue_root()
                    if hr.y >= 50.0 and 110.0 <= hr.z <= 135.0:
                        print(f'Match: c_y={c_y}, u=({u_x},{u_y},{u_z}), l={l_x} -> hand_r Y={hr.y:.1f}, Z={hr.z:.1f}')
                        break
"""

res = execute_blender(code)
print(res)
