"""
build_samurai.py - Generates the Samurai character build rigged to UE5 Mannequin armature.
"""

import sys
import os
import math
sys.path.append(r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Scripts\CharacterBuilders")

import bpy
import builder_common as bc

def build_samurai():
    fbx_base = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_Samurai.fbx"
    
    arm, base_mesh = bc.load_base_model(fbx_base)
    base_mesh.name = "Samurai_BaseBody"
    
    # Materials
    mat_armor = bc.create_pbr_material("M_Samurai_Armor", base_color=(0.55, 0.04, 0.04, 1.0), metallic=0.35, roughness=0.25) # Lacquered Red
    mat_gold = bc.create_pbr_material("M_Samurai_Gold", base_color=(1.0, 0.78, 0.28, 1.0), metallic=0.95, roughness=0.18) # 24k Gold
    mat_iron = bc.create_pbr_material("M_Samurai_Iron", base_color=(0.08, 0.08, 0.09, 1.0), metallic=0.85, roughness=0.35) # Blackened Iron
    mat_fabric = bc.create_pbr_material("M_Samurai_Fabric", base_color=(0.05, 0.08, 0.16, 1.0), metallic=0.0, roughness=0.85) # Indigo Silk
    mat_lacing = bc.create_pbr_material("M_Samurai_Lacing", base_color=(0.85, 0.12, 0.12, 1.0), metallic=0.05, roughness=0.6) # Crimson Cords
    
    bc.assign_material(base_mesh, mat_fabric)
    
    created_pieces = []
    
    # 1. KABUTO HELMET DOME
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.155, location=(0.0, -0.015, 1.74))
    kabuto = bpy.context.active_object
    kabuto.name = "Samurai_Kabuto_Dome"
    kabuto.scale = (1.0, 1.15, 0.95)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(kabuto, mat_armor)
    bc.assign_rigid_weight(kabuto, "head")
    created_pieces.append(kabuto)
    
    # Tehen vent at top
    bpy.ops.mesh.primitive_torus_add(major_radius=0.035, minor_radius=0.01, location=(0.0, -0.015, 1.88))
    tehen = bpy.context.active_object
    tehen.name = "Samurai_Tehen_Gold"
    bc.assign_material(tehen, mat_gold)
    bc.assign_rigid_weight(tehen, "head")
    created_pieces.append(tehen)
    
    # 2. MAEDATE CRESCENT CREST (Front horn)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.01, depth=0.32, location=(0.0, 0.13, 1.83), rotation=(0.0, 1.5708, 0.0))
    crest_base = bpy.context.active_object
    # Flatten into curved crescent horn
    crest_base.scale = (1.1, 0.3, 1.2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    crest_base.name = "Samurai_Maedate_Crescent"
    bc.assign_material(crest_base, mat_gold)
    bc.assign_rigid_weight(crest_base, "head")
    created_pieces.append(crest_base)
    
    # Central golden sun crest disc
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.045, depth=0.015, location=(0.0, 0.138, 1.74), rotation=(1.5708, 0.0, 0.0))
    crest_disc = bpy.context.active_object
    crest_disc.name = "Samurai_Crest_Disc"
    bc.assign_material(crest_disc, mat_gold)
    bc.assign_rigid_weight(crest_disc, "head")
    created_pieces.append(crest_disc)
    
    # 3. SHIKORO (Neck guard tiers)
    for i in range(3):
        z_offset = 1.66 - (i * 0.04)
        rad = 0.175 + (i * 0.02)
        bpy.ops.mesh.primitive_torus_add(major_radius=rad, minor_radius=0.018, location=(0.0, -0.03, z_offset))
        shikoro_tier = bpy.context.active_object
        shikoro_tier.name = f"Samurai_Shikoro_Tier_{i}"
        shikoro_tier.scale = (1.05, 1.25, 0.7)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(shikoro_tier, mat_armor if i % 2 == 0 else mat_iron)
        bc.assign_rigid_weight(shikoro_tier, "head")
        created_pieces.append(shikoro_tier)
        
    # 4. MENPO (Face mask)
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0.0, 0.10, 1.62))
    menpo = bpy.context.active_object
    menpo.name = "Samurai_Menpo_Mask"
    menpo.scale = (1.1, 0.7, 1.2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(menpo, mat_iron)
    bc.assign_rigid_weight(menpo, "head")
    created_pieces.append(menpo)
    
    # 5. DO CUIRASS (Torso chestplate and backplate)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.23, depth=0.38, location=(0.0, -0.01, 1.24))
    cuirass = bpy.context.active_object
    cuirass.name = "Samurai_Do_Cuirass"
    cuirass.scale = (1.1, 0.85, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(cuirass, mat_armor)
    bc.assign_weighted_bones(cuirass, {
        "spine_01": 0.15,
        "spine_02": 0.25,
        "spine_03": 0.35,
        "spine_04": 0.15,
        "spine_05": 0.10
    })
    created_pieces.append(cuirass)
    
    # Munaita gold chest plate
    bpy.ops.mesh.primitive_cube_add(size=0.15, location=(0.0, 0.17, 1.36))
    munaita = bpy.context.active_object
    munaita.name = "Samurai_Munaita_Plate"
    munaita.scale = (1.5, 0.15, 0.7)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(munaita, mat_gold)
    bc.assign_weighted_bones(munaita, {"spine_03": 0.6, "spine_04": 0.4})
    created_pieces.append(munaita)
    
    # 6. SODE (Shoulder shields)
    for side, sign in [("L", 1), ("R", -1)]:
        for tier in range(4):
            z_pos = 1.48 - (tier * 0.045)
            x_pos = sign * (0.23 + (tier * 0.015))
            bpy.ops.mesh.primitive_cube_add(size=0.12, location=(x_pos, 0.01, z_pos))
            sode = bpy.context.active_object
            sode.name = f"Samurai_Sode_{side}_Tier_{tier}"
            sode.scale = (0.25, 1.5, 0.35)
            sode.rotation_euler = (0.0, sign * -0.25, 0.0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            bc.assign_material(sode, mat_armor if tier % 2 == 0 else mat_gold)
            clav_bone = f"clavicle_{side.lower()}"
            arm_bone = f"upperarm_{side.lower()}"
            bc.assign_weighted_bones(sode, {clav_bone: 0.35, arm_bone: 0.65})
            created_pieces.append(sode)
            
    # 7. KOTE (Vambraces / forearm iron plates)
    for side, sign in [("L", 1), ("R", -1)]:
        # Forearm splints
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.065, depth=0.22, location=(sign * 0.39, 0.07, 1.15), rotation=(0.3, sign * -0.2, 0.0))
        kote = bpy.context.active_object
        kote.name = f"Samurai_Kote_{side}"
        kote.scale = (1.0, 0.8, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(kote, mat_iron)
        bc.assign_rigid_weight(kote, f"lowerarm_{side.lower()}")
        created_pieces.append(kote)
        
        # Tekko (Back of hand plates)
        bpy.ops.mesh.primitive_cube_add(size=0.06, location=(sign * 0.46, -0.15, 1.04))
        tekko = bpy.context.active_object
        tekko.name = f"Samurai_Tekko_{side}"
        tekko.scale = (1.0, 0.7, 0.25)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(tekko, mat_gold)
        bc.assign_rigid_weight(tekko, f"hand_{side.lower()}")
        created_pieces.append(tekko)
        
    # 8. OBI SASH & KUSAZURI (Waist sash & hanging thigh tassets)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.21, minor_radius=0.035, location=(0.0, -0.01, 0.96))
    obi = bpy.context.active_object
    obi.name = "Samurai_Obi_Sash"
    obi.scale = (1.1, 0.85, 0.9)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(obi, mat_gold)
    bc.assign_rigid_weight(obi, "pelvis")
    created_pieces.append(obi)
    
    # 6 Hanging Kusazuri plates
    kusazuri_positions = [
        ("Front_L", (0.09, 0.17, 0.84), (0.1, 0.05, 0.0)),
        ("Front_R", (-0.09, 0.17, 0.84), (0.1, -0.05, 0.0)),
        ("Side_L", (0.21, 0.0, 0.84), (0.0, 0.15, 0.0)),
        ("Side_R", (-0.21, 0.0, 0.84), (0.0, -0.15, 0.0)),
        ("Back_L", (0.09, -0.18, 0.84), (-0.1, 0.05, 0.0)),
        ("Back_R", (-0.09, -0.18, 0.84), (-0.1, -0.05, 0.0)),
    ]
    for k_name, pos, rot in kusazuri_positions:
        bpy.ops.mesh.primitive_cube_add(size=0.14, location=pos, rotation=rot)
        k_plate = bpy.context.active_object
        k_plate.name = f"Samurai_Kusazuri_{k_name}"
        k_plate.scale = (0.75, 0.15, 1.4)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(k_plate, mat_armor)
        bc.assign_weighted_bones(k_plate, {"pelvis": 0.75, "spine_01": 0.25})
        created_pieces.append(k_plate)
        
    # Katana Mount Rings on Left Hip
    bpy.ops.mesh.primitive_torus_add(major_radius=0.04, minor_radius=0.008, location=(0.23, 0.03, 0.94), rotation=(0.0, 1.5708, 0.0))
    mount_ring = bpy.context.active_object
    mount_ring.name = "Samurai_Katana_Mount_Ring"
    bc.assign_material(mount_ring, mat_gold)
    bc.assign_rigid_weight(mount_ring, "pelvis")
    created_pieces.append(mount_ring)
    
    # 9. SUNEATE (Shin greaves) & TATEAGE (Knee plates)
    for side, sign in [("L", 1), ("R", -1)]:
        # Shin splint guard
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.08, depth=0.34, location=(sign * 0.12, 0.01, 0.32))
        suneate = bpy.context.active_object
        suneate.name = f"Samurai_Suneate_{side}"
        suneate.scale = (0.9, 0.9, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(suneate, mat_armor)
        bc.assign_rigid_weight(suneate, f"calf_{side.lower()}")
        created_pieces.append(suneate)
        
        # Hexagonal Tateage knee plate
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.075, depth=0.03, location=(sign * 0.12, 0.08, 0.52), rotation=(1.5708, 0.0, 0.0))
        tateage = bpy.context.active_object
        tateage.name = f"Samurai_Tateage_{side}"
        bc.assign_material(tateage, mat_gold)
        bc.assign_rigid_weight(tateage, f"calf_{side.lower()}")
        created_pieces.append(tateage)
        
        # Armored Waraji / Sandal Footwear
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(sign * 0.14, -0.05, 0.04))
        waraji = bpy.context.active_object
        waraji.name = f"Samurai_Waraji_{side}"
        waraji.scale = (0.9, 1.8, 0.4)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(waraji, mat_iron)
        bc.assign_rigid_weight(waraji, f"foot_{side.lower()}")
        created_pieces.append(waraji)
        
    # Join all armor pieces and parent to armature
    bpy.ops.object.select_all(action='DESELECT')
    for p in created_pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = created_pieces[0]
    bpy.ops.object.join()
    
    armor_mesh = created_pieces[0]
    armor_mesh.name = "Samurai_Armor_Mesh"
    
    # Parent armor_mesh to armature
    armor_mesh.parent = arm
    mod = armor_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    
    # Export FBX
    bc.export_fbx(out_fbx)
    return {
        "character": "Samurai",
        "output_fbx": out_fbx,
        "base_mesh": base_mesh.name,
        "armor_mesh": armor_mesh.name,
        "polys": len(armor_mesh.data.polygons) + len(base_mesh.data.polygons)
    }

if __name__ == "__main__":
    res = build_samurai()
    print("Result:", res)
