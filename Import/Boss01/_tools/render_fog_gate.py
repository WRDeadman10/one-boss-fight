"""
Renders updated previews for FogGateFrame.
Outputs:
- Import/Boss01/Weapons/FogGate/FogGateFrame_Front.png (1280x720)
- Import/Boss01/Weapons/FogGate/FogGateFrame_3Qtr.png (1280x720)
"""
import bpy
import math
import os
from mathutils import Vector, Euler

def render_fog_gate():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 0.01

    fbx_path = os.path.abspath('Import/Boss01/Weapons/FogGate/SM_Boss01_FogGateFrame.fbx')
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    gate = bpy.data.objects['SM_Boss01_FogGateFrame']

    # Assign stone material colors
    mat_stone = gate.material_slots['M_Boss01_Arch_Stone'].material
    if mat_stone and mat_stone.use_nodes:
        bsdf = mat_stone.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.22, 0.22, 0.24, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.85

    mat_trim = gate.material_slots['M_Boss01_Arch_Trim'].material
    if mat_trim and mat_trim.use_nodes:
        bsdf = mat_trim.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.35, 0.32, 0.28, 1.0)
            bsdf.inputs['Metallic'].default_value = 0.50
            bsdf.inputs['Roughness'].default_value = 0.50

    mat_rune = gate.material_slots['M_Boss01_Arch_Rune'].material
    if mat_rune and mat_rune.use_nodes:
        bsdf = mat_rune.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.85, 0.70, 0.25, 1.0)
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = (0.95, 0.75, 0.25, 1.0)
                bsdf.inputs['Emission Strength'].default_value = 2.0

    # Lighting
    bpy.ops.object.light_add(type='SUN', location=(400, -600, 800))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.rotation_euler = Euler((math.radians(50), math.radians(15), math.radians(-35)))

    bpy.ops.object.light_add(type='AREA', location=(-500, 500, 600))
    fill = bpy.context.active_object
    fill.data.energy = 5000.0
    fill.data.size = 400.0
    fill.data.color = (0.5, 0.65, 0.95)

    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (0.02, 0.02, 0.025, 1.0)

    # 1. Front View (1280x720)
    bpy.ops.object.camera_add(location=(0, -1300, 360))
    cam_front = bpy.context.active_object
    dir_front = Vector((0, 0, 360)) - cam_front.location
    cam_front.rotation_euler = dir_front.to_track_quat('-Z', 'Y').to_euler()
    cam_front.data.lens = 45.0
    cam_front.data.clip_end = 5000.0
    scene.camera = cam_front
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    out_front = os.path.abspath('Import/Boss01/Weapons/FogGate/FogGateFrame_Front.png')
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {out_front}")

    # 2. 3/4 Perspective View (1280x720)
    bpy.ops.object.camera_add(location=(-900, -950, 550))
    cam_3q = bpy.context.active_object
    dir_vec = Vector((0, 0, 360)) - cam_3q.location
    cam_3q.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
    cam_3q.data.lens = 45.0
    cam_3q.data.clip_end = 5000.0
    scene.camera = cam_3q
    out_3q = os.path.abspath('Import/Boss01/Weapons/FogGate/FogGateFrame_3Qtr.png')
    scene.render.filepath = out_3q
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {out_3q}")

if __name__ == '__main__':
    render_fog_gate()
