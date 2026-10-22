import os
import re
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

clips = [
    ("AN_Riposte_Player_Front", 1.600),
    ("AN_Riposte_Boss_Reaction", 2.000),
    ("AN_Boss01_DeathLegend", 3.500),
    ("AN_Boss01_PhaseRoar", 1.800),
    ("AN_Boss01_StaggerFall", 0.700),
    ("AN_Boss01_StaggerDown", 1.000),
    ("AN_Boss01_StaggerGetUp", 1.400),
    ("AN_Boss01_A3a_Combo1", 0.800),
    ("AN_Boss01_A3b_Combo2", 1.333),
]

anim_dir = os.path.abspath("Import/Boss01/Animations")

code = r"""
import bpy, os
anim_dir = os.path.abspath("Import/Boss01/Animations")
clips = [
    "AN_Riposte_Player_Front.fbx",
    "AN_Riposte_Boss_Reaction.fbx",
    "AN_Boss01_DeathLegend.fbx",
    "AN_Boss01_PhaseRoar.fbx",
    "AN_Boss01_StaggerFall.fbx",
    "AN_Boss01_StaggerDown.fbx",
    "AN_Boss01_StaggerGetUp.fbx",
    "AN_Boss01_A3a_Combo1.fbx",
    "AN_Boss01_A3b_Combo2.fbx",
]

out = {}
for c in clips:
    p = os.path.join(anim_dir, c)
    s = bpy.data.scenes.new("Audit")
    bpy.context.window.scene = s
    bpy.ops.import_scene.fbx(filepath=p)
    arm = next(o for o in s.objects if o.type == 'ARMATURE')
    act = arm.animation_data.action
    f_start = int(act.frame_range[0])
    f_end = int(act.frame_range[1])
    count = f_end - f_start + 1
    dur = (count - 1) / 30.0
    
    pelvis = arm.pose.bones.get('pelvis')
    root = arm.pose.bones.get('root')
    foot_r = arm.pose.bones.get('foot_r')
    foot_l = arm.pose.bones.get('foot_l')
    ball_r = arm.pose.bones.get('ball_r')
    ball_l = arm.pose.bones.get('ball_l')
    
    def get_z(b, frame):
        s.frame_set(frame)
        bpy.context.view_layer.update()
        mat = arm.matrix_world @ b.matrix
        loc = mat.to_translation()
        return round(loc.z if arm.scale.x > 0.5 else loc.z * 100.0, 1)
        
    def get_root_x(frame):
        s.frame_set(frame)
        bpy.context.view_layer.update()
        mat = arm.matrix_world @ root.matrix if root else arm.matrix_world
        loc = mat.to_translation()
        return round(loc.x if arm.scale.x > 0.5 else loc.x * 100.0, 1)
        
    f_mid = (f_start + f_end) // 2
    pel_s = get_z(pelvis, f_start) if pelvis else 0.0
    pel_m = get_z(pelvis, f_mid) if pelvis else 0.0
    pel_e = get_z(pelvis, f_end) if pelvis else 0.0
    
    root_s = get_root_x(f_start)
    root_m = get_root_x(f_mid)
    root_e = get_root_x(f_end)
    
    foot_r_s = get_z(foot_r, f_start) if foot_r else 0.0
    foot_r_e = get_z(foot_r, f_end) if foot_r else 0.0
    
    out[c] = {
        'span': f"F{f_start}..F{f_end}",
        'frames': count,
        'duration': round(dur, 4),
        'pelvis_z': [pel_s, pel_m, pel_e],
        'root_x': [root_s, root_m, root_e],
        'foot_r_z': [foot_r_s, foot_r_e]
    }
    
    for o in list(s.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.scenes.remove(s)

result = out
"""

res = execute_blender(code)
anim_data = res.get("result", {})

print("\n--- CLEAN-SCENE READ-BACK AUDIT ---")
for base, intended in clips:
    fname = f"{base}.fbx"
    p = os.path.join(anim_dir, fname)
    # Check binary TimeMode
    data = open(p, "rb").read(400000)
    m = re.search(rb"TimeModeS\x04\x00\x00\x00enumS\x00\x00\x00\x00S\x00\x00\x00\x00I(.{4})", data, re.S)
    tmode = int.from_bytes(m.group(1), "little") if m else None
    
    info = anim_data.get(fname, {})
    actual_dur = info.get("duration", 0.0)
    span = info.get("span", "")
    frames = info.get("frames", 0)
    pel_z = info.get("pelvis_z", [0, 0, 0])
    root_x = info.get("root_x", [0, 0, 0])
    
    print(f"| {base:28s} | {intended:.3f} s | {actual_dur:.3f} s | {frames:2d} ({span:9s}) | {tmode} (30 fps) | Pelvis: {pel_z[0]}cm -> {pel_z[1]}cm -> {pel_z[2]}cm | Root X: {root_x[0]} -> {root_x[2]} cm |")
