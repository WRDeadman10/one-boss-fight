import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import os
import math
from mathutils import Vector, Quaternion, Euler

anim_dir = "c:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Boss01/Animations"
ref_path = "c:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx"

# Clean scenes
for o in list(bpy.data.objects):
    if o.name.startswith("Temp_") or o.name.startswith("root") or o.name.startswith("SKM_"):
        bpy.data.objects.remove(o, do_unlink=True)
for a in list(bpy.data.armatures):
    if a.name.startswith("root") or a.name.startswith("SKM_"):
        bpy.data.armatures.remove(a, do_unlink=True)

scene = bpy.data.scenes.new("Scene_AuthorClips")
bpy.context.window.scene = scene

scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01

bpy.ops.import_scene.fbx(filepath=ref_path)

# Enforce FPS=30 after FBX import!
scene.render.fps = 30
scene.render.fps_base = 1.0

arm = next(o for o in scene.objects if o.type == 'ARMATURE')
arm.name = "root"
arm.data.name = "root"
arm.data.pose_position = 'POSE'
bpy.context.view_layer.objects.active = arm
arm.select_set(True)

# Remove any meshes imported with reference
for o in list(scene.objects):
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)

# Helper for bone rot
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
    for pb in arm.pose.bones:
        pb.location = Vector((0, 0, 0))
        pb.rotation_quaternion = Quaternion((1, 0, 0, 0))

def export_clip(act_name, f_start, f_end, fbx_filename):
    scene.frame_start = f_start
    scene.frame_end = f_end
    
    # Bake pose
    bpy.ops.nla.bake(
        frame_start=f_start,
        frame_end=f_end,
        only_selected=False,
        visual_keying=True,
        clear_constraints=True,
        bake_types={'POSE'}
    )
    
    act = arm.animation_data.action
    act.name = act_name
    act.use_frame_range = True
    act.frame_start = float(f_start)
    act.frame_end = float(f_end)
    
    # Re-enforce scene FPS immediately before export!
    scene.render.fps = 30
    scene.render.fps_base = 1.0
    
    out_fbx = f"{anim_dir}/{fbx_filename}"
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
# 1. AN_Boss01_PhaseRoar (1.8 s = 54 frames span: frames 0 to 54)
# ===================================================================
arm.animation_data_create()
act_roar = bpy.data.actions.new("ACT_Boss01_PhaseRoar")
arm.animation_data.action = act_roar

# Stance keyframes: (frame, pel_drop, spine_arch, head_back, r_arm_lift, l_arm_flare)
roar_kf = [
    ( 0,   0.0,   0.0,   0.0,  15.0,  15.0), # Combat ready
    ( 6,  -9.0,   5.0,  -8.0,   8.0,   5.0), # Coiled anticipation
    (15,  -3.0, -15.0,  20.0,  55.0,  45.0), # Burst initiation
    (21,  -1.5, -25.0,  38.0,  75.0,  65.0), # ROAR PEAK (Notify 0.70 s)
    (27,  -1.0, -26.0,  40.0,  78.0,  68.0), # Sustained apex hold
    (33,  -1.2, -25.0,  39.0,  76.0,  66.0), # Sustained apex hold
    (39,  -1.5, -23.0,  36.0,  74.0,  62.0), # Apex hold release (1.30 s)
    (48,  -5.0,  -8.0,  10.0,  35.0,  28.0), # Exhale & descent
    (54,   0.0,   0.0,   0.0,  15.0,  15.0), # Settle to combat ready
]

for f, p_drop, sp_arch, h_back, r_lift, l_flare in roar_kf:
    scene.frame_set(f)
    set_loc("pelvis", (p_drop, 0, 0))
    # Pelvis orientation
    set_rot("pelvis", (sp_arch * 0.3, 0, 0))
    # Spine heaves and arches backward
    set_rot("spine_01", (sp_arch * 0.25, 0, 0))
    set_rot("spine_03", (sp_arch * 0.35, 0, 0))
    set_rot("spine_05", (sp_arch * 0.40, 0, 0))
    # Head arches back into howl
    set_rot("neck_01", (h_back * 0.4, 0, 0))
    set_rot("head", (h_back * 0.6, 0, 0))
    # Right arm lifts greatsword high into sky
    set_rot("clavicle_r", (0, r_lift * 0.2, 0))
    set_rot("upperarm_r", (-r_lift * 0.7, -r_lift * 0.5, r_lift * 0.4))
    set_rot("lowerarm_r", (-25.0, 0, 0))
    set_rot("hand_r", (15.0, 0, 0))
    # Left arm flings wide in roaring gesture
    set_rot("clavicle_l", (0, -l_flare * 0.2, 0))
    set_rot("upperarm_l", (-l_flare * 0.6, l_flare * 0.6, -l_flare * 0.4))
    set_rot("lowerarm_l", (-35.0, 0, 0))
    set_rot("hand_l", (20.0, -15.0, 0))
    # Grounded wide legs
    crouch = abs(p_drop) / 12.0
    set_rot("thigh_l", (crouch * 12.0, 0, 15.0))
    set_rot("calf_l", (-crouch * 24.0, 0, 0))
    set_rot("foot_l", (crouch * 12.0, 0, 0))
    set_rot("thigh_r", (crouch * 12.0, 0, -15.0))
    set_rot("calf_r", (-crouch * 24.0, 0, 0))
    set_rot("foot_r", (crouch * 12.0, 0, 0))

fbx_roar = export_clip("ACT_Boss01_PhaseRoar", 0, 54, "AN_Boss01_PhaseRoar.fbx")

# ===================================================================
# 2. AN_Boss01_StaggerFall (0.7 s = 21 frames span: frames 0 to 21)
# ===================================================================
clear_pose()
act_fall = bpy.data.actions.new("ACT_Boss01_StaggerFall")
arm.animation_data.action = act_fall

fall_kf = [
    # (frame, pel_drop_x, pel_recoil_y, spine_pitch, head_pitch, r_knee_bend, l_knee_bend)
    ( 0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0), # Combat idle
    ( 4,  -8.0,  -6.0, -15.0, -18.0,  15.0,  12.0), # Posture break impact recoil
    ( 9, -24.0,  -4.0,  -5.0,  -5.0,  45.0,  35.0), # Knees collapse
    (15, -42.0,   2.0,  15.0,  18.0,  85.0,  55.0), # Right knee hits floor
    (21, -48.0,   4.0,  25.0,  28.0, 105.0,  65.0), # Kneeling rest (end pose)
]

for f, p_drop, p_rec, sp_p, h_p, rk_b, lk_b in fall_kf:
    scene.frame_set(f)
    set_loc("pelvis", (p_drop, p_rec, 0))
    set_rot("pelvis", (sp_p * 0.3, 0, 0))
    set_rot("spine_01", (sp_p * 0.25, 0, 0))
    set_rot("spine_03", (sp_p * 0.35, 0, 0))
    set_rot("spine_05", (sp_p * 0.40, 0, 0))
    set_rot("neck_01", (h_p * 0.4, 0, 0))
    set_rot("head", (h_p * 0.6, 0, 0))
    # Right leg collapses into kneeling
    set_rot("thigh_r", (rk_b * 0.8, 0, -10.0))
    set_rot("calf_r", (-rk_b * 1.1, 0, 0))
    set_rot("foot_r", (rk_b * 0.4, 0, 0))
    # Left leg stays planted forward for balance
    set_rot("thigh_l", (lk_b * 0.7, 0, 15.0))
    set_rot("calf_l", (-lk_b * 0.9, 0, 0))
    set_rot("foot_l", (lk_b * 0.3, 0, 0))
    # Arms rest weapon hilt on ground
    t_arm = f / 21.0
    set_rot("upperarm_r", (-20.0 - t_arm * 25.0, -15.0, 10.0))
    set_rot("lowerarm_r", (-40.0 - t_arm * 20.0, 0, 0))
    set_rot("hand_r", (10.0, 0, 0))
    set_rot("upperarm_l", (-15.0 - t_arm * 20.0, 15.0, -10.0))
    set_rot("lowerarm_l", (-45.0 - t_arm * 15.0, 0, 0))
    set_rot("hand_l", (15.0, 0, 0))

fbx_fall = export_clip("ACT_Boss01_StaggerFall", 0, 21, "AN_Boss01_StaggerFall.fbx")

# ===================================================================
# 3. AN_Boss01_StaggerDown (1.0 s loop: frames 0 to 30, F0 == F30)
# ===================================================================
clear_pose()
act_down = bpy.data.actions.new("ACT_Boss01_StaggerDown")
arm.animation_data.action = act_down

# Heavy exhausted breathing loop
# F0 and F30 must be identical!
down_kf = [
    # (frame, pel_drop_x, spine_pitch, head_pitch, heave)
    ( 0, -48.0, 25.0, 28.0, 0.0), # Base kneeling
    ( 8, -46.5, 20.0, 22.0, 1.5), # Deep ragged inhale
    (15, -45.8, 18.0, 20.0, 2.2), # Inhale peak
    (22, -47.2, 23.0, 26.0, 0.8), # Exhaling drop
    (30, -48.0, 25.0, 28.0, 0.0), # Identical to F0!
]

for f, p_drop, sp_p, h_p, heave in down_kf:
    scene.frame_set(f)
    set_loc("pelvis", (p_drop, 4.0, 0))
    set_rot("pelvis", (sp_p * 0.3, 0, 0))
    set_rot("spine_01", (sp_p * 0.25, 0, 0))
    set_rot("spine_03", (sp_p * 0.35, 0, 0))
    set_rot("spine_05", (sp_p * 0.40, 0, 0))
    set_rot("neck_01", (h_p * 0.4, 0, 0))
    set_rot("head", (h_p * 0.6, 0, 0))
    # Kneeling legs locked
    set_rot("thigh_r", (84.0, 0, -10.0))
    set_rot("calf_r", (-115.0, 0, 0))
    set_rot("foot_r", (42.0, 0, 0))
    set_rot("thigh_l", (45.5, 0, 15.0))
    set_rot("calf_l", (-58.5, 0, 0))
    set_rot("foot_l", (19.5, 0, 0))
    # Arms resting with slight breathing heave
    set_rot("upperarm_r", (-45.0 + heave * 2.0, -15.0, 10.0))
    set_rot("lowerarm_r", (-60.0, 0, 0))
    set_rot("hand_r", (10.0, 0, 0))
    set_rot("upperarm_l", (-35.0 + heave * 2.0, 15.0, -10.0))
    set_rot("lowerarm_l", (-60.0, 0, 0))
    set_rot("hand_l", (15.0, 0, 0))

fbx_down = export_clip("ACT_Boss01_StaggerDown", 0, 30, "AN_Boss01_StaggerDown.fbx")

# ===================================================================
# 4. AN_Boss01_StaggerGetUp (1.4 s = 42 frames span: frames 0 to 42)
# ===================================================================
clear_pose()
act_getup = bpy.data.actions.new("ACT_Boss01_StaggerGetUp")
arm.animation_data.action = act_getup

getup_kf = [
    # (frame, pel_drop_x, pel_recoil_y, spine_pitch, head_pitch, rk_b, lk_b)
    ( 0, -48.0,  4.0,  25.0,  28.0, 105.0,  65.0), # Starts from StaggerDown pose
    ( 6, -46.0,  3.0,  20.0,  15.0,  95.0,  60.0), # Tighten grip, head rises
    (15, -28.0,  1.0,  10.0,  -5.0,  55.0,  40.0), # Driving up through legs
    (27, -10.0, -1.0,   2.0,  -8.0,  22.0,  18.0), # Upright torso, blade swings up
    (36,  -3.0,  0.0,   0.0,  -2.0,   8.0,   8.0), # Re-centering stance
    (42,   0.0,  0.0,   0.0,   0.0,   0.0,   0.0), # Full combat idle recovery
]

for f, p_drop, p_rec, sp_p, h_p, rk_b, lk_b in getup_kf:
    scene.frame_set(f)
    set_loc("pelvis", (p_drop, p_rec, 0))
    set_rot("pelvis", (sp_p * 0.3, 0, 0))
    set_rot("spine_01", (sp_p * 0.25, 0, 0))
    set_rot("spine_03", (sp_p * 0.35, 0, 0))
    set_rot("spine_05", (sp_p * 0.40, 0, 0))
    set_rot("neck_01", (h_p * 0.4, 0, 0))
    set_rot("head", (h_p * 0.6, 0, 0))
    # Legs extending
    set_rot("thigh_r", (rk_b * 0.8, 0, -10.0 * (rk_b / 105.0)))
    set_rot("calf_r", (-rk_b * 1.1, 0, 0))
    set_rot("foot_r", (rk_b * 0.4, 0, 0))
    set_rot("thigh_l", (lk_b * 0.7, 0, 15.0 * (lk_b / 65.0)))
    set_rot("calf_l", (-lk_b * 0.9, 0, 0))
    set_rot("foot_l", (lk_b * 0.3, 0, 0))
    # Arms bringing weapon back to ready stance
    t_rise = f / 42.0
    set_rot("upperarm_r", (-45.0 * (1.0 - t_rise) + (-15.0) * t_rise, -15.0, 10.0))
    set_rot("lowerarm_r", (-60.0 * (1.0 - t_rise) + (-35.0) * t_rise, 0, 0))
    set_rot("hand_r", (10.0, 0, 0))
    set_rot("upperarm_l", (-35.0 * (1.0 - t_rise) + (-20.0) * t_rise, 15.0, -10.0))
    set_rot("lowerarm_l", (-60.0 * (1.0 - t_rise) + (-40.0) * t_rise, 0, 0))
    set_rot("hand_l", (15.0, 0, 0))

fbx_getup = export_clip("ACT_Boss01_StaggerGetUp", 0, 42, "AN_Boss01_StaggerGetUp.fbx")

# -------------------------------------------------------------------
# Clean Scene Read-Back Validation
# -------------------------------------------------------------------
def validate_clip_fresh(fbx_name, expected_f_count, expected_dur):
    p = f"{anim_dir}/{fbx_name}"
    s_val = bpy.data.scenes.new("ValScene")
    bpy.context.window.scene = s_val
    bpy.ops.import_scene.fbx(filepath=p)
    a_val = next(o for o in s_val.objects if o.type == 'ARMATURE')
    act_val = a_val.animation_data.action
    
    # Read curves
    all_ranges = []
    if hasattr(act_val, 'fcurves') and act_val.fcurves:
        all_ranges.extend([c.range() for c in act_val.fcurves])
    if hasattr(act_val, 'layers'):
        for l in act_val.layers:
            for st in l.strips:
                for cb in st.channelbags:
                    all_ranges.extend([c.range() for c in cb.fcurves])
                    
    f_min = min(r[0] for r in all_ranges) if all_ranges else 0
    f_max = max(r[1] for r in all_ranges) if all_ranges else 0
    dur = (f_max - f_min) / 30.0
    f_count = int(f_max - f_min + 1)
    
    # Check start and end pelvis height
    s_val.frame_set(int(f_min))
    bpy.context.view_layer.update()
    pel_start = (a_val.matrix_world @ a_val.pose.bones['pelvis'].matrix.translation).z * 100.0
    
    s_val.frame_set(int(f_max))
    bpy.context.view_layer.update()
    pel_end = (a_val.matrix_world @ a_val.pose.bones['pelvis'].matrix.translation).z * 100.0
    
    for o in list(s_val.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.scenes.remove(s_val)
    
    return {
        "clip": fbx_name,
        "f_min": f_min,
        "f_max": f_max,
        "frame_count": f_count,
        "duration_sec": round(dur, 3),
        "expected_dur": expected_dur,
        "pelvis_z_start": round(pel_start, 1),
        "pelvis_z_end": round(pel_end, 1)
    }

read_roar = validate_clip_fresh("AN_Boss01_PhaseRoar.fbx", 55, 1.800)
read_fall = validate_clip_fresh("AN_Boss01_StaggerFall.fbx", 22, 0.700)
read_down = validate_clip_fresh("AN_Boss01_StaggerDown.fbx", 31, 1.000)
read_getup = validate_clip_fresh("AN_Boss01_StaggerGetUp.fbx", 43, 1.400)

for o in list(scene.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.scenes.remove(scene)

result = {
    "PhaseRoar": read_roar,
    "StaggerFall": read_fall,
    "StaggerDown": read_down,
    "StaggerGetUp": read_getup
}
"""

res = execute_blender(code)
print("Author clips result:")
import json
print(json.dumps(res, indent=2))
