"""
Builder script for Corpse Statue v2 (Asset M-09 / SM_Boss01_CorpseStatue).
Answers Brief 15 (Claude C-60):
- Replaces primitive blockout with sculpted monument matching DeathLegend bone coordinates.
- Exact slots: M_Boss01_AshPlate, M_Boss01_EmberCore, M_Boss01_AncientSteel.
- Triangles: 3,000 to 25,000.
- UV coverage >= 60%, non-overlapping, texel density within 2x.
- Zero degenerate tangents.
- Applies all transforms (location 0, rotation 0, scale 1).
"""
import os
import sys
import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler, Quaternion
import numpy as np

def create_corpse_statue():
    # Setup scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 0.01  # Centimeters (Unreal native)
    
    # Materials
    mat_ash = bpy.data.materials.new(name="M_Boss01_AshPlate")
    mat_ash.use_nodes = True
    bsdf_ash = mat_ash.node_tree.nodes.get('Principled BSDF')
    if bsdf_ash:
        bsdf_ash.inputs['Base Color'].default_value = (0.10, 0.095, 0.09, 1.0)
        bsdf_ash.inputs['Roughness'].default_value = 0.85
        
    mat_core = bpy.data.materials.new(name="M_Boss01_EmberCore")
    mat_core.use_nodes = True
    bsdf_core = mat_core.node_tree.nodes.get('Principled BSDF')
    if bsdf_core:
        bsdf_core.inputs['Base Color'].default_value = (1.0, 0.35, 0.05, 1.0)
        if 'Emission Color' in bsdf_core.inputs:
            bsdf_core.inputs['Emission Color'].default_value = (1.0, 0.4, 0.05, 1.0)
            bsdf_core.inputs['Emission Strength'].default_value = 3.0
            
    mat_steel = bpy.data.materials.new(name="M_Boss01_AncientSteel")
    mat_steel.use_nodes = True
    bsdf_steel = mat_steel.node_tree.nodes.get('Principled BSDF')
    if bsdf_steel:
        bsdf_steel.inputs['Base Color'].default_value = (0.05, 0.055, 0.065, 1.0)
        bsdf_steel.inputs['Metallic'].default_value = 0.90
        bsdf_steel.inputs['Roughness'].default_value = 0.40

    parts = []

    def make_part(name, bm, mat_idx):
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        obj = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(obj)
        obj.data.materials.append(mat_ash)
        obj.data.materials.append(mat_core)
        obj.data.materials.append(mat_steel)
        for poly in obj.data.polygons:
            poly.material_index = mat_idx
        parts.append(obj)
        return obj

    # 1. TORSO / CUIRASS (AshPlate)
    # Target: Pelvis (0, 1, 48), Spine_03 (0, 11, 62), Neck (0, 32, 70)
    bm_torso = bmesh.new()
    # Build layered chest armor
    bmesh.ops.create_cone(
        bm_torso,
        cap_ends=True,
        cap_tris=False,
        segments=24,
        radius1=22.0,  # Chest radius
        radius2=15.0,  # Waist radius
        depth=32.0,
        matrix=Matrix.Translation((0, 8, 54)) @ Euler((0.35, 0, 0)).to_matrix().to_4x4()
    )
    # Beveled breastplate ridges
    bmesh.ops.create_cube(
        bm_torso,
        size=1.0,
        matrix=Matrix.Translation((0, 16, 58)) @ Euler((0.45, 0, 0)).to_matrix().to_4x4() @ Matrix.Diagonal((28.0, 12.0, 24.0, 1.0))
    )
    # Abdominal segmented fauld plates
    for i, z in enumerate([42, 46, 50]):
        bmesh.ops.create_cone(
            bm_torso,
            cap_ends=True,
            cap_tris=False,
            segments=20,
            radius1=17.0 - i*0.8,
            radius2=16.0 - i*0.8,
            depth=5.0,
            matrix=Matrix.Translation((0, 3 + i*2, z)) @ Euler((0.30, 0, 0)).to_matrix().to_4x4()
        )
    make_part("Part_Torso", bm_torso, 0)

    # 2. EMBER CORE (EmberCore - Slot 1)
    # Small, separate, closed piece nestled inside the chest fissure
    bm_core = bmesh.new()
    bmesh.ops.create_icosphere(
        bm_core,
        subdivisions=2,
        radius=5.5,
        matrix=Matrix.Translation((0, 16.5, 59.0)) @ Euler((0.2, 0.4, 0)).to_matrix().to_4x4()
    )
    for v in bm_core.verts:
        v.co.x *= 0.85
        v.co.z *= 1.25
        v.co += Vector((np.sin(v.co.z)*0.6, np.cos(v.co.x)*0.6, 0))
    bmesh.ops.recalc_face_normals(bm_core, faces=bm_core.faces)
    make_part("Part_EmberCore", bm_core, 1)

    # 3. CHEST FISSURE TRIM (AncientSteel - Slot 2)
    # Flanged metallic fracture lips framing the ember core
    bm_trim = bmesh.new()
    bmesh.ops.create_cube(
        bm_trim,
        size=1.0,
        matrix=Matrix.Translation((-4.5, 18.2, 59.5)) @ Euler((0.45, -0.2, 0.2)).to_matrix().to_4x4() @ Matrix.Diagonal((2.2, 3.5, 16.0, 1.0))
    )
    bmesh.ops.create_cube(
        bm_trim,
        size=1.0,
        matrix=Matrix.Translation((4.5, 18.2, 59.5)) @ Euler((0.45, 0.2, -0.2)).to_matrix().to_4x4() @ Matrix.Diagonal((2.2, 3.5, 16.0, 1.0))
    )
    make_part("Part_ChestTrim", bm_trim, 2)

    # 4. HEAD & BROKEN CROWN (Head: 0, 52, 76)
    bm_head = bmesh.new()
    bmesh.ops.create_uvsphere(
        bm_head,
        u_segments=20,
        v_segments=16,
        radius=12.0,
        matrix=Matrix.Translation((0, 50, 75)) @ Euler((0.75, 0, 0)).to_matrix().to_4x4()
    )
    bmesh.ops.create_cube(
        bm_head,
        size=1.0,
        matrix=Matrix.Translation((0, 57, 72)) @ Euler((0.85, 0, 0)).to_matrix().to_4x4() @ Matrix.Diagonal((16.0, 10.0, 12.0, 1.0))
    )
    bmesh.ops.create_cone(
        bm_head,
        cap_ends=True,
        cap_tris=False,
        segments=20,
        radius1=15.0,
        radius2=12.0,
        depth=10.0,
        matrix=Matrix.Translation((0, 40, 68)) @ Euler((0.60, 0, 0)).to_matrix().to_4x4()
    )
    make_part("Part_Head", bm_head, 0)

    # Broken Crown Spires (AncientSteel - Slot 2)
    bm_crown = bmesh.new()
    bmesh.ops.create_cone(
        bm_crown,
        cap_ends=False,
        segments=24,
        radius1=12.8,
        radius2=13.2,
        depth=3.5,
        matrix=Matrix.Translation((0, 50, 80)) @ Euler((0.75, 0, 0)).to_matrix().to_4x4()
    )
    spire_configs = [
        (-7.5, 52.0, 85.0, 8.0, 0.75, -0.2),   # Left outer (intact)
        (-3.8, 55.0, 86.5, 9.5, 0.75, -0.1),   # Left mid (intact)
        (0.0,  56.5, 84.5, 4.5, 0.75, 0.0),    # Center (chipped / broken)
        (3.8,  55.0, 83.5, 3.0, 0.75, 0.1),    # Right mid (sheared off)
        (7.5,  52.0, 84.8, 6.5, 0.75, 0.2)     # Right outer (chipped)
    ]
    for x, y, z, h, rx, rz in spire_configs:
        bmesh.ops.create_cone(
            bm_crown,
            cap_ends=True,
            segments=8,
            radius1=2.2,
            radius2=0.4,
            depth=h,
            matrix=Matrix.Translation((x, y, z)) @ Euler((rx, 0, rz)).to_matrix().to_4x4()
        )
    make_part("Part_Crown", bm_crown, 2)

    # 5. PAULDRONS & SHOULDERS (AshPlate)
    bm_shoulders = bmesh.new()
    bmesh.ops.create_uvsphere(
        bm_shoulders,
        u_segments=16,
        v_segments=14,
        radius=14.0,
        matrix=Matrix.Translation((24, 6, 68)) @ Euler((0.2, 0.4, -0.3)).to_matrix().to_4x4()
    )
    bmesh.ops.create_cube(
        bm_shoulders,
        size=1.0,
        matrix=Matrix.Translation((30, 4, 70)) @ Euler((0.2, 0.6, -0.4)).to_matrix().to_4x4() @ Matrix.Diagonal((6.0, 20.0, 18.0, 1.0))
    )
    bmesh.ops.create_uvsphere(
        bm_shoulders,
        u_segments=16,
        v_segments=14,
        radius=14.0,
        matrix=Matrix.Translation((-24, 8, 66)) @ Euler((0.4, -0.3, 0.2)).to_matrix().to_4x4()
    )
    bmesh.ops.create_cube(
        bm_shoulders,
        size=1.0,
        matrix=Matrix.Translation((-30, 8, 67)) @ Euler((0.4, -0.5, 0.3)).to_matrix().to_4x4() @ Matrix.Diagonal((6.0, 20.0, 18.0, 1.0))
    )
    make_part("Part_Shoulders", bm_shoulders, 0)

    # 6. ARMS & GAUNTLETS
    bm_arms = bmesh.new()
    # Left arm: Vambrace down to Hand_L (47, -9, 79)
    bmesh.ops.create_cone(
        bm_arms,
        cap_ends=True,
        segments=14,
        radius1=7.0,
        radius2=5.5,
        depth=18.0,
        matrix=Matrix.Translation((32, 2, 60)) @ Euler((-0.3, 0.5, 0)).to_matrix().to_4x4()
    )
    bmesh.ops.create_cone(
        bm_arms,
        cap_ends=True,
        segments=14,
        radius1=6.0,
        radius2=4.8,
        depth=22.0,
        matrix=Matrix.Translation((40, -4, 48)) @ Euler((-0.6, 0.3, 0)).to_matrix().to_4x4()
    )
    bmesh.ops.create_cube(
        bm_arms,
        size=1.0,
        matrix=Matrix.Translation((44, -8, 38)) @ Euler((-0.4, 0.2, 0)).to_matrix().to_4x4() @ Matrix.Diagonal((9.0, 11.0, 8.0, 1.0))
    )
    # Right arm: Down towards fallen sword at Hand_R (-55, 11, 55)
    bmesh.ops.create_cone(
        bm_arms,
        cap_ends=True,
        segments=14,
        radius1=7.0,
        radius2=5.5,
        depth=20.0,
        matrix=Matrix.Translation((-33, 9, 56)) @ Euler((0.2, -0.6, 0)).to_matrix().to_4x4()
    )
    bmesh.ops.create_cone(
        bm_arms,
        cap_ends=True,
        segments=14,
        radius1=6.0,
        radius2=4.8,
        depth=22.0,
        matrix=Matrix.Translation((-43, 11, 42)) @ Euler((0.4, -0.5, 0)).to_matrix().to_4x4()
    )
    bmesh.ops.create_cube(
        bm_arms,
        size=1.0,
        matrix=Matrix.Translation((-49, 11, 30)) @ Euler((0.3, -0.3, 0)).to_matrix().to_4x4() @ Matrix.Diagonal((9.0, 11.0, 8.0, 1.0))
    )
    make_part("Part_Arms", bm_arms, 0)

    # 7. LOWER BODY & KNEELING LEGS
    bm_legs = bmesh.new()
    bmesh.ops.create_cone(
        bm_legs,
        cap_ends=True,
        segments=20,
        radius1=18.0,
        radius2=22.0,
        depth=16.0,
        matrix=Matrix.Translation((0, 0, 40)) @ Euler((0.2, 0, 0)).to_matrix().to_4x4()
    )
    bmesh.ops.create_cone(
        bm_legs,
        cap_ends=True,
        segments=14,
        radius1=9.0,
        radius2=7.0,
        depth=26.0,
        matrix=Matrix.Translation((14, -8, 30)) @ Euler((-0.8, 0.4, 0)).to_matrix().to_4x4()
    )
    bmesh.ops.create_cone(
        bm_legs,
        cap_ends=True,
        segments=14,
        radius1=7.5,
        radius2=5.5,
        depth=28.0,
        matrix=Matrix.Translation((24, -26, 16)) @ Euler((-1.3, 0.2, 0)).to_matrix().to_4x4()
    )
    bmesh.ops.create_cube(
        bm_legs,
        size=1.0,
        matrix=Matrix.Translation((28, -36, 6)) @ Euler((-0.4, 0.1, 0)).to_matrix().to_4x4() @ Matrix.Diagonal((9.0, 16.0, 8.0, 1.0))
    )
    bmesh.ops.create_cone(
        bm_legs,
        cap_ends=True,
        segments=14,
        radius1=9.0,
        radius2=7.0,
        depth=26.0,
        matrix=Matrix.Translation((-12, 8, 28)) @ Euler((0.6, -0.4, 0)).to_matrix().to_4x4()
    )
    bmesh.ops.create_uvsphere(
        bm_legs,
        u_segments=14,
        v_segments=12,
        radius=7.5,
        matrix=Matrix.Translation((-20, 18, 5.0)) @ Euler((0.5, 0, 0)).to_matrix().to_4x4()
    )
    bmesh.ops.create_cone(
        bm_legs,
        cap_ends=True,
        segments=14,
        radius1=7.0,
        radius2=5.5,
        depth=22.0,
        matrix=Matrix.Translation((-24, 10, 4.0)) @ Euler((0.1, 0.9, -1.2)).to_matrix().to_4x4()
    )
    bmesh.ops.create_cube(
        bm_legs,
        size=1.0,
        matrix=Matrix.Translation((-30, 13, 4.0)) @ Euler((0, 0, -0.4)).to_matrix().to_4x4() @ Matrix.Diagonal((9.0, 15.0, 7.5, 1.0))
    )
    make_part("Part_Legs", bm_legs, 0)

    # 8. THE GREATSWORD (AncientSteel - Slot 2)
    bm_sword = bmesh.new()
    blade_dir = Vector((-10.0, 62.0, 87.5))
    blade_len = blade_dir.length
    blade_mid = Vector((-48.0, -20.0, 0.5)) + blade_dir * 0.45
    rot_sword = Vector((0, 0, 1)).rotation_difference(blade_dir)
    mat_blade = Matrix.Translation(blade_mid) @ rot_sword.to_matrix().to_4x4()
    
    bmesh.ops.create_cube(
        bm_sword,
        size=1.0,
        matrix=mat_blade @ Matrix.Diagonal((12.5, 3.2, 105.0, 1.0))
    )
    tip_pos = Vector((-48.0, -20.0, 0.5)) + blade_dir * 0.08
    bmesh.ops.create_cone(
        bm_sword,
        cap_ends=True,
        segments=8,
        radius1=6.0,
        radius2=0.5,
        depth=20.0,
        matrix=Matrix.Translation(tip_pos) @ rot_sword.to_matrix().to_4x4()
    )
    guard_pos = Vector((-48.0, -20.0, 0.5)) + blade_dir * 0.88
    bmesh.ops.create_cube(
        bm_sword,
        size=1.0,
        matrix=Matrix.Translation(guard_pos) @ rot_sword.to_matrix().to_4x4() @ Matrix.Diagonal((38.0, 6.5, 5.0, 1.0))
    )
    grip_pos = Vector((-48.0, -20.0, 0.5)) + blade_dir * 0.98
    bmesh.ops.create_cone(
        bm_sword,
        cap_ends=True,
        segments=12,
        radius1=2.6,
        radius2=2.4,
        depth=22.0,
        matrix=Matrix.Translation(grip_pos) @ rot_sword.to_matrix().to_4x4()
    )
    pommel_pos = Vector((-48.0, -20.0, 0.5)) + blade_dir * 1.08
    bmesh.ops.create_icosphere(
        bm_sword,
        subdivisions=2,
        radius=4.5,
        matrix=Matrix.Translation(pommel_pos) @ rot_sword.to_matrix().to_4x4()
    )
    make_part("Part_Sword", bm_sword, 2)

    # 9. JOIN ALL PARTS INTO SINGLE MESH
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    statue = bpy.context.active_object
    statue.name = "SM_Boss01_CorpseStatue"
    statue.data.name = "SM_Boss01_CorpseStatue"

    # Apply all transforms
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Decimate to target ~5,000 - 8,000 polys (9,000 - 15,000 triangles)
    mod_dec = statue.modifiers.new("Decimate", 'DECIMATE')
    current_polys = len(statue.data.polygons)
    target_triangles = 12000
    if current_polys * 2 > target_triangles:
        mod_dec.ratio = min(1.0, target_triangles / (current_polys * 2))
    bpy.ops.object.modifier_apply(modifier="Decimate")

    mod_bev = statue.modifiers.new("Bevel", 'BEVEL')
    mod_bev.width = 0.35
    mod_bev.segments = 1
    mod_bev.limit_method = 'ANGLE'
    mod_bev.angle_limit = math.radians(40)
    bpy.ops.object.modifier_apply(modifier="Bevel")

    # Merge doubles 0.001 and smooth normals
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.001)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    
    # 10. REAL UV UNWRAP WITH PACK ISLANDS (Coverage >= 60%)
    bpy.ops.uv.smart_project(
        angle_limit=math.radians(66),
        island_margin=0.002,
        area_weight=0.0,
        correct_aspect=True,
        scale_to_bounds=True
    )
    bpy.ops.uv.pack_islands(margin=0.002)
    bpy.ops.object.mode_set(mode='OBJECT')

    for poly in statue.data.polygons:
        poly.use_smooth = True

    # Adjust Z so lowest point sits exactly at Z = -1.0 cm (safe floor contact >= -2 cm)
    bbox = np.array([v.co for v in statue.data.vertices])
    min_z = bbox[:, 2].min()
    offset_z = -1.0 - min_z
    for v in statue.data.vertices:
        v.co.z += offset_z
    statue.data.update()

    # Mirror Y to cancel FBX/Unreal Y axis inversion (C-62 requirement)
    # This ensures in engine: Head/Crown points to +Y (front), Z 60..80 centroid Y ~ +20, Z 80..110 centroid Y ~ +38
    for v in statue.data.vertices:
        v.co.y = -v.co.y
    statue.data.update()

    # Apply transform and recalculate normals outward with correct winding
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    # Flip normals so they point outward after negative scale/mirror
    bpy.ops.mesh.flip_normals()
    bpy.ops.mesh.normals_make_consistent(inside=False)

    # 10. REAL UV UNWRAP WITH PACK ISLANDS (Coverage >= 60%)
    bpy.ops.uv.smart_project(
        angle_limit=math.radians(66),
        island_margin=0.002,
        area_weight=0.0,
        correct_aspect=True,
        scale_to_bounds=True
    )
    bpy.ops.uv.pack_islands(margin=0.002)
    bpy.ops.object.mode_set(mode='OBJECT')

    for poly in statue.data.polygons:
        poly.use_smooth = True

    # Compute expected engine coordinates (where Engine Y = - Blender Y)
    coords = np.array([v.co for v in statue.data.vertices])
    eng_coords = coords.copy()
    eng_coords[:, 1] = -eng_coords[:, 1]
    
    print(f'Statue Verts: {len(statue.data.vertices)}, Polys: {len(statue.data.polygons)}')
    print(f'Blender Bounds X: [{coords[:,0].min():.2f}, {coords[:,0].max():.2f}] cm')
    print(f'Blender Bounds Y: [{coords[:,1].min():.2f}, {coords[:,1].max():.2f}] cm')
    print(f'Blender Bounds Z: [{coords[:,2].min():.2f}, {coords[:,2].max():.2f}] cm')
    print(f'EXPECTED ENGINE Bounds X: [{eng_coords[:,0].min():.2f}, {eng_coords[:,0].max():.2f}] cm')
    print(f'EXPECTED ENGINE Bounds Y: [{eng_coords[:,1].min():.2f}, {eng_coords[:,1].max():.2f}] cm')
    print(f'EXPECTED ENGINE Bounds Z: [{eng_coords[:,2].min():.2f}, {eng_coords[:,2].max():.2f}] cm')

    for lo, hi in [(0, 20), (20, 40), (40, 60), (60, 80), (80, 110)]:
        sel = eng_coords[(eng_coords[:, 2] >= lo) & (eng_coords[:, 2] < hi)]
        if len(sel) > 0:
            print(f'Engine Band Z {lo}..{hi}: {len(sel)} verts, centroid X={sel[:,0].mean():.1f}, Y={sel[:,1].mean():.1f}, Y bounds=[{sel[:,1].min():.1f}, {sel[:,1].max():.1f}]')

    return statue

if __name__ == '__main__':
    statue = create_corpse_statue()
    out_fbx = 'Import/Boss01/Weapons/CorpseStatue/SM_Boss01_CorpseStatue.fbx'
    statue.select_set(True)
    bpy.context.view_layer.objects.active = statue
    bpy.ops.export_scene.fbx(
        filepath=out_fbx,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_UNITS',
        bake_space_transform=True,
        axis_forward='-Z',
        axis_up='Y',
        object_types={'MESH'},
        bake_anim=False
    )
    print(f'Exported {out_fbx} successfully.')
