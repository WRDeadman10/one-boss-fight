"""
generate_master_builds.py - Master builder for all 6 detailed character builds in Blender.
Produces true-scale, culturally authentic, fully rigged characters for UE5 SK_CombatMannequin.
"""

import sys
import os
import math

sys.path.append(r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Scripts\CharacterBuilders")
import bpy
from mathutils import Matrix, Vector
import builder_common as bc

FBX_MANNY = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
FBX_QUINN = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_Quinn.fbx"
FBX_GREY  = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Greystone.fbx"
OUT_DIR   = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds"

def render_preview(character_name):
    """Renders a front preview of the character to disk."""
    cam = bpy.context.scene.camera
    if not cam:
        cam_data = bpy.data.cameras.new("Cam")
        cam = bpy.data.objects.new("Cam", cam_data)
        bpy.context.scene.collection.objects.link(cam)
        bpy.context.scene.camera = cam

    # Front camera looking from -Y towards +Y
    cam.location = (0.0, -2.8, 1.25)
    cam.rotation_euler = (math.radians(88), 0.0, 0.0)

    for l in [o for o in bpy.data.objects if o.type == 'LIGHT']:
        bpy.data.objects.remove(l, do_unlink=True)

    light_data = bpy.data.lights.new(name="FrontLight", type='AREA')
    light_data.energy = 800.0
    light_data.size = 2.0
    light = bpy.data.objects.new("FrontLight", light_data)
    bpy.context.scene.collection.objects.link(light)
    light.location = (0.6, -2.0, 1.6)
    light.rotation_euler = (math.radians(45), math.radians(15), 0.0)

    rim_data = bpy.data.lights.new(name="RimLight", type='AREA')
    rim_data.energy = 500.0
    rim_data.size = 2.0
    rim = bpy.data.objects.new("RimLight", rim_data)
    bpy.context.scene.collection.objects.link(rim)
    rim.location = (-0.6, 1.8, 1.6)

    out_png = os.path.join(OUT_DIR, f"preview_{character_name.lower()}.png")
    bpy.context.scene.render.filepath = out_png
    bpy.context.scene.render.resolution_x = 720
    bpy.context.scene.render.resolution_y = 1080
    bpy.ops.render.render(write_still=True)
    return out_png

# -------------------------------------------------------------
# 1. BUILD VIKING
# -------------------------------------------------------------
def build_viking():
    arm, base_mesh = bc.load_base_model(FBX_MANNY)
    base_mesh.name = "Viking_Undersuit"
    
    mat_iron = bc.create_pbr_material("M_Viking_Iron", base_color=(0.28, 0.29, 0.32, 1.0), metallic=0.94, roughness=0.32)
    mat_silver = bc.create_pbr_material("M_Viking_Silver", base_color=(0.86, 0.88, 0.90, 1.0), metallic=0.96, roughness=0.18)
    mat_leather = bc.create_pbr_material("M_Viking_Leather", base_color=(0.14, 0.08, 0.04, 1.0), metallic=0.02, roughness=0.68)
    mat_fur = bc.create_pbr_material("M_Viking_Fur", base_color=(0.36, 0.32, 0.28, 1.0), metallic=0.0, roughness=0.95)
    mat_wool = bc.create_pbr_material("M_Viking_Wool", base_color=(0.06, 0.16, 0.08, 1.0), metallic=0.0, roughness=0.85)
    mat_beard = bc.create_pbr_material("M_Viking_Beard", base_color=(0.32, 0.18, 0.07, 1.0), metallic=0.0, roughness=0.80)
    mat_shield_red = bc.create_pbr_material("M_Viking_ShieldPaint", base_color=(0.58, 0.08, 0.08, 1.0), metallic=0.05, roughness=0.55)
    
    bc.assign_material(base_mesh, mat_wool)
    created = []
    
    # Gjermundbu Helmet Dome
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=15.5, location=(0.0, -2.0, 172.0))
    helm = bpy.context.active_object
    helm.scale = (1.02, 1.15, 1.02)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(helm, mat_iron)
    bc.assign_rigid_weight(helm, "head")
    created.append(helm)
    
    # Helmet Rim Band
    bpy.ops.mesh.primitive_torus_add(major_radius=15.8, minor_radius=1.4, location=(0.0, -2.0, 166.0))
    helm_rim = bpy.context.active_object
    helm_rim.scale = (1.02, 1.15, 0.8)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(helm_rim, mat_silver)
    bc.assign_rigid_weight(helm_rim, "head")
    created.append(helm_rim)
    
    # Cross Bands
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.6, depth=33.0, location=(0.0, -2.0, 178.0), rotation=(1.5708, 0.0, 0.0))
    rib_fb = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(rib_fb, mat_silver)
    bc.assign_rigid_weight(rib_fb, "head")
    created.append(rib_fb)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.6, depth=33.0, location=(0.0, -2.0, 178.0), rotation=(0.0, 1.5708, 0.0))
    rib_lr = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(rib_lr, mat_silver)
    bc.assign_rigid_weight(rib_lr, "head")
    created.append(rib_lr)
    
    # Apex Spike
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=2.5, radius2=0.5, depth=6.0, location=(0.0, -2.0, 190.0))
    apex_spike = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(apex_spike, mat_silver)
    bc.assign_rigid_weight(apex_spike, "head")
    created.append(apex_spike)
    
    # Spectacle Ocular Eye Guards (In front at Y = -14.0)
    for side, x in [("L", 4.8), ("R", -4.8)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=4.2, minor_radius=1.2, location=(x, -14.0, 166.0), rotation=(1.5708, 0.0, 0.0))
        ocular = bpy.context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(ocular, mat_iron)
        bc.assign_rigid_weight(ocular, "head")
        created.append(ocular)
        
    # Nasal Guard
    bpy.ops.mesh.primitive_cube_add(size=6.0, location=(0.0, -15.2, 162.0))
    nasal = bpy.context.active_object
    nasal.scale = (0.32, 0.25, 1.8)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(nasal, mat_iron)
    bc.assign_rigid_weight(nasal, "head")
    created.append(nasal)
    
    # Chainmail Aventail
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=17.5, depth=18.0, location=(0.0, 0.0, 155.0))
    aventail = bpy.context.active_object
    aventail.scale = (1.05, 1.15, 1.0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(aventail, mat_iron)
    bc.assign_weighted_bones(aventail, {"neck_01": 0.6, "head": 0.4})
    created.append(aventail)
    
    # Braided Beard & Mustache
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=2.5, depth=14.0, location=(0.0, -13.5, 159.0), rotation=(0.0, 1.5708, 0.0))
    mustache = bpy.context.active_object
    mustache.scale = (1.0, 0.6, 0.8)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(mustache, mat_beard)
    bc.assign_rigid_weight(mustache, "head")
    created.append(mustache)
    
    bpy.ops.mesh.primitive_cube_add(size=14.0, location=(0.0, -11.0, 148.0))
    chin_beard = bpy.context.active_object
    chin_beard.scale = (1.1, 0.9, 1.4)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(chin_beard, mat_beard)
    bc.assign_rigid_weight(chin_beard, "head")
    created.append(chin_beard)
    
    # Dual Braided Plaits
    for side, x in [("L", 4.5), ("R", -4.5)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=2.8, depth=32.0, location=(x, -12.5, 134.0), rotation=(-0.20, 0.0, 0.0))
        braid = bpy.context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(braid, mat_beard)
        bc.assign_weighted_bones(braid, {"head": 0.6, "neck_01": 0.4})
        created.append(braid)
        
        for r_idx, r_z in [(0, 142.0), (1, 126.0)]:
            bpy.ops.mesh.primitive_torus_add(major_radius=2.8, minor_radius=0.8, location=(x, -13.0, r_z))
            b_ring = bpy.context.active_object
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bc.assign_material(b_ring, mat_silver)
            bc.assign_rigid_weight(b_ring, "head")
            created.append(b_ring)
            
    # Fur Shoulder Mantle
    bpy.ops.mesh.primitive_torus_add(major_radius=25.0, minor_radius=7.5, location=(0.0, -1.0, 146.0))
    fur_mantle = bpy.context.active_object
    fur_mantle.scale = (1.25, 1.05, 0.9)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(fur_mantle, mat_fur)
    bc.assign_weighted_bones(fur_mantle, {"spine_04": 0.3, "spine_05": 0.4, "clavicle_l": 0.15, "clavicle_r": 0.15})
    created.append(fur_mantle)
    
    # Fur Back Cape
    bpy.ops.mesh.primitive_cube_add(size=22.0, location=(0.0, 16.0, 128.0))
    fur_cape = bpy.context.active_object
    fur_cape.scale = (1.5, 0.4, 2.4)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(fur_cape, mat_fur)
    bc.assign_weighted_bones(fur_cape, {"spine_03": 0.4, "spine_04": 0.4, "spine_05": 0.2})
    created.append(fur_cape)
    
    # Raven Brooches
    for side, x in [("L", 11.0), ("R", -11.0)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=3.8, depth=1.8, location=(x, -15.0, 144.0), rotation=(1.5708, 0.0, 0.0))
        brooch = bpy.context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(brooch, mat_silver)
        bc.assign_weighted_bones(brooch, {"spine_05": 0.5, f"clavicle_{side.lower()}": 0.5})
        created.append(brooch)
        
    # Lamellar Cuirass
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=24.0, depth=36.0, location=(0.0, -2.0, 122.0))
    cuirass = bpy.context.active_object
    cuirass.scale = (1.12, 0.88, 1.0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(cuirass, mat_leather)
    bc.assign_weighted_bones(cuirass, {"spine_01": 0.15, "spine_02": 0.25, "spine_03": 0.35, "spine_04": 0.15, "spine_05": 0.10})
    created.append(cuirass)
    
    # Lamellar Plates on Chest
    for row in range(3):
        z_lam = 133.0 - (row * 7.0)
        for col in range(4):
            x_lam = -12.0 + (col * 8.0)
            bpy.ops.mesh.primitive_cube_add(size=5.0, location=(x_lam, -17.0, z_lam))
            lam_p = bpy.context.active_object
            lam_p.scale = (1.2, 0.15, 1.0)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bc.assign_material(lam_p, mat_iron)
            bc.assign_weighted_bones(lam_p, {"spine_03": 0.7, "spine_04": 0.3})
            created.append(lam_p)
            
    # Valknut Medallion
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=4.5, depth=1.8, location=(0.0, -17.5, 122.0), rotation=(1.5708, 0.0, 0.0))
    valknut = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(valknut, mat_silver)
    bc.assign_weighted_bones(valknut, {"spine_02": 0.5, "spine_03": 0.5})
    created.append(valknut)
    
    # Norse Round Shield on Back (Radius = 36 cm at Y = +22.0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=36.0, depth=3.5, location=(0.0, 22.0, 126.0), rotation=(1.5708, 0.0, 0.0))
    shield_body = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(shield_body, mat_shield_red)
    bc.assign_weighted_bones(shield_body, {"spine_03": 0.6, "spine_04": 0.4})
    created.append(shield_body)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=36.0, minor_radius=1.8, location=(0.0, 22.0, 126.0), rotation=(1.5708, 0.0, 0.0))
    shield_rim = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(shield_rim, mat_iron)
    bc.assign_weighted_bones(shield_rim, {"spine_03": 0.6, "spine_04": 0.4})
    created.append(shield_rim)
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=8.5, location=(0.0, 25.0, 126.0))
    shield_boss = bpy.context.active_object
    shield_boss.scale = (1.0, 0.5, 1.0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(shield_boss, mat_iron)
    bc.assign_weighted_bones(shield_boss, {"spine_03": 0.6, "spine_04": 0.4})
    created.append(shield_boss)
    
    # Forearm Bracers & Hands
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=7.0, depth=23.0, location=(sign * 39.0, -7.0, 115.0), rotation=(0.3, sign * -0.2, 0.0))
        bracer = bpy.context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(bracer, mat_leather)
        bc.assign_rigid_weight(bracer, f"lowerarm_{side.lower()}")
        created.append(bracer)
        
        bpy.ops.mesh.primitive_cube_add(size=8.0, location=(sign * 46.0, -15.0, 104.0))
        hand = bpy.context.active_object
        hand.scale = (0.9, 0.7, 0.4)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(hand, mat_leather)
        bc.assign_rigid_weight(hand, f"hand_{side.lower()}")
        created.append(hand)
        
    # War Belt & Buckle
    bpy.ops.mesh.primitive_torus_add(major_radius=22.0, minor_radius=4.2, location=(0.0, -2.0, 96.0))
    war_belt = bpy.context.active_object
    war_belt.scale = (1.1, 0.86, 0.9)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(war_belt, mat_leather)
    bc.assign_rigid_weight(war_belt, "pelvis")
    created.append(war_belt)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=4.8, minor_radius=1.4, location=(0.0, -18.0, 96.0), rotation=(1.5708, 0.0, 0.0))
    buckle = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(buckle, mat_iron)
    bc.assign_rigid_weight(buckle, "pelvis")
    created.append(buckle)
    
    bpy.ops.mesh.primitive_cube_add(size=10.0, location=(-21.0, -4.0, 87.0))
    pouch = bpy.context.active_object
    pouch.scale = (0.6, 0.9, 1.1)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(pouch, mat_leather)
    bc.assign_rigid_weight(pouch, "pelvis")
    created.append(pouch)
    
    # Boots & Fur
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=10.5, minor_radius=3.0, location=(sign * 12.0, -1.5, 50.0))
        boot_fur = bpy.context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(boot_fur, mat_fur)
        bc.assign_rigid_weight(boot_fur, f"calf_{side.lower()}")
        created.append(boot_fur)
        
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=8.5, depth=36.0, location=(sign * 12.0, -1.5, 30.0))
        boot_shaft = bpy.context.active_object
        boot_shaft.scale = (0.92, 0.92, 1.0)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(boot_shaft, mat_leather)
        bc.assign_rigid_weight(boot_shaft, f"calf_{side.lower()}")
        created.append(boot_shaft)
        
        bpy.ops.mesh.primitive_cube_add(size=11.0, location=(sign * 14.0, -6.0, 4.0))
        boot_foot = bpy.context.active_object
        boot_foot.scale = (0.9, 1.9, 0.45)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(boot_foot, mat_leather)
        bc.assign_rigid_weight(boot_foot, f"foot_{side.lower()}")
        created.append(boot_foot)
        
    bpy.ops.object.select_all(action='DESELECT')
    for p in created:
        p.select_set(True)
    bpy.context.view_layer.objects.active = created[0]
    bpy.ops.object.join()
    
    char_armor = created[0]
    char_armor.name = "Viking_Armor_Rigged"
    char_armor.parent = arm
    char_armor.matrix_parent_inverse = Matrix.Identity(4)
    mod = char_armor.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    
    out_fbx = os.path.join(OUT_DIR, "SKM_Viking.fbx")
    bc.export_fbx(out_fbx)
    render_preview("Viking")
    return "Viking complete"

# -------------------------------------------------------------
# 2. BUILD INDIAN YODDHA
# -------------------------------------------------------------
def build_indian_yoddha():
    arm, base_mesh = bc.load_base_model(FBX_MANNY)
    base_mesh.name = "Yoddha_Undersuit"
    
    mat_gold = bc.create_pbr_material("M_Yoddha_Gold", base_color=(0.95, 0.76, 0.22, 1.0), metallic=0.95, roughness=0.20)
    mat_bronze = bc.create_pbr_material("M_Yoddha_Bronze", base_color=(0.76, 0.46, 0.20, 1.0), metallic=0.90, roughness=0.28)
    mat_steel = bc.create_pbr_material("M_Yoddha_Steel", base_color=(0.66, 0.68, 0.72, 1.0), metallic=0.92, roughness=0.25)
    mat_saffron = bc.create_pbr_material("M_Yoddha_Saffron", base_color=(0.96, 0.44, 0.04, 1.0), metallic=0.04, roughness=0.75)
    mat_maroon = bc.create_pbr_material("M_Yoddha_Maroon", base_color=(0.48, 0.05, 0.08, 1.0), metallic=0.04, roughness=0.78)
    mat_ruby = bc.create_pbr_material("M_Yoddha_Ruby", base_color=(0.88, 0.02, 0.08, 1.0), metallic=0.2, roughness=0.08, specular=0.95)
    
    bc.assign_material(base_mesh, mat_maroon)
    created = []
    
    # 1. Conical Shirostra Helmet (Z=170 to 195 cm)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=15.5, radius2=2.0, depth=25.0, location=(0.0, -1.0, 180.0))
    shirostra = bpy.context.active_object
    shirostra.scale = (1.0, 1.1, 1.0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(shirostra, mat_steel)
    bc.assign_rigid_weight(shirostra, "head")
    created.append(shirostra)
    
    # Golden Kalash Plume Finial at top
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=3.0, radius2=0.5, depth=12.0, location=(0.0, -1.0, 196.0))
    finial = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(finial, mat_gold)
    bc.assign_rigid_weight(finial, "head")
    created.append(finial)
    
    # Royal Saffron Pagri Turban Folds around helmet base
    for i in range(3):
        z_off = 168.0 + (i * 3.5)
        rad = 16.5 + (i * 1.0)
        bpy.ops.mesh.primitive_torus_add(major_radius=rad, minor_radius=2.5, location=(0.0, -1.5, z_off))
        pagri = bpy.context.active_object
        pagri.scale = (1.05, 1.15, 0.8)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(pagri, mat_saffron)
        bc.assign_rigid_weight(pagri, "head")
        created.append(pagri)
        
    # Nasal Guard Bar & Tilak Medallion in front (-Y)
    bpy.ops.mesh.primitive_cube_add(size=8.0, location=(0.0, -13.0, 168.0))
    nasal = bpy.context.active_object
    nasal.scale = (0.2, 0.3, 1.5)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(nasal, mat_gold)
    bc.assign_rigid_weight(nasal, "head")
    created.append(nasal)
    
    # Ruby Sandalwood Tilak on Forehead
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=3.5, depth=1.5, location=(0.0, -13.5, 176.0), rotation=(1.5708, 0.0, 0.0))
    tilak = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(tilak, mat_ruby)
    bc.assign_rigid_weight(tilak, "head")
    created.append(tilak)
    
    # 2. Golden Surya Kavacha (Sun God Torso Cuirass)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=23.0, depth=38.0, location=(0.0, -2.0, 124.0))
    kavacha = bpy.context.active_object
    kavacha.scale = (1.1, 0.86, 1.0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(kavacha, mat_gold)
    bc.assign_weighted_bones(kavacha, {"spine_01": 0.15, "spine_02": 0.25, "spine_03": 0.35, "spine_04": 0.15, "spine_05": 0.10})
    created.append(kavacha)
    
    # Embossed Central Surya Sun Disc on front (-Y = -17.0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=7.5, depth=2.0, location=(0.0, -17.0, 134.0), rotation=(1.5708, 0.0, 0.0))
    surya_disc = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(surya_disc, mat_bronze)
    bc.assign_weighted_bones(surya_disc, {"spine_03": 0.7, "spine_04": 0.3})
    created.append(surya_disc)
    
    # Ruby Eye in Center of Sun Disc
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=2.5, location=(0.0, -18.0, 134.0))
    ruby_eye = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(ruby_eye, mat_ruby)
    bc.assign_weighted_bones(ruby_eye, {"spine_03": 0.7, "spine_04": 0.3})
    created.append(ruby_eye)
    
    # 8 Radiating Sunburst Rays
    for r_idx in range(8):
        angle = (r_idx / 8.0) * (2.0 * math.pi)
        ray_x = math.cos(angle) * 11.0
        ray_z = 134.0 + (math.sin(angle) * 11.0)
        bpy.ops.mesh.primitive_cube_add(size=3.0, location=(ray_x, -16.5, ray_z), rotation=(0.0, -angle, 0.0))
        ray = bpy.context.active_object
        ray.scale = (0.4, 0.2, 1.8)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(ray, mat_gold)
        bc.assign_weighted_bones(ray, {"spine_03": 0.7, "spine_04": 0.3})
        created.append(ray)
        
    # Hansli / Layered Royal Torc Necklace
    bpy.ops.mesh.primitive_torus_add(major_radius=16.0, minor_radius=2.5, location=(0.0, 2.0, 148.0))
    hansli = bpy.context.active_object
    hansli.scale = (1.1, 0.9, 0.6)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(hansli, mat_gold)
    bc.assign_weighted_bones(hansli, {"spine_05": 0.5, "neck_01": 0.5})
    created.append(hansli)
    
    # 3. Traditional Indian Dhal Shield on Back (+Y = +22.0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=32.0, depth=3.0, location=(0.0, 22.0, 126.0), rotation=(1.5708, 0.0, 0.0))
    dhal = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(dhal, mat_steel)
    bc.assign_weighted_bones(dhal, {"spine_03": 0.6, "spine_04": 0.4})
    created.append(dhal)
    
    # 4 Brass Boss Pins (Phul) on Dhal Shield
    for b_x, b_z in [(8, 134), (-8, 134), (8, 118), (-8, 118)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=3.2, location=(b_x, 24.5, b_z))
        phul = bpy.context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(phul, mat_gold)
        bc.assign_weighted_bones(phul, {"spine_03": 0.6, "spine_04": 0.4})
        created.append(phul)
        
    # 4. Angada Armlets & Dastana Bracers
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=8.0, minor_radius=2.0, location=(sign * 25.0, 2.0, 136.0), rotation=(0.2, sign * -0.3, 0.0))
        angada = bpy.context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(angada, mat_gold)
        bc.assign_rigid_weight(angada, f"upperarm_{side.lower()}")
        created.append(angada)
        
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=6.8, depth=22.0, location=(sign * 39.0, -7.0, 115.0), rotation=(0.3, sign * -0.2, 0.0))
        dastana = bpy.context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(dastana, mat_steel)
        bc.assign_rigid_weight(dastana, f"lowerarm_{side.lower()}")
        created.append(dastana)
        
    # 5. Kamarbandh Belt & Long Front Patka Sash
    bpy.ops.mesh.primitive_torus_add(major_radius=21.0, minor_radius=3.5, location=(0.0, -1.0, 96.0))
    kamar = bpy.context.active_object
    kamar.scale = (1.1, 0.86, 0.8)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(kamar, mat_gold)
    bc.assign_rigid_weight(kamar, "pelvis")
    created.append(kamar)
    
    # Ceremonial Patka Sash hanging down the front (-Y = -18.0)
    bpy.ops.mesh.primitive_cube_add(size=16.0, location=(0.0, -18.0, 65.0))
    patka = bpy.context.active_object
    patka.scale = (0.9, 0.08, 3.8)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(patka, mat_saffron)
    bc.assign_weighted_bones(patka, {"pelvis": 0.6, "spine_01": 0.2, "thigh_l": 0.1, "thigh_r": 0.1})
    created.append(patka)
    
    # Patka Gold Medallion at end
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=6.5, depth=2.0, location=(0.0, -18.5, 38.0), rotation=(1.5708, 0.0, 0.0))
    patka_pendant = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bc.assign_material(patka_pendant, mat_gold)
    bc.assign_weighted_bones(patka_pendant, {"pelvis": 0.7, "spine_01": 0.3})
    created.append(patka_pendant)
    
    # 6. Jangha Kavacha (Greaves) & Mojari Shoes
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=8.2, depth=36.0, location=(sign * 12.0, -1.5, 32.0))
        greave = bpy.context.active_object
        greave.scale = (0.9, 0.9, 1.0)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(greave, mat_bronze)
        bc.assign_rigid_weight(greave, f"calf_{side.lower()}")
        created.append(greave)
        
        # Mojari with curved toe
        bpy.ops.mesh.primitive_cube_add(size=10.0, location=(sign * 14.0, -4.0, 4.0))
        mojari = bpy.context.active_object
        mojari.scale = (0.9, 1.8, 0.4)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(mojari, mat_maroon)
        bc.assign_rigid_weight(mojari, f"foot_{side.lower()}")
        created.append(mojari)
        
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=3.5, radius2=0.5, depth=8.0, location=(sign * 14.0, -13.0, 6.0), rotation=(0.4, 0.0, 0.0))
        curved_toe = bpy.context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bc.assign_material(curved_toe, mat_gold)
        bc.assign_rigid_weight(curved_toe, f"foot_{side.lower()}")
        created.append(curved_toe)
        
    bpy.ops.object.select_all(action='DESELECT')
    for p in created:
        p.select_set(True)
    bpy.context.view_layer.objects.active = created[0]
    bpy.ops.object.join()
    
    char_armor = created[0]
    char_armor.name = "Yoddha_Armor_Rigged"
    char_armor.parent = arm
    char_armor.matrix_parent_inverse = Matrix.Identity(4)
    mod = char_armor.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    
    out_fbx = os.path.join(OUT_DIR, "SKM_IndianYoddha.fbx")
    bc.export_fbx(out_fbx)
    render_preview("IndianYoddha")
    return "Indian Yoddha complete"

if __name__ == "__main__":
    v_res = build_viking()
    print("Viking:", v_res)
    y_res = build_indian_yoddha()
    print("Yoddha:", y_res)
