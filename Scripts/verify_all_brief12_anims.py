import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import os
import math
from mathutils import Vector, Quaternion

anim_dir = os.path.abspath("Import/Boss01/Animations")

clips = [
    "AN_Boss01_StaggerDown.fbx",
    "AN_Boss01_StaggerFall.fbx",
    "AN_Riposte_Boss_Reaction.fbx",
    "AN_Boss01_PhaseRoar.fbx",
    "AN_Boss01_DeathLegend.fbx",
    "AN_Riposte_Player_Front.fbx",
    "AN_Boss01_DormantIdle.fbx",
    "AN_Boss01_Wake.fbx"
]

results = {}

for clip in clips:
    path = os.path.join(anim_dir, clip)
    if not os.path.exists(path):
        results[clip] = {"error": "File does not exist"}
        continue
        
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    
    scene = bpy.context.scene
    arm = next((o for o in scene.objects if o.type == 'ARMATURE'), None)
    if not arm:
        results[clip] = {"error": "No armature found"}
        continue
        
    act = arm.animation_data.action if arm.animation_data else None
    if not act:
        results[clip] = {"error": "No action found"}
        continue
        
    if act.slots:
        arm.animation_data.action_slot = act.slots[0]
        
    f_start = int(act.frame_range[0])
    f_end = int(act.frame_range[1])
    f_count = f_end - f_start + 1
    duration = (f_count - 1) / 30.0
    
    # Read bones
    bone_names = [b.name for b in arm.data.bones]
    has_root_first = (bone_names[0] == "root") if bone_names else False
    dup_suffixes = [b for b in bone_names if ".00" in b]
    
    # Sample key frames
    scene.frame_set(f_start)
    bpy.context.view_layer.update()
    
    # Measure pelvis and feet at f_start, f_mid, f_end
    def get_measurements(f):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        pb_pelvis = arm.pose.bones.get("pelvis")
        pb_foot_l = arm.pose.bones.get("foot_l")
        pb_foot_r = arm.pose.bones.get("foot_r")
        pb_calf_l = arm.pose.bones.get("calf_l")
        pb_calf_r = arm.pose.bones.get("calf_r")
        pb_ball_l = arm.pose.bones.get("ball_l")
        pb_ball_r = arm.pose.bones.get("ball_r")
        pb_hand_r = arm.pose.bones.get("hand_r")
        pb_head = arm.pose.bones.get("head")
        
        mw = arm.matrix_world
        
        pelvis_w = (mw @ pb_pelvis.matrix).to_translation() if pb_pelvis else Vector((0,0,0))
        foot_l_w = (mw @ pb_foot_l.matrix).to_translation() if pb_foot_l else Vector((0,0,0))
        foot_r_w = (mw @ pb_foot_r.matrix).to_translation() if pb_foot_r else Vector((0,0,0))
        calf_l_w = (mw @ pb_calf_l.matrix).to_translation() if pb_calf_l else Vector((0,0,0))
        calf_r_w = (mw @ pb_calf_r.matrix).to_translation() if pb_calf_r else Vector((0,0,0))
        ball_l_w = (mw @ pb_ball_l.matrix).to_translation() if pb_ball_l else Vector((0,0,0))
        ball_r_w = (mw @ pb_ball_r.matrix).to_translation() if pb_ball_r else Vector((0,0,0))
        hand_r_w = (mw @ pb_hand_r.matrix).to_translation() if pb_hand_r else Vector((0,0,0))
        head_w = (mw @ pb_head.matrix).to_translation() if pb_head else Vector((0,0,0))
        
        return {
            "root_loc": [round(v, 2) for v in arm.location],
            "root_rot": [round(math.degrees(v), 2) for v in arm.rotation_euler],
            "pelvis_z": round(pelvis_w.z, 2),
            "pelvis_w": [round(v, 2) for v in pelvis_w],
            "calf_l_z": round(calf_l_w.z, 2), # knee location
            "calf_r_z": round(calf_r_w.z, 2),
            "ankle_l_z": round(foot_l_w.z, 2),
            "ankle_r_z": round(foot_r_w.z, 2),
            "ball_l_z": round(ball_l_w.z, 2),
            "ball_r_z": round(ball_r_w.z, 2),
            "hand_r_w": [round(v, 2) for v in hand_r_w],
            "head_w": [round(v, 2) for v in head_w]
        }
        
    f_mid = (f_start + f_end) // 2
    
    results[clip] = {
        "frame_start": f_start,
        "frame_end": f_end,
        "frame_count": f_count,
        "duration": duration,
        "bone_count": len(bone_names),
        "first_bone": bone_names[0] if bone_names else None,
        "dup_suffixes": dup_suffixes,
        "f_start_meas": get_measurements(f_start),
        "f_mid_meas": get_measurements(f_mid),
        "f_end_meas": get_measurements(f_end)
    }

# Also verify seam between AN_Boss01_StaggerDown (F30) and AN_Riposte_Boss_Reaction (F0)
# Import both into scenes or measure in isolation
# We will do isolated pose vector comparison
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(anim_dir, "AN_Boss01_StaggerDown.fbx"))
arm1 = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
if arm1.animation_data and arm1.animation_data.action and arm1.animation_data.action.slots:
    arm1.animation_data.action_slot = arm1.animation_data.action.slots[0]
bpy.context.scene.frame_set(30)
bpy.context.view_layer.update()
pose_down_f30 = {b.name: [(arm1.matrix_world @ b.matrix).to_translation(), b.rotation_quaternion.copy()] for b in arm1.pose.bones}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(anim_dir, "AN_Riposte_Boss_Reaction.fbx"))
arm2 = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
if arm2.animation_data and arm2.animation_data.action and arm2.animation_data.action.slots:
    arm2.animation_data.action_slot = arm2.animation_data.action.slots[0]
bpy.context.scene.frame_set(0)
bpy.context.view_layer.update()
pose_react_f0 = {b.name: [(arm2.matrix_world @ b.matrix).to_translation(), b.rotation_quaternion.copy()] for b in arm2.pose.bones}

max_loc_diff = 0.0
max_rot_diff = 0.0
for bname in pose_down_f30:
    if bname in pose_react_f0:
        loc1, rot1 = pose_down_f30[bname]
        loc2, rot2 = pose_react_f0[bname]
        ldiff = (loc1 - loc2).length
        rdiff = abs(rot1.dot(rot2))
        qdiff = 1.0 - rdiff
        if ldiff > max_loc_diff:
            max_loc_diff = ldiff
        if qdiff > max_rot_diff:
            max_rot_diff = qdiff

seam_info = {
    "stagger_down_f30_vs_reaction_f0": {
        "max_world_loc_diff_cm": round(max_loc_diff, 4),
        "max_quat_diff": round(max_rot_diff, 6),
        "seamless": (max_loc_diff < 0.01 and max_rot_diff < 0.01)
    }
}

# Player riposte kinematics verification
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(anim_dir, "AN_Riposte_Player_Front.fbx"))
arm_p = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
if arm_p.animation_data and arm_p.animation_data.action and arm_p.animation_data.action.slots:
    arm_p.animation_data.action_slot = arm_p.animation_data.action.slots[0]

# Check root forward along +Y (which is -ry in Blender)
# Root yaw
# Check f21 (0.7s) and f24 (0.8s)
bpy.context.scene.frame_set(21)
bpy.context.view_layer.update()
root_f21_y = -arm_p.location.y
root_f21_yaw = math.degrees(arm_p.rotation_euler.z)

bpy.context.scene.frame_set(24)
bpy.context.view_layer.update()
root_f24 = arm_p.location.copy()
mw_p = arm_p.matrix_world
pb_hand_r = arm_p.pose.bones.get("hand_r")
hand_f24_w = mw_p @ pb_hand_r.matrix.to_translation()
# Ahead of root in UE component space:
# UE Y is -Blender Y.
# Ahead of root means: (-hand_f24_w.y) - (-root_f24.y) = root_f24.y - hand_f24_w.y
hand_ahead_cm = root_f24.y - hand_f24_w.y
hand_height_cm = hand_f24_w.z

# Body movement inside root frame between f14 and f24
# Sum of bone local displacements
movement_sum = 0.0
for f in range(14, 25):
    bpy.context.scene.frame_set(f)
    bpy.context.view_layer.update()
    for pb in arm_p.pose.bones:
        movement_sum += pb.location.length

# Recovery movement after f36
root_f36_y = -arm_p.location.y
bpy.context.scene.frame_set(48)
bpy.context.view_layer.update()
root_f48_y = -arm_p.location.y
recovery_cm = abs(root_f48_y - root_f36_y)

player_riposte_info = {
    "root_yaw_f21_deg": round(root_f21_yaw, 2),
    "root_f21_forward_cm": round(root_f21_y, 2),
    "hand_ahead_f24_cm": round(hand_ahead_cm, 2),
    "hand_height_f24_cm": round(hand_height_cm, 2),
    "body_movement_f14_f24_cm": round(movement_sum, 2),
    "recovery_f36_f48_cm": round(recovery_cm, 2)
}

result = {
    "clips": results,
    "seam": seam_info,
    "player_riposte": player_riposte_info
}
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
