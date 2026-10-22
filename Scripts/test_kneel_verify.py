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
arm.data.pose_position = 'POSE'

for o in list(bpy.context.scene.objects):
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)

scene = bpy.context.scene
scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01

arm.animation_data_create()
act = bpy.data.actions.new('TestKneel')
arm.animation_data.action = act
if act.slots:
    arm.animation_data.action_slot = act.slots[0]

def set_rot(pb_name, euler_deg):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()
        pb.keyframe_insert('rotation_quaternion')

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.location = Vector(loc_cm)
        pb.keyframe_insert('location')

# Setup corrected kneel pose on frame 0
scene.frame_set(0)
set_loc('pelvis', (-48.0, 4.0, 0))
set_rot('pelvis', (25.0 * 0.3, 0, 0))

# Corrected Kneel Legs:
set_rot('thigh_l', (45.5, 0, 15.0))
set_rot('calf_l', (0, -100.0, -80.0))
set_rot('foot_l', (0, 30.0, -50.0))

set_rot('thigh_r', (84.0, 0, -10.0))
set_rot('calf_r', (0, 95.0, -80.0))
set_rot('foot_r', (0, -60.0, -15.0))

# Arms:
set_rot('upperarm_r', (-45.0, -15.0, 10.0))
set_rot('lowerarm_r', (-60.0, 0, 0))
set_rot('hand_r', (10.0, 0, 0))
set_rot('upperarm_l', (-35.0, 15.0, -10.0))
set_rot('lowerarm_l', (-60.0, 0, 0))
set_rot('hand_l', (15.0, 0, 0))

# Export to temp FBX
out_fbx = os.path.abspath('Import/Boss01/Animations/test_kneel_export.fbx')
bpy.ops.export_scene.fbx(
    filepath=out_fbx,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',
    axis_forward='-Z',
    axis_up='Y',
    object_types={'ARMATURE'},
    add_leaf_bones=False,
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_actions=False,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=0.0
)

# Now read back in a clean scene and measure exactly as review_report11 does
s2 = bpy.data.scenes.new('CleanAudit')
bpy.context.window.scene = s2
bpy.ops.import_scene.fbx(filepath=out_fbx)
arm2 = next(o for o in s2.objects if o.type == 'ARMATURE')
act2 = arm2.animation_data.action
if act2.slots:
    arm2.animation_data.action_slot = act2.slots[0]
s2.frame_set(0)
bpy.context.view_layer.update()

def ue_pos(b):
    pb = arm2.pose.bones[b]
    mw = arm2.matrix_world @ pb.matrix
    loc = mw.to_translation()
    return (round(loc.x if arm2.scale.x > 0.5 else loc.x * 100.0, 1),
            round(-loc.y if arm2.scale.x > 0.5 else -loc.y * 100.0, 1),
            round(loc.z if arm2.scale.x > 0.5 else loc.z * 100.0, 1))

print('CLEAN READ-BACK OF KNEEL:')
for b in ['pelvis', 'thigh_l', 'calf_l', 'foot_l', 'ball_l', 'thigh_r', 'calf_r', 'foot_r', 'ball_r']:
    print(f'  {b:10s}: {ue_pos(b)}')
"""

res = execute_blender(code)
print(res)
