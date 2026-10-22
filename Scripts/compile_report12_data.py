import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os, math
from mathutils import Vector

anim_dir = os.path.abspath("Import/Boss01/Animations")
weap_dir = os.path.abspath("Import/Boss01/Weapons")

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

clip_data = {}
for c in clips:
    path = os.path.join(anim_dir, c)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
    act = arm.animation_data.action
    if act.slots:
        arm.animation_data.action_slot = act.slots[0]
        
    f_start = int(round(act.frame_range[0]))
    f_end = int(round(act.frame_range[1]))
    f_count = f_end - f_start + 1
    duration = (f_count - 1) / 30.0
    
    def sample_frame(f):
        bpy.context.scene.frame_set(f)
        bpy.context.view_layer.update()
        mw = arm.matrix_world
        p = (mw @ arm.pose.bones['pelvis'].matrix).to_translation()
        h = (mw @ arm.pose.bones['head'].matrix).to_translation()
        fl = (mw @ arm.pose.bones['foot_l'].matrix).to_translation()
        fr = (mw @ arm.pose.bones['foot_r'].matrix).to_translation()
        bl = (mw @ arm.pose.bones['ball_l'].matrix).to_translation()
        br = (mw @ arm.pose.bones['ball_r'].matrix).to_translation()
        cl = (mw @ arm.pose.bones['calf_l'].matrix).to_translation()
        cr = (mw @ arm.pose.bones['calf_r'].matrix).to_translation()
        return {
            "pelvis_z": round(p.z * 100.0, 2),
            "head_z": round(h.z * 100.0, 2),
            "ankle_l_z": round(fl.z * 100.0, 2),
            "ankle_r_z": round(fr.z * 100.0, 2),
            "ball_l_z": round(bl.z * 100.0, 2),
            "ball_r_z": round(br.z * 100.0, 2),
            "knee_l_z": round(cl.z * 100.0, 2),
            "knee_r_z": round(cr.z * 100.0, 2)
        }
        
    f_mid = (f_start + f_end) // 2
    clip_data[c] = {
        "span": f"{f_start}..{f_end}",
        "frames": f_count,
        "duration": round(duration, 4),
        "f_start": sample_frame(f_start),
        "f_mid": sample_frame(f_mid),
        "f_end": sample_frame(f_end)
    }

weapons = ["SM_Boss01_Greatsword.fbx", "SM_Boss01_DexSword_L.fbx", "SM_Boss01_DexSword_R.fbx"]
weap_data = {}
for w in weapons:
    path = os.path.join(weap_dir, w)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    mesh = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
    empties = [o for o in bpy.context.scene.objects if o.type == 'EMPTY']
    
    v_x = [v.co.x for v in mesh.data.vertices]
    v_y = [v.co.y for v in mesh.data.vertices]
    v_z = [v.co.z for v in mesh.data.vertices]
    
    slots = {m.name: sum(1 for p in mesh.data.polygons if p.material_index == idx) for idx, m in enumerate(mesh.data.materials)}
    sockets = {e.name.replace("SOCKET_", ""): [round(v * 100.0, 2) for v in e.location] for e in empties}
    
    weap_data[w] = {
        "dimensions_cm": [round((max(v_x) - min(v_x)) * 100.0, 2), round((max(v_y) - min(v_y)) * 100.0, 2), round((max(v_z) - min(v_z)) * 100.0, 2)],
        "polygons": len(mesh.data.polygons),
        "slots": slots,
        "sockets": sockets,
        "loc": [round(v, 3) for v in mesh.location],
        "rot": [round(math.degrees(v), 3) for v in mesh.rotation_euler],
        "scale": [round(v, 3) for v in mesh.scale]
    }

result = {
    "clips": clip_data,
    "weapons": weap_data
}
"""

res = execute_blender(code)
import json
with open("report12_data.json", "w") as f:
    json.dump(res.get("result", {}), f, indent=2)
print("Saved report12_data.json")
