"""
build_viking.py - Generates the Viking (Norse Jarl / Berserker) build rigged to UE5 Mannequin armature.
"""

import sys
import os
import math
sys.path.append(r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Scripts\CharacterBuilders")

import bpy
import builder_common as bc

def build_viking():
    fbx_base = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_Viking.fbx"
    
    arm, base_mesh = bc.load_base_model(fbx_base)
    base_mesh.name = "Viking_BaseBody"
    
    # Materials
    mat_iron = bc.create_pbr_material("M_Viking_Iron", base_color=(0.35, 0.36, 0.38, 1.0), metallic=0.92, roughness=0.38) # Weathered Norse Iron
    mat_leather = bc.create_pbr_material("M_Viking_Leather", base_color=(0.14, 0.08, 0.04, 1.0), metallic=0.04, roughness=0.72) # Hardened Studded Leather
    mat_fur = bc.create_pbr_material("M_Viking_Fur", base_color=(0.42, 0.38, 0.34, 1.0), metallic=0.0, roughness=0.92) # Wolf Grey Pelt
    mat_wool = bc.create_pbr_material("M_Viking_Wool", base_color=(0.06, 0.18, 0.08, 1.0), metallic=0.0, roughness=0.88) # Forest Green Wool
    mat_silver = bc.create_pbr_material("M_Viking_Silver", base_color=(0.82, 0.84, 0.86, 1.0), metallic=0.95, roughness=0.22) # Norse Silver
    mat_hair = bc.create_pbr_material("M_Viking_Hair", base_color=(0.45, 0.25, 0.10, 1.0), metallic=0.0, roughness=0.85) # Braided Beard Hair
    
    bc.assign_material(base_mesh, mat_wool)
    created_pieces = []
    
    # 1. GJERMUNDBU SPECTACLE HELMET & MAIL AVENTAIL
    # Iron Spangenhelm Dome
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.155, location=(0.0, -0.015, 1.74))
    helm = bpy.context.active_object
    helm.name = "Viking_Helm_Dome"
    helm.scale = (1.0, 1.12, 1.02)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(helm, mat_iron)
    bc.assign_rigid_weight(helm, "head")
    created_pieces.append(helm)
    
    # Cross Bands (Iron reinforcement ribs)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.015, depth=0.32, location=(0.0, -0.015, 1.80), rotation=(1.5708, 0.0, 0.0))
    rib_fb = bpy.context.active_object
    rib_fb.name = "Viking_Rib_FrontBack"
    bc.assign_material(rib_fb, mat_silver)
    bc.assign_rigid_weight(rib_fb, "head")
    created_pieces.append(rib_fb)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.015, depth=0.32, location=(0.0, -0.015, 1.80), rotation=(0.0, 1.5708, 0.0))
    rib_lr = bpy.context.active_object
    rib_lr.name = "Viking_Rib_LeftRight"
    bc.assign_material(rib_lr, mat_silver)
    bc.assign_rigid_weight(rib_lr, "head")
    created_pieces.append(rib_lr)
    
    # Spectacle Ocular Eye Guards (Twin ocular rings + nasal bridge)
    for eye_side, eye_x in [("L", 0.045), ("R", -0.045)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.042, minor_radius=0.010, location=(eye_x, 0.135, 1.68), rotation=(1.5708, 0.0, 0.0))
        ocular = bpy.context.active_object
        ocular.name = f"Viking_Ocular_{eye_side}"
        bc.assign_material(ocular, mat_iron)
        bc.assign_rigid_weight(ocular, "head")
        created_pieces.append(ocular)
        
    # Nasal Guard
    bpy.ops.mesh.primitive_cube_add(size=0.06, location=(0.0, 0.145, 1.64))
    nasal = bpy.context.active_object
    nasal.name = "Viking_Nasal_Bar"
    nasal.scale = (0.25, 0.2, 1.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(nasal, mat_iron)
    bc.assign_rigid_weight(nasal, "head")
    created_pieces.append(nasal)
    
    # Chainmail Aventail / Neck Drape
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.17, depth=0.16, location=(0.0, -0.02, 1.56))
    aventail = bpy.context.active_object
    aventail.name = "Viking_Mail_Aventail"
    aventail.scale = (1.05, 1.15, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(aventail, mat_iron)
    bc.assign_weighted_bones(aventail, {"neck_01": 0.6, "head": 0.4})
    created_pieces.append(aventail)
    
    # Braided Warrior Beard (Dual hanging braids)
    for b_side, b_x in [("L", 0.035), ("R", -0.035)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.025, depth=0.28, location=(b_x, 0.11, 1.50), rotation=(0.15, 0.0, 0.0))
        braid = bpy.context.active_object
        braid.name = f"Viking_Braid_{b_side}"
        bc.assign_material(braid, mat_hair)
        bc.assign_rigid_weight(braid, "head")
        created_pieces.append(braid)
        
        # Silver Beard Ring
        bpy.ops.mesh.primitive_torus_add(major_radius=0.022, minor_radius=0.006, location=(b_x, 0.12, 1.40))
        b_ring = bpy.context.active_object
        b_ring.name = f"Viking_BeardRing_{b_side}"
        bc.assign_material(b_ring, mat_silver)
        bc.assign_rigid_weight(b_ring, "head")
        created_pieces.append(b_ring)
        
    # 2. HEAVY FUR SHOULDER MANTLE
    # Main Fur Mantle Collar
    bpy.ops.mesh.primitive_torus_add(major_radius=0.24, minor_radius=0.065, location=(0.0, 0.0, 1.46))
    fur_collar = bpy.context.active_object
    fur_collar.name = "Viking_Fur_Mantle"
    fur_collar.scale = (1.2, 0.95, 0.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(fur_collar, mat_fur)
    bc.assign_weighted_bones(fur_collar, {
        "spine_04": 0.3,
        "spine_05": 0.4,
        "clavicle_l": 0.15,
        "clavicle_r": 0.15
    })
    created_pieces.append(fur_collar)
    
    # Fur back pelt drape
    bpy.ops.mesh.primitive_cube_add(size=0.20, location=(0.0, -0.16, 1.34))
    fur_back = bpy.context.active_object
    fur_back.name = "Viking_Fur_BackPelt"
    fur_back.scale = (1.5, 0.35, 1.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(fur_back, mat_fur)
    bc.assign_weighted_bones(fur_back, {"spine_03": 0.4, "spine_04": 0.4, "spine_05": 0.2})
    created_pieces.append(fur_back)
    
    # Twin Silver Raven Brooches at collar
    for br_side, br_x in [("L", 0.10), ("R", -0.10)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.035, depth=0.015, location=(br_x, 0.15, 1.44), rotation=(1.5708, 0.0, 0.0))
        brooch = bpy.context.active_object
        brooch.name = f"Viking_Raven_Brooch_{br_side}"
        bc.assign_material(brooch, mat_silver)
        bc.assign_weighted_bones(brooch, {"spine_05": 0.5, f"clavicle_{br_side.lower()}": 0.5})
        created_pieces.append(brooch)
        
    # 3. LAMELLAR & HARDENED LEATHER CUIRASS
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.23, depth=0.38, location=(0.0, -0.01, 1.24))
    cuirass = bpy.context.active_object
    cuirass.name = "Viking_Leather_Cuirass"
    cuirass.scale = (1.1, 0.86, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(cuirass, mat_leather)
    bc.assign_weighted_bones(cuirass, {
        "spine_01": 0.15,
        "spine_02": 0.25,
        "spine_03": 0.35,
        "spine_04": 0.15,
        "spine_05": 0.10
    })
    created_pieces.append(cuirass)
    
    # Iron Lamellar Plates across Chest
    for row in range(3):
        z_lam = 1.35 - (row * 0.07)
        for col in range(4):
            x_lam = -0.12 + (col * 0.08)
            bpy.ops.mesh.primitive_cube_add(size=0.05, location=(x_lam, 0.17, z_lam))
            lam_plate = bpy.context.active_object
            lam_plate.name = f"Viking_Lamellar_{row}_{col}"
            lam_plate.scale = (1.2, 0.15, 1.0)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bc.assign_material(lam_plate, mat_iron)
            bc.assign_weighted_bones(lam_plate, {"spine_03": 0.7, "spine_04": 0.3})
            created_pieces.append(lam_plate)
            
    # Valknut Knotwork Medallion on Center Chest
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.045, depth=0.018, location=(0.0, 0.175, 1.22), rotation=(1.5708, 0.0, 0.0))
    valknut = bpy.context.active_object
    valknut.name = "Viking_Valknut_Medallion"
    bc.assign_material(valknut, mat_silver)
    bc.assign_weighted_bones(valknut, {"spine_02": 0.5, "spine_03": 0.5})
    created_pieces.append(valknut)
    
    # 4. SPANGEN BRACERS & LEATHER WRAPS
    for side, sign in [("L", 1), ("R", -1)]:
        # Heavy leather forearm bracer
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.068, depth=0.22, location=(sign * 0.39, 0.07, 1.15), rotation=(0.3, sign * -0.2, 0.0))
        bracer = bpy.context.active_object
        bracer.name = f"Viking_Bracer_{side}"
        bc.assign_material(bracer, mat_leather)
        bc.assign_rigid_weight(bracer, f"lowerarm_{side.lower()}")
        created_pieces.append(bracer)
        
        # Steel reinforcement splint bands on bracer
        for s_idx in range(2):
            z_s = 1.18 - (s_idx * 0.08)
            bpy.ops.mesh.primitive_torus_add(major_radius=0.065, minor_radius=0.010, location=(sign * 0.39, 0.07, z_s), rotation=(0.3, sign * -0.2, 0.0))
            splint = bpy.context.active_object
            splint.name = f"Viking_Splint_{side}_{s_idx}"
            bc.assign_material(splint, mat_iron)
            bc.assign_rigid_weight(splint, f"lowerarm_{side.lower()}")
            created_pieces.append(splint)
            
        # Studded Hand Wrap
        bpy.ops.mesh.primitive_cube_add(size=0.07, location=(sign * 0.46, -0.15, 1.04))
        hand_wrap = bpy.context.active_object
        hand_wrap.name = f"Viking_HandWrap_{side}"
        hand_wrap.scale = (0.9, 0.7, 0.3)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(hand_wrap, mat_leather)
        bc.assign_rigid_weight(hand_wrap, f"hand_{side.lower()}")
        created_pieces.append(hand_wrap)
        
    # 5. STUDDED WAR BELT & TUNIC SKIRT
    bpy.ops.mesh.primitive_torus_add(major_radius=0.21, minor_radius=0.04, location=(0.0, -0.01, 0.96))
    war_belt = bpy.context.active_object
    war_belt.name = "Viking_War_Belt"
    war_belt.scale = (1.1, 0.86, 0.9)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(war_belt, mat_leather)
    bc.assign_rigid_weight(war_belt, "pelvis")
    created_pieces.append(war_belt)
    
    # Heavy Iron Ring Buckle
    bpy.ops.mesh.primitive_torus_add(major_radius=0.045, minor_radius=0.012, location=(0.0, 0.18, 0.96), rotation=(1.5708, 0.0, 0.0))
    buckle = bpy.context.active_object
    buckle.name = "Viking_Ring_Buckle"
    bc.assign_material(buckle, mat_iron)
    bc.assign_rigid_weight(buckle, "pelvis")
    created_pieces.append(buckle)
    
    # Leather Hip Pouch on Right Hip
    bpy.ops.mesh.primitive_cube_add(size=0.09, location=(-0.19, 0.05, 0.88))
    pouch = bpy.context.active_object
    pouch.name = "Viking_Hip_Pouch"
    pouch.scale = (0.6, 0.9, 1.1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(pouch, mat_leather)
    bc.assign_rigid_weight(pouch, "pelvis")
    created_pieces.append(pouch)
    
    # 6. FUR-CUFFED CROSS-GARTERED BOOTS
    for side, sign in [("L", 1), ("R", -1)]:
        # Fur cuff at knee/top of boot
        bpy.ops.mesh.primitive_torus_add(major_radius=0.095, minor_radius=0.025, location=(sign * 0.12, 0.015, 0.48))
        boot_fur = bpy.context.active_object
        boot_fur.name = f"Viking_Boot_Fur_{side}"
        bc.assign_material(boot_fur, mat_fur)
        bc.assign_rigid_weight(boot_fur, f"calf_{side.lower()}")
        created_pieces.append(boot_fur)
        
        # Leather boot shaft with cross-straps
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.082, depth=0.34, location=(sign * 0.12, 0.015, 0.30))
        boot_shaft = bpy.context.active_object
        boot_shaft.name = f"Viking_Boot_Shaft_{side}"
        boot_shaft.scale = (0.9, 0.9, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(boot_shaft, mat_leather)
        bc.assign_rigid_weight(boot_shaft, f"calf_{side.lower()}")
        created_pieces.append(boot_shaft)
        
        # Solid leather boot foot
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(sign * 0.14, -0.04, 0.04))
        boot_foot = bpy.context.active_object
        boot_foot.name = f"Viking_Boot_Foot_{side}"
        boot_foot.scale = (0.9, 1.8, 0.45)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(boot_foot, mat_leather)
        bc.assign_rigid_weight(boot_foot, f"foot_{side.lower()}")
        created_pieces.append(boot_foot)
        
    # Join armor pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in created_pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = created_pieces[0]
    bpy.ops.object.join()
    
    armor_mesh = created_pieces[0]
    armor_mesh.name = "Viking_Armor_Mesh"
    armor_mesh.parent = arm
    mod = armor_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    
    bc.export_fbx(out_fbx)
    return {
        "character": "Viking",
        "output_fbx": out_fbx,
        "base_mesh": base_mesh.name,
        "armor_mesh": armor_mesh.name,
        "polys": len(armor_mesh.data.polygons) + len(base_mesh.data.polygons)
    }

if __name__ == "__main__":
    res = build_viking()
    print("Result:", res)
