import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import bmesh
import math
import os
import mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.fps = 30
scene.render.fps_base = 1.0

fbx_path = os.path.abspath("Import/Boss01/Weapons/SM_Boss01_Greatsword.fbx")
out_dir = os.path.abspath("Import/Boss01/Weapons")
tex_dir = os.path.abspath("Import/Boss01/Weapons/Textures")

bpy.ops.import_scene.fbx(filepath=fbx_path)

sw_obj = bpy.data.objects.get("SM_Boss01_Greatsword")
if not sw_obj:
    raise RuntimeError("Failed to import SM_Boss01_Greatsword")

# Rotate upright so length is along Z (height 1.846m, centered at Z = 0.71m)
sw_obj.rotation_euler = (math.radians(90), 0, 0)
bpy.context.view_layer.update()

# Set world background to neutral studio grey
world = bpy.data.worlds.new("World_Studio")
scene.world = world
world.use_nodes = True
bg_node = next((n for n in world.node_tree.nodes if n.type == 'BACKGROUND'), None)
if bg_node:
    bg_node.inputs['Color'].default_value = (0.32, 0.33, 0.35, 1.0)
    bg_node.inputs['Strength'].default_value = 0.8

# Large studio backdrop plane behind sword (20m x 20m)
mesh_bg = bpy.data.meshes.new("Studio_Backdrop")
o_bg = bpy.data.objects.new("Studio_Backdrop", mesh_bg)
scene.collection.objects.link(o_bg)
bm_bg = bmesh.new()
bmesh.ops.create_grid(bm_bg, size=20.0)
bm_bg.to_mesh(mesh_bg)
bm_bg.free()
o_bg.location = (0.0, 3.0, 0.71)
o_bg.rotation_euler = (math.radians(90), 0, 0)

mat_bg = bpy.data.materials.new("M_Backdrop")
mat_bg.use_nodes = True
bsdf_bg = next((n for n in mat_bg.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_bg:
    bsdf_bg.inputs['Base Color'].default_value = (0.30, 0.31, 0.33, 1.0)
    bsdf_bg.inputs['Roughness'].default_value = 0.9
mesh_bg.materials.append(mat_bg)

# Studio Lights without shadow cast on backdrop to avoid dark pointed artifact
def make_sun(name, rot_euler, energy, color):
    lamp_data = bpy.data.lights.new(name=name, type='SUN')
    lamp_data.energy = energy
    lamp_data.color = color
    lamp_data.use_shadow = False
    lamp_obj = bpy.data.objects.new(name=name, object_data=lamp_data)
    lamp_obj.rotation_euler = rot_euler
    scene.collection.objects.link(lamp_obj)
    return lamp_obj

make_sun("Key", (math.radians(52), math.radians(20), math.radians(-30)), 4.8, (1.0, 0.98, 0.92))
make_sun("Fill", (math.radians(45), math.radians(-25), math.radians(45)), 2.8, (0.85, 0.92, 1.0))
make_sun("Rim", (math.radians(-65), math.radians(35), math.radians(145)), 5.5, (1.0, 0.75, 0.35))

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.film_transparent = False

# 1. Cam_8m: Full length at distance exactly 8.0 meters (800 cm) from sword
cam_8m_data = bpy.data.cameras.new("Cam_Sw_8m")
cam_8m_data.lens = 72.0
cam_8m = bpy.data.objects.new("Cam_Sw_8m", cam_8m_data)
cam_8m.location = (0.0, -8.0, 0.71)
cam_8m.rotation_euler = (math.radians(90), 0.0, 0.0)
scene.collection.objects.link(cam_8m)

# 2. Cam_Close: Crossguard hub, 5 spires, and ricasso (Z ~ 0.16m)
cam_close_data = bpy.data.cameras.new("Cam_Sw_Close")
cam_close_data.lens = 65.0
cam_close = bpy.data.objects.new("Cam_Sw_Close", cam_close_data)
cam_close.location = (0.0, -1.10, 0.18)
cam_close.rotation_euler = (math.radians(88), 0.0, 0.0)
scene.collection.objects.link(cam_close)

# 3. Cam_GuardGrip: Hilt assembly (pommel, grip, guard, spires: Z ~ 0.02m)
cam_grip_data = bpy.data.cameras.new("Cam_Sw_Grip")
cam_grip_data.lens = 60.0
cam_grip = bpy.data.objects.new("Cam_Sw_Grip", cam_grip_data)
cam_grip.location = (0.0, -1.20, 0.03)
cam_grip.rotation_euler = (math.radians(89), 0.0, 0.0)
scene.collection.objects.link(cam_grip)

# Material setups
mat_blade = bpy.data.materials.new("M_Boss01_Blade")
mat_blade.use_nodes = True
bsdf_bl = next(n for n in mat_blade.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bc_path = os.path.join(tex_dir, "T_Boss01_Greatsword_BaseColor.png")
if os.path.exists(bc_path):
    tex_img = mat_blade.node_tree.nodes.new('ShaderNodeTexImage')
    tex_img.image = bpy.data.images.load(bc_path)
    mat_blade.node_tree.links.new(tex_img.outputs['Color'], bsdf_bl.inputs['Base Color'])
else:
    bsdf_bl.inputs['Base Color'].default_value = (0.22, 0.23, 0.25, 1.0)
bsdf_bl.inputs['Metallic'].default_value = 0.85
bsdf_bl.inputs['Roughness'].default_value = 0.35

mat_guard = bpy.data.materials.new("M_Boss01_Guard_Grip")
mat_guard.use_nodes = True
bsdf_gd = next(n for n in mat_guard.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_gd.inputs['Base Color'].default_value = (0.16, 0.16, 0.18, 1.0)
bsdf_gd.inputs['Metallic'].default_value = 0.88
bsdf_gd.inputs['Roughness'].default_value = 0.40

# Unshaded vibrant amber emission for fuller
mat_glow = bpy.data.materials.new("M_Boss01_Blade_Glow")
mat_glow.use_nodes = True
gnodes = mat_glow.node_tree.nodes
gnodes.clear()
out_node = gnodes.new('ShaderNodeOutputMaterial')
em_node = gnodes.new('ShaderNodeEmission')
em_node.inputs['Color'].default_value = (1.0, 0.35, 0.0, 1.0)
em_node.inputs['Strength'].default_value = 24.0
mat_glow.node_tree.links.new(em_node.outputs['Emission'], out_node.inputs['Surface'])

# Assign textured materials to existing slots without clearing to preserve polygon material indices!
sw_obj.data.materials[0] = mat_blade
sw_obj.data.materials[1] = mat_guard
sw_obj.data.materials[2] = mat_glow

# Clay material
mat_clay = bpy.data.materials.new("M_Clay_Studio")
mat_clay.use_nodes = True
bsdf_c = next(n for n in mat_clay.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_c.inputs['Base Color'].default_value = (0.65, 0.65, 0.66, 1.0)
bsdf_c.inputs['Roughness'].default_value = 0.55
bsdf_c.inputs['Metallic'].default_value = 0.0

# 1. Render Greatsword_Textured_8m.png
scene.camera = cam_8m
scene.render.filepath = os.path.join(out_dir, "Greatsword_Textured_8m.png")
bpy.ops.render.render(write_still=True)
print("Rendered Greatsword_Textured_8m.png")

# 2. Render Greatsword_GuardGrip_Close.png
scene.camera = cam_grip
scene.render.filepath = os.path.join(out_dir, "Greatsword_GuardGrip_Close.png")
bpy.ops.render.render(write_still=True)
print("Rendered Greatsword_GuardGrip_Close.png")

# 3. Render Greatsword_Clay_Close.png (assign clay to all slots)
for i in range(len(sw_obj.data.materials)):
    sw_obj.data.materials[i] = mat_clay
scene.camera = cam_close
scene.render.filepath = os.path.join(out_dir, "Greatsword_Clay_Close.png")
bpy.ops.render.render(write_still=True)
print("Rendered Greatsword_Clay_Close.png")

# 4. Render Greatsword_Wire_Close.png using ShaderNodeWireframe directly on clay shader
mat_wire_studio = bpy.data.materials.new("M_Wire_Studio")
mat_wire_studio.use_nodes = True
wnodes = mat_wire_studio.node_tree.nodes
wnodes.clear()
out_w = wnodes.new('ShaderNodeOutputMaterial')
mix_w = wnodes.new('ShaderNodeMixShader')
wire_w = wnodes.new('ShaderNodeWireframe')
wire_w.inputs['Size'].default_value = 0.0022
wire_w.use_pixel_size = False

bsdf_c2 = wnodes.new('ShaderNodeBsdfPrincipled')
bsdf_c2.inputs['Base Color'].default_value = (0.65, 0.65, 0.66, 1.0)
bsdf_c2.inputs['Roughness'].default_value = 0.55
bsdf_c2.inputs['Metallic'].default_value = 0.0

em_black = wnodes.new('ShaderNodeEmission')
em_black.inputs['Color'].default_value = (0.01, 0.01, 0.01, 1.0)
em_black.inputs['Strength'].default_value = 1.0

mat_wire_studio.node_tree.links.new(wire_w.outputs['Fac'], mix_w.inputs['Fac'])
mat_wire_studio.node_tree.links.new(bsdf_c2.outputs['BSDF'], mix_w.inputs[1])
mat_wire_studio.node_tree.links.new(em_black.outputs['Emission'], mix_w.inputs[2])
mat_wire_studio.node_tree.links.new(mix_w.outputs['Shader'], out_w.inputs['Surface'])

for i in range(len(sw_obj.data.materials)):
    sw_obj.data.materials[i] = mat_wire_studio

scene.render.filepath = os.path.join(out_dir, "Greatsword_Wire_Close.png")
bpy.ops.render.render(write_still=True)
print("Rendered Greatsword_Wire_Close.png")

result = {"rendered": 4, "status": "ok"}
"""

res = execute_blender(code)
print("Render execution response:", res)
