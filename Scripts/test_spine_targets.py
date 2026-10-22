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

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.location = Vector(loc_cm)

def clear_pose():
    arm.location = Vector((0, 0, 0))
    arm.rotation_euler = Euler((0, 0, 0))
    for pb in arm.pose.bones:
        pb.location = Vector((0, 0, 0))
        pb.rotation_quaternion = Quaternion((1, 0, 0, 0))

def get_ue_pos(bname):
    pb = arm.pose.bones[bname]
    mw = arm.matrix_world @ pb.matrix
    loc = mw.to_translation()
    return Vector((loc.x * 100.0, -loc.y * 100.0, loc.z * 100.0))

# -------------------------------------------------------------
# Test 1: PhaseRoar peak at 0.7s (head minus pelvis Y <= -12 cm, head Z >= 150 cm)
# -------------------------------------------------------------
clear_pose()
# Roar posture: leaning back to howl
set_loc('pelvis', (-1.5, 0, 0))
set_rot('pelvis', (0, 0, -8.0))
set_rot('spine_01', (0, 0, -6.0))
set_rot('spine_03', (0, 0, -8.0))
set_rot('spine_05', (0, 0, -10.0))
set_rot('neck_01', (0, 0, -10.0))
set_rot('head', (0, 0, -15.0))
bpy.context.view_layer.update()
p_pel = get_ue_pos('pelvis')
p_head = get_ue_pos('head')
diff_roar = p_head - p_pel
print(f'Roar peak: head - pelvis = ({diff_roar.x:.1f}, {diff_roar.y:.1f}, {diff_roar.z:.1f}) cm, head Z = {p_head.z:.1f} cm')

# -------------------------------------------------------------
# Test 2: Reaction at 0.8s (head minus pelvis Y <= -15 cm, Z <= 64 cm; neck minus pelvis Y <= -8 cm)
# -------------------------------------------------------------
clear_pose()
set_loc('pelvis', (-48.0, 4.0, 0))
set_rot('thigh_l', (75, 0, 10))
set_rot('calf_l', (0, -120, -60))
set_rot('foot_l', (0, -30, -30))
set_rot('thigh_r', (85, 0, -20))
set_rot('calf_r', (0, 120, -40))
set_rot('foot_r', (0, 60, 30))

# Recoil pitch back
set_rot('pelvis', (0, 0, -6.0))
set_rot('spine_01', (0, 0, -8.0))
set_rot('spine_03', (0, 0, -10.0))
set_rot('spine_05', (0, 0, -12.0))
set_rot('neck_01', (0, 0, -12.0))
set_rot('head', (0, 0, -18.0))
bpy.context.view_layer.update()
p_pel = get_ue_pos('pelvis')
p_head = get_ue_pos('head')
p_neck = get_ue_pos('neck_01')
diff_react_h = p_head - p_pel
diff_react_n = p_neck - p_pel
print(f'Reaction impact: head - pel = ({diff_react_h.x:.1f}, {diff_react_h.y:.1f}, {diff_react_h.z:.1f}) cm, neck - pel Y = {diff_react_n.y:.1f} cm')

# -------------------------------------------------------------
# Test 3: Death slumped forward at 2.5s (head minus pelvis Y >= +30 cm, head Z <= 90 cm)
# -------------------------------------------------------------
clear_pose()
set_loc('pelvis', (-52.0, 4.0, 0)) # drop pelvis slightly more in death slump
set_rot('thigh_l', (75, 0, 10))
set_rot('calf_l', (0, -120, -60))
set_rot('foot_l', (0, -30, -30))
set_rot('thigh_r', (85, 0, -20))
set_rot('calf_r', (0, 120, -40))
set_rot('foot_r', (0, 60, 30))

# Slump forward heavily over knees (around local Z)
set_rot('pelvis', (0, 0, 15.0))
set_rot('spine_01', (0, 0, 15.0))
set_rot('spine_03', (0, 0, 18.0))
set_rot('spine_05', (0, 0, 20.0))
set_rot('neck_01', (0, 0, 15.0))
set_rot('head', (0, 0, 20.0))
bpy.context.view_layer.update()
p_pel = get_ue_pos('pelvis')
p_head = get_ue_pos('head')
diff_death = p_head - p_pel
print(f'Death slump: head - pel = ({diff_death.x:.1f}, {diff_death.y:.1f}, {diff_death.z:.1f}) cm, head Z = {p_head.z:.1f} cm')

# -------------------------------------------------------------
# Test 4: StaggerFall fold forward at 0.35s (head minus pelvis Y >= +10 cm)
# -------------------------------------------------------------
clear_pose()
set_loc('pelvis', (-24.0, 0, 0))
set_rot('pelvis', (0, 0, 8.0))
set_rot('spine_01', (0, 0, 8.0))
set_rot('spine_03', (0, 0, 10.0))
set_rot('spine_05', (0, 0, 10.0))
set_rot('neck_01', (0, 0, 6.0))
set_rot('head', (0, 0, 8.0))
bpy.context.view_layer.update()
p_pel = get_ue_pos('pelvis')
p_head = get_ue_pos('head')
diff_fall = p_head - p_pel
print(f'StaggerFall fold: head - pel = ({diff_fall.x:.1f}, {diff_fall.y:.1f}, {diff_fall.z:.1f}) cm')
"""

res = execute_blender(code)
print(res)
