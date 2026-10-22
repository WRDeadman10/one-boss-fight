import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

out_dir = os.path.abspath("Import/Boss01/Weapons")

def render_sword_views(side_name):
    fbx_path = os.path.join(out_dir, f"SM_Boss01_DexSword_{side_name}.fbx")
    
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = 30
    scene.render.fps_base = 1.0
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    sw_obj = next(o for o in scene.objects if o.type == 'MESH')
    
    # Rotate upright along Z (length 100 cm: -0.18m to +0.82m)
    # 3/4 angle showing blade curve and glowing fuller channel (+35 deg for L, -35 deg for R)
    angle_z = 35.0 if side_name == 'L' else -35.0
    sw_obj.rotation_euler = (math.radians(90), 0, math.radians(angle_z))
    bpy.context.view_layer.update()
    
    # Neutral studio world
    world = bpy.data.worlds.new("World_DexStudio")
    scene.world = world
    world.use_nodes = True
    bg_node = next((n for n in world.node_tree.nodes if n.type == 'BACKGROUND'), None)
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.28, 0.29, 0.31, 1.0)
        bg_node.inputs['Strength'].default_value = 0.8
        
    # Backdrop plane behind sword (18m x 18m)
    mesh_bg = bpy.data.meshes.new("Studio_Backdrop")
    o_bg = bpy.data.objects.new("Studio_Backdrop", mesh_bg)
    scene.collection.objects.link(o_bg)
    bm_bg = bmesh.new()
    bmesh.ops.create_grid(bm_bg, size=18.0)
    bm_bg.to_mesh(mesh_bg)
    bm_bg.free()
    o_bg.location = (0.0, 3.5, 0.32)
    o_bg.rotation_euler = (math.radians(90), 0, 0)
    
    mat_bg = bpy.data.materials.new("M_Backdrop")
    mat_bg.use_nodes = True
    bsdf_bg = next(n for n in mat_bg.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf_bg.inputs['Base Color'].default_value = (0.28, 0.29, 0.31, 1.0)
    mesh_bg.materials.append(mat_bg)
    
    # 3-Point studio lights (no shadow on backdrop)
    def make_sun(name, rot_euler, energy, color):
        lamp_data = bpy.data.lights.new(name=name, type='SUN')
        lamp_data.energy = energy
        lamp_data.color = color
        lamp_data.use_shadow = False
        lamp_obj = bpy.data.objects.new(name=name, object_data=lamp_data)
        lamp_obj.rotation_euler = rot_euler
        scene.collection.objects.link(lamp_obj)
        return lamp_obj
        
    make_sun("Key", (math.radians(52), math.radians(20), math.radians(-30)), 4.0, (1.0, 0.98, 0.92))
    make_sun("Fill", (math.radians(45), math.radians(-25), math.radians(45)), 2.2, (0.85, 0.92, 1.0))
    make_sun("Rim", (math.radians(-65), math.radians(35), math.radians(145)), 4.5, (1.0, 0.75, 0.35))
    
    # Setup shaders directly in imported material slots
    for mat in sw_obj.data.materials:
        mat.use_nodes = True
        if "Glow" in mat.name:
            mat.node_tree.nodes.clear()
            out_node = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
            em_node = mat.node_tree.nodes.new('ShaderNodeEmission')
            em_node.inputs['Color'].default_value = (1.0, 0.35, 0.02, 1.0) # Rich amber
            em_node.inputs['Strength'].default_value = 2.5
            mat.node_tree.links.new(em_node.outputs['Emission'], out_node.inputs['Surface'])
        elif "Guard" in mat.name:
            bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if bsdf:
                bsdf.inputs['Base Color'].default_value = (0.10, 0.10, 0.12, 1.0)
                bsdf.inputs['Metallic'].default_value = 0.85
                bsdf.inputs['Roughness'].default_value = 0.35
        else:
            bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if bsdf:
                bsdf.inputs['Base Color'].default_value = (0.75, 0.77, 0.80, 1.0)
                bsdf.inputs['Metallic'].default_value = 0.95
                bsdf.inputs['Roughness'].default_value = 0.18
                
    # 1. Front Camera: Entire sword (100 cm length, diagonal roll across 16:9 canvas, backed up to 2.15m, 48mm lens)
    cam_front_data = bpy.data.cameras.new(f"Cam_{side_name}_Front")
    cam_front_data.lens = 48.0
    cam_front = bpy.data.objects.new(f"Cam_{side_name}_Front", cam_front_data)
    cam_front.location = (0.0, -2.15, 0.32)
    roll_angle = 35.0 if side_name == 'L' else -35.0
    cam_front.rotation_euler = (math.radians(90), math.radians(roll_angle), 0.0)
    scene.collection.objects.link(cam_front)
    
    # 2. Close Camera: Guard & first 20 cm of blade (Z = 0.12m, distance 1.05m, 55mm lens)
    cam_close_data = bpy.data.cameras.new(f"Cam_{side_name}_Close")
    cam_close_data.lens = 55.0
    cam_close = bpy.data.objects.new(f"Cam_{side_name}_Close", cam_close_data)
    cam_close.location = (0.0, -1.05, 0.12)
    cam_close.rotation_euler = (math.radians(90), 0.0, 0.0)
    scene.collection.objects.link(cam_close)
    
    # Render Front
    scene.camera = cam_front
    front_png = os.path.join(out_dir, f"DexSword_{side_name}_Front.png")
    scene.render.filepath = front_png
    bpy.ops.render.render(write_still=True)
    
    # Render Close
    scene.camera = cam_close
    close_png = os.path.join(out_dir, f"DexSword_{side_name}_Close.png")
    scene.render.filepath = close_png
    bpy.ops.render.render(write_still=True)
    
    return [front_png, close_png]

rendered = []
rendered.extend(render_sword_views("L"))
rendered.extend(render_sword_views("R"))

result = {"rendered": rendered, "status": "ok"}
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
