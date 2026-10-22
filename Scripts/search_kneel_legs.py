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

for o in list(bpy.context.scene.objects):
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)

scene = bpy.context.scene
scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01

def set_rot(pb_name, euler_deg):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.location = Vector(loc_cm)

set_loc('pelvis', (-48.0, 4.0, 0))

def get_ue_pos(bname):
    pb = arm.pose.bones[bname]
    mw = arm.matrix_world @ pb.matrix
    loc = mw.to_translation()
    return Vector((loc.x * 100.0, -loc.y * 100.0, loc.z * 100.0))

# Left Leg: search over thigh_l, calf_l, foot_l
print('SEARCHING LEFT LEG:')
found_l = []
for t_x in [30, 45, 60, 75]:
    for t_z in [0, 10, 20]:
        for c_y in [-120, -100, -80, -60]:
            for c_z in [-100, -80, -60, -40]:
                for f_y in [-60, -30, 0, 30, 60]:
                    for f_z in [-60, -30, 0, 30, 60]:
                        set_rot('thigh_l', (t_x, 0, t_z))
                        set_rot('calf_l', (0, c_y, c_z))
                        set_rot('foot_l', (0, f_y, f_z))
                        bpy.context.view_layer.update()
                        
                        kz = get_ue_pos('calf_l').z
                        az = get_ue_pos('foot_l').z
                        bz = get_ue_pos('ball_l').z
                        
                        if 2.5 <= kz <= 5.0 and 5.0 <= az <= 10.0 and 0.0 <= bz <= 5.0:
                            err = abs(kz - 3.6) + abs(az - 7.5) + abs(bz - 1.5)
                            found_l.append((err, (t_x, t_z, c_y, c_z, f_y, f_z), kz, az, bz))

found_l.sort()
for err, params, kz, az, bz in found_l[:5]:
    print(f'L: params={params} -> knee={kz:.1f}, ankle={az:.1f}, ball={bz:.1f}')

# Right Leg: search over thigh_r, calf_r, foot_r
print('SEARCHING RIGHT LEG:')
found_r = []
for t_x in [45, 60, 75, 85]:
    for t_z in [-20, -10, 0]:
        for c_y in [60, 80, 100, 120]:
            for c_z in [-100, -80, -60, -40]:
                for f_y in [-60, -30, 0, 30, 60]:
                    for f_z in [-60, -30, 0, 30, 60]:
                        set_rot('thigh_r', (t_x, 0, t_z))
                        set_rot('calf_r', (0, c_y, c_z))
                        set_rot('foot_r', (0, f_y, f_z))
                        bpy.context.view_layer.update()
                        
                        kz = get_ue_pos('calf_r').z
                        az = get_ue_pos('foot_r').z
                        bz = get_ue_pos('ball_r').z
                        
                        if 2.5 <= kz <= 5.0 and 5.0 <= az <= 10.0 and 0.0 <= bz <= 5.0:
                            err = abs(kz - 3.6) + abs(az - 7.5) + abs(bz - 1.5)
                            found_r.append((err, (t_x, t_z, c_y, c_z, f_y, f_z), kz, az, bz))

found_r.sort()
for err, params, kz, az, bz in found_r[:5]:
    print(f'R: params={params} -> knee={kz:.1f}, ankle={az:.1f}, ball={bz:.1f}')
"""

res = execute_blender(code)
print(res)
