import os, sys
sys.path.insert(0, 'Scripts')
from blender_exec import execute_blender

code = """
import bpy, os, math
from mathutils import Vector, Euler

ref_path = os.path.abspath('Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
scene.render.fps_base = 1.0
bpy.ops.import_scene(filepath=ref_path) if False else None
bpy.ops.import_scene.fbx(filepath=ref_path)

arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arm.name = 'root'
arm.data.name = 'root'
arm.data.pose_position = 'POSE'

for o in list(bpy.context.scene.objects):
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.location = Vector(loc_cm)
        pb.keyframe_insert('location')

def set_rot(pb_name, euler_deg):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()
        pb.keyframe_insert('rotation_quaternion')

arm.animation_data_create()
act = bpy.data.actions.new('ACT_Death_Test')
arm.animation_data.action = act
if act.slots:
    arm.animation_data.action_slot = act.slots[0]

# Frame 0 to 105 (3.5s)
for f in range(106):
    bpy.context.scene.frame_set(f)
    t = f / 105.0
    if f < 24:
        # Start standing
        set_loc('pelvis', (0.0, 0.0, 0.0))
        set_rot('pelvis', (0.0, 0.0, 0.0))
        set_rot('thigh_l', (0.0, 0.0, 5.0))
        set_rot('calf_l', (0.0, 0.0, 0.0))
        set_rot('foot_l', (0.0, 0.0, 0.0))
        set_rot('thigh_r', (0.0, 0.0, -5.0))
        set_rot('calf_r', (0.0, 0.0, 0.0))
        set_rot('foot_r', (0.0, 0.0, 0.0))
        set_rot('upperarm_r', (-15.0, -25.0, 15.0))
        set_rot('lowerarm_r', (-25.0, 0.0, 0.0))
        set_rot('hand_r', (15.0, 0.0, 0.0))
    elif f >= 75:
        # Held slump from 2.5s to 3.5s (bitwise exact!)
        p_drop = -48.0
        set_loc('pelvis', (p_drop, 4.0, 0.0))
        sp_slump = -26.0
        set_rot('pelvis', (0.0, 0.0, sp_slump * 0.4))
        set_rot('spine_01', (0.0, 0.0, sp_slump * 0.6))
        set_rot('spine_03', (0.0, 0.0, sp_slump * 0.8))
        set_rot('spine_05', (0.0, 0.0, sp_slump * 1.0))
        set_rot('neck_01', (0.0, 0.0, sp_slump * 0.7))
        set_rot('head', (0.0, 0.0, sp_slump * 0.8))
        
        # Compensated kneel legs (thigh_r 74 instead of 85, foot_r adjusted)
        set_rot('thigh_l', (75.0, 0.0, 10.0))
        set_rot('calf_l', (0.0, -120.0, -60.0))
        set_rot('foot_l', (0.0, -25.0, -25.0))
        set_rot('thigh_r', (74.0, 0.0, -20.0))
        set_rot('calf_r', (0.0, 120.0, -40.0))
        set_rot('foot_r', (0.0, 45.0, 20.0))
        
        # Arm & hand holding sword resting on floor (hand_r X = -30.0)
        set_rot('upperarm_r', (-20.0, -10.0, -15.0))
        set_rot('lowerarm_r', (-30.0, 0.0, 0.0))
        set_rot('hand_r', (-30.0, 0.0, 0.0))
        set_rot('upperarm_l', (-20.0, 10.0, 15.0))
        set_rot('lowerarm_l', (-30.0, 0.0, 0.0))
        set_rot('hand_l', (20.0, 0.0, 0.0))
    else:
        # Transition 0.8s to 2.5s (f=24..75)
        u = (f - 24.0) / 51.0
        p_drop = -48.0 * (u ** 1.5)
        set_loc('pelvis', (p_drop, 4.0 * u, 0.0))
        sp_slump = -26.0 * (u ** 2.0)
        set_rot('pelvis', (0.0, 0.0, sp_slump * 0.4))
        set_rot('spine_01', (0.0, 0.0, sp_slump * 0.6))
        set_rot('spine_03', (0.0, 0.0, sp_slump * 0.8))
        set_rot('spine_05', (0.0, 0.0, sp_slump * 1.0))
        set_rot('neck_01', (0.0, 0.0, sp_slump * 0.7))
        set_rot('head', (0.0, 0.0, sp_slump * 0.8))
        
        set_rot('thigh_l', (75.0 * u, 0.0, 5.0 + 5.0 * u))
        set_rot('calf_l', (0.0, -120.0 * u, -60.0 * u))
        set_rot('foot_l', (0.0, -25.0 * u, -25.0 * u))
        set_rot('thigh_r', (74.0 * u, 0.0, -5.0 - 15.0 * u))
        set_rot('calf_r', (0.0, 120.0 * u, -40.0 * u))
        set_rot('foot_r', (0.0, 45.0 * u, 20.0 * u))
        
        set_rot('upperarm_r', (-15.0 - 5.0 * u, -25.0 + 15.0 * u, 15.0 - 30.0 * u))
        set_rot('lowerarm_r', (-25.0 - 5.0 * u, 0.0, 0.0))
        set_rot('hand_r', (15.0 - 45.0 * u, 0.0, 0.0))
        set_rot('upperarm_l', (-15.0 - 5.0 * u, 20.0 - 10.0 * u, -15.0 + 30.0 * u))
        set_rot('lowerarm_l', (-35.0 + 5.0 * u, 0.0, 0.0))
        set_rot('hand_l', (20.0, -15.0 + 15.0 * u, 0.0))

out_fbx = os.path.abspath('Import/Boss01/Animations/AN_Boss01_DeathLegend.fbx')
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
)
print('Exported test DeathLegend.fbx')
"""
res = execute_blender(code)
print(res['result'])
