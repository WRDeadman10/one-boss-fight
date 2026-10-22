import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import os
import bmesh
import math
from mathutils import Vector, Euler, Matrix

out_dir = os.path.abspath("Import/Boss01/Weapons")
os.makedirs(out_dir, exist_ok=True)

def build_sword(side_name, mirror_x=False):
    scene_name = f"Scene_DexSword_{side_name}"
    scene = bpy.data.scenes.new(scene_name)
    bpy.context.window.scene = scene
    scene.render.fps = 30
    scene.render.fps_base = 1.0
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 0.01

    obj_name = f"SM_Boss01_DexSword_{side_name}"
    
    # Purge existing
    for o in list(bpy.data.objects):
        if o.name.startswith(obj_name) or (o.name.startswith("SOCKET_") and o.name in scene.objects):
            bpy.data.objects.remove(o, do_unlink=True)
            
    bm = bmesh.new()
    
    # Slots:
    # 0: M_Boss01_DexBlade
    # 1: M_Boss01_DexGuard_Grip
    # 2: M_Boss01_DexBlade_Glow
    
    sign = -1.0 if mirror_x else 1.0
    
    # Total length: 100.0 cm (-18.0 to +82.0 cm)
    # 1. Kashira / Pommel (-18.0 to -16.0 cm)
    n_seg = 10
    v_pom_bot = bm.verts.new(Vector((0.0, 0.0, -18.0)))
    pom_ring1 = []
    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        pom_ring1.append(bm.verts.new(Vector((
            1.4 * math.cos(ang),
            1.8 * math.sin(ang),
            -17.2
        ))))
    pom_ring2 = []
    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        pom_ring2.append(bm.verts.new(Vector((
            1.2 * math.cos(ang),
            1.6 * math.sin(ang),
            -16.0
        ))))
        
    bm.verts.ensure_lookup_table()
    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f_bot = bm.faces.new([v_pom_bot, pom_ring1[i], pom_ring1[ni]])
        f_mid = bm.faces.new([pom_ring1[i], pom_ring1[ni], pom_ring2[ni], pom_ring2[i]])
        f_bot.material_index = 1
        f_mid.material_index = 1
        
    # 2. Grip / Tsuka (-16.0 to 0.0 cm) - 10 cross sections with diamond wrap profile
    n_grip = 10
    prev_ring = pom_ring2
    for ig in range(1, n_grip + 1):
        t = ig / float(n_grip)
        z = -16.0 * (1.0 - t) + 0.0 * t
        r_x = 1.1 + 0.08 * math.sin(t * math.pi)
        r_y = 1.5 + 0.12 * math.sin(t * math.pi)
        curr_ring = []
        for i in range(n_seg):
            ang = 2.0 * math.pi * i / n_seg
            diamond = 0.06 * math.sin(ang * 4.0 + t * 6.0 * math.pi)
            curr_ring.append(bm.verts.new(Vector((
                (r_x + diamond) * math.cos(ang),
                (r_y + diamond) * math.sin(ang),
                z
            ))))
        bm.verts.ensure_lookup_table()
        for i in range(n_seg):
            ni = (i + 1) % n_seg
            f_g = bm.faces.new([prev_ring[i], prev_ring[ni], curr_ring[ni], curr_ring[i]])
            f_g.material_index = 1
        prev_ring = curr_ring
        
    # 3. Tsuba / Guard (0.0 to 1.4 cm) - flared oval guard plate welded to grip
    tsuba_bot = prev_ring
    # Outer guard rim (16 segments)
    n_tsuba = 16
    tsuba_rim_low = []
    tsuba_rim_mid = []
    tsuba_rim_top = []
    for i in range(n_tsuba):
        ang = 2.0 * math.pi * i / n_tsuba
        # Curved scimitar tsuba shape: 7.6 cm x 6.2 cm
        rx = 3.6 + 0.3 * math.cos(ang * 2.0)
        ry = 3.0 + 0.2 * math.sin(ang * 2.0)
        tsuba_rim_low.append(bm.verts.new(Vector((rx * math.cos(ang), ry * math.sin(ang), 0.2))))
        tsuba_rim_mid.append(bm.verts.new(Vector(((rx + 0.2) * math.cos(ang), (ry + 0.2) * math.sin(ang), 0.7))))
        tsuba_rim_top.append(bm.verts.new(Vector((rx * math.cos(ang), ry * math.sin(ang), 1.2))))
        
    bm.verts.ensure_lookup_table()
    # Connect grip top (n_seg=10) to tsuba rim low (n_tsuba=16) using intermediate transition
    # Fan connection
    for i in range(n_tsuba):
        ni = (i + 1) % n_tsuba
        # Outer rim bevels
        f_rim1 = bm.faces.new([tsuba_rim_low[i], tsuba_rim_low[ni], tsuba_rim_mid[ni], tsuba_rim_mid[i]])
        f_rim2 = bm.faces.new([tsuba_rim_mid[i], tsuba_rim_mid[ni], tsuba_rim_top[ni], tsuba_rim_top[i]])
        f_rim1.material_index = 1
        f_rim2.material_index = 1
        
    # Bottom transition from grip to rim
    for i in range(n_seg):
        ni = (i + 1) % n_seg
        # map to tsuba rim
        j1 = int(round(i * (n_tsuba / n_seg))) % n_tsuba
        j2 = int(round(ni * (n_tsuba / n_seg))) % n_tsuba
        if j1 != j2:
            f_b = bm.faces.new([tsuba_bot[i], tsuba_bot[ni], tsuba_rim_low[j2], tsuba_rim_low[j1]])
            f_b.material_index = 1
            
    # Habaki / Blade collar top (1.4 cm)
    habaki_ring = []
    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        habaki_ring.append(bm.verts.new(Vector((
            0.8 * math.cos(ang),
            1.3 * math.sin(ang),
            1.4
        ))))
    bm.verts.ensure_lookup_table()
    for i in range(n_seg):
        ni = (i + 1) % n_seg
        j1 = int(round(i * (n_tsuba / n_seg))) % n_tsuba
        j2 = int(round(ni * (n_tsuba / n_seg))) % n_tsuba
        if j1 != j2:
            f_top = bm.faces.new([tsuba_rim_top[j1], tsuba_rim_top[j2], habaki_ring[ni], habaki_ring[i]])
            f_top.material_index = 1
            
    # 4. Blade: Z = 1.4 to 82.0 cm (curved katana/scimitar)
    # The blade cross section has:
    # - Back spine (M_Boss01_DexBlade)
    # - Fuller / groove channel (M_Boss01_DexBlade_Glow)
    # - Main bevel & sharp cutting edge (M_Boss01_DexBlade)
    # Curve sori: X offset = sign * 4.5 * sin(pi * (z - 1.4) / (82.0 - 1.4))
    
    n_blade_slices = 26
    blade_slices = []
    
    for ib in range(n_blade_slices + 1):
        tb = ib / float(n_blade_slices)
        z = 1.4 * (1.0 - tb) + 82.0 * tb
        
        # Sori curve
        x_curve = sign * 4.5 * math.sin(math.pi * tb)
        
        # Blade width (along Y) tapers from 3.2 cm at base to 1.8 cm near tip
        w_y = (3.2 * (1.0 - tb) + 1.8 * tb) if tb < 0.9 else (1.8 * (1.0 - (tb - 0.9) / 0.1) + 0.1)
        # Blade thickness (along X) tapers from 0.7 cm to 0.25 cm
        th_x = 0.70 * (1.0 - tb) + 0.25 * tb
        
        # 6 vertices per slice:
        # V0: Spine top (+X side, -Y back)
        # V1: Fuller upper groove
        # V2: Fuller lower groove
        # V3: Cutting edge (+Y front)
        # V4: Left fuller lower groove (-X side)
        # V5: Left fuller upper groove (-X side)
        # V6: Spine back (-Y)
        
        v_spine = bm.verts.new(Vector((x_curve, -w_y * 0.45, z)))
        v_fuller_r_up = bm.verts.new(Vector((x_curve + th_x * 0.45, -w_y * 0.20, z)))
        v_fuller_r_dn = bm.verts.new(Vector((x_curve + th_x * 0.25, -w_y * 0.05, z)))
        v_edge = bm.verts.new(Vector((x_curve, w_y * 0.55, z)))
        v_fuller_l_dn = bm.verts.new(Vector((x_curve - th_x * 0.25, -w_y * 0.05, z)))
        v_fuller_l_up = bm.verts.new(Vector((x_curve - th_x * 0.45, -w_y * 0.20, z)))
        
        blade_slices.append((v_spine, v_fuller_r_up, v_fuller_r_dn, v_edge, v_fuller_l_dn, v_fuller_l_up, z, x_curve))
        
    bm.verts.ensure_lookup_table()
    
    # Connect habaki to first blade slice
    b0 = blade_slices[0]
    # bridge habaki ring to blade slice 0
    f_h0 = bm.faces.new([habaki_ring[0], habaki_ring[1], b0[1], b0[0]])
    f_h1 = bm.faces.new([habaki_ring[1], habaki_ring[2], b0[2], b0[1]])
    f_h2 = bm.faces.new([habaki_ring[2], habaki_ring[3], b0[3], b0[2]])
    f_h3 = bm.faces.new([habaki_ring[3], habaki_ring[4], b0[4], b0[3]])
    f_h4 = bm.faces.new([habaki_ring[4], habaki_ring[5], b0[5], b0[4]])
    f_h5 = bm.faces.new([habaki_ring[5], habaki_ring[0], b0[0], b0[5]])
    for f in (f_h0, f_h1, f_h2, f_h3, f_h4, f_h5):
        f.material_index = 0
        
    # Connect blade slices along length
    for ib in range(n_blade_slices):
        s1 = blade_slices[ib]
        s2 = blade_slices[ib + 1]
        tb = ib / float(n_blade_slices)
        
        # 1. Spine panel: s1[0], s2[0], s2[1], s1[1] -> M_Boss01_DexBlade (slot 0)
        f_sp_r = bm.faces.new([s1[0], s2[0], s2[1], s1[1]])
        f_sp_r.material_index = 0
        
        # 2. Fuller glow panel: s1[1], s2[1], s2[2], s1[2]
        # In lower 75% of blade, fuller glows with amber emission! (slot 2)
        f_glow_r = bm.faces.new([s1[1], s2[1], s2[2], s1[2]])
        f_glow_r.material_index = 2 if (0.05 <= tb <= 0.80) else 0
        
        # 3. Main blade bevel to edge: s1[2], s2[2], s2[3], s1[3] -> slot 0
        f_edge_r = bm.faces.new([s1[2], s2[2], s2[3], s1[3]])
        f_edge_r.material_index = 0
        
        # 4. Left side bevel to edge: s1[3], s2[3], s2[4], s1[4] -> slot 0
        f_edge_l = bm.faces.new([s1[3], s2[3], s2[4], s1[4]])
        f_edge_l.material_index = 0
        
        # 5. Left fuller glow panel: s1[4], s2[4], s2[5], s1[5] -> slot 2
        f_glow_l = bm.faces.new([s1[4], s2[4], s2[5], s1[5]])
        f_glow_l.material_index = 2 if (0.05 <= tb <= 0.80) else 0
        
        # 6. Left spine panel: s1[5], s2[5], s2[0], s1[0] -> slot 0
        f_sp_l = bm.faces.new([s1[5], s2[5], s2[0], s1[0]])
        f_sp_l.material_index = 0
        
    # Cap tip (Kissaki)
    s_tip = blade_slices[-1]
    v_kissaki_tip = bm.verts.new(Vector((s_tip[7], 0.0, 82.0)))
    f_tip1 = bm.faces.new([s_tip[0], s_tip[1], v_kissaki_tip])
    f_tip2 = bm.faces.new([s_tip[1], s_tip[2], v_kissaki_tip])
    f_tip3 = bm.faces.new([s_tip[2], s_tip[3], v_kissaki_tip])
    f_tip4 = bm.faces.new([s_tip[3], s_tip[4], v_kissaki_tip])
    f_tip5 = bm.faces.new([s_tip[4], s_tip[5], v_kissaki_tip])
    f_tip6 = bm.faces.new([s_tip[5], s_tip[0], v_kissaki_tip])
    for f in (f_tip1, f_tip2, f_tip3, f_tip4, f_tip5, f_tip6):
        f.material_index = 0
        
    mesh = bpy.data.meshes.new(obj_name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(obj_name, mesh)
    scene.collection.objects.link(obj)
    
    # Get or create materials without duplicate suffixes
    def get_or_create_mat(mat_name, base_col, metal, rough, is_glow=False):
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(mat_name)
            mat.use_nodes = True
            if is_glow:
                mat.node_tree.nodes.clear()
                out_node = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
                em_node = mat.node_tree.nodes.new('ShaderNodeEmission')
                em_node.inputs['Color'].default_value = (1.0, 0.38, 0.0, 1.0)
                em_node.inputs['Strength'].default_value = 25.0
                mat.node_tree.links.new(em_node.outputs['Emission'], out_node.inputs['Surface'])
            else:
                bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
                bsdf.inputs['Base Color'].default_value = base_col
                bsdf.inputs['Metallic'].default_value = metal
                bsdf.inputs['Roughness'].default_value = rough
        return mat
        
    mat_blade = get_or_create_mat("M_Boss01_DexBlade", (0.78, 0.80, 0.82, 1.0), 0.95, 0.22)
    mat_guard = get_or_create_mat("M_Boss01_DexGuard_Grip", (0.10, 0.10, 0.11, 1.0), 0.8, 0.45)
    mat_glow = get_or_create_mat("M_Boss01_DexBlade_Glow", None, None, None, is_glow=True)
    
    mesh.materials.append(mat_blade)
    mesh.materials.append(mat_guard)
    mesh.materials.append(mat_glow)
    
    # 7 child sockets matching SM_Boss01_Greatsword:
    # BladeStart, MiddleSocket, BladeEnd, Weapon_Start, Weapon_End, TrailStartSocket, TrailEndSocket
    mid_idx = n_blade_slices // 2
    mid_slice = blade_slices[mid_idx]
    
    # Remove any existing socket empties in scene/data to avoid .001 suffixes
    for o in list(bpy.data.objects):
        if o.name.startswith("SOCKET_"):
            bpy.data.objects.remove(o, do_unlink=True)
            
    sockets_info = [
        ("SOCKET_BladeStart", (0.0, 0.0, 2.0)),
        ("SOCKET_MiddleSocket", (mid_slice[7], 0.0, mid_slice[6])),
        ("SOCKET_BladeEnd", (blade_slices[-1][7], 0.0, 81.5)),
        ("SOCKET_Weapon_Start", (0.0, 0.0, 2.0)),
        ("SOCKET_Weapon_End", (blade_slices[-1][7], 0.0, 82.0)),
        ("SOCKET_TrailStartSocket", (0.0, 0.0, 2.0)),
        ("SOCKET_TrailEndSocket", (blade_slices[-1][7], 0.0, 82.0))
    ]
    
    created_sockets = []
    for s_name, s_loc in sockets_info:
        empty = bpy.data.objects.new(s_name, None)
        empty.empty_display_type = 'ARROWS'
        empty.empty_display_size = 4.0
        empty.location = s_loc
        empty.parent = obj
        scene.collection.objects.link(empty)
        created_sockets.append(empty)
        
    # Verify transforms: identity
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    
    # Export FBX
    fbx_out = os.path.join(out_dir, f"{obj_name}.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    for em in created_sockets:
        em.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    bpy.ops.export_scene.fbx(
        filepath=fbx_out,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_UNITS',
        bake_space_transform=True,
        axis_forward='-Z',
        axis_up='Y',
        object_types={'MESH', 'EMPTY'},
        bake_anim=False
    )
    
    v_z = [v.co.z for v in mesh.vertices]
    v_x = [v.co.x for v in mesh.vertices]
    v_y = [v.co.y for v in mesh.vertices]
    slot_counts = {m.name: sum(1 for p in mesh.polygons if p.material_index == idx) for idx, m in enumerate(mesh.materials)}
    
    return {
        "file": fbx_out,
        "length_cm": round(max(v_z) - min(v_z), 2),
        "z_span": [round(min(v_z), 2), round(max(v_z), 2)],
        "x_span": [round(min(v_x), 2), round(max(v_x), 2)],
        "y_span": [round(min(v_y), 2), round(max(v_y), 2)],
        "polygons": len(mesh.polygons),
        "slot_counts": slot_counts,
        "sockets": len(created_sockets)
    }

res_l = build_sword("L", mirror_x=True)
res_r = build_sword("R", mirror_x=False)

result = {
    "DexSword_L": res_l,
    "DexSword_R": res_r
}
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
