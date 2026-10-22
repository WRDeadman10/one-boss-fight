import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import os
import math
from mathutils import Vector

anim_dir = os.path.abspath("Import/Boss01/Animations")

def inspect_clip(clip_name, frames_to_check):
    path = os.path.join(anim_dir, clip_name)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
    if arm.animation_data and arm.animation_data.action and arm.animation_data.action.slots:
        arm.animation_data.action_slot = arm.animation_data.action.slots[0]
        
    out = {}
    for f in frames_to_check:
        bpy.context.scene.frame_set(f)
        bpy.context.view_layer.update()
        mw = arm.matrix_world
        pb_pelvis = arm.pose.bones.get("pelvis")
        pb_neck = arm.pose.bones.get("neck_01")
        pb_head = arm.pose.bones.get("head")
        pb_calf_l = arm.pose.bones.get("calf_l")
        pb_calf_r = arm.pose.bones.get("calf_r")
        pb_foot_l = arm.pose.bones.get("foot_l")
        pb_foot_r = arm.pose.bones.get("foot_r")
        pb_ball_l = arm.pose.bones.get("ball_l")
        pb_ball_r = arm.pose.bones.get("ball_r")
        pb_hand_r = arm.pose.bones.get("hand_r")
        
        pelvis_w = mw @ pb_pelvis.matrix.to_translation()
        neck_w = mw @ pb_neck.matrix.to_translation()
        head_w = mw @ pb_head.matrix.to_translation()
        foot_l_w = mw @ pb_foot_l.matrix.to_translation()
        foot_r_w = mw @ pb_foot_r.matrix.to_translation()
        ball_l_w = mw @ pb_ball_l.matrix.to_translation()
        ball_r_w = mw @ pb_ball_r.matrix.to_translation()
        calf_l_w = mw @ pb_calf_l.matrix.to_translation()
        calf_r_w = mw @ pb_calf_r.matrix.to_translation()
        hand_r_w = mw @ pb_hand_r.matrix.to_translation()
        
        # In UE component space (cm):
        # Note: in Blender, if FBX imported with 1m = 100 units or scale 1.0, let's see actual coordinate scale
        # If Blender units are meters (e.g. 0.48m), UE is cm (* 100) or check if imported as cm
        # Let's inspect raw numbers and also scaled
        ue_head_rel_pelvis = Vector((head_w.x - pelvis_w.x, -(head_w.y - pelvis_w.y), head_w.z - pelvis_w.z))
        ue_neck_rel_pelvis = Vector((neck_w.x - pelvis_w.x, -(neck_w.y - pelvis_w.y), neck_w.z - pelvis_w.z))
        
        out[f] = {
            "pelvis_w": [round(v, 4) for v in pelvis_w],
            "head_w": [round(v, 4) for v in head_w],
            "ue_head_rel_pelvis": [round(v, 4) for v in ue_head_rel_pelvis],
            "ue_neck_rel_pelvis": [round(v, 4) for v in ue_neck_rel_pelvis],
            "calf_l_z": round(calf_l_w.z, 4),
            "calf_r_z": round(calf_r_w.z, 4),
            "ankle_l_z": round(foot_l_w.z, 4),
            "ankle_r_z": round(foot_r_w.z, 4),
            "ball_l_z": round(ball_l_w.z, 4),
            "ball_r_z": round(ball_r_w.z, 4),
            "arm_loc": [round(v, 4) for v in arm.location],
            "hand_r_w": [round(v, 4) for v in hand_r_w]
        }
    return out

checks = {
    "AN_Riposte_Boss_Reaction.fbx": [0, 24, 39, 60], # 0s, 0.8s, 1.3s, 2.0s
    "AN_Boss01_DeathLegend.fbx": [0, 24, 40, 75, 105], # 0s, 0.8s, 1.33s, 2.5s, 3.5s
    "AN_Boss01_PhaseRoar.fbx": [0, 21, 54], # 0s, 0.7s, 1.8s
    "AN_Boss01_StaggerFall.fbx": [0, 10, 21], # 0s, 0.35s, 0.7s
    "AN_Boss01_StaggerDown.fbx": [0, 15, 30],
    "AN_Riposte_Player_Front.fbx": [0, 14, 21, 24, 36, 48],
    "AN_Boss01_DormantIdle.fbx": [0, 75, 150],
    "AN_Boss01_Wake.fbx": [0, 45, 75, 105]
}

result = {}
for clip, frames in checks.items():
    result[clip] = inspect_clip(clip, frames)
"""

res = execute_blender(code)
import json
with open("kinematics_result.json", "w") as f:
    json.dump(res.get("result", {}), f, indent=2)
print("Saved kinematics_result.json")
