import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import bmesh
import math
from mathutils import Vector, Euler

# Select Scene_Greatsword or active scene with SM_Boss01_Greatsword
scene = bpy.data.scenes.get("Scene_Greatsword")
if not scene or "SM_Boss01_Greatsword" not in scene.objects:
    for s in bpy.data.scenes:
        if "SM_Boss01_Greatsword" in s.objects:
            scene = s
            break

bpy.context.window.scene = scene
scene.render.engine = 'BLENDER_EEVEE'

# Remove existing lights and cameras in this scene
for o in list(scene.objects):
    if o.type in ['LIGHT', 'CAMERA']:
        bpy.data.objects.remove(o, do_unlink=True)
    if "Backdrop" in o.name:
        bpy.data.objects.remove(o, do_unlink=True)

# 1. Studio Lighting using SUN lamps (constant studio illumination without falloff)
def make_sun(name, rot_euler, energy, color):
    lamp_data = bpy.data.lights.new(name=name, type='SUN')
    lamp_data.energy = energy
    lamp_data.color = color
    lamp_obj = bpy.data.objects.new(name=name, object_data=lamp_data)
    lamp_obj.rotation_euler = rot_euler
    scene.collection.objects.link(lamp_obj)
    return lamp_obj

l_key = make_sun("Sw_Studio_Key", (math.radians(55), math.radians(20), math.radians(-35)), 5.0, (1.0, 0.98, 0.92))
l_fill = make_sun("Sw_Studio_Fill", (math.radians(45), math.radians(-25), math.radians(55)), 3.0, (0.85, 0.92, 1.0))
l_rim = make_sun("Sw_Studio_Rim", (math.radians(-65), math.radians(35), math.radians(140)), 6.5, (1.0, 0.70, 0.35))

# Backdrop disk behind sword
mesh_bg = bpy.data.meshes.new("Sw_Backdrop")
o_bg = bpy.data.objects.new("Sw_Backdrop", mesh_bg)
scene.collection.objects.link(o_bg)
bm_bg = bmesh.new()
bmesh.ops.create_circle(bm_bg, cap_ends=True, radius=350.0, segments=32)
bm_bg.to_mesh(mesh_bg)
bm_bg.free()
o_bg.location = (0, 150.0, 71.0)
o_bg.rotation_euler = (math.radians(90), 0, 0)

mat_bg = bpy.data.materials.new("M_Sw_Backdrop")
mat_bg.use_nodes = True
bsdf_bg = next((n for n in mat_bg.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_bg:
    bsdf_bg.inputs['Base Color'].default_value = (0.28, 0.29, 0.32, 1.0)
    bsdf_bg.inputs['Roughness'].default_value = 0.85
mesh_bg.materials.append(mat_bg)

sw_obj = scene.objects["SM_Boss01_Greatsword"]
out_dir = "c:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Boss01/Weapons"

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.film_transparent = False

# Cameras:
# 1. Cam_8m: Full length (Z from -21.33 to 163.30, center Z = 71.0)
cam_8m_data = bpy.data.cameras.new("Cam_Sw_8m")
cam_8m_data.lens = 38.0
cam_8m = bpy.data.objects.new("Cam_Sw_8m", cam_8m_data)
cam_8m.location = (0.0, -320.0, 71.0)
cam_8m.rotation_euler = (math.radians(90), 0.0, math.radians(25)) # Diagonal roll
scene.collection.objects.link(cam_8m)

# 2. Cam_Close: Crossguard hub, 5 spires, and ricasso (Z ~ 15 cm)
cam_close_data = bpy.data.cameras.new("Cam_Sw_Close")
cam_close_data.lens = 70.0
cam_close = bpy.data.objects.new("Cam_Sw_Close", cam_close_data)
cam_close.location = (0.0, -100.0, 16.0)
cam_close.rotation_euler = (math.radians(86), 0.0, 0.0)
scene.collection.objects.link(cam_close)

# 3. Cam_GuardGrip: Hilt assembly (pommel, grip, guard, spires: Z ~ 0 cm)
cam_grip_data = bpy.data.cameras.new("Cam_Sw_Grip")
cam_grip_data.lens = 65.0
cam_grip = bpy.data.objects.new("Cam_Sw_Grip", cam_grip_data)
cam_grip.location = (0.0, -115.0, 2.0)
cam_grip.rotation_euler = (math.radians(88), 0.0, 0.0)
scene.collection.objects.link(cam_grip)

# Backup materials
orig_mats = list(sw_obj.data.materials)

# Clay material (neutral matte grey)
mat_clay = bpy.data.materials.new("M_Clay_Studio")
mat_clay.use_nodes = True
bsdf_c = next(n for n in mat_clay.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_c.inputs['Base Color'].default_value = (0.62, 0.62, 0.62, 1.0)
bsdf_c.inputs['Roughness'].default_value = 0.55
bsdf_c.inputs['Metallic'].default_value = 0.0

# 1. Render Greatsword_Clay_Close.png
sw_obj.data.materials.clear()
sw_obj.data.materials.append(mat_clay)
scene.camera = cam_close
scene.render.filepath = f"{out_dir}/Greatsword_Clay_Close.png"
bpy.ops.render.render(write_still=True)
print("Rendered Greatsword_Clay_Close.png")

# 2. Render Greatsword_Wire_Close.png
wire_mod = sw_obj.modifiers.new("Wireframe", 'WIREFRAME')
wire_mod.thickness = 0.12
wire_mod.use_replace = False
wire_mat = bpy.data.materials.new("M_Wire_Studio")
wire_mat.use_nodes = True
bsdf_w = next(n for n in wire_mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_w.inputs['Base Color'].default_value = (0.08, 0.08, 0.08, 1.0)
bsdf_w.inputs['Roughness'].default_value = 0.9
sw_obj.data.materials.append(wire_mat)
wire_mod.material_offset = 1
scene.render.filepath = f"{out_dir}/Greatsword_Wire_Close.png"
bpy.ops.render.render(write_still=True)
print("Rendered Greatsword_Wire_Close.png")
sw_obj.modifiers.remove(wire_mod)

# Restore textured materials
sw_obj.data.materials.clear()
for m in orig_mats:
    sw_obj.data.materials.append(m)

# 3. Render Greatsword_GuardGrip_Close.png
scene.camera = cam_grip
scene.render.filepath = f"{out_dir}/Greatsword_GuardGrip_Close.png"
bpy.ops.render.render(write_still=True)
print("Rendered Greatsword_GuardGrip_Close.png")

# 4. Render Greatsword_Textured_8m.png
scene.camera = cam_8m
scene.render.filepath = f"{out_dir}/Greatsword_Textured_8m.png"
bpy.ops.render.render(write_still=True)
print("Rendered Greatsword_Textured_8m.png")

result = {"rendered": 4, "status": "ok"}
"""

res = execute_blender(code)
print("Render execution response:", res)
