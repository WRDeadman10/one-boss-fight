import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix

# Clean all conflicting objects across all datablocks first
for o in list(bpy.data.objects):
    if o.name.startswith("root") or o.name.startswith("SK_Boss01_Crown") or o.name.startswith("SKM_"):
        bpy.data.objects.remove(o, do_unlink=True)
for a in list(bpy.data.armatures):
    if a.name.startswith("root") or a.name.startswith("SKM_"):
        bpy.data.armatures.remove(a, do_unlink=True)
for m in list(bpy.data.meshes):
    if m.name.startswith("SK_Boss01_Crown"):
        bpy.data.meshes.remove(m, do_unlink=True)

# Create fresh scene
scene = bpy.data.scenes.new("Scene_Crown")
bpy.context.window.scene = scene
scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01

ref_path = "c:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx"
bpy.ops.import_scene.fbx(filepath=ref_path)

# Enforce FPS=30 after FBX import
scene.render.fps = 30
scene.render.fps_base = 1.0

arm = next(o for o in scene.objects if o.type == 'ARMATURE')
arm.name = "root"
arm.data.name = "root"
arm.data.pose_position = 'REST'
bpy.context.view_layer.objects.active = arm

# Remove any meshes imported with reference
for o in list(scene.objects):
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)

# Build Hero Crown seated directly on head cowl
# Head top vertex: Z = 160.28 cm. Center: X = 0.0, Y = -13.0 cm.
# Crown base ring sits at Z = 155.0 cm (5.28 cm overlap into cowl).
bm = bmesh.new()

n_ring = 24
cx = 0.0
cy = -13.0
rx_base = 11.2
ry_base = 13.8

# 1. Base ring outer and inner bands (double-walled circlet for thickness)
z_bot = 155.0
z_mid = 158.0
z_top = 161.0

r_bot_out = []
r_bot_in  = []
r_mid_out = []
r_mid_in  = []
r_top_out = []
r_top_in  = []

for i in range(n_ring):
    theta = 2.0 * math.pi * i / n_ring
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    
    # Outer radius
    xo = cx + (rx_base + 0.9) * cos_t
    yo = cy + (ry_base + 0.9) * sin_t
    
    # Inner radius
    xi = cx + rx_base * cos_t
    yi = cy + ry_base * sin_t
    
    r_bot_out.append(bm.verts.new(Vector((xo, yo, z_bot))))
    r_bot_in.append(bm.verts.new(Vector((xi, yi, z_bot))))
    
    r_mid_out.append(bm.verts.new(Vector((xo + 0.3 * cos_t, yo + 0.3 * sin_t, z_mid))))
    r_mid_in.append(bm.verts.new(Vector((xi, yi, z_mid))))
    
    r_top_out.append(bm.verts.new(Vector((xo, yo, z_top))))
    r_top_in.append(bm.verts.new(Vector((xi, yi, z_top))))

bm.verts.ensure_lookup_table()

# Bridge ring levels
for i in range(n_ring):
    ni = (i + 1) % n_ring
    # Bottom closure face
    f_bot = bm.faces.new([r_bot_in[i], r_bot_in[ni], r_bot_out[ni], r_bot_out[i]])
    # Outer wall bot-mid
    f_ow1 = bm.faces.new([r_bot_out[i], r_bot_out[ni], r_mid_out[ni], r_mid_out[i]])
    # Outer wall mid-top
    f_ow2 = bm.faces.new([r_mid_out[i], r_mid_out[ni], r_top_out[ni], r_top_out[i]])
    # Inner wall bot-mid
    f_iw1 = bm.faces.new([r_bot_in[ni], r_bot_in[i], r_mid_in[i], r_mid_in[ni]])
    # Inner wall mid-top
    f_iw2 = bm.faces.new([r_mid_in[ni], r_mid_in[i], r_top_in[i], r_top_in[ni]])
    # Top closure face between spires
    f_top = bm.faces.new([r_top_out[i], r_top_out[ni], r_top_in[ni], r_top_in[i]])
    
    for f in [f_bot, f_ow1, f_ow2, f_iw1, f_iw2, f_top]:
        f.material_index = 0 # Gold / Iron base

# 2. Gothic cathedral crown spires (8 spires around perimeter)
# Indices in ring:
# i=18: front center peak (theta = 3pi/2, pointing towards front -Y)
# i=15, 21: front-left and front-right
# i=12, 0: temple left and temple right
# i=3, 9: back-left and back-right
# i=6: back broken crown spire
spire_rims = [
    (17, 19, 178.0, 1.0),   # 1. Front center majestic peak (Z = 178.0 cm)
    (20, 22, 172.5, 0.8),   # 2. Front-left spire
    (14, 16, 172.5, 0.8),   # 3. Front-right spire
    (23,  1, 168.0, 0.6),   # 4. Temple left
    (11, 13, 168.0, 0.6),   # 5. Temple right
    ( 2,  4, 170.0, 0.7),   # 6. Rear left
    ( 8, 10, 170.0, 0.7),   # 7. Rear right
    ( 5,  7, 164.5, 0.5)    # 8. Rear broken/jagged spire (fallen king motif)
]

for i1, i2, tip_z, tip_w in spire_rims:
    # Outer and inner rim vertices
    vo1 = r_top_out[i1]
    vo2 = r_top_out[i2]
    vi1 = r_top_in[i1]
    vi2 = r_top_in[i2]
    
    mid_cos = (vo1.co.x + vo2.co.x) * 0.5 - cx
    mid_sin = (vo1.co.y + vo2.co.y) * 0.5 - cy
    length = math.sqrt(mid_cos*mid_cos + mid_sin*mid_sin)
    dir_x = mid_cos / length
    dir_y = mid_sin / length
    
    # Outer tip and inner tip for 3D thickness
    tip_out = bm.verts.new(Vector((cx + (rx_base + 0.6) * dir_x, cy + (ry_base + 0.6) * dir_y, tip_z)))
    tip_in  = bm.verts.new(Vector((cx + rx_base * dir_x, cy + ry_base * dir_y, tip_z - 0.5)))
    
    sf_out = bm.faces.new([vo1, vo2, tip_out])
    sf_in  = bm.faces.new([vi2, vi1, tip_in])
    sf_l   = bm.faces.new([vo1, tip_out, tip_in, vi1])
    sf_r   = bm.faces.new([vo2, vi2, tip_in, tip_out])
    
    for f in [sf_out, sf_in, sf_l, sf_r]:
        f.material_index = 0

# 3. Inset ember jewels along mid-circlet (Material Slot 1: M_Boss01_Blade_Glow / EmberGlow)
# Place 6 glowing ember gems between main spires
gem_indices = [16, 19, 22, 1, 10, 13]
for gi in gem_indices:
    g_vo1 = r_mid_out[gi]
    g_vo2 = r_mid_out[(gi + 1) % n_ring]
    gx = (g_vo1.co.x + g_vo2.co.x) * 0.5
    gy = (g_vo1.co.y + g_vo2.co.y) * 0.5
    # Direction outward
    dx = gx - cx
    dy = gy - cy
    dl = math.sqrt(dx*dx + dy*dy)
    g_peak = bm.verts.new(Vector((gx + (dx/dl)*0.55, gy + (dy/dl)*0.55, z_mid)))
    
    # Diamond gem facet
    gv_top = bm.verts.new(Vector((gx, gy, z_mid + 1.2)))
    gv_bot = bm.verts.new(Vector((gx, gy, z_mid - 1.2)))
    
    gf1 = bm.faces.new([g_vo1, g_peak, gv_top])
    gf2 = bm.faces.new([g_peak, g_vo2, gv_top])
    gf3 = bm.faces.new([g_vo1, gv_bot, g_peak])
    gf4 = bm.faces.new([g_peak, gv_bot, g_vo2])
    for gf in [gf1, gf2, gf3, gf4]:
        gf.material_index = 1 # Ember glow

bm.normal_update()

crown_mesh = bpy.data.meshes.new("SK_Boss01_Crown")
bm.to_mesh(crown_mesh)
bm.free()

crown_obj = bpy.data.objects.new("SK_Boss01_Crown", crown_mesh)
scene.collection.objects.link(crown_obj)

# Clean material slots
mat_metal = bpy.data.materials.get("M_Boss01_BlackPlate")
if not mat_metal:
    mat_metal = bpy.data.materials.new("M_Boss01_BlackPlate")
mat_glow = bpy.data.materials.get("M_Boss01_EmberGlow")
if not mat_glow:
    mat_glow = bpy.data.materials.new("M_Boss01_EmberGlow")
mat_trim = bpy.data.materials.get("M_Boss01_GoldTrim")
if not mat_trim:
    mat_trim = bpy.data.materials.new("M_Boss01_GoldTrim")

crown_mesh.materials.append(mat_metal)
crown_mesh.materials.append(mat_glow)
crown_mesh.materials.append(mat_trim)

for p in crown_mesh.polygons:
    p.use_smooth = True

# Skin to head bone
crown_obj.parent = arm
mod_arm = crown_obj.modifiers.new("Armature", 'ARMATURE')
mod_arm.object = arm

# Create vertex group for all bones, weight 1.0 to 'head'
for b in arm.data.bones:
    vg = crown_obj.vertex_groups.new(name=b.name)
    if b.name == 'head':
        all_indices = list(range(len(crown_mesh.vertices)))
        vg.add(all_indices, 1.0, 'REPLACE')

bpy.context.view_layer.objects.active = crown_obj
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
crown_obj.select_set(True)

out_crown_fbx = "c:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Boss01/SK_Boss01_Crown.fbx"

bpy.ops.export_scene.fbx(
    filepath=out_crown_fbx,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',
    axis_forward='-Z',
    axis_up='Y',
    object_types={'ARMATURE', 'MESH'},
    use_mesh_modifiers=True,
    add_leaf_bones=False,
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    bake_anim=False
)

c_zs = [v.co.z for v in crown_mesh.vertices]
result = {
    "verts": len(crown_mesh.vertices),
    "polys": len(crown_mesh.polygons),
    "z_min": round(min(c_zs), 2),
    "z_max": round(max(c_zs), 2),
    "z_span": round(max(c_zs) - min(c_zs), 2)
}
"""

res = execute_blender(code)
print("Seated crown result:", res.get("result"))
print("Stdout:", res.get("stdout"))
if res.get("stderr"):
    print("ERR:", res.get("stderr"))
