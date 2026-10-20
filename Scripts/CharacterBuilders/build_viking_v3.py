"""
build_viking_v3.py - True centimeter-scale, authentic detailed Viking character.
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
    base_mesh.name = "Viking_Undersuit"
    
    # Materials
    mat_iron = bc.create_pbr_material("M_Viking_Iron", base_color=(0.32, 0.33, 0.36, 1.0), metallic=0.92, roughness=0.35)
    mat_silver = bc.create_pbr_material("M_Viking_Silver", base_color=(0.85, 0.86, 0.88, 1.0), metallic=0.96, roughness=0.20)
    mat_leather = bc.create_pbr_material("M_Viking_Leather", base_color=(0.14, 0.08, 0.04, 1.0), metallic=0.02, roughness=0.72)
    mat_fur = bc.create_pbr_material("M_Viking_Fur", base_color=(0.36, 0.33, 0.30, 1.0), metallic=0.0, roughness=0.95)
    mat_wool = bc.create_pbr_material("M_Viking_Wool", base_color=(0.06, 0.16, 0.08, 1.0), metallic=0.0, roughness=0.88)
    mat_beard = bc.create_pbr_material("M_Viking_Beard", base_color=(0.32, 0.18, 0.07, 1.0), metallic=0.0, roughness=0.82)
    mat_shield_wood = bc.create_pbr_material("M_Viking_ShieldWood", base_color=(0.38, 0.24, 0.12, 1.0), metallic=0.0, roughness=0.75)
    mat_shield_red = bc.create_pbr_material("M_Viking_ShieldPaint", base_color=(0.58, 0.08, 0.08, 1.0), metallic=0.05, roughness=0.60)
    mat_skin = bc.create_pbr_material("M_Viking_Skin", base_color=(0.82, 0.62, 0.50, 1.0), metallic=0.0, roughness=0.55)
    
    bc.assign_material(base_mesh, mat_wool)
    created_pieces = []
    
    # ---------------- 1. GJERMUNDBU SPECTACLE HELMET (at true cm scale: Z=165 to 192 cm) ----------------
    # Iron Spangenhelm Dome
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=15.5, location=(0.0, -1.5, 173.0))
    helm = bpy.context.active_object
    helm.name = "Viking_Helm_Dome"
    helm.scale = (1.02, 1.15, 1.02)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(helm, mat_iron)
    bc.assign_rigid_weight(helm, "head")
    created_pieces.append(helm)
    
    # Helmet Rim Band
    bpy.ops.mesh.primitive_torus_add(major_radius=15.8, minor_radius=1.4, location=(0.0, -1.5, 168.0))
    helm_rim = bpy.context.active_object
    helm_rim.name = "Viking_Helm_Rim"
    helm_rim.scale = (1.02, 1.15, 0.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(helm_rim, mat_silver)
    bc.assign_rigid_weight(helm_rim, "head")
    created_pieces.append(helm_rim)
    
    # Cross Bands (Front-to-back & side-to-side)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.6, depth=33.0, location=(0.0, -1.5, 178.0), rotation=(1.5708, 0.0, 0.0))
    rib_fb = bpy.context.active_object
    rib_fb.name = "Viking_Rib_FB"
    bc.assign_material(rib_fb, mat_silver)
    bc.assign_rigid_weight(rib_fb, "head")
    created_pieces.append(rib_fb)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.6, depth=33.0, location=(0.0, -1.5, 178.0), rotation=(0.0, 1.5708, 0.0))
    rib_lr = bpy.context.active_object
    rib_lr.name = "Viking_Rib_LR"
    bc.assign_material(rib_lr, mat_silver)
    bc.assign_rigid_weight(rib_lr, "head")
    created_pieces.append(rib_lr)
    
    # Apex Spike
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=2.5, radius2=0.5, depth=6.0, location=(0.0, -1.5, 191.0))
    apex_spike = bpy.context.active_object
    apex_spike.name = "Viking_Apex_Spike"
    bc.assign_material(apex_spike, mat_silver)
    bc.assign_rigid_weight(apex_spike, "head")
    created_pieces.append(apex_spike)
    
    # Spectacle Ocular Eye Guards (Iconic Viking Mask)
    for eye_side, eye_x in [("L", 4.8), ("R", -4.8)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=4.2, minor_radius=1.2, location=(eye_x, 13.5, 168.0), rotation=(1.5708, 0.0, 0.0))
        ocular = bpy.context.active_object
        ocular.name = f"Viking_Ocular_{eye_side}"
        bc.assign_material(ocular, mat_iron)
        bc.assign_rigid_weight(ocular, "head")
        created_pieces.append(ocular)
        
    # Nasal Guard Bar
    bpy.ops.mesh.primitive_cube_add(size=6.0, location=(0.0, 15.0, 163.0))
    nasal = bpy.context.active_object
    nasal.name = "Viking_Nasal_Bar"
    nasal.scale = (0.3, 0.25, 1.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(nasal, mat_iron)
    bc.assign_rigid_weight(nasal, "head")
    created_pieces.append(nasal)
    
    # Chainmail Aventail (Neck drape behind helmet)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=17.5, depth=18.0, location=(0.0, -2.0, 155.0))
    aventail = bpy.context.active_object
    aventail.name = "Viking_Mail_Aventail"
    aventail.scale = (1.05, 1.15, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(aventail, mat_iron)
    bc.assign_weighted_bones(aventail, {"neck_01": 0.6, "head": 0.4})
    created_pieces.append(aventail)
    
    # ---------------- 2. MASSIVE BRAIDED BEARD (Z=130 to 160 cm) ----------------
    # Upper Mustache
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=2.5, depth=14.0, location=(0.0, 12.5, 159.0), rotation=(0.0, 1.5708, 0.0))
    mustache = bpy.context.active_object
    mustache.name = "Viking_Mustache"
    mustache.scale = (1.0, 0.6, 0.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(mustache, mat_beard)
    bc.assign_rigid_weight(mustache, "head")
    created_pieces.append(mustache)
    
    # Main Chin Beard Mass
    bpy.ops.mesh.primitive_cube_add(size=14.0, location=(0.0, 10.0, 148.0))
    chin_beard = bpy.context.active_object
    chin_beard.name = "Viking_Chin_Beard"
    chin_beard.scale = (1.1, 0.9, 1.4)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(chin_beard, mat_beard)
    bc.assign_rigid_weight(chin_beard, "head")
    created_pieces.append(chin_beard)
    
    # Twin Braided Warrior Plaits (Hanging down over chest)
    for b_side, b_x in [("L", 4.5), ("R", -4.5)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=2.8, depth=32.0, location=(b_x, 11.5, 134.0), rotation=(0.20, 0.0, 0.0))
        braid = bpy.context.active_object
        braid.name = f"Viking_Braid_{b_side}"
        bc.assign_material(braid, mat_beard)
        bc.assign_weighted_bones(braid, {"head": 0.6, "neck_01": 0.4})
        created_pieces.append(braid)
        
        # Silver Beard Rings
        for r_idx, r_z in [(0, 142.0), (1, 126.0)]:
            bpy.ops.mesh.primitive_torus_add(major_radius=2.8, minor_radius=0.8, location=(b_x, 12.0, r_z))
            b_ring = bpy.context.active_object
            b_ring.name = f"Viking_BeardRing_{b_side}_{r_idx}"
            bc.assign_material(b_ring, mat_silver)
            bc.assign_rigid_weight(b_ring, "head")
            created_pieces.append(b_ring)
            
    # ---------------- 3. HEAVY FUR SHOULDER MANTLE (Z=140 to 155 cm) ----------------
    bpy.ops.mesh.primitive_torus_add(major_radius=25.0, minor_radius=7.5, location=(0.0, -1.0, 146.0))
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
    
    # Back Fur Cape Drape
    bpy.ops.mesh.primitive_cube_add(size=22.0, location=(0.0, -16.0, 128.0))
    fur_cape = bpy.context.active_object
    fur_cape.name = "Viking_Fur_Cape"
    fur_cape.scale = (1.5, 0.4, 2.4)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(fur_cape, mat_fur)
    bc.assign_weighted_bones(fur_cape, {"spine_03": 0.4, "spine_04": 0.4, "spine_05": 0.2})
    created_pieces.append(fur_cape)
    
    # Twin Silver Raven Brooches at collar
    for br_side, br_x in [("L", 11.0), ("R", -11.0)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=3.8, depth=1.8, location=(br_x, 15.0, 144.0), rotation=(1.5708, 0.0, 0.0))
        brooch = bpy.context.active_object
        brooch.name = f"Viking_Raven_Brooch_{br_side}"
        bc.assign_material(brooch, mat_silver)
        bc.assign_weighted_bones(brooch, {"spine_05": 0.5, f"clavicle_{br_side.lower()}": 0.5})
        created_pieces.append(brooch)
        
    # ---------------- 4. LAMELLAR & LEATHER CUIRASS (Z=105 to 142 cm) ----------------
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=24.0, depth=36.0, location=(0.0, -1.0, 122.0))
    cuirass = bpy.context.active_object
    cuirass.name = "Viking_Lamellar_Cuirass"
    cuirass.scale = (1.12, 0.88, 1.0)
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
    
    # Iron Lamellar Plates across chest
    for row in range(3):
        z_lam = 133.0 - (row * 7.0)
        for col in range(4):
            x_lam = -12.0 + (col * 8.0)
            bpy.ops.mesh.primitive_cube_add(size=5.0, location=(x_lam, 17.0, z_lam))
            lam_p = bpy.context.active_object
            lam_p.name = f"Viking_Lamellar_{row}_{col}"
            lam_p.scale = (1.2, 0.15, 1.0)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bc.assign_material(lam_p, mat_iron)
            bc.assign_weighted_bones(lam_p, {"spine_03": 0.7, "spine_04": 0.3})
            created_pieces.append(lam_p)
            
    # Central Valknut Knotwork Medallion
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=4.5, depth=1.8, location=(0.0, 17.5, 122.0), rotation=(1.5708, 0.0, 0.0))
    valknut = bpy.context.active_object
    valknut.name = "Viking_Valknut"
    bc.assign_material(valknut, mat_silver)
    bc.assign_weighted_bones(valknut, {"spine_02": 0.5, "spine_03": 0.5})
    created_pieces.append(valknut)
    
    # ---------------- 5. NORSE ROUND SHIELD (SLUNG ON BACK) ----------------
    # Circular Oak Plank Shield Body (Radius = 36 cm!)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=36.0, depth=3.5, location=(0.0, -22.0, 126.0), rotation=(1.5708, 0.0, 0.0))
    shield_body = bpy.context.active_object
    shield_body.name = "Viking_Round_Shield"
    bc.assign_material(shield_body, mat_shield_red)
    bc.assign_weighted_bones(shield_body, {"spine_03": 0.6, "spine_04": 0.4})
    created_pieces.append(shield_body)
    
    # Outer Iron Rim Band
    bpy.ops.mesh.primitive_torus_add(major_radius=36.0, minor_radius=1.8, location=(0.0, -22.0, 126.0), rotation=(1.5708, 0.0, 0.0))
    shield_rim = bpy.context.active_object
    shield_rim.name = "Viking_Shield_Rim"
    bc.assign_material(shield_rim, mat_iron)
    bc.assign_weighted_bones(shield_rim, {"spine_03": 0.6, "spine_04": 0.4})
    created_pieces.append(shield_rim)
    
    # Central Heavy Iron Boss (Umbo)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=8.5, location=(0.0, -25.0, 126.0))
    shield_boss = bpy.context.active_object
    shield_boss.name = "Viking_Shield_Boss"
    shield_boss.scale = (1.0, 0.5, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(shield_boss, mat_iron)
    bc.assign_weighted_bones(shield_boss, {"spine_03": 0.6, "spine_04": 0.4})
    created_pieces.append(shield_boss)
    
    # ---------------- 6. ARMS, SPANGEN BRACERS & COMBAT WRAPS ----------------
    for side, sign in [("L", 1), ("R", -1)]:
        # Heavy leather forearm bracer
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=7.0, depth=23.0, location=(sign * 39.0, 7.0, 115.0), rotation=(0.3, sign * -0.2, 0.0))
        bracer = bpy.context.active_object
        bracer.name = f"Viking_Bracer_{side}"
        bc.assign_material(bracer, mat_leather)
        bc.assign_rigid_weight(bracer, f"lowerarm_{side.lower()}")
        created_pieces.append(bracer)
        
        # Steel reinforcement splint bands on bracer
        for s_idx in range(2):
            z_s = 119.0 - (s_idx * 8.0)
            bpy.ops.mesh.primitive_torus_add(major_radius=7.0, minor_radius=1.0, location=(sign * 39.0, 7.0, z_s), rotation=(0.3, sign * -0.2, 0.0))
            splint = bpy.context.active_object
            splint.name = f"Viking_BracerSplint_{side}_{s_idx}"
            bc.assign_material(splint, mat_iron)
            bc.assign_rigid_weight(splint, f"lowerarm_{side.lower()}")
            created_pieces.append(splint)
            
        # Studded Hand Combat Wrap
        bpy.ops.mesh.primitive_cube_add(size=8.0, location=(sign * 46.0, -15.0, 104.0))
        hand = bpy.context.active_object
        hand.name = f"Viking_Hand_{side}"
        hand.scale = (0.9, 0.7, 0.4)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(hand, mat_leather)
        bc.assign_rigid_weight(hand, f"hand_{side.lower()}")
        created_pieces.append(hand)
        
    # ---------------- 7. STUDDED WAR BELT & HIP POUCH (Z=90 to 102 cm) ----------------
    bpy.ops.mesh.primitive_torus_add(major_radius=22.0, minor_radius=4.2, location=(0.0, -1.0, 96.0))
    war_belt = bpy.context.active_object
    war_belt.name = "Viking_War_Belt"
    war_belt.scale = (1.1, 0.86, 0.9)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(war_belt, mat_leather)
    bc.assign_rigid_weight(war_belt, "pelvis")
    created_pieces.append(war_belt)
    
    # Heavy Iron Ring Buckle
    bpy.ops.mesh.primitive_torus_add(major_radius=4.8, minor_radius=1.4, location=(0.0, 18.0, 96.0), rotation=(1.5708, 0.0, 0.0))
    buckle = bpy.context.active_object
    buckle.name = "Viking_Iron_Buckle"
    bc.assign_material(buckle, mat_iron)
    bc.assign_rigid_weight(buckle, "pelvis")
    created_pieces.append(buckle)
    
    # Leather Pouch on Right Hip
    bpy.ops.mesh.primitive_cube_add(size=10.0, location=(-21.0, 4.0, 87.0))
    pouch = bpy.context.active_object
    pouch.name = "Viking_Hip_Pouch"
    pouch.scale = (0.6, 0.9, 1.1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(pouch, mat_leather)
    bc.assign_rigid_weight(pouch, "pelvis")
    created_pieces.append(pouch)
    
    # Woolen Tunic Skirt
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=24.0, depth=18.0, location=(0.0, -1.0, 86.0))
    tunic_skirt = bpy.context.active_object
    tunic_skirt.name = "Viking_Tunic_Skirt"
    tunic_skirt.scale = (1.12, 0.88, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(tunic_skirt, mat_wool)
    bc.assign_weighted_bones(tunic_skirt, {"pelvis": 0.8, "spine_01": 0.2})
    created_pieces.append(tunic_skirt)
    
    # ---------------- 8. CROSS-GARTERED LEGS & FUR BOOTS (Z=0 to 55 cm) ----------------
    for side, sign in [("L", 1), ("R", -1)]:
        # Fur cuff at knee/top of boot
        bpy.ops.mesh.primitive_torus_add(major_radius=10.5, minor_radius=3.0, location=(sign * 12.0, 1.5, 50.0))
        boot_fur = bpy.context.active_object
        boot_fur.name = f"Viking_Boot_Fur_{side}"
        bc.assign_material(boot_fur, mat_fur)
        bc.assign_rigid_weight(boot_fur, f"calf_{side.lower()}")
        created_pieces.append(boot_fur)
        
        # Leather boot shaft
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=8.5, depth=36.0, location=(sign * 12.0, 1.5, 30.0))
        boot_shaft = bpy.context.active_object
        boot_shaft.name = f"Viking_Boot_Shaft_{side}"
        boot_shaft.scale = (0.92, 0.92, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(boot_shaft, mat_leather)
        bc.assign_rigid_weight(boot_shaft, f"calf_{side.lower()}")
        created_pieces.append(boot_shaft)
        
        # Cross-gartering binding straps
        for s_idx in range(3):
            z_strap = 40.0 - (s_idx * 9.0)
            bpy.ops.mesh.primitive_torus_add(major_radius=8.8, minor_radius=0.8, location=(sign * 12.0, 1.5, z_strap))
            strap = bpy.context.active_object
            strap.name = f"Viking_Strap_{side}_{s_idx}"
            bc.assign_material(strap, mat_wool)
            bc.assign_rigid_weight(strap, f"calf_{side.lower()}")
            created_pieces.append(strap)
            
        # Sturdy Leather Riding Boot Foot
        bpy.ops.mesh.primitive_cube_add(size=11.0, location=(sign * 14.0, -4.0, 4.0))
        boot_foot = bpy.context.active_object
        boot_foot.name = f"Viking_Boot_Foot_{side}"
        boot_foot.scale = (0.9, 1.9, 0.45)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(boot_foot, mat_leather)
        bc.assign_rigid_weight(boot_foot, f"foot_{side.lower()}")
        created_pieces.append(boot_foot)
        
    # Join all armor pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in created_pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = created_pieces[0]
    bpy.ops.object.join()
    
    char_armor = created_pieces[0]
    char_armor.name = "Viking_Armor_Rigged"
    char_armor.parent = arm
    mod = char_armor.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    
    # Export FBX
    bc.export_fbx(out_fbx)
    return {
        "character": "Viking",
        "output_fbx": out_fbx,
        "polys": len(char_armor.data.polygons) + len(base_mesh.data.polygons)
    }

if __name__ == "__main__":
    res = build_viking()
    print("Result:", res)
