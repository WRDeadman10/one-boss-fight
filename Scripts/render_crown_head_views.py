import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import math
from mathutils import Vector, Euler

# Fresh scene
scene = bpy.data.scenes.new("Scene_Crown_Render")
bpy.context.window.scene = scene

scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01
scene.render.engine = 'BLENDER_EEVEE'

body_path = "c:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Boss01/SK_Boss01_Body.fbx"
crown_path = "c:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Boss01/SK_Boss01_Crown.fbx"
mantle_path = "c:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Boss01/SK_Boss01_Mantle.fbx"

bpy.ops.import_scene.fbx(filepath=body_path)
body_mesh = next(o for o in scene.objects if o.type == 'MESH')
body_arm = next(o for o in scene.objects if o.type == 'ARMATURE')

bpy.ops.import_scene.fbx(filepath=crown_path)
crown_mesh = next(o for o in scene.objects if o.type == 'MESH' and "Crown" in o.name)

# Studio Lights
def make_sun(name, rot_euler, energy, color):
    lamp_data = bpy.data.lights.new(name=name, type='SUN')
    lamp_data.energy = energy
    lamp_data.color = color
    lamp_obj = bpy.data.objects.new(name=name, object_data=lamp_data)
    lamp_obj.rotation_euler = rot_euler
    scene.collection.objects.link(lamp_obj)
    return lamp_obj

make_sun("C_Studio_Key", (math.radians(50), math.radians(20), math.radians(-30)), 4.5, (1.0, 0.98, 0.92))
make_sun("C_Studio_Fill", (math.radians(45), math.radians(-30), math.radians(60)), 3.0, (0.85, 0.92, 1.0))
make_sun("C_Studio_Rim", (math.radians(-60), math.radians(35), math.radians(145)), 5.5, (1.0, 0.75, 0.40))

# Backdrop disk behind head
mesh_bg = bpy.data.meshes.new("C_Backdrop")
o_bg = bpy.data.objects.new("C_Backdrop", mesh_bg)
scene.collection.objects.link(o_bg)
import bmesh
bm_bg = bmesh.new()
bmesh.ops.create_circle(bm_bg, cap_ends=True, radius=180.0, segments=32)
bm_bg.to_mesh(mesh_bg)
bm_bg.free()
o_bg.location = (0, 100.0, 165.0)
o_bg.rotation_euler = (math.radians(90), 0, 0)

mat_bg = bpy.data.materials.new("M_CrownBackdrop")
mat_bg.use_nodes = True
bsdf_bg = next((n for n in mat_bg.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_bg:
    bsdf_bg.inputs['Base Color'].default_value = (0.24, 0.25, 0.28, 1.0)
    bsdf_bg.inputs['Roughness'].default_value = 0.85
mesh_bg.materials.append(mat_bg)

out_dir = "c:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Boss01/Concepts"
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.film_transparent = False

# Camera 1: Head & Crown Front View (tight framing on head and crown)
# Head center: X = 0, Y = -13, Z = 165 cm
cam_front_data = bpy.data.cameras.new("Cam_CrownHead_Front")
cam_front_data.lens = 75.0
cam_front = bpy.data.objects.new("Cam_CrownHead_Front", cam_front_data)
cam_front.location = (0.0, -95.0, 166.0)
cam_front.rotation_euler = (math.radians(90), 0.0, 0.0)
scene.collection.objects.link(cam_front)

# Camera 2: Head & Crown Side View (strictly profile view: looking from +X to -X)
cam_side_data = bpy.data.cameras.new("Cam_CrownHead_Side")
cam_side_data.lens = 75.0
cam_side = bpy.data.objects.new("Cam_CrownHead_Side", cam_side_data)
cam_side.location = (85.0, -13.0, 166.0)
cam_side.rotation_euler = (math.radians(90), 0.0, math.radians(90))
scene.collection.objects.link(cam_side)

# 1. Render Crown_Head_Front.png
scene.camera = cam_front
scene.render.filepath = f"{out_dir}/Crown_Head_Front.png"
bpy.ops.render.render(write_still=True)
print("Rendered Crown_Head_Front.png")

# 2. Render Crown_Head_Side.png
scene.camera = cam_side
scene.render.filepath = f"{out_dir}/Crown_Head_Side.png"
bpy.ops.render.render(write_still=True)
print("Rendered Crown_Head_Side.png")

# 3. Also update Variant1_CathedralEmber_Close.png with head + crown close
scene.render.resolution_x = 960
scene.render.resolution_y = 720
scene.camera = cam_front
scene.render.filepath = f"{out_dir}/Variant1_CathedralEmber_Close.png"
bpy.ops.render.render(write_still=True)
print("Rendered Variant1_CathedralEmber_Close.png")

# 4. Render Variant1_CathedralEmber_Front.png (full body + seated crown)
bpy.ops.import_scene.fbx(filepath=mantle_path)
cam_full_data = bpy.data.cameras.new("Cam_Full_Front")
cam_full_data.lens = 42.0
cam_full = bpy.data.objects.new("Cam_Full_Front", cam_full_data)
cam_full.location = (0.0, -320.0, 95.0)
cam_full.rotation_euler = (math.radians(90), 0.0, 0.0)
scene.collection.objects.link(cam_full)

scene.camera = cam_full
scene.render.filepath = f"{out_dir}/Variant1_CathedralEmber_Front.png"
bpy.ops.render.render(write_still=True)
print("Rendered Variant1_CathedralEmber_Front.png")

for o in list(scene.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.scenes.remove(scene)

result = {"status": "ok"}
"""

res = execute_blender(code)
print("Render crown response:", res.get("result"))
print("Stdout:", res.get("stdout"))
if res.get("stderr"):
    print("ERR:", res.get("stderr"))
