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
    return mw.to_translation().z * 100.0 # in cm

def get_pos(bname):
    pb = arm.pose.bones[bname]
    mw = arm.matrix_world @ pb.matrix
    v = mw.to_translation()
    return Vector((v.x * 100.0, v.y * 100.0, v.z * 100.0))

# Let's test thigh and calf rotations:
# In rest pose:
# thigh_l is at Z=93.5 cm
# calf_l is at Z=50.3 cm (knee)
# foot_l is at Z=8.2 cm (ankle)
# ball_l is at Z=1.0 cm

# If pelvis drops to Z ~ 46 cm:
# thigh_l rotates forward so knee touches floor (Z ~ 4-6 cm).
# calf_l bends backward so shin lies flat on floor (Z ~ 4-8 cm).
# foot_l extends/flexes so ankle is ~ 6-8 cm, ball is ~ 0-2 cm.

for t_rot_x in [75.0, 80.0, 85.0]:
    for c_rot_x in [-140.0, -150.0, -160.0]:
        for ft_rot_x in [30.0, 45.0, 60.0]:
            # Apply to left leg
            arm.pose.bones['pelvis'].location = Vector((-48.0 / 100.0, 0, 0)) # wait, check axis of pel_drop
            arm.pose.bones['thigh_l'].rotation_quaternion = Euler((math.radians(t_rot_x), 0, math.radians(10.0))).to_quaternion()
            arm.pose.bones['calf_l'].rotation_quaternion = Euler((math.radians(c_rot_x), 0, 0)).to_quaternion()
            arm.pose.bones['foot_l'].rotation_quaternion = Euler((math.radians(ft_rot_x), 0, 0)).to_quaternion()
            bpy.context.view_layer.update()
            
            kz = get_z('calf_l')
            az = get_z('foot_l')
            bz = get_z('ball_l')
            pz = get_z('pelvis')
            if 0.0 <= kz <= 10.0 and az >= 3.0 and bz >= -1.0:
                print(f'Match: t={t_rot_x}, c={c_rot_x}, ft={ft_rot_x} -> Pelvis Z={pz:.1f}, Knee Z={kz:.1f}, Ankle Z={az:.1f}, Ball Z={bz:.1f}')
"""

res = execute_blender(code)
print(res)
