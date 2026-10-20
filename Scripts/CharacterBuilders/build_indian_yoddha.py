"""
build_indian_yoddha.py - Generates the Indian Yoddha (Kshatriya Warrior) build rigged to UE5 Mannequin armature.
"""

import sys
import os
import math
sys.path.append(r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Scripts\CharacterBuilders")

import bpy
import builder_common as bc

def build_indian_yoddha():
    fbx_base = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_IndianYoddha.fbx"
    
    arm, base_mesh = bc.load_base_model(fbx_base)
    base_mesh.name = "Yoddha_BaseBody"
    
    # Materials
    mat_gold = bc.create_pbr_material("M_Yoddha_Gold", base_color=(0.95, 0.75, 0.22, 1.0), metallic=0.95, roughness=0.22) # Antique Royal Gold
    mat_bronze = bc.create_pbr_material("M_Yoddha_Bronze", base_color=(0.75, 0.45, 0.20, 1.0), metallic=0.90, roughness=0.30) # Surya Bronze
    mat_steel = bc.create_pbr_material("M_Yoddha_Steel", base_color=(0.65, 0.67, 0.70, 1.0), metallic=0.92, roughness=0.28) # Wootz Steel
    mat_saffron = bc.create_pbr_material("M_Yoddha_Saffron", base_color=(0.95, 0.42, 0.05, 1.0), metallic=0.05, roughness=0.75) # Royal Saffron Silk
    mat_maroon = bc.create_pbr_material("M_Yoddha_Maroon", base_color=(0.45, 0.05, 0.08, 1.0), metallic=0.05, roughness=0.80) # Deep Maroon Silk
    mat_gem = bc.create_pbr_material("M_Yoddha_Ruby", base_color=(0.85, 0.02, 0.08, 1.0), metallic=0.2, roughness=0.1, specular=0.9) # Ruby Inset
    
    bc.assign_material(base_mesh, mat_maroon)
    created_pieces = []
    
    # 1. SHIROSTRA HELMET & ROYAL PAGRI (Kshatriya Warrior Conical Helm + Turban)
    # Steel Conical Helm Bowl
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.155, radius2=0.02, depth=0.25, location=(0.0, -0.01, 1.80))
    shirostra = bpy.context.active_object
    shirostra.name = "Yoddha_Shirostra_Dome"
    shirostra.scale = (1.0, 1.1, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(shirostra, mat_steel)
    bc.assign_rigid_weight(shirostra, "head")
    created_pieces.append(shirostra)
    
    # Crown Spike / Kalash Plume Finial at Top
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.03, radius2=0.005, depth=0.12, location=(0.0, -0.01, 1.96))
    finial = bpy.context.active_object
    finial.name = "Yoddha_Crown_Finial"
    bc.assign_material(finial, mat_gold)
    bc.assign_rigid_weight(finial, "head")
    created_pieces.append(finial)
    
    # Saffron Silk Pagri (Turban folds wrapped around base of helmet)
    for i in range(3):
        z_offset = 1.68 + (i * 0.035)
        rad = 0.165 + (i * 0.01)
        bpy.ops.mesh.primitive_torus_add(major_radius=rad, minor_radius=0.025, location=(0.0, -0.015, z_offset))
        pagri_fold = bpy.context.active_object
        pagri_fold.name = f"Yoddha_Pagri_Fold_{i}"
        pagri_fold.scale = (1.05, 1.15, 0.8)
        pagri_fold.rotation_euler = (0.05 * (i - 1), 0.02 * (i - 1), 0.0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        bc.assign_material(pagri_fold, mat_saffron)
        bc.assign_rigid_weight(pagri_fold, "head")
        created_pieces.append(pagri_fold)
        
    # Nasal Guard Bar & Forehead Tilak Emblem
    bpy.ops.mesh.primitive_cube_add(size=0.08, location=(0.0, 0.125, 1.68))
    nasal = bpy.context.active_object
    nasal.name = "Yoddha_Nasal_Guard"
    nasal.scale = (0.2, 0.3, 1.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(nasal, mat_gold)
    bc.assign_rigid_weight(nasal, "head")
    created_pieces.append(nasal)
    
    # Ruby Tilak Medallion
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.035, depth=0.015, location=(0.0, 0.128, 1.76), rotation=(1.5708, 0.0, 0.0))
    tilak = bpy.context.active_object
    tilak.name = "Yoddha_Tilak_Medallion"
    bc.assign_material(tilak, mat_gem)
    bc.assign_rigid_weight(tilak, "head")
    created_pieces.append(tilak)
    
    # 2. SURYA KAVACHA (Golden Sun God Torso Cuirass)
    # Main Cuirass
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.225, depth=0.38, location=(0.0, -0.01, 1.25))
    kavacha = bpy.context.active_object
    kavacha.name = "Yoddha_Surya_Kavacha"
    kavacha.scale = (1.1, 0.86, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(kavacha, mat_gold)
    bc.assign_weighted_bones(kavacha, {
        "spine_01": 0.15,
        "spine_02": 0.25,
        "spine_03": 0.35,
        "spine_04": 0.15,
        "spine_05": 0.10
    })
    created_pieces.append(kavacha)
    
    # Embossed Surya (Central Solar Disc + Sunburst Rays on Chest)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.07, depth=0.02, location=(0.0, 0.165, 1.34), rotation=(1.5708, 0.0, 0.0))
    surya_disc = bpy.context.active_object
    surya_disc.name = "Yoddha_Surya_Disc"
    bc.assign_material(surya_disc, mat_bronze)
    bc.assign_weighted_bones(surya_disc, {"spine_03": 0.7, "spine_04": 0.3})
    created_pieces.append(surya_disc)
    
    # Central Ruby Eye in Sun Disc
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.025, location=(0.0, 0.175, 1.34))
    surya_ruby = bpy.context.active_object
    surya_ruby.name = "Yoddha_Surya_Ruby"
    bc.assign_material(surya_ruby, mat_gem)
    bc.assign_weighted_bones(surya_ruby, {"spine_03": 0.7, "spine_04": 0.3})
    created_pieces.append(surya_ruby)
    
    # 8 Radiating Sunburst Rays
    for ray_idx in range(8):
        angle = (ray_idx / 8.0) * (2.0 * math.pi)
        ray_x = 0.0 + (math.cos(angle) * 0.10)
        ray_z = 1.34 + (math.sin(angle) * 0.10)
        bpy.ops.mesh.primitive_cube_add(size=0.03, location=(ray_x, 0.162, ray_z), rotation=(0.0, -angle, 0.0))
        ray = bpy.context.active_object
        ray.name = f"Yoddha_Surya_Ray_{ray_idx}"
        ray.scale = (0.4, 0.2, 1.8)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(ray, mat_gold)
        bc.assign_weighted_bones(ray, {"spine_03": 0.7, "spine_04": 0.3})
        created_pieces.append(ray)
        
    # Kanthavaran / Heavy Gold Collar Necklace
    bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.025, location=(0.0, 0.02, 1.48))
    kanthavaran = bpy.context.active_object
    kanthavaran.name = "Yoddha_Kanthavaran_Necklace"
    kanthavaran.scale = (1.1, 0.9, 0.6)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(kanthavaran, mat_gold)
    bc.assign_weighted_bones(kanthavaran, {"spine_05": 0.5, "neck_01": 0.5})
    created_pieces.append(kanthavaran)
    
    # 3. ANGADA (Golden Bicep Armlets) & FOREARM BRACERS
    for side, sign in [("L", 1), ("R", -1)]:
        # Angada Bicep Armlet
        bpy.ops.mesh.primitive_torus_add(major_radius=0.08, minor_radius=0.02, location=(sign * 0.25, 0.02, 1.36))
        angada = bpy.context.active_object
        angada.name = f"Yoddha_Angada_{side}"
        angada.rotation_euler = (0.2, sign * -0.3, 0.0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        bc.assign_material(angada, mat_gold)
        bc.assign_rigid_weight(angada, f"upperarm_{side.lower()}")
        created_pieces.append(angada)
        
        # Inset Ruby in Angada
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.02, location=(sign * 0.32, 0.03, 1.36))
        angada_gem = bpy.context.active_object
        angada_gem.name = f"Yoddha_Angada_Gem_{side}"
        bc.assign_material(angada_gem, mat_gem)
        bc.assign_rigid_weight(angada_gem, f"upperarm_{side.lower()}")
        created_pieces.append(angada_gem)
        
        # Steel & Gold Vambrace on Forearm
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.065, depth=0.22, location=(sign * 0.39, 0.07, 1.15), rotation=(0.3, sign * -0.2, 0.0))
        vambrace = bpy.context.active_object
        vambrace.name = f"Yoddha_Vambrace_{side}"
        bc.assign_material(vambrace, mat_steel)
        bc.assign_rigid_weight(vambrace, f"lowerarm_{side.lower()}")
        created_pieces.append(vambrace)
        
        # Golden Wrist Cuff (Kangan)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.055, minor_radius=0.012, location=(sign * 0.44, -0.05, 1.08))
        kangan = bpy.context.active_object
        kangan.name = f"Yoddha_Kangan_{side}"
        bc.assign_material(kangan, mat_gold)
        bc.assign_rigid_weight(kangan, f"hand_{side.lower()}")
        created_pieces.append(kangan)
        
    # 4. ROYAL DHOTI, KAMARBANDH & PATKA SASH
    # Kamarbandh (Golden Gemmed Waist Belt)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.21, minor_radius=0.035, location=(0.0, -0.01, 0.96))
    kamarbandh = bpy.context.active_object
    kamarbandh.name = "Yoddha_Kamarbandh_Belt"
    kamarbandh.scale = (1.1, 0.86, 0.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(kamarbandh, mat_gold)
    bc.assign_rigid_weight(kamarbandh, "pelvis")
    created_pieces.append(kamarbandh)
    
    # Royal Patka (Front Ceremonial Embroidered Sash hanging down)
    bpy.ops.mesh.primitive_cube_add(size=0.16, location=(0.0, 0.18, 0.65))
    patka = bpy.context.active_object
    patka.name = "Yoddha_Patka_Sash"
    patka.scale = (0.9, 0.08, 3.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(patka, mat_saffron)
    bc.assign_weighted_bones(patka, {"pelvis": 0.6, "spine_01": 0.2, "thigh_l": 0.1, "thigh_r": 0.1})
    created_pieces.append(patka)
    
    # Golden Border / Medallion at base of Patka
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.065, depth=0.02, location=(0.0, 0.185, 0.38), rotation=(1.5708, 0.0, 0.0))
    patka_pendant = bpy.context.active_object
    patka_pendant.name = "Yoddha_Patka_Pendant"
    bc.assign_material(patka_pendant, mat_gold)
    bc.assign_weighted_bones(patka_pendant, {"pelvis": 0.7, "spine_01": 0.3})
    created_pieces.append(patka_pendant)
    
    # Dhoti pleated thigh wraps
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.135, depth=0.35, location=(sign * 0.10, -0.01, 0.78))
        dhoti_wrap = bpy.context.active_object
        dhoti_wrap.name = f"Yoddha_Dhoti_Wrap_{side}"
        bc.assign_material(dhoti_wrap, mat_maroon)
        bc.assign_rigid_weight(dhoti_wrap, f"thigh_{side.lower()}")
        created_pieces.append(dhoti_wrap)
        
    # 5. JANGHA KAVACHA (Bronze Shin Greaves) & WARRIOR MOJARI
    for side, sign in [("L", 1), ("R", -1)]:
        # Bronze engraved shin guard
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.082, depth=0.36, location=(sign * 0.12, 0.015, 0.32))
        greave = bpy.context.active_object
        greave.name = f"Yoddha_Greave_{side}"
        greave.scale = (0.9, 0.9, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(greave, mat_bronze)
        bc.assign_rigid_weight(greave, f"calf_{side.lower()}")
        created_pieces.append(greave)
        
        # Golden knee disc
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.065, depth=0.025, location=(sign * 0.12, 0.085, 0.52), rotation=(1.5708, 0.0, 0.0))
        knee_disc = bpy.context.active_object
        knee_disc.name = f"Yoddha_Knee_Disc_{side}"
        bc.assign_material(knee_disc, mat_gold)
        bc.assign_rigid_weight(knee_disc, f"calf_{side.lower()}")
        created_pieces.append(knee_disc)
        
        # Leather Mojari shoe with curved steel toe
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(sign * 0.14, -0.04, 0.04))
        mojari = bpy.context.active_object
        mojari.name = f"Yoddha_Mojari_{side}"
        mojari.scale = (0.9, 1.8, 0.4)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(mojari, mat_maroon)
        bc.assign_rigid_weight(mojari, f"foot_{side.lower()}")
        created_pieces.append(mojari)
        
        # Pointed curved golden toe cap
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.035, radius2=0.005, depth=0.08, location=(sign * 0.14, 0.09, 0.06), rotation=(-0.4, 0.0, 0.0))
        toe_cap = bpy.context.active_object
        toe_cap.name = f"Yoddha_Toe_Cap_{side}"
        bc.assign_material(toe_cap, mat_gold)
        bc.assign_rigid_weight(toe_cap, f"foot_{side.lower()}")
        created_pieces.append(toe_cap)
        
    # Join armor pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in created_pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = created_pieces[0]
    bpy.ops.object.join()
    
    armor_mesh = created_pieces[0]
    armor_mesh.name = "Yoddha_Armor_Mesh"
    armor_mesh.parent = arm
    mod = armor_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    
    bc.export_fbx(out_fbx)
    return {
        "character": "IndianYoddha",
        "output_fbx": out_fbx,
        "base_mesh": base_mesh.name,
        "armor_mesh": armor_mesh.name,
        "polys": len(armor_mesh.data.polygons) + len(base_mesh.data.polygons)
    }

if __name__ == "__main__":
    res = build_indian_yoddha()
    print("Result:", res)
