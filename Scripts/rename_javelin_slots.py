import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy

s = bpy.data.scenes.new("Scene_Javelin")
bpy.context.window.scene = s

s.render.fps = 30
s.render.fps_base = 1.0
s.unit_settings.system = 'METRIC'
s.unit_settings.scale_length = 0.01

fbx_path = "c:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Boss01/Weapons/SM_Boss01_EmberJavelin.fbx"
bpy.ops.import_scene.fbx(filepath=fbx_path)

jav_obj = next((o for o in s.objects if o.type == 'MESH'), None)
if not jav_obj:
    raise RuntimeError("Failed to import javelin")

# Check current material slots
print("Current slots:", [m.name for m in jav_obj.data.materials])

# Create / rename materials
rename_map = {
    "M_Boss01_Blade": "M_Boss01_Javelin_Iron",
    "M_Boss01_Guard_Grip": "M_Boss01_Javelin_Grip",
    "M_Boss01_Blade_Glow": "M_Boss01_Javelin_Glow"
}

for idx, m in enumerate(jav_obj.data.materials):
    clean_base = m.name.split('.')[0]
    target_name = rename_map.get(clean_base, clean_base)
    # Check if target material already exists
    target_mat = bpy.data.materials.get(target_name)
    if not target_mat:
        m.name = target_name
    else:
        jav_obj.data.materials[idx] = target_mat

print("Renamed slots:", [m.name for m in jav_obj.data.materials])

# Export clean FBX
bpy.ops.object.select_all(action='DESELECT')
jav_obj.select_set(True)
bpy.context.view_layer.objects.active = jav_obj

bpy.ops.export_scene.fbx(
    filepath=fbx_path,
    use_selection=True,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',
    bake_space_transform=True,
    bake_anim=False
)

slot_counts = {m.name: sum(1 for p in jav_obj.data.polygons if p.material_index == idx) for idx, m in enumerate(jav_obj.data.materials)}

for o in list(s.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.scenes.remove(s)

result = {
    "slots": [m.name for m in jav_obj.data.materials],
    "slot_counts": slot_counts
}
"""

res = execute_blender(code)
print("Javelin rename result:", res.get("result"))
print("Stdout:", res.get("stdout"))
if res.get("stderr"):
    print("ERR:", res.get("stderr"))
