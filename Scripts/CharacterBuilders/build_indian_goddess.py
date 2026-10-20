"""
build_indian_goddess.py - Generates the Indian Goddess (Devi / Durga Warrior) build rigged to UE5 Mannequin armature.
"""

import sys
import os
import math
sys.path.append(r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Scripts\CharacterBuilders")

import bpy
import builder_common as bc

def build_indian_goddess():
    fbx_base = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_Quinn.fbx"
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_IndianGoddess.fbx"
    
    arm, base_mesh = bc.load_base_model(fbx_base)
    base_mesh.name = "Goddess_BaseBody"
    
    # Materials
    mat_gold = bc.create_pbr_material("M_Goddess_Gold", base_color=(1.0, 0.82, 0.25, 1.0), metallic=0.98, roughness=0.15) # 24k Divine Gold
    mat_crimson = bc.create_pbr_material("M_Goddess_Crimson", base_color=(0.75, 0.04, 0.08, 1.0), metallic=0.05, roughness=0.70) # Sacred Kumkum Silk
    mat_emerald = bc.create_pbr_material("M_Goddess_Emerald", base_color=(0.02, 0.45, 0.18, 1.0), metallic=0.15, roughness=0.20) # Royal Emerald
    mat_ruby = bc.create_pbr_material("M_Goddess_Ruby", base_color=(0.95, 0.02, 0.10, 1.0), metallic=0.2, roughness=0.08, specular=0.95) # Radiant Ruby
    mat_pearl = bc.create_pbr_material("M_Goddess_Pearl", base_color=(0.96, 0.95, 0.92, 1.0), metallic=0.1, roughness=0.25) # Luminous Pearl
    
    bc.assign_material(base_mesh, mat_crimson)
    created_pieces = []
    
    # 1. KIRITAMUKUTA (Towering Divine Golden Crown) & PRABHAVALI (Celestial Aureole)
    # Tier 1 Crown Base
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.145, depth=0.08, location=(0.0, -0.01, 1.76))
    crown_base = bpy.context.active_object
    crown_base.name = "Goddess_Crown_Tier1"
    crown_base.scale = (1.0, 1.08, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(crown_base, mat_gold)
    bc.assign_rigid_weight(crown_base, "head")
    created_pieces.append(crown_base)
    
    # Tier 2 Conical Spire
    bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.12, radius2=0.04, depth=0.18, location=(0.0, -0.01, 1.88))
    crown_tier2 = bpy.context.active_object
    crown_tier2.name = "Goddess_Crown_Tier2"
    bc.assign_material(crown_tier2, mat_gold)
    bc.assign_rigid_weight(crown_tier2, "head")
    created_pieces.append(crown_tier2)
    
    # Kalash Finial at apex
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.04, location=(0.0, -0.01, 1.99))
    kalash = bpy.context.active_object
    kalash.name = "Goddess_Crown_Kalash"
    bc.assign_material(kalash, mat_gold)
    bc.assign_rigid_weight(kalash, "head")
    created_pieces.append(kalash)
    
    # Ruby Jewel on Crown Center
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.025, location=(0.0, 0.14, 1.76))
    crown_ruby = bpy.context.active_object
    crown_ruby.name = "Goddess_Crown_Ruby"
    bc.assign_material(crown_ruby, mat_ruby)
    bc.assign_rigid_weight(crown_ruby, "head")
    created_pieces.append(crown_ruby)
    
    # Prabhavali (Radiating Celestial Sunburst Aureole / Halo behind the head)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.28, depth=0.015, location=(0.0, -0.12, 1.76), rotation=(1.5708, 0.0, 0.0))
    halo = bpy.context.active_object
    halo.name = "Goddess_Celestial_Halo"
    bc.assign_material(halo, mat_gold)
    bc.assign_rigid_weight(halo, "head")
    created_pieces.append(halo)
    
    # 12 Halo Ray Spikes
    for r_idx in range(12):
        angle = (r_idx / 12.0) * (2.0 * math.pi)
        ray_x = math.cos(angle) * 0.32
        ray_z = 1.76 + (math.sin(angle) * 0.32)
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.02, radius2=0.002, depth=0.12, location=(ray_x, -0.12, ray_z), rotation=(0.0, -angle + 1.5708, 0.0))
        halo_ray = bpy.context.active_object
        halo_ray.name = f"Goddess_Halo_Ray_{r_idx}"
        bc.assign_material(halo_ray, mat_gold)
        bc.assign_rigid_weight(halo_ray, "head")
        created_pieces.append(halo_ray)
        
    # Jhumka Earrings (Hanging bell earrings)
    for j_side, j_sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.025, radius2=0.008, depth=0.05, location=(j_sign * 0.12, -0.01, 1.60), rotation=(3.1415, 0.0, 0.0))
        jhumka = bpy.context.active_object
        jhumka.name = f"Goddess_Jhumka_{j_side}"
        bc.assign_material(jhumka, mat_gold)
        bc.assign_rigid_weight(jhumka, "head")
        created_pieces.append(jhumka)
        
    # 2. SWARNA KAVACHA (Form-Fitting Golden Torso Cuirass & Lotus Medallion)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.20, depth=0.36, location=(0.0, -0.01, 1.25))
    kavacha = bpy.context.active_object
    kavacha.name = "Goddess_Swarna_Kavacha"
    kavacha.scale = (1.05, 0.82, 1.0)
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
    
    # Sacred Lotus Medallion on Chest
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.065, depth=0.015, location=(0.0, 0.155, 1.32), rotation=(1.5708, 0.0, 0.0))
    lotus = bpy.context.active_object
    lotus.name = "Goddess_Lotus_Medallion"
    bc.assign_material(lotus, mat_gold)
    bc.assign_weighted_bones(lotus, {"spine_03": 0.7, "spine_04": 0.3})
    created_pieces.append(lotus)
    
    # Central Ruby Gem in Lotus
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.022, location=(0.0, 0.165, 1.32))
    lotus_ruby = bpy.context.active_object
    lotus_ruby.name = "Goddess_Lotus_Ruby"
    bc.assign_material(lotus_ruby, mat_ruby)
    bc.assign_weighted_bones(lotus_ruby, {"spine_03": 0.7, "spine_04": 0.3})
    created_pieces.append(lotus_ruby)
    
    # Hasli / Layered Pearl & Gold Choker Necklace
    bpy.ops.mesh.primitive_torus_add(major_radius=0.14, minor_radius=0.02, location=(0.0, 0.02, 1.46))
    choker = bpy.context.active_object
    choker.name = "Goddess_Gold_Choker"
    choker.scale = (1.05, 0.85, 0.6)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(choker, mat_gold)
    bc.assign_weighted_bones(choker, {"neck_01": 0.5, "spine_05": 0.5})
    created_pieces.append(choker)
    
    # 3. BAJUBAND (Armlets) & BATTLE BANGLES (Chudiyan)
    for side, sign in [("L", 1), ("R", -1)]:
        # Peacock Crested Bajuband on Upper Arm
        bpy.ops.mesh.primitive_torus_add(major_radius=0.068, minor_radius=0.016, location=(sign * 0.22, 0.02, 1.36))
        bajuband = bpy.context.active_object
        bajuband.name = f"Goddess_Bajuband_{side}"
        bajuband.rotation_euler = (0.2, sign * -0.3, 0.0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        bc.assign_material(bajuband, mat_gold)
        bc.assign_rigid_weight(bajuband, f"upperarm_{side.lower()}")
        created_pieces.append(bajuband)
        
        # Inset Emerald in Bajuband
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.018, location=(sign * 0.28, 0.03, 1.36))
        baju_gem = bpy.context.active_object
        baju_gem.name = f"Goddess_Bajuband_Gem_{side}"
        bc.assign_material(baju_gem, mat_emerald)
        bc.assign_rigid_weight(baju_gem, f"upperarm_{side.lower()}")
        created_pieces.append(baju_gem)
        
        # Stack of 3 Gold Battle Bangles on Forearm
        for b_idx in range(3):
            z_b = 1.18 - (b_idx * 0.04)
            bpy.ops.mesh.primitive_torus_add(major_radius=0.052, minor_radius=0.008, location=(sign * 0.36, 0.06, z_b), rotation=(0.3, sign * -0.2, 0.0))
            bangle = bpy.context.active_object
            bangle.name = f"Goddess_Bangle_{side}_{b_idx}"
            bc.assign_material(bangle, mat_gold)
            bc.assign_rigid_weight(bangle, f"lowerarm_{side.lower()}")
            created_pieces.append(bangle)
            
        # Haathphool Golden Hand Chain
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.018, location=(sign * 0.44, -0.14, 1.05))
        haathphool = bpy.context.active_object
        haathphool.name = f"Goddess_Haathphool_{side}"
        bc.assign_material(haathphool, mat_gold)
        bc.assign_rigid_weight(haathphool, f"hand_{side.lower()}")
        created_pieces.append(haathphool)
        
    # 4. KAMARBANDH (Golden Waistband) & WARRIOR BATTLE SAREE DRAPE
    bpy.ops.mesh.primitive_torus_add(major_radius=0.19, minor_radius=0.032, location=(0.0, -0.01, 0.98))
    kamarbandh = bpy.context.active_object
    kamarbandh.name = "Goddess_Kamarbandh_Belt"
    kamarbandh.scale = (1.08, 0.84, 0.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(kamarbandh, mat_gold)
    bc.assign_rigid_weight(kamarbandh, "pelvis")
    created_pieces.append(kamarbandh)
    
    # Emerald Clasp at center of Kamarbandh
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.04, depth=0.02, location=(0.0, 0.16, 0.98), rotation=(1.5708, 0.0, 0.0))
    belt_clasp = bpy.context.active_object
    belt_clasp.name = "Goddess_Belt_Clasp"
    bc.assign_material(belt_clasp, mat_emerald)
    bc.assign_rigid_weight(belt_clasp, "pelvis")
    created_pieces.append(belt_clasp)
    
    # Pleated Battle Saree Wrap (Kachha Style)
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.13, depth=0.36, location=(sign * 0.10, -0.01, 0.80))
        saree_wrap = bpy.context.active_object
        saree_wrap.name = f"Goddess_Saree_Wrap_{side}"
        bc.assign_material(saree_wrap, mat_crimson)
        bc.assign_rigid_weight(saree_wrap, f"thigh_{side.lower()}")
        created_pieces.append(saree_wrap)
        
    # Front Zari Gold Drape
    bpy.ops.mesh.primitive_cube_add(size=0.15, location=(0.0, 0.16, 0.68))
    zari_drape = bpy.context.active_object
    zari_drape.name = "Goddess_Zari_Drape"
    zari_drape.scale = (0.8, 0.06, 3.6)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(zari_drape, mat_gold)
    bc.assign_weighted_bones(zari_drape, {"pelvis": 0.6, "spine_01": 0.2, "thigh_l": 0.1, "thigh_r": 0.1})
    created_pieces.append(zari_drape)
    
    # 5. GHUNGROO & GOLDEN GREAVES (Payal & Anklets)
    for side, sign in [("L", 1), ("R", -1)]:
        # Gold filigree shin protector
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.076, depth=0.34, location=(sign * 0.12, 0.015, 0.32))
        greave = bpy.context.active_object
        greave.name = f"Goddess_Greave_{side}"
        greave.scale = (0.9, 0.9, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(greave, mat_gold)
        bc.assign_rigid_weight(greave, f"calf_{side.lower()}")
        created_pieces.append(greave)
        
        # Heavy Ghungroo Bell Anklet ring
        bpy.ops.mesh.primitive_torus_add(major_radius=0.065, minor_radius=0.015, location=(sign * 0.13, 0.0, 0.12))
        payal = bpy.context.active_object
        payal.name = f"Goddess_Payal_{side}"
        bc.assign_material(payal, mat_gold)
        bc.assign_rigid_weight(payal, f"foot_{side.lower()}")
        created_pieces.append(payal)
        
        # Red Alta-decorated warrior footwear
        bpy.ops.mesh.primitive_cube_add(size=0.09, location=(sign * 0.14, -0.03, 0.04))
        paduka = bpy.context.active_object
        paduka.name = f"Goddess_Footwear_{side}"
        paduka.scale = (0.85, 1.8, 0.4)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(paduka, mat_crimson)
        bc.assign_rigid_weight(paduka, f"foot_{side.lower()}")
        created_pieces.append(paduka)
        
    # Join armor pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in created_pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = created_pieces[0]
    bpy.ops.object.join()
    
    armor_mesh = created_pieces[0]
    armor_mesh.name = "Goddess_Armor_Mesh"
    armor_mesh.parent = arm
    mod = armor_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    
    bc.export_fbx(out_fbx)
    return {
        "character": "IndianGoddess",
        "output_fbx": out_fbx,
        "base_mesh": base_mesh.name,
        "armor_mesh": armor_mesh.name,
        "polys": len(armor_mesh.data.polygons) + len(base_mesh.data.polygons)
    }

if __name__ == "__main__":
    res = build_indian_goddess()
    print("Result:", res)
