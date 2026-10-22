import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import os
import math
from mathutils import Vector, Euler, Matrix, Quaternion

anim_dir = os.path.abspath("Import/Boss01/Animations")

v_blade_bone_bl = Vector((-0.8035, 0.2102, 1.4060))
grip_offset_bone_bl = Vector((-0.1390, -0.0261, 0.0489))

def get_sword_in_ue(arm):
    pb = arm.pose.bones['hand_r']
    mw = arm.matrix_world @ pb.matrix
    grip_bl = mw @ grip_offset_bone_bl
    rot_world = mw.to_quaternion()
    v_world = rot_world @ v_blade_bone_bl
    tip_bl = grip_bl + v_world
    
    grip_ue = Vector((grip_bl.x * 100.0, -grip_bl.y * 100.0, grip_bl.z * 100.0))
    tip_ue = Vector((tip_bl.x * 100.0, -tip_bl.y * 100.0, tip_bl.z * 100.0))
    return grip_ue, tip_ue

def get_bone_ue(arm, bname):
    pb = arm.pose.bones[bname]
    mw = arm.matrix_world @ pb.matrix
    loc = mw.translation
    return Vector((loc.x * 100.0, -loc.y * 100.0, loc.z * 100.0))

results = {}

for clip in ["AN_Boss01_DeathLegend", "AN_Boss01_DormantIdle", "AN_Boss01_Wake"]:
    fbx_p = os.path.join(anim_dir, f"{clip}.fbx")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx_p)
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    act = arm.animation_data.action
    
    f_start = int(round(act.frame_range[0]))
    f_end = int(round(act.frame_range[1]))
    num_frames = f_end - f_start + 1
    duration = (num_frames - 1) / 30.0
    
    data = {
        "frames": num_frames,
        "span": f"{f_start}..{f_end}",
        "duration": duration,
    }
    
    scene = bpy.context.scene
    
    if clip == "AN_Boss01_DormantIdle":
        # Check loop closure: F0 vs F150
        scene.frame_set(f_start)
        bpy.context.view_layer.update()
        f0_bones = {b.name: get_bone_ue(arm, b.name) for b in arm.pose.bones}
        g0, t0 = get_sword_in_ue(arm)
        
        scene.frame_set(f_end)
        bpy.context.view_layer.update()
        fend_bones = {b.name: get_bone_ue(arm, b.name) for b in arm.pose.bones}
        loop_err = max((fend_bones[b] - f0_bones[b]).length for b in f0_bones)
        
        # Check breathing at t=2.5s (f=75)
        scene.frame_set(75)
        bpy.context.view_layer.update()
        f75_bones = {b.name: get_bone_ue(arm, b.name) for b in arm.pose.bones}
        worst_breath, worst_bone = 0.0, ""
        for b in f0_bones:
            d = (f75_bones[b] - f0_bones[b]).length
            if d > worst_breath:
                worst_breath, worst_bone = d, b
                
        # Kneel feet over loop
        min_ank, min_ball = 999.0, 999.0
        for f in range(f_start, f_end + 1, 5):
            scene.frame_set(f)
            bpy.context.view_layer.update()
            fl, fr = get_bone_ue(arm, "foot_l").z, get_bone_ue(arm, "foot_r").z
            bl, br = get_bone_ue(arm, "ball_l").z, get_bone_ue(arm, "ball_r").z
            min_ank = min(min_ank, fl, fr)
            min_ball = min(min_ball, bl, br)
            
        data.update({
            "loop_closure": loop_err,
            "breath_worst_2_5s": worst_breath,
            "breath_worst_bone": worst_bone,
            "min_ankle": min_ank,
            "min_ball": min_ball,
            "sword_grip_f0": [round(x, 2) for x in g0],
            "sword_tip_f0": [round(x, 2) for x in t0],
        })
        
    elif clip == "AN_Boss01_DeathLegend":
        scene.frame_set(f_start)
        bpy.context.view_layer.update()
        pel_start = get_bone_ue(arm, "pelvis").z
        
        f25 = f_start + 75 # 2.50 s
        scene.frame_set(f25)
        bpy.context.view_layer.update()
        pel25 = get_bone_ue(arm, "pelvis")
        head25 = get_bone_ue(arm, "head")
        hp25 = head25 - pel25
        g25, t25 = get_sword_in_ue(arm)
        f25_bones = {b.name: get_bone_ue(arm, b.name) for b in arm.pose.bones}
        
        scene.frame_set(f_end) # 3.50 s
        bpy.context.view_layer.update()
        fend_bones = {b.name: get_bone_ue(arm, b.name) for b in arm.pose.bones}
        held_err = max((fend_bones[b] - f25_bones[b]).length for b in f25_bones)
        
        # Kneeling frames 1.4s to 3.5s (f = f_start + 42 .. f_end)
        min_ank, min_ball = 999.0, 999.0
        for f in range(f_start + 42, f_end + 1):
            scene.frame_set(f)
            bpy.context.view_layer.update()
            fl, fr = get_bone_ue(arm, "foot_l").z, get_bone_ue(arm, "foot_r").z
            bl, br = get_bone_ue(arm, "ball_l").z, get_bone_ue(arm, "ball_r").z
            min_ank = min(min_ank, fl, fr)
            min_ball = min(min_ball, bl, br)
            
        data.update({
            "pelvis_start_z": pel_start,
            "pelvis_2_5s_z": pel25.z,
            "head_2_5s_z": head25.z,
            "head_minus_pelvis_y": hp25.y,
            "held_2_5_to_3_5_diff": held_err,
            "min_ankle_kneeling": min_ank,
            "min_ball_kneeling": min_ball,
            "sword_tip_2_5s_z": t25.z,
        })
        
    elif clip == "AN_Boss01_Wake":
        scene.frame_set(f_start)
        bpy.context.view_layer.update()
        g0, t0 = get_sword_in_ue(arm)
        
        scene.frame_set(f_start + 30) # 1.0 s
        bpy.context.view_layer.update()
        g30, t30 = get_sword_in_ue(arm)
        
        scene.frame_set(f_start + 45) # 1.5 s
        bpy.context.view_layer.update()
        g45, t45 = get_sword_in_ue(arm)
        
        scene.frame_set(f_start + 75) # 2.5 s
        bpy.context.view_layer.update()
        pel75 = get_bone_ue(arm, "pelvis").z
        
        scene.frame_set(f_end) # 3.5 s
        bpy.context.view_layer.update()
        pel_end = get_bone_ue(arm, "pelvis").z
        
        data.update({
            "sword_tip_0s_z": t0.z,
            "sword_tip_1s_z": t30.z,
            "sword_tip_1_5s_z": t45.z,
            "pelvis_2_5s_z": pel75,
            "pelvis_end_z": pel_end,
        })
        
    results[clip] = data

result = results
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
