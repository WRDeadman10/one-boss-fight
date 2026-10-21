import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

anim_dir = os.path.abspath(r"Import\Boss01\Animations")

code = f"""
import bpy
import glob
import os

anim_files = sorted(glob.glob(r"{anim_dir}/*.fbx"))
results = []

for f in anim_files:
    fname = os.path.basename(f)
    s = bpy.data.scenes.new("TestVal")
    bpy.context.window.scene = s
    bpy.ops.import_scene.fbx(filepath=f)
    
    arm = next((o for o in s.objects if o.type == 'ARMATURE'), None)
    if not arm:
        continue
    act = arm.animation_data.action
    all_ranges = []
    if hasattr(act, 'fcurves') and act.fcurves:
        all_ranges.extend([c.range() for c in act.fcurves])
    if hasattr(act, 'layers'):
        for l in act.layers:
            for st in l.strips:
                for cb in st.channelbags:
                    all_ranges.extend([c.range() for c in cb.fcurves])
                    
    f_min = min(r[0] for r in all_ranges) if all_ranges else 0
    f_max = max(r[1] for r in all_ranges) if all_ranges else 0
    f_count = int(f_max - f_min + 1) if all_ranges else 0
    dur = (f_max - f_min) / 30.0 if all_ranges else 0.0
    
    # Read pelvis sample at start, mid, end
    s.frame_set(int(f_min))
    bpy.context.view_layer.update()
    p_start = (arm.matrix_world @ arm.pose.bones['pelvis'].matrix.translation).z * 100.0
    
    mid_f = int((f_min + f_max) * 0.5)
    s.frame_set(mid_f)
    bpy.context.view_layer.update()
    p_mid = (arm.matrix_world @ arm.pose.bones['pelvis'].matrix.translation).z * 100.0
    
    s.frame_set(int(f_max))
    bpy.context.view_layer.update()
    p_end = (arm.matrix_world @ arm.pose.bones['pelvis'].matrix.translation).z * 100.0
    
    bones = [b.name for b in arm.data.bones]
    first_bone = bones[0] if bones else None
    
    for o in list(s.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.scenes.remove(s)
    
    results.append({{
        "name": fname,
        "first_bone": first_bone,
        "bone_count": len(bones),
        "f_min": f_min,
        "f_max": f_max,
        "frames": f_count,
        "duration": round(dur, 3),
        "pelvis_start": round(p_start, 1),
        "pelvis_mid": round(p_mid, 1),
        "pelvis_end": round(p_end, 1)
    }})

result = {{"anims": results}}
"""

res = execute_blender(code)
import json
print(json.dumps(res.get("result"), indent=2))
