import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import os
import math
from mathutils import Vector, Quaternion, Euler

anim_dir = os.path.abspath("Import/Boss01/Animations")
ref_path = os.path.abspath("Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx")

# Clean existing scene/armature data
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01

bpy.ops.import_scene.fbx(filepath=ref_path)

# Enforce FPS=30 after FBX import
scene.render.fps = 30
scene.render.fps_base = 1.0

arm = next(o for o in scene.objects if o.type == 'ARMATURE')
arm.name = "root"
arm.data.name = "root"
arm.data.pose_position = 'POSE'
bpy.context.view_layer.objects.active = arm
arm.select_set(True)

# Remove any helper meshes
for o in list(scene.objects):
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)

def set_rot(pb_name, euler_deg):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()
        pb.keyframe_insert("rotation_quaternion")

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.location = Vector(loc_cm)
        pb.keyframe_insert("location")

def clear_pose():
    arm.location = Vector((0, 0, 0))
    arm.rotation_euler = Euler((0, 0, 0))
    for pb in arm.pose.bones:
        pb.location = Vector((0, 0, 0))
        pb.rotation_quaternion = Quaternion((1, 0, 0, 0))

def export_clip(act_name, f_start, f_end, fbx_filename):
    scene.frame_start = f_start
    scene.frame_end = f_end
    
    bpy.ops.nla.bake(
        frame_start=f_start,
        frame_end=f_end,
        only_selected=False,
        visual_keying=True,
        clear_constraints=True,
        bake_types={'POSE', 'OBJECT'}
    )
    
    act = arm.animation_data.action
    act.name = act_name
    act.use_frame_range = True
    act.frame_start = float(f_start)
    act.frame_end = float(f_end)
    
    scene.render.fps = 30
    scene.render.fps_base = 1.0
    
    out_fbx = os.path.join(anim_dir, fbx_filename)
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    
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
    return out_fbx

# ===================================================================
# 1. AN_Riposte_Player_Front (1.600 s = 49 frames: 0 to 48)
# Root motion forward 90 cm: X=150.0 cm to X=60.0 cm facing -X
# Impact at 0.80 s (Frame 24)
# ===================================================================
clear_pose()
arm.animation_data_create()
act_player = bpy.data.actions.new("ACT_Riposte_Player_Front")
arm.animation_data.action = act_player

player_kf = [
    # (frame, root_x, pelvis_drop, spine_yaw, spine_pitch, r_arm_raise, r_arm_strike, l_arm_guard, step_phase)
    ( 0, 150.0,   0.0,   0.0,   0.0,  15.0,   0.0,  15.0,  0.0), # Combat ready idle at 150 cm
    ( 6, 138.0,  -4.0,  12.0,   5.0,  35.0, -10.0,  20.0,  0.3), # Drive forward, right foot steps
    (14, 102.0,  -6.0,  25.0,   8.0,  65.0, -25.0,  25.0,  0.7), # Heavy windup, left foot plants
    (20,  68.0,  -3.0,  30.0,  10.0,  85.0, -35.0,  30.0,  0.95),# Apex draw, weight shifts forward
    (24,  60.0,  -8.0,  -5.0,  25.0,  15.0,  75.0,  40.0,  1.0), # IMPACT (0.80 s): lethal thrust/chop to chest!
    (30,  60.0,  -7.5,  -4.0,  24.0,  16.0,  72.0,  38.0,  1.0), # Impact hold (embedded thrust)
    (36,  60.0,  -5.0,   2.0,  16.0,  25.0,  45.0,  30.0,  0.8), # Wrench blade free / extraction
    (42,  60.0,  -2.0,   1.0,   8.0,  20.0,  20.0,  22.0,  0.4), # Recoil back to combat stance
    (48,  60.0,   0.0,   0.0,   0.0,  15.0,   0.0,  15.0,  0.0), # Combat ready idle at 60 cm
]

for f, rx, p_drop, sp_yaw, sp_pitch, r_raise, r_strike, l_guard, step in player_kf:
    scene.frame_set(f)
    # Root motion: advance along X in world on Armature object
    arm.location = Vector((rx, 0, 0))
    arm.rotation_euler = Euler((0, 0, math.radians(180)))
    arm.keyframe_insert("location")
    arm.keyframe_insert("rotation_euler")
        
    set_loc("pelvis", (p_drop, 0, 0))
    set_rot("pelvis", (sp_pitch * 0.3, sp_yaw * 0.2, 0))
    set_rot("spine_01", (sp_pitch * 0.2, sp_yaw * 0.25, 0))
    set_rot("spine_03", (sp_pitch * 0.3, sp_yaw * 0.35, 0))
    set_rot("spine_05", (sp_pitch * 0.4, sp_yaw * 0.40, 0))
    set_rot("neck_01", (sp_pitch * 0.2, 0, 0))
    set_rot("head", (-sp_pitch * 0.3, 0, 0))
    
    # Right arm: windup -> forward lethal thrust
    set_rot("clavicle_r", (0, 0, sp_yaw * 0.2))
    set_rot("upperarm_r", (r_strike - r_raise * 0.5, -25.0 - r_raise * 0.3, 20.0))
    set_rot("lowerarm_r", (-30.0 + r_strike * 0.6, 0, 0))
    set_rot("hand_r", (15.0, 0, 0))
    
    # Left arm: balance and guide grip
    set_rot("clavicle_l", (0, 0, -sp_yaw * 0.2))
    set_rot("upperarm_l", (-15.0 - l_guard * 0.4, 20.0, -15.0))
    set_rot("lowerarm_l", (-40.0 - l_guard * 0.3, 0, 0))
    set_rot("hand_l", (10.0, 0, 0))
    
    # Leg stride and plant
    set_rot("thigh_r", (step * 25.0, 0, -5.0))
    set_rot("calf_r", (-step * 35.0, 0, 0))
    set_rot("foot_r", (step * 10.0, 0, 0))
    set_rot("thigh_l", (-step * 18.0, 0, 5.0))
    set_rot("calf_l", (-step * 10.0, 0, 0))
    set_rot("foot_l", (step * 8.0, 0, 0))

fbx_player = export_clip("ACT_Riposte_Player_Front", 0, 48, "AN_Riposte_Player_Front.fbx")

# ===================================================================
# 2. AN_Riposte_Boss_Reaction (2.000 s = 61 frames: 0 to 60)
# In place, starts in StaggerDown kneeling pose, takes hit at 0.80 s (Frame 24),
# ends in exact kneeling pose of StaggerDown Frame 0 (F60 == F0)
# ===================================================================
clear_pose()
arm.animation_data_create()
act_boss_react = bpy.data.actions.new("ACT_Riposte_Boss_Reaction")
arm.animation_data.action = act_boss_react

# Base kneeling constants (identical to AN_Boss01_StaggerDown F0 / F30)
KNEEL_PEL_LOC = (-48.0, 4.0, 0)
KNEEL_PEL_ROT = (25.0 * 0.3, 0, 0)
KNEEL_SP1_ROT = (25.0 * 0.25, 0, 0)
KNEEL_SP3_ROT = (25.0 * 0.35, 0, 0)
KNEEL_SP5_ROT = (25.0 * 0.40, 0, 0)
KNEEL_NK1_ROT = (28.0 * 0.4, 0, 0)
KNEEL_HD_ROT  = (28.0 * 0.6, 0, 0)
KNEEL_TH_R    = (84.0, 0, -10.0)
KNEEL_CF_R    = (-115.0, 0, 0)
KNEEL_FT_R    = (42.0, 0, 0)
KNEEL_TH_L    = (45.5, 0, 15.0)
KNEEL_CF_L    = (-58.5, 0, 0)
KNEEL_FT_L    = (19.5, 0, 0)
KNEEL_UA_R    = (-45.0, -15.0, 10.0)
KNEEL_LA_R    = (-60.0, 0, 0)
KNEEL_HD_R    = (10.0, 0, 0)
KNEEL_UA_L    = (-35.0, 15.0, -10.0)
KNEEL_LA_L    = (-60.0, 0, 0)
KNEEL_HD_L    = (15.0, 0, 0)

react_kf = [
    # (frame, recoil_x, recoil_y, spine_recoil, head_snap, l_arm_lift, r_brace)
    ( 0,   0.0,  0.0,   0.0,   0.0,   0.0,  0.0), # StaggerDown resting pose
    (12,  -0.5,  0.2,   1.0,   0.8,   0.5,  0.2), # Slight pre-hit breathing tremor
    (20,  -0.8,  0.4,   2.0,   1.5,   1.0,  0.4), # Imminent strike anticipation
    (24,  -8.5, -4.5, -38.0, -42.0,  55.0, 18.0), # IMPACT (0.80 s): violent chest recoil!
    (28,  -7.0, -3.8, -32.0, -38.0,  62.0, 15.0), # Maximum extension, left hand high in air
    (34,  -4.0, -1.8, -18.0, -22.0,  40.0, 10.0), # Torso begins shuddering collapse
    (42,   2.5,  2.0,  15.0,  18.0,  15.0, -5.0), # Heavy slump forward
    (52,   1.0,  0.8,   6.0,   8.0,   4.0, -2.0), # Righting posture
    (60,   0.0,  0.0,   0.0,   0.0,   0.0,  0.0), # Bitwise IDENTICAL to F0!
]

for f, rx, ry, sp_rec, h_snap, l_lift, r_br in react_kf:
    scene.frame_set(f)
    arm.location = Vector((0, 0, 0))
    arm.rotation_euler = Euler((0, 0, 0))
    arm.keyframe_insert("location")
    arm.keyframe_insert("rotation_euler")
    
    set_loc("pelvis", (KNEEL_PEL_LOC[0] + rx, KNEEL_PEL_LOC[1] + ry, 0))
    set_rot("pelvis", (KNEEL_PEL_ROT[0] + sp_rec * 0.25, 0, 0))
    set_rot("spine_01", (KNEEL_SP1_ROT[0] + sp_rec * 0.25, 0, 0))
    set_rot("spine_03", (KNEEL_SP3_ROT[0] + sp_rec * 0.35, 0, 0))
    set_rot("spine_05", (KNEEL_SP5_ROT[0] + sp_rec * 0.40, 0, 0))
    set_rot("neck_01", (KNEEL_NK1_ROT[0] + h_snap * 0.4, 0, 0))
    set_rot("head", (KNEEL_HD_ROT[0] + h_snap * 0.6, 0, 0))
    
    set_rot("thigh_r", KNEEL_TH_R)
    set_rot("calf_r", KNEEL_CF_R)
    set_rot("foot_r", KNEEL_FT_R)
    set_rot("thigh_l", KNEEL_TH_L)
    set_rot("calf_l", KNEEL_CF_L)
    set_rot("foot_l", KNEEL_FT_L)
    
    set_rot("upperarm_r", (KNEEL_UA_R[0] + r_br * 0.5, KNEEL_UA_R[1], KNEEL_UA_R[2]))
    set_rot("lowerarm_r", (KNEEL_LA_R[0] + r_br * 0.3, 0, 0))
    set_rot("hand_r", KNEEL_HD_R)
    
    set_rot("upperarm_l", (KNEEL_UA_L[0] + l_lift * 0.8, KNEEL_UA_L[1] + l_lift * 0.3, KNEEL_UA_L[2]))
    set_rot("lowerarm_l", (KNEEL_LA_L[0] + l_lift * 0.4, 0, 0))
    set_rot("hand_l", (KNEEL_HD_L[0] + l_lift * 0.2, 0, 0))

fbx_boss_react = export_clip("ACT_Riposte_Boss_Reaction", 0, 60, "AN_Riposte_Boss_Reaction.fbx")

# ===================================================================
# 3. AN_Boss01_DeathLegend (3.500 s = 106 frames: 0 to 105)
# In place, from combat idle, knees give way, drops to both knees,
# head sags, body slumps forward, held rest pose from F75 to F105
# ===================================================================
clear_pose()
arm.animation_data_create()
act_death = bpy.data.actions.new("ACT_Boss01_DeathLegend")
arm.animation_data.action = act_death

death_kf = [
    # (frame, pel_drop, pel_forward, spine_slump, head_sag, leg_collapse, arm_drop)
    (  0,   0.0,  0.0,   0.0,   0.0,   0.0,   0.0), # Combat ready idle
    ( 12,  -6.0,  1.5,  -5.0,  -8.0,  10.0,   5.0), # Stagger / knees buckle
    ( 24, -18.0,  3.0,   8.0,  12.0,  30.0,  12.0), # Losing balance, dropping
    ( 40, -36.0,  5.0,  22.0,  28.0,  70.0,  25.0), # Both knees strike the ground
    ( 60, -48.0,  6.5,  38.0,  45.0,  95.0,  40.0), # Heavy slump forward, head bows
    ( 75, -52.0,  7.0,  46.0,  55.0, 102.0,  48.0), # Full fatal rest posture achieved
    ( 90, -52.0,  7.0,  46.0,  55.0, 102.0,  48.0), # Held rest (zero movement)
    (105, -52.0,  7.0,  46.0,  55.0, 102.0,  48.0), # Held rest (zero movement)
]

for f, p_drop, p_fwd, sp_sl, h_sag, leg_col, a_drop in death_kf:
    scene.frame_set(f)
    arm.location = Vector((0, 0, 0))
    arm.rotation_euler = Euler((0, 0, 0))
    arm.keyframe_insert("location")
    arm.keyframe_insert("rotation_euler")
    
    set_loc("pelvis", (p_drop, p_fwd, 0))
    set_rot("pelvis", (sp_sl * 0.25, 0, 0))
    set_rot("spine_01", (sp_sl * 0.25, 0, 0))
    set_rot("spine_03", (sp_sl * 0.35, 0, 0))
    set_rot("spine_05", (sp_sl * 0.40, 0, 0))
    set_rot("neck_01", (h_sag * 0.4, 0, 0))
    set_rot("head", (h_sag * 0.6, 0, 0))
    
    set_rot("thigh_r", (leg_col * 0.85, 0, -8.0))
    set_rot("calf_r", (-leg_col * 1.15, 0, 0))
    set_rot("foot_r", (leg_col * 0.42, 0, 0))
    set_rot("thigh_l", (leg_col * 0.82, 0, 8.0))
    set_rot("calf_l", (-leg_col * 1.12, 0, 0))
    set_rot("foot_l", (leg_col * 0.40, 0, 0))
    
    set_rot("upperarm_r", (-20.0 - a_drop * 0.6, -10.0, 5.0))
    set_rot("lowerarm_r", (-30.0 - a_drop * 0.5, 0, 0))
    set_rot("hand_r", (10.0, 0, 0))
    set_rot("upperarm_l", (-15.0 - a_drop * 0.5, 10.0, -5.0))
    set_rot("lowerarm_l", (-25.0 - a_drop * 0.5, 0, 0))
    set_rot("hand_l", (10.0, 0, 0))

fbx_death = export_clip("ACT_Boss01_DeathLegend", 0, 105, "AN_Boss01_DeathLegend.fbx")

result = {
    "player_clip": fbx_player,
    "boss_react_clip": fbx_boss_react,
    "death_clip": fbx_death
}
"""

res = execute_blender(code)
print("Author clips response:", res)
