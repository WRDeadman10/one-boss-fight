"""
build_viking_v2.py - Builds a detailed, authentic Viking warrior model in Blender
rigged to the UE5 Mannequin armature (SK_CombatMannequin).
"""

import sys
import os
import math

sys.path.append(r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Scripts\CharacterBuilders")
import bpy
import builder_common as bc

def build_detailed_viking():
    fbx_base = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_Viking.fbx"
    
    arm, base_mesh = bc.load_base_model(fbx_base)
    # Remove the robot mannequin body so it doesn't show as a colored robot!
    if base_mesh:
        bpy.data.objects.remove(base_mesh, do_unlink=True)
        
    created_pieces = []
    
    # ---------------- MATERIALS ----------------
    mat_skin = bc.create_pbr_material("M_Viking_Skin", base_color=(0.82, 0.62, 0.50, 1.0), metallic=0.0, roughness=0.55) # Weathered Nordic Skin
    mat_iron = bc.create_pbr_material("M_Viking_Iron", base_color=(0.32, 0.33, 0.35, 1.0), metallic=0.92, roughness=0.35) # Hammered Iron
    mat_silver = bc.create_pbr_material("M_Viking_Silver", base_color=(0.85, 0.86, 0.88, 1.0), metallic=0.96, roughness=0.20) # Engraved Silver
    mat_leather = bc.create_pbr_material("M_Viking_Leather", base_color=(0.14, 0.08, 0.04, 1.0), metallic=0.02, roughness=0.70) # Dark Hardened Leather
    mat_fur = bc.create_pbr_material("M_Viking_Fur", base_color=(0.38, 0.35, 0.32, 1.0), metallic=0.0, roughness=0.95) # Wolf Fur Mantle
    mat_tunic = bc.create_pbr_material("M_Viking_Wool", base_color=(0.08, 0.18, 0.10, 1.0), metallic=0.0, roughness=0.85) # Forest Green Wool Tunic
    mat_pants = bc.create_pbr_material("M_Viking_Breeches", base_color=(0.15, 0.14, 0.13, 1.0), metallic=0.0, roughness=0.80) # Charcoal Wool Pants
    mat_beard = bc.create_pbr_material("M_Viking_Beard", base_color=(0.35, 0.20, 0.08, 1.0), metallic=0.0, roughness=0.80) # Auburn / Brown Beard
    mat_shield_wood = bc.create_pbr_material("M_Viking_ShieldWood", base_color=(0.40, 0.25, 0.12, 1.0), metallic=0.0, roughness=0.75) # Oak Planks
    mat_shield_paint = bc.create_pbr_material("M_Viking_ShieldPaint", base_color=(0.55, 0.08, 0.08, 1.0), metallic=0.05, roughness=0.60) # Crimson Norse Paint
    
    # ---------------- 1. HUMAN HEAD & FACE ----------------
    # Cranium & Face Base
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=18, radius=0.135, location=(0.0, 0.0, 1.68))
    head_base = bpy.context.active_object
    head_base.name = "Viking_Head"
    head_base.scale = (0.95, 1.15, 1.20)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(head_base, mat_skin)
    bc.assign_rigid_weight(head_base, "head")
    created_pieces.append(head_base)
    
    # Sculpted Rugged Jaw & Chin
    bpy.ops.mesh.primitive_cube_add(size=0.12, location=(0.0, 0.06, 1.58))
    jaw = bpy.context.active_object
    jaw.name = "Viking_Jaw"
    jaw.scale = (0.9, 1.1, 0.7)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(jaw, mat_skin)
    bc.assign_rigid_weight(jaw, "head")
    created_pieces.append(jaw)
    
    # Sculpted Norse Nose
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.022, radius2=0.005, depth=0.055, location=(0.0, 0.145, 1.67), rotation=(-1.3, 0.0, 0.0))
    nose = bpy.context.active_object
    nose.name = "Viking_Nose"
    bc.assign_material(nose, mat_skin)
    bc.assign_rigid_weight(nose, "head")
    created_pieces.append(nose)
    
    # Thick Warrior Neck
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.11, depth=0.14, location=(0.0, 0.02, 1.52))
    neck = bpy.context.active_object
    neck.name = "Viking_Neck"
    bc.assign_material(neck, mat_skin)
    bc.assign_weighted_bones(neck, {"neck_01": 0.6, "head": 0.4})
    created_pieces.append(neck)
    
    # ---------------- 2. GJERMUNDBU SPECTACLE HELMET ----------------
    # Iron Spangenhelm Dome
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.155, location=(0.0, -0.015, 1.74))
    helm = bpy.context.active_object
    helm.name = "Viking_Helm_Dome"
    helm.scale = (1.02, 1.14, 1.02)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(helm, mat_iron)
    bc.assign_rigid_weight(helm, "head")
    created_pieces.append(helm)
    
    # Helmet Rim Band
    bpy.ops.mesh.primitive_torus_add(major_radius=0.158, minor_radius=0.014, location=(0.0, -0.015, 1.68))
    helm_rim = bpy.context.active_object
    helm_rim.name = "Viking_Helm_Rim"
    helm_rim.scale = (1.02, 1.14, 0.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(helm_rim, mat_silver)
    bc.assign_rigid_weight(helm_rim, "head")
    created_pieces.append(helm_rim)
    
    # Cross Bands (Front-to-back & side-to-side)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.016, depth=0.34, location=(0.0, -0.015, 1.80), rotation=(1.5708, 0.0, 0.0))
    rib_fb = bpy.context.active_object
    rib_fb.name = "Viking_Rib_FB"
    bc.assign_material(rib_fb, mat_silver)
    bc.assign_rigid_weight(rib_fb, "head")
    created_pieces.append(rib_fb)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.016, depth=0.34, location=(0.0, -0.015, 1.80), rotation=(0.0, 1.5708, 0.0))
    rib_lr = bpy.context.active_object
    rib_lr.name = "Viking_Rib_LR"
    bc.assign_material(rib_lr, mat_silver)
    bc.assign_rigid_weight(rib_lr, "head")
    created_pieces.append(rib_lr)
    
    # Apex Spike / Rivet
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.025, radius2=0.005, depth=0.06, location=(0.0, -0.015, 1.91))
    apex_spike = bpy.context.active_object
    apex_spike.name = "Viking_Apex_Spike"
    bc.assign_material(apex_spike, mat_silver)
    bc.assign_rigid_weight(apex_spike, "head")
    created_pieces.append(apex_spike)
    
    # Spectacle Ocular Eye Guards (The iconic Gjermundbu mask)
    for eye_side, eye_x in [("L", 0.048), ("R", -0.048)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.042, minor_radius=0.012, location=(eye_x, 0.14, 1.68), rotation=(1.5708, 0.0, 0.0))
        ocular = bpy.context.active_object
        ocular.name = f"Viking_Ocular_{eye_side}"
        bc.assign_material(ocular, mat_iron)
        bc.assign_rigid_weight(ocular, "head")
        created_pieces.append(ocular)
        
    # Nasal Guard extending down between spectacles
    bpy.ops.mesh.primitive_cube_add(size=0.06, location=(0.0, 0.155, 1.63))
    nasal = bpy.context.active_object
    nasal.name = "Viking_Nasal_Guard"
    nasal.scale = (0.28, 0.22, 1.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(nasal, mat_iron)
    bc.assign_rigid_weight(nasal, "head")
    created_pieces.append(nasal)
    
    # Chainmail Aventail (Draped around neck and jaw)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.175, depth=0.18, location=(0.0, -0.02, 1.55))
    aventail = bpy.context.active_object
    aventail.name = "Viking_Mail_Aventail"
    aventail.scale = (1.05, 1.15, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(aventail, mat_iron)
    bc.assign_weighted_bones(aventail, {"neck_01": 0.6, "head": 0.4})
    created_pieces.append(aventail)
    
    # ---------------- 3. BRAIDED VIKING BEARD & HAIR ----------------
    # Upper Mustache
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.025, depth=0.14, location=(0.0, 0.13, 1.59), rotation=(0.0, 1.5708, 0.0))
    mustache = bpy.context.active_object
    mustache.name = "Viking_Mustache"
    mustache.scale = (1.0, 0.6, 0.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(mustache, mat_beard)
    bc.assign_rigid_weight(mustache, "head")
    created_pieces.append(mustache)
    
    # Full Chin Beard Mass
    bpy.ops.mesh.primitive_cube_add(size=0.14, location=(0.0, 0.10, 1.48))
    chin_beard = bpy.context.active_object
    chin_beard.name = "Viking_Chin_Beard"
    chin_beard.scale = (1.1, 0.9, 1.3)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(chin_beard, mat_beard)
    bc.assign_rigid_weight(chin_beard, "head")
    created_pieces.append(chin_beard)
    
    # Twin Braided Warrior Beard Plaits hanging down to chest
    for b_side, b_x in [("L", 0.045), ("R", -0.045)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.028, depth=0.32, location=(b_x, 0.11, 1.36), rotation=(0.20, 0.0, 0.0))
        braid = bpy.context.active_object
        braid.name = f"Viking_Braid_{b_side}"
        bc.assign_material(braid, mat_beard)
        bc.assign_weighted_bones(braid, {"head": 0.6, "neck_01": 0.4})
        created_pieces.append(braid)
        
        # Engraved Silver Beard Rings / Beads
        for ring_idx, ring_z in [(0, 1.42), (1, 1.28)]:
            bpy.ops.mesh.primitive_torus_add(major_radius=0.028, minor_radius=0.008, location=(b_x, 0.12, ring_z))
            b_ring = bpy.context.active_object
            b_ring.name = f"Viking_Beard_Ring_{b_side}_{ring_idx}"
            bc.assign_material(b_ring, mat_silver)
            bc.assign_rigid_weight(b_ring, "head")
            created_pieces.append(b_ring)
            
    # ---------------- 4. HEAVY FUR SHOULDER MANTLE ----------------
    # Main Fur Mantle (Broad thick pelt resting on shoulders)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.25, minor_radius=0.075, location=(0.0, -0.01, 1.46))
    fur_mantle = bpy.context.active_object
    fur_mantle.name = "Viking_Fur_Mantle"
    fur_mantle.scale = (1.25, 1.05, 0.9)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(fur_mantle, mat_fur)
    bc.assign_weighted_bones(fur_mantle, {
        "spine_04": 0.3,
        "spine_05": 0.4,
        "clavicle_l": 0.15,
        "clavicle_r": 0.15
    })
    created_pieces.append(fur_mantle)
    
    # Back Fur Cape Drape (Flowing pelt covering upper-to-mid back)
    bpy.ops.mesh.primitive_cube_add(size=0.22, location=(0.0, -0.16, 1.30))
    fur_cape = bpy.context.active_object
    fur_cape.name = "Viking_Fur_Cape"
    fur_cape.scale = (1.5, 0.4, 2.2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(fur_cape, mat_fur)
    bc.assign_weighted_bones(fur_cape, {"spine_03": 0.4, "spine_04": 0.4, "spine_05": 0.2})
    created_pieces.append(fur_cape)
    
    # Twin Silver Raven Brooches at collar
    for br_side, br_x in [("L", 0.11), ("R", -0.11)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.038, depth=0.018, location=(br_x, 0.15, 1.44), rotation=(1.5708, 0.0, 0.0))
        brooch = bpy.context.active_object
        brooch.name = f"Viking_Raven_Brooch_{br_side}"
        bc.assign_material(brooch, mat_silver)
        bc.assign_weighted_bones(brooch, {"spine_05": 0.5, f"clavicle_{br_side.lower()}": 0.5})
        created_pieces.append(brooch)
        
    # ---------------- 5. TORSO, WOOLEN TUNIC & LAMELLAR VEST ----------------
    # Broad Muscular Torso & Tunic
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.235, depth=0.42, location=(0.0, -0.01, 1.24))
    torso_tunic = bpy.context.active_object
    torso_tunic.name = "Viking_Wool_Tunic"
    torso_tunic.scale = (1.14, 0.88, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(torso_tunic, mat_tunic)
    bc.assign_weighted_bones(torso_tunic, {
        "spine_01": 0.15,
        "spine_02": 0.25,
        "spine_03": 0.35,
        "spine_04": 0.15,
        "spine_05": 0.10
    })
    created_pieces.append(torso_tunic)
    
    # Hardened Leather Lamellar Cuirass Vest
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.245, depth=0.34, location=(0.0, -0.01, 1.25))
    lamellar_vest = bpy.context.active_object
    lamellar_vest.name = "Viking_Lamellar_Vest"
    lamellar_vest.scale = (1.12, 0.86, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(lamellar_vest, mat_leather)
    bc.assign_weighted_bones(lamellar_vest, {
        "spine_02": 0.35,
        "spine_03": 0.45,
        "spine_04": 0.20
    })
    created_pieces.append(lamellar_vest)
    
    # Cross-body Baldric Belt (Slung from right shoulder to left hip)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.28, minor_radius=0.022, location=(0.0, 0.0, 1.24), rotation=(0.4, 0.6, 0.0))
    baldric = bpy.context.active_object
    baldric.name = "Viking_Baldric"
    baldric.scale = (1.1, 0.85, 0.9)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(baldric, mat_leather)
    bc.assign_weighted_bones(baldric, {"spine_03": 0.6, "spine_04": 0.4})
    created_pieces.append(baldric)
    
    # ---------------- 6. NORSE ROUND SHIELD (Mounted on Back) ----------------
    # Circular Oak Plank Body
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.36, depth=0.035, location=(0.0, -0.22, 1.26), rotation=(1.5708, 0.0, 0.0))
    shield_body = bpy.context.active_object
    shield_body.name = "Viking_Round_Shield"
    bc.assign_material(shield_body, mat_shield_paint)
    bc.assign_weighted_bones(shield_body, {"spine_03": 0.6, "spine_04": 0.4})
    created_pieces.append(shield_body)
    
    # Outer Iron Rim Band
    bpy.ops.mesh.primitive_torus_add(major_radius=0.36, minor_radius=0.018, location=(0.0, -0.22, 1.26), rotation=(1.5708, 0.0, 0.0))
    shield_rim = bpy.context.active_object
    shield_rim.name = "Viking_Shield_Rim"
    bc.assign_material(shield_rim, mat_iron)
    bc.assign_weighted_bones(shield_rim, {"spine_03": 0.6, "spine_04": 0.4})
    created_pieces.append(shield_rim)
    
    # Central Heavy Iron Boss (Umbo)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.085, location=(0.0, -0.25, 1.26))
    shield_boss = bpy.context.active_object
    shield_boss.name = "Viking_Shield_Boss"
    shield_boss.scale = (1.0, 0.5, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(shield_boss, mat_iron)
    bc.assign_weighted_bones(shield_boss, {"spine_03": 0.6, "spine_04": 0.4})
    created_pieces.append(shield_boss)
    
    # ---------------- 7. MUSCULAR ARMS & BRACERS ----------------
    for side, sign in [("L", 1), ("R", -1)]:
        # Upper Arm (Bicep/Tricep)
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.075, depth=0.24, location=(sign * 0.25, 0.02, 1.36), rotation=(0.2, sign * -0.3, 0.0))
        bicep = bpy.context.active_object
        bicep.name = f"Viking_UpperArm_{side}"
        bc.assign_material(bicep, mat_skin)
        bc.assign_rigid_weight(bicep, f"upperarm_{side.lower()}")
        created_pieces.append(bicep)
        
        # Upper arm leather strap with silver ring
        bpy.ops.mesh.primitive_torus_add(major_radius=0.078, minor_radius=0.012, location=(sign * 0.25, 0.02, 1.38), rotation=(0.2, sign * -0.3, 0.0))
        bicep_band = bpy.context.active_object
        bicep_band.name = f"Viking_BicepBand_{side}"
        bc.assign_material(bicep_band, mat_leather)
        bc.assign_rigid_weight(bicep_band, f"upperarm_{side.lower()}")
        created_pieces.append(bicep_band)
        
        # Forearm with Thick Laced Leather Spangen Bracer
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.070, depth=0.23, location=(sign * 0.39, 0.07, 1.15), rotation=(0.3, sign * -0.2, 0.0))
        bracer = bpy.context.active_object
        bracer.name = f"Viking_Bracer_{side}"
        bc.assign_material(bracer, mat_leather)
        bc.assign_rigid_weight(bracer, f"lowerarm_{side.lower()}")
        created_pieces.append(bracer)
        
        # Iron Reinforcement Plates on Bracer
        for s_idx in range(2):
            z_s = 1.19 - (s_idx * 0.08)
            bpy.ops.mesh.primitive_torus_add(major_radius=0.070, minor_radius=0.010, location=(sign * 0.39, 0.07, z_s), rotation=(0.3, sign * -0.2, 0.0))
            splint = bpy.context.active_object
            splint.name = f"Viking_BracerSplint_{side}_{s_idx}"
            bc.assign_material(splint, mat_iron)
            bc.assign_rigid_weight(splint, f"lowerarm_{side.lower()}")
            created_pieces.append(splint)
            
        # Heavy Combat Hand & Leather Wraps
        bpy.ops.mesh.primitive_cube_add(size=0.08, location=(sign * 0.46, -0.15, 1.04))
        hand = bpy.context.active_object
        hand.name = f"Viking_Hand_{side}"
        hand.scale = (0.9, 0.7, 0.4)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(hand, mat_leather)
        bc.assign_rigid_weight(hand, f"hand_{side.lower()}")
        created_pieces.append(hand)
        
    # ---------------- 8. WAR BELT & BREECHES ----------------
    # Studded Leather War Belt
    bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.042, location=(0.0, -0.01, 0.96))
    war_belt = bpy.context.active_object
    war_belt.name = "Viking_War_Belt"
    war_belt.scale = (1.1, 0.86, 0.9)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(war_belt, mat_leather)
    bc.assign_rigid_weight(war_belt, "pelvis")
    created_pieces.append(war_belt)
    
    # Heavy Iron Ring Buckle
    bpy.ops.mesh.primitive_torus_add(major_radius=0.048, minor_radius=0.014, location=(0.0, 0.18, 0.96), rotation=(1.5708, 0.0, 0.0))
    buckle = bpy.context.active_object
    buckle.name = "Viking_Iron_Buckle"
    bc.assign_material(buckle, mat_iron)
    bc.assign_rigid_weight(buckle, "pelvis")
    created_pieces.append(buckle)
    
    # Leather Pouch on Right Hip
    bpy.ops.mesh.primitive_cube_add(size=0.10, location=(-0.21, 0.04, 0.87))
    pouch = bpy.context.active_object
    pouch.name = "Viking_Hip_Pouch"
    pouch.scale = (0.6, 0.9, 1.1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(pouch, mat_leather)
    bc.assign_rigid_weight(pouch, "pelvis")
    created_pieces.append(pouch)
    
    # Woolen Tunic Skirt Hem
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.24, depth=0.18, location=(0.0, -0.01, 0.86))
    tunic_skirt = bpy.context.active_object
    tunic_skirt.name = "Viking_Tunic_Skirt"
    tunic_skirt.scale = (1.12, 0.88, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(tunic_skirt, mat_tunic)
    bc.assign_weighted_bones(tunic_skirt, {"pelvis": 0.8, "spine_01": 0.2})
    created_pieces.append(tunic_skirt)
    
    # ---------------- 9. LEGS, CROSS-GARTERED BREECHES & FUR BOOTS ----------------
    for side, sign in [("L", 1), ("R", -1)]:
        # Upper Thigh Breeches
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.13, depth=0.38, location=(sign * 0.10, -0.01, 0.76))
        thigh = bpy.context.active_object
        thigh.name = f"Viking_Thigh_{side}"
        bc.assign_material(thigh, mat_pants)
        bc.assign_rigid_weight(thigh, f"thigh_{side.lower()}")
        created_pieces.append(thigh)
        
        # Thick Fur Cuff at top of boots
        bpy.ops.mesh.primitive_torus_add(major_radius=0.105, minor_radius=0.030, location=(sign * 0.12, 0.015, 0.50))
        boot_fur = bpy.context.active_object
        boot_fur.name = f"Viking_Boot_Fur_{side}"
        bc.assign_material(boot_fur, mat_fur)
        bc.assign_rigid_weight(boot_fur, f"calf_{side.lower()}")
        created_pieces.append(boot_fur)
        
        # Cross-Gartered Leather Calf & Boot Shaft
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.085, depth=0.36, location=(sign * 0.12, 0.015, 0.30))
        boot_shaft = bpy.context.active_object
        boot_shaft.name = f"Viking_Boot_Shaft_{side}"
        boot_shaft.scale = (0.92, 0.92, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(boot_shaft, mat_leather)
        bc.assign_rigid_weight(boot_shaft, f"calf_{side.lower()}")
        created_pieces.append(boot_shaft)
        
        # Criss-Cross Binding Straps (Winding bands)
        for s_idx in range(3):
            z_strap = 0.40 - (s_idx * 0.09)
            bpy.ops.mesh.primitive_torus_add(major_radius=0.088, minor_radius=0.008, location=(sign * 0.12, 0.015, z_strap))
            strap = bpy.context.active_object
            strap.name = f"Viking_Strap_{side}_{s_idx}"
            bc.assign_material(strap, mat_tunic)
            bc.assign_rigid_weight(strap, f"calf_{side.lower()}")
            created_pieces.append(strap)
            
        # Sturdy Leather Riding Boot Foot
        bpy.ops.mesh.primitive_cube_add(size=0.11, location=(sign * 0.14, -0.04, 0.04))
        boot_foot = bpy.context.active_object
        boot_foot.name = f"Viking_Boot_Foot_{side}"
        boot_foot.scale = (0.9, 1.9, 0.45)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(boot_foot, mat_leather)
        bc.assign_rigid_weight(boot_foot, f"foot_{side.lower()}")
        created_pieces.append(boot_foot)
        
    # Join all pieces into one high-detail character mesh
    bpy.ops.object.select_all(action='DESELECT')
    for p in created_pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = created_pieces[0]
    bpy.ops.object.join()
    
    char_mesh = created_pieces[0]
    char_mesh.name = "Viking_Warrior_Mesh"
    
    # Parent to UE5 armature
    char_mesh.parent = arm
    mod = char_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    
    # Export FBX
    bc.export_fbx(out_fbx)
    return {
        "character": "Viking",
        "output_fbx": out_fbx,
        "mesh_name": char_mesh.name,
        "polys": len(char_mesh.data.polygons),
        "verts": len(char_mesh.data.vertices),
        "materials": [m.name for m in char_mesh.data.materials if m]
    }

if __name__ == "__main__":
    res = build_detailed_viking()
    print("Result:", res)
