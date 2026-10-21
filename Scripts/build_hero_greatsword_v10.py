import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix

# Create fresh scene
scene = bpy.data.scenes.new("Scene_Greatsword")
bpy.context.window.scene = scene
scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01

# Purge any objects across all data with conflicting names
for o in list(bpy.data.objects):
    if o.name.startswith("SM_Boss01_Greatsword") or o.name.startswith("SOCKET_"):
        bpy.data.objects.remove(o, do_unlink=True)

# Purge meshes with same name
for m in list(bpy.data.meshes):
    if m.name.startswith("SM_Boss01_Greatsword"):
        bpy.data.meshes.remove(m, do_unlink=True)

for o in list(scene.objects):
    bpy.data.objects.remove(o, do_unlink=True)

bm = bmesh.new()

# Material slot indices:
# Slot 0: M_Boss01_Blade
# Slot 1: M_Boss01_Guard_Grip
# Slot 2: M_Boss01_Blade_Glow

# Coordinate System:
# Grip center is at Z = 0.0.
# Pommel is at Z = -21.33 to -16.50
# Grip is at Z = -16.50 to +1.00
# Guard Hub is at Z = +1.00 to +11.00
# 5 Crown Spires rise from Z ~ 10.0 to Z ~ 20.0-22.0 (height 9.5 to 11.0 cm)
# Quillons sweep outward to X = -31.0 and +31.0 (span 62.0 cm, thickness Y = 7.64 cm)
# Blade starts at Z = +1.0 (ricasso) / +15.0 (cutting edge) up to Z = 163.30 (span 184.63 cm)

# -------------------------------------------------------------
# 1. POMMEL: Z = -21.33 to -16.50 cm (12-sided faceted cathedral pommel)
# -------------------------------------------------------------
n_pom = 12
v_pom_bot = bm.verts.new(Vector((0.0, 0.0, -21.33)))
pom_r1 = [bm.verts.new(Vector((3.4 * math.cos(2*math.pi*i/n_pom), 2.8 * math.sin(2*math.pi*i/n_pom), -19.0))) for i in range(n_pom)]
pom_r2 = [bm.verts.new(Vector((2.2 * math.cos(2*math.pi*i/n_pom), 1.8 * math.sin(2*math.pi*i/n_pom), -16.5))) for i in range(n_pom)]

bm.verts.ensure_lookup_table()
for i in range(n_pom):
    ni = (i + 1) % n_pom
    f1 = bm.faces.new([v_pom_bot, pom_r1[i], pom_r1[ni]])
    f2 = bm.faces.new([pom_r1[i], pom_r1[ni], pom_r2[ni], pom_r2[i]])
    f1.material_index = 1
    f2.material_index = 1

# -------------------------------------------------------------
# 2. GRIP: Z = -16.50 to +1.00 cm (14 rings, fluted leather wrap)
# -------------------------------------------------------------
n_grip_levels = 14
grip_rings = [pom_r2]
for ig in range(1, n_grip_levels):
    t = ig / (n_grip_levels - 1)
    z = -16.50 * (1.0 - t) + 1.00 * t
    r = 2.1 + 0.15 * math.sin(t * math.pi)
    ring = []
    for i in range(n_pom):
        ang = 2 * math.pi * i / n_pom
        wrap_bump = 0.12 * math.sin(ang * 2.0 + t * 8.0 * math.pi)
        ring.append(bm.verts.new(Vector(((r + wrap_bump) * 1.05 * math.cos(ang), (r + wrap_bump) * 0.90 * math.sin(ang), z))))
    grip_rings.append(ring)

bm.verts.ensure_lookup_table()
for ig in range(n_grip_levels - 1):
    for i in range(n_pom):
        ni = (i + 1) % n_pom
        f = bm.faces.new([grip_rings[ig][i], grip_rings[ig][ni], grip_rings[ig + 1][ni], grip_rings[ig + 1][i]])
        f.material_index = 1

# -------------------------------------------------------------
# 3. CROSSGUARD HUB: Z = +1.00 to +11.00 cm (24 perimeter vertices)
# -------------------------------------------------------------
n_hub = 24
hub_bot = [bm.verts.new(Vector((6.8 * math.cos(2*math.pi*i/n_hub), 3.82 * math.sin(2*math.pi*i/n_hub), 1.0))) for i in range(n_hub)]
hub_mid = [bm.verts.new(Vector((7.2 * math.cos(2*math.pi*i/n_hub), 3.82 * math.sin(2*math.pi*i/n_hub), 6.0))) for i in range(n_hub)]
hub_top = [bm.verts.new(Vector((7.0 * math.cos(2*math.pi*i/n_hub), 3.80 * math.sin(2*math.pi*i/n_hub), 11.0))) for i in range(n_hub)]

bm.verts.ensure_lookup_table()
# Connect grip top (12 verts) to hub bottom (24 verts)
for i in range(n_pom):
    ni = (i + 1) % n_pom
    h0, h1, h2 = i * 2, (i * 2 + 1) % n_hub, ((i + 1) * 2) % n_hub
    f1 = bm.faces.new([grip_rings[-1][i], grip_rings[-1][ni], hub_bot[h2], hub_bot[h1]])
    f2 = bm.faces.new([grip_rings[-1][i], hub_bot[h1], hub_bot[h0]])
    f1.material_index = 1
    f2.material_index = 1

# Hub walls (leave gaps at X extremes for quillons: i=0..2 and i=12..14)
for i in range(n_hub):
    ni = (i + 1) % n_hub
    if i not in [0, 1, 12, 13]:
        f1 = bm.faces.new([hub_bot[i], hub_bot[ni], hub_mid[ni], hub_mid[i]])
        f2 = bm.faces.new([hub_mid[i], hub_mid[ni], hub_top[ni], hub_top[i]])
        f1.material_index = 1
        f2.material_index = 1

# -------------------------------------------------------------
# 4. THICK QUILLONS WELDED TO HUB (span 62.0 cm: X = -31.0 to +31.0)
# -------------------------------------------------------------
for sign_x, h_root in [(1.0, [hub_bot[0], hub_top[0], hub_top[2], hub_bot[2]]),
                       (-1.0, [hub_bot[12], hub_top[12], hub_top[14], hub_bot[14]])]:
    q_profile = [
        (sign_x * 12.0, 3.5, 5.5, 3.0),
        (sign_x * 18.0, 3.2, 5.2, 2.7),
        (sign_x * 23.5, 2.8, 6.5, 2.4),
        (sign_x * 28.0, 2.2, 8.8, 2.0),
        (sign_x * 30.2, 1.4, 10.8, 1.4),
        (sign_x * 31.0, 0.6, 11.5, 0.6),
    ]
    prev_qr = h_root
    for x, yt, zc, zt in q_profile:
        qr = [
            bm.verts.new(Vector((x, -yt, zc))),
            bm.verts.new(Vector((x, 0.0, zc + zt))),
            bm.verts.new(Vector((x, yt, zc))),
            bm.verts.new(Vector((x, 0.0, zc - zt))),
        ]
        for j in range(4):
            nj = (j + 1) % 4
            f = bm.faces.new([prev_qr[j], prev_qr[nj], qr[nj], qr[j]])
            f.material_index = 1
        prev_qr = qr
    v_tip = bm.verts.new(Vector((sign_x * 31.0, 0.0, 12.0)))
    for j in range(4):
        nj = (j + 1) % 4
        f = bm.faces.new([prev_qr[j], prev_qr[nj], v_tip])
        f.material_index = 1

# -------------------------------------------------------------
# 5. FIVE PROMINENT GUARD SPIRES (> 8 cm tall, readable at 8 m)
# -------------------------------------------------------------
# Spires are 3D gothic crown pyramids rising from guard top (Z = 10 to 11 cm)
# Spire 1 (outer left):  X = -17.0, Y = +1.5, base Z = 9.5,  tip Z = 19.5 (10.0 cm tall)
# Spire 2 (inner left):  X =  -8.0, Y = -1.2, base Z = 10.5, tip Z = 21.0 (10.5 cm tall)
# Spire 3 (center peak): X =   0.0, Y = -2.5, base Z = 11.0, tip Z = 22.5 (11.5 cm tall)
# Spire 4 (inner right): X =  +8.0, Y = -1.2, base Z = 10.5, tip Z = 21.0 (10.5 cm tall)
# Spire 5 (outer right): X = +17.0, Y = +1.5, base Z = 9.5,  tip Z = 19.5 (10.0 cm tall)
spire_specs = [
    (-17.0,  1.5,  9.5, 19.5, 2.2, 1.8),
    ( -8.0, -1.2, 10.5, 21.0, 2.6, 2.0),
    (  0.0, -2.5, 11.0, 22.5, 3.0, 2.2),
    (  8.0, -1.2, 10.5, 21.0, 2.6, 2.0),
    ( 17.0,  1.5,  9.5, 19.5, 2.2, 1.8)
]

for sx, sy, sbz, stz, sw, sth in spire_specs:
    v0 = bm.verts.new(Vector((sx - sw*0.5, sy - sth*0.5, sbz)))
    v1 = bm.verts.new(Vector((sx + sw*0.5, sy - sth*0.5, sbz)))
    v2 = bm.verts.new(Vector((sx + sw*0.5, sy + sth*0.5, sbz)))
    v3 = bm.verts.new(Vector((sx - sw*0.5, sy + sth*0.5, sbz)))
    v_tip = bm.verts.new(Vector((sx, sy, stz)))
    
    # 4 faces of pyramid
    f0 = bm.faces.new([v0, v1, v_tip])
    f1 = bm.faces.new([v1, v2, v_tip])
    f2 = bm.faces.new([v2, v3, v_tip])
    f3 = bm.faces.new([v3, v0, v_tip])
    for f in [f0, f1, f2, f3]:
        f.material_index = 1

# -------------------------------------------------------------
# 6. STEPPED RICASSO & BLADE WITH DEEP RECESSED FULLER
# -------------------------------------------------------------
# Z stations from Z = 11.0 to Z = 163.30 cm (origin at grip)
blade_levels = [
    # (z, hw, y_thick, is_glow, has_flukes)
    (11.0,   5.8, 1.80, False),  # Ricasso collar
    (15.0,   5.6, 1.70, True),   # BladeStart / Weapon Start / TrailStartSocket
    (21.0,   5.5, 1.60, True),
    (27.0,   7.8, 1.60, True),   # Parrying flukes (stepped ricasso)
    (31.0,   9.2, 1.60, True),   # Fluke tips
    (33.0,   6.2, 1.50, True),   # Post-fluke waist
    (38.0,   5.5, 1.50, True),   # Blade proper
    (55.0,   5.4, 1.40, True),
    (78.0,   5.2, 1.35, True),   # MiddleSocket
    (98.0,   5.0, 1.30, True),
    (118.0,  4.6, 1.20, True),
    (138.0,  4.0, 1.10, True),
    (140.0,  3.8, 1.05, True),   # BladeEnd
    (142.0,  3.6, 1.00, True),   # Weapon End / TrailEndSocket
    (148.0,  3.2, 0.90, False),  # Fuller ends
    (155.0,  2.0, 0.70, False),  # Tip taper
    (163.30, 0.04, 0.08, False)  # Apex piercer point
]

blade_rings = []
for z, hw, y_thick, is_glow in blade_levels:
    x_edge = hw
    if is_glow:
        x_f_sh = min(1.5, hw * 0.35)
        x_f_fl = x_f_sh * 0.55
        y_f_fl = max(0.18, y_thick * 0.25) # Deep fuller recess (1.2 to 1.4 cm deep!)
    else:
        x_f_sh = hw * 0.4
        x_f_fl = x_f_sh * 0.5
        y_f_fl = y_thick * 0.85
    
    ring = [
        bm.verts.new(Vector((-x_edge, 0.0, z))),
        bm.verts.new(Vector((-x_f_sh, y_thick, z))),
        bm.verts.new(Vector((-x_f_fl, y_f_fl, z))),
        bm.verts.new(Vector((0.0, y_f_fl, z))),
        bm.verts.new(Vector((x_f_fl, y_f_fl, z))),
        bm.verts.new(Vector((x_f_sh, y_thick, z))),
        bm.verts.new(Vector((x_edge, 0.0, z))),
        bm.verts.new(Vector((x_f_sh, -y_thick, z))),
        bm.verts.new(Vector((x_f_fl, -y_f_fl, z))),
        bm.verts.new(Vector((0.0, -y_f_fl, z))),
        bm.verts.new(Vector((-x_f_fl, -y_f_fl, z))),
        bm.verts.new(Vector((-x_f_sh, -y_thick, z))),
    ]
    blade_rings.append((z, ring, is_glow))

bm.verts.ensure_lookup_table()

# Bridge hub top (24 verts) to blade root (12 verts)
for i in range(12):
    ni = (i + 1) % 12
    h0 = i * 2
    h1 = (i * 2 + 1) % n_hub
    h2 = ((i + 1) * 2) % n_hub
    f1 = bm.faces.new([blade_rings[0][1][i], blade_rings[0][1][ni], hub_top[h2], hub_top[h1]])
    f2 = bm.faces.new([blade_rings[0][1][i], hub_top[h1], hub_top[h0]])
    f1.material_index = 0
    f2.material_index = 0

for l in range(len(blade_levels) - 1):
    z0, r0, g0 = blade_rings[l]
    z1, r1, g1 = blade_rings[l + 1]
    is_active_glow = (g0 and g1)
    for j in range(12):
        nj = (j + 1) % 12
        f = bm.faces.new([r0[j], r0[nj], r1[nj], r1[j]])
        is_fuller_floor = j in [2, 3, 8, 9]
        if is_active_glow and is_fuller_floor:
            f.material_index = 2 # M_Boss01_Blade_Glow (inside recessed groove only!)
        else:
            f.material_index = 0 # M_Boss01_Blade

# Tip closure
v_apex = bm.verts.new(Vector((0.0, 0.0, 163.30)))
for j in range(12):
    nj = (j + 1) % 12
    f = bm.faces.new([blade_rings[-1][1][j], blade_rings[-1][1][nj], v_apex])
    f.material_index = 0

bm.normal_update()

# Create / retrieve materials with clean names (NO BLENDER SUFFIXES)
def get_clean_mat(name, color, metallic, roughness, emission=None):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        if emission:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = emission[0]
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = emission[1]
    return mat

mat_blade = get_clean_mat("M_Boss01_Blade", (0.12, 0.12, 0.14, 1.0), 0.94, 0.28)
mat_guard = get_clean_mat("M_Boss01_Guard_Grip", (0.06, 0.06, 0.07, 1.0), 0.88, 0.40)
mat_glow = get_clean_mat("M_Boss01_Blade_Glow", (1.0, 0.38, 0.03, 1.0), 0.10, 0.20, ((1.0, 0.42, 0.04, 1.0), 16.0))

sw_mesh = bpy.data.meshes.new("SM_Boss01_Greatsword")
sw_mesh.materials.append(mat_blade)
sw_mesh.materials.append(mat_guard)
sw_mesh.materials.append(mat_glow)

bm.to_mesh(sw_mesh)
bm.free()

sw_obj = bpy.data.objects.new("SM_Boss01_Greatsword", sw_mesh)
scene.collection.objects.link(sw_obj)

for p in sw_mesh.polygons:
    p.use_smooth = True

# Add 7 socket empties as children of SM_Boss01_Greatsword
# Positions matching SM_Boss01_Greatsword_Sockets.txt exactly:
sockets_info = [
    ("SOCKET_BladeStart", (0.0, 0.0, 15.00)),
    ("SOCKET_MiddleSocket", (0.0, 0.0, 78.00)),
    ("SOCKET_BladeEnd", (0.0, 0.0, 140.00)),
    ("SOCKET_Weapon_Start", (0.0, 0.0, 15.00)),
    ("SOCKET_Weapon_End", (0.0, 0.0, 142.00)),
    ("SOCKET_TrailStartSocket", (0.0, 0.0, 15.00)),
    ("SOCKET_TrailEndSocket", (0.0, 0.0, 142.00))
]

created_sockets = []
for s_name, s_loc in sockets_info:
    empty = bpy.data.objects.new(s_name, None)
    empty.empty_display_type = 'ARROWS'
    empty.empty_display_size = 5.0
    empty.location = s_loc
    empty.parent = sw_obj
    scene.collection.objects.link(empty)
    created_sockets.append(empty)

# Verify dimensions and bounds
dims = [round(d, 3) for d in sw_obj.dimensions]
v_x = [v.co.x for v in sw_mesh.vertices]
v_y = [v.co.y for v in sw_mesh.vertices]
v_z = [v.co.z for v in sw_mesh.vertices]
poly_count = len(sw_mesh.polygons)
slot_counts = {m.name: sum(1 for p in sw_mesh.polygons if p.material_index == idx) for idx, m in enumerate(sw_mesh.materials)}

# Export to Import/Boss01/Weapons/SM_Boss01_Greatsword.fbx
out_fbx = "c:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Boss01/Weapons/SM_Boss01_Greatsword.fbx"

bpy.ops.object.select_all(action='DESELECT')
sw_obj.select_set(True)
for em in created_sockets:
    em.select_set(True)
bpy.context.view_layer.objects.active = sw_obj

bpy.ops.export_scene.fbx(
    filepath=out_fbx,
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

result = {
    "dimensions": dims,
    "x_span": [round(min(v_x), 3), round(max(v_x), 3), round(max(v_x) - min(v_x), 3)],
    "y_span": [round(min(v_y), 3), round(max(v_y), 3), round(max(v_y) - min(v_y), 3)],
    "z_span": [round(min(v_z), 3), round(max(v_z), 3), round(max(v_z) - min(v_z), 3)],
    "polygon_count": poly_count,
    "slot_counts": slot_counts,
    "socket_count": len(created_sockets)
}
"""

res = execute_blender(code)
print("Execution result:")
import json
print(json.dumps(res, indent=2))
