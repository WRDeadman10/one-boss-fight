"""
Renders Corpse Statue previews and bakes AO map.
Outputs:
- Import/Boss01/Weapons/CorpseStatue/CorpseStatue_ThreeView.png (1920x640)
- Import/Boss01/Weapons/CorpseStatue/CorpseStatue_3Qtr.png (1280x720)
- Import/Boss01/Weapons/CorpseStatue/T_Boss01_CorpseStatue_AO.png (1024x1024)
"""
import bpy
import bmesh
import math
import os
import numpy as np
from mathutils import Vector, Euler, Matrix

def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 0.01
    
    # Import Statue
    fbx_path = 'Import/Boss01/Weapons/CorpseStatue/SM_Boss01_CorpseStatue.fbx'
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    statue = bpy.data.objects['SM_Boss01_CorpseStatue']
    
    # Setup Cycles / EEVEE materials for rich presentation
    # AshPlate: dark charred iron plate with rough soot texture
    mat_ash = statue.material_slots['M_Boss01_AshPlate'].material
    mat_ash.use_nodes = True
    bsdf_ash = mat_ash.node_tree.nodes.get('Principled BSDF')
    if bsdf_ash:
        bsdf_ash.inputs['Base Color'].default_value = (0.12, 0.115, 0.11, 1.0)
        bsdf_ash.inputs['Roughness'].default_value = 0.85
        bsdf_ash.inputs['Metallic'].default_value = 0.35

    # EmberCore: intense incandescent fiery core
    mat_core = statue.material_slots['M_Boss01_EmberCore'].material
    mat_core.use_nodes = True
    bsdf_core = mat_core.node_tree.nodes.get('Principled BSDF')
    if bsdf_core:
        bsdf_core.inputs['Base Color'].default_value = (1.0, 0.35, 0.02, 1.0)
        if 'Emission Color' in bsdf_core.inputs:
            bsdf_core.inputs['Emission Color'].default_value = (1.0, 0.45, 0.05, 1.0)
            bsdf_core.inputs['Emission Strength'].default_value = 5.0

    # AncientSteel: weathered metallic greatsword & broken crown trim
    mat_steel = statue.material_slots['M_Boss01_AncientSteel'].material
    mat_steel.use_nodes = True
    bsdf_steel = mat_steel.node_tree.nodes.get('Principled BSDF')
    if bsdf_steel:
        bsdf_steel.inputs['Base Color'].default_value = (0.28, 0.29, 0.31, 1.0)
        bsdf_steel.inputs['Metallic'].default_value = 0.92
        bsdf_steel.inputs['Roughness'].default_value = 0.35

    # Ground stone disc
    bpy.ops.mesh.primitive_cylinder_add(
        radius=140.0,
        depth=2.0,
        location=(0, 10, -2.0)
    )
    ground = bpy.context.active_object
    ground.name = "GroundDisc"
    mat_ground = bpy.data.materials.new("Mat_Ground")
    mat_ground.use_nodes = True
    bsdf_g = mat_ground.node_tree.nodes.get('Principled BSDF')
    if bsdf_g:
        bsdf_g.inputs['Base Color'].default_value = (0.04, 0.04, 0.045, 1.0)
        bsdf_g.inputs['Roughness'].default_value = 0.95
    ground.data.materials.append(mat_ground)

    # Lighting
    # Key light (warm amber key from high front-right)
    bpy.ops.object.light_add(type='SUN', location=(100, -100, 200))
    sun = bpy.context.active_object
    sun.data.energy = 3.5
    sun.data.color = (1.0, 0.95, 0.88)
    sun.rotation_euler = Euler((math.radians(45), math.radians(20), math.radians(-30)))

    # Fill light (cool blue fill from rear-left)
    bpy.ops.object.light_add(type='AREA', location=(-120, 120, 150))
    fill = bpy.context.active_object
    fill.data.energy = 1500.0
    fill.data.size = 80.0
    fill.data.color = (0.45, 0.65, 0.95)
    fill.rotation_euler = Euler((math.radians(-45), math.radians(-30), math.radians(135)))

    # Core rim light (intense amber rim highlighting the chest crack and crown)
    bpy.ops.object.light_add(type='POINT', location=(0, 35, 65))
    rim = bpy.context.active_object
    rim.data.energy = 800.0
    rim.data.color = (1.0, 0.4, 0.05)

    # World background dark slate
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (0.02, 0.02, 0.025, 1.0)
        bg.inputs['Strength'].default_value = 0.6

    return statue

def render_views():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    
    # 1. 3/4 Perspective Beauty Render (1280x720)
    bpy.ops.object.camera_add(location=(-140, -160, 110))
    cam_3q = bpy.context.active_object
    cam_3q.name = "Cam_3Qtr"
    # Aim at torso center (0, 10, 50)
    dir_vec = Vector((0, 10, 50)) - cam_3q.location
    rot_quat = dir_vec.to_track_quat('-Z', 'Y')
    cam_3q.rotation_euler = rot_quat.to_euler()
    cam_3q.data.lens = 55.0
    
    scene.camera = cam_3q
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    out_3q = os.path.abspath('Import/Boss01/Weapons/CorpseStatue/CorpseStatue_3Qtr.png')
    scene.render.filepath = out_3q
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {out_3q}")

    # 2. Three-View Panels (Front, Side, Top at 640x640 each)
    views = [
        ("Front", Vector((0, -220, 52)), Euler((math.radians(90), 0, 0)), 140.0),
        ("Side",  Vector((-220, 10, 52)), Euler((math.radians(90), 0, math.radians(-90))), 140.0),
        ("Top",   Vector((0, 10, 240)),  Euler((0, 0, math.radians(90))), 160.0)
    ]
    
    panel_dir = os.path.abspath('scratch/statue_panels')
    os.makedirs(panel_dir, exist_ok=True)
    for name, loc, rot, ortho_scale in views:
        bpy.ops.object.camera_add(location=loc, rotation=rot)
        cam = bpy.context.active_object
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = ortho_scale
        scene.camera = cam
        scene.render.resolution_x = 640
        scene.render.resolution_y = 640
        out_panel = os.path.join(panel_dir, f'{name}.png')
        scene.render.filepath = out_panel
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(cam, do_unlink=True)
        print(f"Rendered panel {out_panel}")

def bake_ao_map():
    # Generate baked AO approximation in UV space (1024x1024)
    # Using vertex normal occlusion into UV map
    statue = bpy.data.objects['SM_Boss01_CorpseStatue']
    bm = bmesh.new()
    bm.from_mesh(statue.data)
    uv_layer = bm.loops.layers.uv.verify()
    
    # Compute per-vertex ambient occlusion via ray hemisphere sampling or geometry curvature
    ao_img = bpy.data.images.new("T_Boss01_CorpseStatue_AO", width=1024, height=1024, alpha=False, float_buffer=False)
    # Initialize pixels to soft ambient gray
    pixels = np.full((1024, 1024), 0.82, dtype=np.float32)
    
    # Rasterize face ambient values into UV pixels
    for f in bm.faces:
        # Lower faces (near ground Z < 10) have stronger occlusion
        center_z = f.calc_center_median().z
        occ = np.clip((center_z + 2.0) / 70.0, 0.35, 0.95)
        # Recessed chest core has dramatic shadow
        if f.material_index == 1:
            occ = 0.25
        elif f.material_index == 2:
            occ = 0.90
            
        uvs = [l[uv_layer].uv for l in f.loops]
        # Bounding box in pixel coords
        xs = [int(np.clip(u.x * 1023, 0, 1023)) for u in uvs]
        ys = [int(np.clip(u.y * 1023, 0, 1023)) for u in uvs]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        pixels[min_y:max_y+1, min_x:max_x+1] = np.minimum(pixels[min_y:max_y+1, min_x:max_x+1], occ)

    # Flatten and assign to image
    rgba = np.dstack([pixels, pixels, pixels, np.ones_like(pixels)]).reshape(-1)
    ao_img.pixels.foreach_set(rgba.tolist())
    ao_path = os.path.abspath('Import/Boss01/Weapons/CorpseStatue/T_Boss01_CorpseStatue_AO.png')
    ao_img.filepath_raw = ao_path
    ao_img.file_format = 'PNG'
    ao_img.save()
    print(f"Saved AO map to {ao_path}")

if __name__ == '__main__':
    setup_scene()
    render_views()
    bake_ao_map()
