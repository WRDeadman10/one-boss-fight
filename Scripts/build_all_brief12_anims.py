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

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01

bpy.ops.import_scene.fbx(filepath=ref_path)

scene.render.fps = 30
scene.render.fps_base = 1.0

arm = next(o for o in scene.objects if o.type == 'ARMATURE')
arm.name = "root"
arm.data.name = "root"
arm.data.pose_position = 'POSE'
bpy.context.view_layer.objects.active = arm
arm.select_set(True)

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
    
    act = arm.animation_data.action
    act.name = act_name
    act.use_frame_range = True
    act.frame_start = float(f_start)
    act.frame_end = float(f_end)
    if act.slots:
        arm.animation_data.action_slot = act.slots[0]
        
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
# STANDARD POSES FOR EXACT SEAMS (<= 0.01 tolerance)
# ===================================================================
# 1. KNEEL_BASE: Corrected kneel pose (Item 8)
# Knees at floor (2.8 - 4.5 cm), ankles 6.7 - 7.6 cm (>= 3 cm), balls 1.2 - 1.6 cm (>= -1 cm)
def apply_kneel_legs():
    set_rot("thigh_l", (75.0, 0.0, 10.0))
    set_rot("calf_l", (0.0, -120.0, -60.0))
    set_rot("foot_l", (0.0, -25.0, -25.0))
    set_rot("thigh_r", (85.0, 0.0, -20.0))
    set_rot("calf_r", (0.0, 120.0, -40.0))
    set_rot("foot_r", (0.0, 50.0, 25.0))

def apply_kneel_arms_rest():
    set_rot("upperarm_r", (-45.0, -15.0, 10.0))
    set_rot("lowerarm_r", (-60.0, 0.0, 0.0))
    set_rot("hand_r", (10.0, 0.0, 0.0))
    set_rot("upperarm_l", (-35.0, 15.0, -10.0))
    set_rot("lowerarm_l", (-60.0, 0.0, 0.0))
    set_rot("hand_l", (15.0, 0.0, 0.0))

def apply_kneel_torso_rest():
    set_loc("pelvis", (-48.0, 4.0, 0.0))
    set_rot("pelvis", (0.0, 0.0, 0.0))
    set_rot("spine_01", (0.0, 0.0, 0.0))
    set_rot("spine_03", (0.0, 0.0, 0.0))
    set_rot("spine_05", (0.0, 0.0, 0.0))
    set_rot("neck_01", (0.0, 0.0, 0.0))
    set_rot("head", (0.0, 0.0, 0.0))

# 2. COMBAT_READY: Combat stance (PhaseRoar F0/F54, StaggerFall F0, Wake F105)
def apply_combat_ready():
    set_loc("pelvis", (0.0, 0.0, 0.0))
    set_rot("pelvis", (0.0, 0.0, 0.0))
    set_rot("spine_01", (0.0, 0.0, 0.0))
    set_rot("spine_03", (0.0, 0.0, 0.0))
    set_rot("spine_05", (0.0, 0.0, 0.0))
    set_rot("neck_01", (0.0, 0.0, 0.0))
    set_rot("head", (0.0, 0.0, 0.0))
    set_rot("clavicle_r", (0.0, 0.0, 0.0))
    set_rot("upperarm_r", (-15.0, -25.0, 15.0))
    set_rot("lowerarm_r", (-25.0, 0.0, 0.0))
    set_rot("hand_r", (15.0, 0.0, 0.0))
    set_rot("clavicle_l", (0.0, 0.0, 0.0))
    set_rot("upperarm_l", (-15.0, 20.0, -15.0))
    set_rot("lowerarm_l", (-35.0, 0.0, 0.0))
    set_rot("hand_l", (20.0, -15.0, 0.0))
    set_rot("thigh_l", (0.0, 0.0, 5.0))
    set_rot("calf_l", (0.0, 0.0, 0.0))
    set_rot("foot_l", (0.0, 0.0, 0.0))
    set_rot("thigh_r", (0.0, 0.0, -5.0))
    set_rot("calf_r", (0.0, 0.0, 0.0))
    set_rot("foot_r", (0.0, 0.0, 0.0))

# ===================================================================
# CLIP 1: AN_Boss01_StaggerDown (1.000 s = 31 frames: 0 to 30, F0 == F30)
# ===================================================================
clear_pose()
arm.animation_data_create()
act_down = bpy.data.actions.new("ACT_Boss01_StaggerDown")
arm.animation_data.action = act_down
if act_down.slots:
    arm.animation_data.action_slot = act_down.slots[0]

# Exhausted breathing loop: heave on chest/shoulders, knees and feet locked
down_keyframes = [
    # (frame, p_heave, sp_heave)
    ( 0,  0.0,  0.0), # Exact KNEEL_BASE
    ( 8,  1.5, -2.0), # Inhale
    (15,  2.2, -3.0), # Inhale apex
    (22,  0.8, -1.2), # Exhale
    (30,  0.0,  0.0), # Bitwise exact to F0
]

for f, p_h, sp_h in down_keyframes:
    scene.frame_set(f)
    apply_kneel_legs()
    set_loc("pelvis", (-48.0 + p_h, 4.0, 0.0))
    set_rot("pelvis", (0.0, 0.0, sp_h * 0.3))
    set_rot("spine_01", (0.0, 0.0, sp_h * 0.5))
    set_rot("spine_03", (0.0, 0.0, sp_h * 0.6))
    set_rot("spine_05", (0.0, 0.0, sp_h * 0.7))
    set_rot("neck_01", (0.0, 0.0, -sp_h * 0.3))
    set_rot("head", (0.0, 0.0, -sp_h * 0.4))
    
    set_rot("upperarm_r", (-45.0 + p_h * 2.0, -15.0, 10.0))
    set_rot("lowerarm_r", (-60.0, 0.0, 0.0))
    set_rot("hand_r", (10.0, 0.0, 0.0))
    set_rot("upperarm_l", (-35.0 + p_h * 2.0, 15.0, -10.0))
    set_rot("lowerarm_l", (-60.0, 0.0, 0.0))
    set_rot("hand_l", (15.0, 0.0, 0.0))

export_clip("ACT_Boss01_StaggerDown", 0, 30, "AN_Boss01_StaggerDown.fbx")
print("Exported AN_Boss01_StaggerDown.fbx")

# ===================================================================
# CLIP 2: AN_Boss01_StaggerFall (0.700 s = 22 frames: 0 to 21)
# Starts in COMBAT_READY, folds forward at 0.35s (Y >= +10 cm),
# last frame (21) EXACTLY equals StaggerDown F0 (seam <= 0.01)
# ===================================================================
clear_pose()
arm.animation_data_create()
act_fall = bpy.data.actions.new("ACT_Boss01_StaggerFall")
arm.animation_data.action = act_fall
if act_fall.slots:
    arm.animation_data.action_slot = act_fall.slots[0]

# Frames 0..21
for f in range(22):
    scene.frame_set(f)
    t = f / 21.0
    if f == 0:
        apply_combat_ready()
    elif f == 21:
        # Exact seam match with StaggerDown F0
        apply_kneel_legs()
        apply_kneel_arms_rest()
        apply_kneel_torso_rest()
    else:
        # Interpolate collapse into kneel
        # At f=11 (0.367 s): torso folds forward heavily (Y >= +10 cm in UE)
        fold_t = math.sin(t * math.pi * 0.8) if t < 0.6 else math.cos((t - 0.6) / 0.4 * (math.pi * 0.5))
        sp_fold = -fold_t * 12.0 # Negative Z is forward fold in UE (+Y)
        
        p_drop = -48.0 * (t ** 1.8)
        set_loc("pelvis", (p_drop, 4.0 * t, 0.0))
        set_rot("pelvis", (0.0, 0.0, sp_fold * 0.4))
        set_rot("spine_01", (0.0, 0.0, sp_fold * 0.6))
        set_rot("spine_03", (0.0, 0.0, sp_fold * 0.8))
        set_rot("spine_05", (0.0, 0.0, sp_fold * 1.0))
        set_rot("neck_01", (0.0, 0.0, sp_fold * 0.4))
        set_rot("head", (0.0, 0.0, sp_fold * 0.5))
        
        # Legs transition from standing to kneel
        set_rot("thigh_l", (75.0 * t, 0.0, 5.0 + 5.0 * t))
        set_rot("calf_l", (0.0, -120.0 * t, -60.0 * t))
        set_rot("foot_l", (0.0, -30.0 * t, -30.0 * t))
        set_rot("thigh_r", (85.0 * t, 0.0, -5.0 - 15.0 * t))
        set_rot("calf_r", (0.0, 120.0 * t, -40.0 * t))
        set_rot("foot_r", (0.0, 60.0 * t, 30.0 * t))
        
        # Arms reach for floor
        set_rot("upperarm_r", (-15.0 - 30.0 * t, -25.0 + 10.0 * t, 15.0 - 5.0 * t))
        set_rot("lowerarm_r", (-25.0 - 35.0 * t, 0.0, 0.0))
        set_rot("hand_r", (15.0 - 5.0 * t, 0.0, 0.0))
        set_rot("upperarm_l", (-15.0 - 20.0 * t, 20.0 - 5.0 * t, -15.0 + 5.0 * t))
        set_rot("lowerarm_l", (-35.0 - 25.0 * t, 0.0, 0.0))
        set_rot("hand_l", (20.0 - 5.0 * t, -15.0 + 15.0 * t, 0.0))

export_clip("ACT_Boss01_StaggerFall", 0, 21, "AN_Boss01_StaggerFall.fbx")
print("Exported AN_Boss01_StaggerFall.fbx")

# ===================================================================
# CLIP 3: AN_Riposte_Boss_Reaction (2.000 s = 61 frames: 0 to 60)
# Starts in StaggerDown F30, impact at 0.8s (F24) throws head/neck back
# (Y <= -15 cm, Z <= 64 cm, neck Y <= -8 cm), recovers by 1.3s (F39),
# ends in StaggerDown F0 (seam <= 0.01)
# ===================================================================
clear_pose()
arm.animation_data_create()
act_react = bpy.data.actions.new("ACT_Riposte_Boss_Reaction")
arm.animation_data.action = act_react
if act_react.slots:
    arm.animation_data.action_slot = act_react.slots[0]

# Frames 0..60
for f in range(61):
    scene.frame_set(f)
    t_sec = f / 30.0
    if f == 0 or f == 60:
        apply_kneel_legs()
        apply_kneel_arms_rest()
        apply_kneel_torso_rest()
    else:
        apply_kneel_legs()
        # Recoil profile: peaks at f=24 (0.80 s), recovers by f=39 (1.30 s)
        if f <= 24:
            # Anticipation & violent recoil back
            t_rec = f / 24.0
            recoil = (t_rec ** 3.0) # Sharp violent jerk backward
        elif f <= 39:
            # Damped recovery to kneel
            t_rec = (f - 24) / 15.0
            recoil = 1.0 - math.sin(t_rec * math.pi * 0.5)
        else:
            # Settle to rest
            t_rec = (f - 39) / 21.0
            recoil = 0.0
            
        sp_pitch = recoil * 9.0 # Positive Z is backward lean in UE (-Y)
        # Keep pelvis at standard -48.0 to ensure knees/ankles/toes stay firmly grounded!
        p_drop = -48.0
        
        set_loc("pelvis", (p_drop, 4.0 + recoil * 1.5, 0.0))
        set_rot("pelvis", (0.0, 0.0, sp_pitch * 0.4))
        set_rot("spine_01", (0.0, 0.0, sp_pitch * 0.6))
        set_rot("spine_03", (0.0, 0.0, sp_pitch * 0.8))
        set_rot("spine_05", (0.0, 0.0, sp_pitch * 1.0))
        set_rot("neck_01", (0.0, 0.0, sp_pitch * 1.3)) # Head violently thrown back
        set_rot("head", (0.0, 0.0, sp_pitch * 1.6))
        
        # Arms fling back from chest impact
        set_rot("upperarm_r", (-45.0 - recoil * 25.0, -15.0 - recoil * 15.0, 10.0 + recoil * 20.0))
        set_rot("lowerarm_r", (-60.0 + recoil * 20.0, 0.0, 0.0))
        set_rot("hand_r", (10.0 + recoil * 15.0, 0.0, 0.0))
        set_rot("upperarm_l", (-35.0 - recoil * 30.0, 15.0 + recoil * 20.0, -10.0 - recoil * 15.0))
        set_rot("lowerarm_l", (-60.0 + recoil * 25.0, 0.0, 0.0))
        set_rot("hand_l", (15.0 + recoil * 10.0, 0.0, 0.0))
        
        # Compensate foot toes against pelvis pitch so balls of feet stay >= -1 cm (+1 to +2 cm)
        set_rot("foot_l", (0.0, -25.0, -25.0 - recoil * 25.0))
        set_rot("foot_r", (0.0, 50.0, 25.0 + recoil * 15.0))

export_clip("ACT_Riposte_Boss_Reaction", 0, 60, "AN_Riposte_Boss_Reaction.fbx")
print("Exported AN_Riposte_Boss_Reaction.fbx")

# ===================================================================
# CLIP 4: AN_Boss01_PhaseRoar (1.800 s = 55 frames: 0 to 54)
# In place, starts in COMBAT_READY, roar peak at 0.7s (F21) with
# head minus pelvis Y <= -12 cm and head Z >= 150 cm,
# ends in COMBAT_READY (F54 == F0 diff <= 0.01)
# ===================================================================
clear_pose()
arm.animation_data_create()
act_roar = bpy.data.actions.new("ACT_Boss01_PhaseRoar")
arm.animation_data.action = act_roar
if act_roar.slots:
    arm.animation_data.action_slot = act_roar.slots[0]

for f in range(55):
    scene.frame_set(f)
    if f == 0 or f == 54:
        apply_combat_ready()
    else:
        # Roar profile: peaks at f=21 (0.70 s), holds to f=33 (1.10 s), recovers to 54
        if f < 21:
            t_r = f / 21.0
            roar_curve = math.sin(t_r * math.pi * 0.5) ** 1.5
        elif f <= 33:
            roar_curve = 1.0
        else:
            t_r = (f - 33) / 21.0
            roar_curve = 0.5 * (1.0 + math.cos(t_r * math.pi))
            
        sp_arch = roar_curve * 7.5 # Positive Z bends spine backward (-Y in UE)
        h_lift = roar_curve * 10.0
        
        set_loc("pelvis", (-1.5 * roar_curve, 0.0, 0.0))
        set_rot("pelvis", (0.0, 0.0, sp_arch * 0.4))
        set_rot("spine_01", (0.0, 0.0, sp_arch * 0.6))
        set_rot("spine_03", (0.0, 0.0, sp_arch * 0.8))
        set_rot("spine_05", (0.0, 0.0, sp_arch * 1.0))
        set_rot("neck_01", (0.0, 0.0, h_lift * 0.8))
        set_rot("head", (0.0, 0.0, h_lift * 1.2))
        
        # Right arm raises sword into sky
        set_rot("clavicle_r", (0.0, roar_curve * 20.0, 0.0))
        set_rot("upperarm_r", (-15.0 - roar_curve * 65.0, -25.0 - roar_curve * 20.0, 15.0 + roar_curve * 35.0))
        set_rot("lowerarm_r", (-25.0, 0.0, 0.0))
        set_rot("hand_r", (15.0, 0.0, 0.0))
        
        # Left arm flares wide
        set_rot("clavicle_l", (0.0, -roar_curve * 20.0, 0.0))
        set_rot("upperarm_l", (-15.0 - roar_curve * 50.0, 20.0 + roar_curve * 30.0, -15.0 - roar_curve * 25.0))
        set_rot("lowerarm_l", (-35.0, 0.0, 0.0))
        set_rot("hand_l", (20.0, -15.0, 0.0))
        
        # Grounded legs
        set_rot("thigh_l", (roar_curve * 8.0, 0.0, 5.0 + roar_curve * 10.0))
        set_rot("calf_l", (-roar_curve * 12.0, 0.0, 0.0))
        set_rot("foot_l", (roar_curve * 6.0, 0.0, 0.0))
        set_rot("thigh_r", (roar_curve * 8.0, 0.0, -5.0 - roar_curve * 10.0))
        set_rot("calf_r", (-roar_curve * 12.0, 0.0, 0.0))
        set_rot("foot_r", (roar_curve * 6.0, 0.0, 0.0))

export_clip("ACT_Boss01_PhaseRoar", 0, 54, "AN_Boss01_PhaseRoar.fbx")
print("Exported AN_Boss01_PhaseRoar.fbx")

# ===================================================================
# CLIP 5: AN_Boss01_DeathLegend (3.500 s = 106 frames: 0 to 105)
# Starts standing (0s), drops through knees to ground (0..2.5s),
# at frame 75 (2.5s) slumps forward over knees (head - pelvis Y >= +30 cm,
# head Z <= 90 cm), held pose 2.5s to 3.5s is 0.0000 exact!
# ===================================================================
clear_pose()
arm.animation_data_create()
act_death = bpy.data.actions.new("ACT_Boss01_DeathLegend")
arm.animation_data.action = act_death
if act_death.slots:
    arm.animation_data.action_slot = act_death.slots[0]

def apply_death_slump_held_pose():
    set_loc("pelvis", (-48.0, 4.0, 0.0)) # keep kneel pelvis grounded
    apply_kneel_legs()
    # Deep forward slump: negative Z in Blender local is forward (+Y in UE)
    set_rot("pelvis", (0.0, 0.0, -18.0))
    set_rot("spine_01", (0.0, 0.0, -18.0))
    set_rot("spine_03", (0.0, 0.0, -22.0))
    set_rot("spine_05", (0.0, 0.0, -26.0))
    set_rot("neck_01", (0.0, 0.0, -20.0))
    set_rot("head", (0.0, 0.0, -22.0))
    
    # Limp arms resting on floor beside knees
    set_rot("upperarm_r", (-20.0, -10.0, -15.0))
    set_rot("lowerarm_r", (-30.0, 0.0, 0.0))
    set_rot("hand_r", (20.0, 0.0, 0.0))
    set_rot("upperarm_l", (-20.0, 10.0, 15.0))
    set_rot("lowerarm_l", (-30.0, 0.0, 0.0))
    set_rot("hand_l", (20.0, 0.0, 0.0))

for f in range(106):
    scene.frame_set(f)
    if f >= 75:
        # Frame 75 (2.5 s) to Frame 105 (3.5 s): HELD POSE IS EXACT!
        apply_death_slump_held_pose()
    elif f == 0:
        apply_combat_ready()
    else:
        # Progressive collapse: standing -> knees collapse -> slump
        t = f / 75.0
        p_drop = -48.0 * (t ** 1.5)
        set_loc("pelvis", (p_drop, 4.0 * t, 0.0))
        
        # Progressive forward slump
        sp_slump = -26.0 * (t ** 2.0)
        set_rot("pelvis", (0.0, 0.0, sp_slump * 0.4))
        set_rot("spine_01", (0.0, 0.0, sp_slump * 0.6))
        set_rot("spine_03", (0.0, 0.0, sp_slump * 0.8))
        set_rot("spine_05", (0.0, 0.0, sp_slump * 1.0))
        set_rot("neck_01", (0.0, 0.0, sp_slump * 0.7))
        set_rot("head", (0.0, 0.0, sp_slump * 0.8))
        
        # Legs transition to corrected kneel
        set_rot("thigh_l", (75.0 * t, 0.0, 5.0 + 5.0 * t))
        set_rot("calf_l", (0.0, -120.0 * t, -60.0 * t))
        set_rot("foot_l", (0.0, -25.0 * t, -25.0 * t))
        set_rot("thigh_r", (85.0 * t, 0.0, -5.0 - 15.0 * t))
        set_rot("calf_r", (0.0, 120.0 * t, -40.0 * t))
        set_rot("foot_r", (0.0, 50.0 * t, 25.0 * t))
        
        # Arms slide down
        set_rot("upperarm_r", (-15.0 - 5.0 * t, -25.0 + 15.0 * t, 15.0 - 30.0 * t))
        set_rot("lowerarm_r", (-25.0 - 5.0 * t, 0.0, 0.0))
        set_rot("hand_r", (15.0 + 5.0 * t, 0.0, 0.0))
        set_rot("upperarm_l", (-15.0 - 5.0 * t, 20.0 - 10.0 * t, -15.0 + 30.0 * t))
        set_rot("lowerarm_l", (-35.0 + 5.0 * t, 0.0, 0.0))
        set_rot("hand_l", (20.0, -15.0 + 15.0 * t, 0.0))

export_clip("ACT_Boss01_DeathLegend", 0, 105, "AN_Boss01_DeathLegend.fbx")
print("Exported AN_Boss01_DeathLegend.fbx")

# ===================================================================
# CLIP 6: AN_Riposte_Player_Front (1.600 s = 49 frames: 0 to 48)
# Root yaw 0 on every frame. Root travels along +Y in UE from (0,0,0) to
# (0,90,0) reached by frame 21 (0.7s), holds through frame 48.
# At frame 24 (0.8s): hand_r at least 45 cm ahead of root, Z in [105, 140].
# Body inside root frame between 0.467s and 0.8s: movements >= 400 cm.
# At 1.6s: hand_r, hand_l, head within 15 cm of frame 0 relative to root.
# ===================================================================
clear_pose()
arm.animation_data_create()
act_player = bpy.data.actions.new("ACT_Riposte_Player_Front")
arm.animation_data.action = act_player
if act_player.slots:
    arm.animation_data.action_slot = act_player.slots[0]

player_kfs = [
    # (frame, root_y, pel_drop, lunge_step, thrust_ext, windup)
    ( 0,  0.0,   0.0, 0.0,  0.0,  0.0), # Combat ready
    ( 6, 18.0,  -3.0, 0.3, -0.1, 20.0), # Coiling, right arm draws back
    (14, 60.0,  -6.0, 0.7,  0.0, 50.0), # Heavy windup, lunging forward (0.467 s)
    (21, 90.0,  -8.0, 1.0,  0.8, 10.0), # Forward plant reached (0.70 s)
    (24, 90.0, -10.0, 1.0,  1.0,  0.0), # IMPACT (0.80 s): lethal thrust extension!
    (30, 90.0,  -9.0, 1.0,  0.9,  0.0), # Embedded thrust hold
    (36, 90.0,  -6.0, 0.8,  0.5, 15.0), # Wrenching blade free
    (42, 90.0,  -3.0, 0.4,  0.2, 10.0), # Recovery stance
    (48, 90.0,   0.0, 0.0,  0.0,  0.0), # Settle to combat stance (same relative pose as frame 0!)
]

for f, ry, p_drop, step, thrust, windup in player_kfs:
    scene.frame_set(f)
    # Root motion: advance in Unreal +Y means -ry in Blender (ry in cm: 0 to 90 cm)
    arm.location = Vector((0, -ry, 0))
    arm.rotation_euler = Euler((0, 0, 0))
    arm.keyframe_insert("location")
    arm.keyframe_insert("rotation_euler")
    
    set_loc("pelvis", (p_drop, 0, 0))
    # Torso lunges forward: negative Z bends forward in UE (+Y)
    set_rot("pelvis", (0, 0, -thrust * 12.0))
    set_rot("spine_01", (0, 0, -thrust * 10.0))
    set_rot("spine_03", (0, 0, -thrust * 8.0))
    set_rot("spine_05", (0, 0, -thrust * 6.0))
    set_rot("neck_01", (0, 0, thrust * 6.0))
    set_rot("head", (0, 0, thrust * 8.0))
    
    # Right arm: windup -> powerful forward thrust
    # Rotation around local Z drives arm forward in Unreal +Y!
    # At impact (thrust=1.0): upperarm_r Z is -65 deg (reaches 55 cm ahead!)
    u_z = -thrust * 65.0 + windup * 0.3
    u_x = -15.0 - windup * 0.4 + thrust * 25.0
    u_y = -25.0 + thrust * 15.0
    set_rot("clavicle_r", (0, -thrust * 14.0, 0))
    set_rot("upperarm_r", (u_x, u_y, u_z))
    set_rot("lowerarm_r", (-25.0 + thrust * 20.0, 0, 0))
    set_rot("hand_r", (15.0, 0, 0))
    
    # Left arm: guard balance
    set_rot("clavicle_l", (0, thrust * 8.0, 0))
    set_rot("upperarm_l", (-15.0, 20.0, -15.0))
    set_rot("lowerarm_l", (-35.0 + windup * 0.2, 0, 0))
    set_rot("hand_l", (20.0, -15.0, 0))
    
    # Legs stride and plant
    set_rot("thigh_r", (step * 35.0, 0, -8.0))
    set_rot("calf_r", (-step * 45.0, 0, 0))
    set_rot("foot_r", (step * 15.0, 0, 0))
    set_rot("thigh_l", (-step * 25.0, 0, 8.0))
    set_rot("calf_l", (-step * 20.0, 0, 0))
    set_rot("foot_l", (step * 10.0, 0, 0))

export_clip("ACT_Riposte_Player_Front", 0, 48, "AN_Riposte_Player_Front.fbx")
print("Exported AN_Riposte_Player_Front.fbx")

# ===================================================================
# CLIP 7: AN_Boss01_DormantIdle (5.000 s loop = 151 frames: 0 to 150)
# Boss kneels (corrected kneel pose), sword planted point down in floor,
# both hands on pommel, head bowed, slow breathing loop (chest, shoulders, head mm).
# Frame 0 == Frame 150 bitwise exact (0.0000). In place.
# ===================================================================
clear_pose()
arm.animation_data_create()
act_dormant = bpy.data.actions.new("ACT_Boss01_DormantIdle")
arm.animation_data.action = act_dormant
if act_dormant.slots:
    arm.animation_data.action_slot = act_dormant.slots[0]

def apply_dormant_base():
    apply_kneel_legs()
    set_loc("pelvis", (-48.0, 4.0, 0.0))
    # Head bowed reverently forward
    set_rot("pelvis", (0.0, 0.0, -4.0))
    set_rot("spine_01", (0.0, 0.0, -5.0))
    set_rot("spine_03", (0.0, 0.0, -6.0))
    set_rot("spine_05", (0.0, 0.0, -7.0))
    set_rot("neck_01", (0.0, 0.0, -8.0))
    set_rot("head", (0.0, 0.0, -10.0)) # bowed head looking down
    
    # Both hands clasped on sword pommel in front of chest/pelvis
    # Right hand:
    set_rot("upperarm_r", (-35.0, -20.0, -15.0))
    set_rot("lowerarm_r", (-75.0, 0.0, 0.0))
    set_rot("hand_r", (20.0, 0.0, 0.0))
    # Left hand clasped over right:
    set_rot("upperarm_l", (-35.0, 20.0, 15.0))
    set_rot("lowerarm_l", (-75.0, 0.0, 0.0))
    set_rot("hand_l", (20.0, 0.0, 0.0))

# 5.0s loop: 151 frames (0..150)
for f in range(151):
    scene.frame_set(f)
    t_cycle = f / 150.0
    # Two slow meditative breath cycles over 5 seconds
    breath = math.sin(t_cycle * 2.0 * math.pi)
    
    apply_dormant_base()
    # Subtle breathing on chest and spine (millimetre scale)
    set_loc("pelvis", (-48.0 + breath * 0.4, 4.0, 0.0))
    set_rot("spine_03", (0.0, 0.0, -6.0 - breath * 0.8))
    set_rot("spine_05", (0.0, 0.0, -7.0 - breath * 1.0))
    set_rot("neck_01", (0.0, 0.0, -8.0 + breath * 0.4))
    set_rot("head", (0.0, 0.0, -10.0 + breath * 0.5))

export_clip("ACT_Boss01_DormantIdle", 0, 150, "AN_Boss01_DormantIdle.fbx")
print("Exported AN_Boss01_DormantIdle.fbx")

# ===================================================================
# CLIP 8: AN_Boss01_Wake (3.500 s = 106 frames: 0 to 105)
# Starts in DormantIdle F0 pose (diff <= 0.01).
# 0.0 - 1.0s (F0..F30): Head lifts, boss awakens.
# 1.0 - 2.0s (F30..F60): Hands tighten, sword pulled from floor.
#     Mark SwordFree at 1.50 s (F45).
# 2.0 - 3.0s (F60..F90): Boss rises from kneel to full height.
#     Mark StandUp at 2.50 s (F75).
# 3.0 - 3.5s (F90..F105): Settle into combat ready (PhaseRoar F0 pose).
# ===================================================================
clear_pose()
arm.animation_data_create()
act_wake = bpy.data.actions.new("ACT_Boss01_Wake")
arm.animation_data.action = act_wake
if act_wake.slots:
    arm.animation_data.action_slot = act_wake.slots[0]

for f in range(106):
    scene.frame_set(f)
    if f == 0:
        # Exact match with DormantIdle F0
        apply_dormant_base()
    elif f >= 105:
        # Exact match with COMBAT_READY / PhaseRoar F0
        apply_combat_ready()
    elif f <= 30:
        # Phase 1: Head lifts, torso stirs (0.0 to 1.0 s)
        t1 = f / 30.0
        apply_kneel_legs()
        set_loc("pelvis", (-48.0, 4.0, 0.0))
        # Spine and head un-bow to alert kneeling
        sp_bow = -7.0 * (1.0 - t1)
        hd_bow = -10.0 * (1.0 - t1) + 5.0 * t1
        set_rot("pelvis", (0.0, 0.0, sp_bow * 0.4))
        set_rot("spine_01", (0.0, 0.0, sp_bow * 0.6))
        set_rot("spine_03", (0.0, 0.0, sp_bow * 0.8))
        set_rot("spine_05", (0.0, 0.0, sp_bow * 1.0))
        set_rot("neck_01", (0.0, 0.0, hd_bow * 0.6))
        set_rot("head", (0.0, 0.0, hd_bow * 1.0))
        # Hands still on pommel
        set_rot("upperarm_r", (-35.0, -20.0, -15.0))
        set_rot("lowerarm_r", (-75.0, 0.0, 0.0))
        set_rot("hand_r", (20.0, 0.0, 0.0))
        set_rot("upperarm_l", (-35.0, 20.0, 15.0))
        set_rot("lowerarm_l", (-75.0, 0.0, 0.0))
        set_rot("hand_l", (20.0, 0.0, 0.0))
    elif f <= 60:
        # Phase 2: Pull sword from floor (1.0 to 2.0 s, SwordFree at 1.5s = F45)
        t2 = (f - 30) / 30.0
        apply_kneel_legs()
        set_loc("pelvis", (-48.0 + 4.0 * t2, 4.0 - 2.0 * t2, 0.0))
        set_rot("pelvis", (0.0, 0.0, 0.0))
        set_rot("spine_01", (0.0, 0.0, 0.0))
        set_rot("spine_03", (0.0, 0.0, 0.0))
        set_rot("spine_05", (0.0, 0.0, 0.0))
        set_rot("neck_01", (0.0, 0.0, 5.0 * (1.0 - t2)))
        set_rot("head", (0.0, 0.0, 5.0 * (1.0 - t2)))
        # Arms heave upward, lifting sword hilt
        set_rot("upperarm_r", (-35.0 + 15.0 * t2, -20.0 - 5.0 * t2, -15.0 + 30.0 * t2))
        set_rot("lowerarm_r", (-75.0 + 35.0 * t2, 0.0, 0.0))
        set_rot("hand_r", (20.0, 0.0, 0.0))
        set_rot("upperarm_l", (-35.0 + 15.0 * t2, 20.0 + 5.0 * t2, 15.0 - 25.0 * t2))
        set_rot("lowerarm_l", (-75.0 + 30.0 * t2, 0.0, 0.0))
        set_rot("hand_l", (20.0, 0.0, 0.0))
    elif f <= 90:
        # Phase 3: Boss rises from kneel to full standing height (2.0 to 3.0 s, StandUp at 2.5s = F75)
        t3 = (f - 60) / 30.0
        p_drop = -44.0 * (1.0 - t3)
        set_loc("pelvis", (p_drop, 2.0 * (1.0 - t3), 0.0))
        set_rot("pelvis", (0.0, 0.0, 0.0))
        set_rot("spine_01", (0.0, 0.0, 0.0))
        set_rot("spine_03", (0.0, 0.0, 0.0))
        set_rot("spine_05", (0.0, 0.0, 0.0))
        set_rot("neck_01", (0.0, 0.0, 0.0))
        set_rot("head", (0.0, 0.0, 0.0))
        
        # Legs unbend from kneel to standing
        set_rot("thigh_l", (75.0 * (1.0 - t3), 0.0, 10.0 * (1.0 - t3) + 5.0 * t3))
        set_rot("calf_l", (0.0, -120.0 * (1.0 - t3), -60.0 * (1.0 - t3)))
        set_rot("foot_l", (0.0, -30.0 * (1.0 - t3), -30.0 * (1.0 - t3)))
        set_rot("thigh_r", (85.0 * (1.0 - t3), 0.0, -20.0 * (1.0 - t3) - 5.0 * t3))
        set_rot("calf_r", (0.0, 120.0 * (1.0 - t3), -40.0 * (1.0 - t3)))
        set_rot("foot_r", (0.0, 60.0 * (1.0 - t3), 30.0 * (1.0 - t3)))
        
        # Arms swing sword up toward combat idle
        set_rot("upperarm_r", (-20.0 + 5.0 * t3, -25.0, 15.0))
        set_rot("lowerarm_r", (-40.0 + 15.0 * t3, 0.0, 0.0))
        set_rot("hand_r", (20.0 - 5.0 * t3, 0.0, 0.0))
        set_rot("upperarm_l", (-20.0 + 5.0 * t3, 25.0 - 5.0 * t3, -10.0 - 5.0 * t3))
        set_rot("lowerarm_l", (-45.0 + 10.0 * t3, 0.0, 0.0))
        set_rot("hand_l", (20.0, -15.0 * t3, 0.0))
    else:
        # Phase 4: Settle into combat ready stance (3.0 to 3.5 s)
        t4 = (f - 90) / 15.0
        apply_combat_ready()

export_clip("ACT_Boss01_Wake", 0, 105, "AN_Boss01_Wake.fbx")
print("Exported AN_Boss01_Wake.fbx")

result = {"status": "all 8 clips exported successfully"}
"""

res = execute_blender(code)
print(res)
