"""
build_medieval_warrior.py - Generates the Medieval Warrior (Knight Paladin) build rigged to UE5 Mannequin armature.
"""

import sys
import os
import math
sys.path.append(r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Scripts\CharacterBuilders")

import bpy
import builder_common as bc

def build_medieval_warrior():
    fbx_base = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_MedievalWarrior.fbx"
    
    arm, base_mesh = bc.load_base_model(fbx_base)
    base_mesh.name = "Knight_BaseBody"
    
    # Materials
    mat_steel = bc.create_pbr_material("M_Knight_Steel", base_color=(0.78, 0.80, 0.84, 1.0), metallic=0.96, roughness=0.18) # Polished Plate Steel
    mat_brass = bc.create_pbr_material("M_Knight_Brass", base_color=(0.88, 0.72, 0.28, 1.0), metallic=0.92, roughness=0.25) # Brass Rivets & Trim
    mat_dark_steel = bc.create_pbr_material("M_Knight_DarkSteel", base_color=(0.30, 0.32, 0.35, 1.0), metallic=0.90, roughness=0.35) # Dark Steel / Chainmail
    mat_blue = bc.create_pbr_material("M_Knight_Blue", base_color=(0.04, 0.16, 0.45, 1.0), metallic=0.05, roughness=0.75) # Royal Cobalt Azure
    mat_leather = bc.create_pbr_material("M_Knight_Leather", base_color=(0.18, 0.10, 0.06, 1.0), metallic=0.02, roughness=0.70) # Brown Saddle Leather
    
    bc.assign_material(base_mesh, mat_dark_steel)
    created_pieces = []
    
    # 1. ARMET / GREAT BASINET HELMET WITH POINTED VISOR
    # Helmet Bowl
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.155, location=(0.0, -0.015, 1.74))
    helm = bpy.context.active_object
    helm.name = "Knight_Helmet_Bowl"
    helm.scale = (1.0, 1.15, 1.05)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(helm, mat_steel)
    bc.assign_rigid_weight(helm, "head")
    created_pieces.append(helm)
    
    # Central Ridge Crest running front-to-back
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.012, depth=0.30, location=(0.0, -0.01, 1.84), rotation=(1.5708, 0.0, 0.0))
    ridge = bpy.context.active_object
    ridge.name = "Knight_Helmet_Ridge"
    ridge.scale = (0.5, 1.0, 1.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(ridge, mat_brass)
    bc.assign_rigid_weight(ridge, "head")
    created_pieces.append(ridge)
    
    # Pointed Hounskull / Pig-Face Visor with Vision Slits
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.11, radius2=0.015, depth=0.18, location=(0.0, 0.16, 1.66), rotation=(-1.35, 0.0, 0.0))
    visor = bpy.context.active_object
    visor.name = "Knight_Visor_Hounskull"
    visor.scale = (1.1, 1.0, 0.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(visor, mat_steel)
    bc.assign_rigid_weight(visor, "head")
    created_pieces.append(visor)
    
    # Horizontal Brass Vision Slit Trim
    bpy.ops.mesh.primitive_cube_add(size=0.08, location=(0.0, 0.15, 1.71))
    slit = bpy.context.active_object
    slit.name = "Knight_Vision_Slit"
    slit.scale = (1.6, 0.15, 0.15)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(slit, mat_brass)
    bc.assign_rigid_weight(slit, "head")
    created_pieces.append(slit)
    
    # Flared Steel Gorget Neck Guard
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.16, depth=0.12, location=(0.0, 0.0, 1.54))
    gorget = bpy.context.active_object
    gorget.name = "Knight_Gorget_Collar"
    gorget.scale = (1.1, 1.0, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(gorget, mat_steel)
    bc.assign_weighted_bones(gorget, {"neck_01": 0.5, "spine_05": 0.5})
    created_pieces.append(gorget)
    
    # Royal Feather Plume at apex
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.03, radius2=0.005, depth=0.22, location=(0.0, -0.12, 1.90), rotation=(0.4, 0.0, 0.0))
    plume = bpy.context.active_object
    plume.name = "Knight_Helmet_Plume"
    bc.assign_material(plume, mat_blue)
    bc.assign_rigid_weight(plume, "head")
    created_pieces.append(plume)
    
    # 2. GOTHIC FLUTED BREASTPLATE & BACKPLATE
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.235, depth=0.40, location=(0.0, -0.01, 1.25))
    cuirass = bpy.context.active_object
    cuirass.name = "Knight_Plate_Cuirass"
    cuirass.scale = (1.12, 0.88, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(cuirass, mat_steel)
    bc.assign_weighted_bones(cuirass, {
        "spine_01": 0.15,
        "spine_02": 0.25,
        "spine_03": 0.35,
        "spine_04": 0.15,
        "spine_05": 0.10
    })
    created_pieces.append(cuirass)
    
    # Heraldic Shield on Chest
    bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.075, depth=0.018, location=(0.0, 0.175, 1.34), rotation=(1.5708, 0.0, 0.0))
    heraldic = bpy.context.active_object
    heraldic.name = "Knight_Heraldic_Shield"
    heraldic.scale = (1.0, 1.3, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(heraldic, mat_blue)
    bc.assign_weighted_bones(heraldic, {"spine_03": 0.7, "spine_04": 0.3})
    created_pieces.append(heraldic)
    
    # Brass Lion Emblem inside shield
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.035, depth=0.015, location=(0.0, 0.185, 1.35), rotation=(1.5708, 0.0, 0.0))
    lion = bpy.context.active_object
    lion.name = "Knight_Lion_Emblem"
    bc.assign_material(lion, mat_brass)
    bc.assign_weighted_bones(lion, {"spine_03": 0.7, "spine_04": 0.3})
    created_pieces.append(lion)
    
    # 3. MASSIVE PAULDRONS WITH SWORD-BREAKERS (Gardbrace)
    for side, sign in [("L", 1), ("R", -1)]:
        # Main domed shoulder bell
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.14, location=(sign * 0.25, 0.01, 1.48))
        pauldron = bpy.context.active_object
        pauldron.name = f"Knight_Pauldron_{side}"
        pauldron.scale = (0.9, 1.25, 0.85)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(pauldron, mat_steel)
        bc.assign_weighted_bones(pauldron, {f"clavicle_{side.lower()}": 0.4, f"upperarm_{side.lower()}": 0.6})
        created_pieces.append(pauldron)
        
        # Upright flared Sword-Breaker ridge (Gardbrace)
        bpy.ops.mesh.primitive_cube_add(size=0.12, location=(sign * 0.20, 0.02, 1.56))
        breaker = bpy.context.active_object
        breaker.name = f"Knight_SwordBreaker_{side}"
        breaker.scale = (0.2, 1.2, 0.8)
        breaker.rotation_euler = (0.0, sign * -0.2, 0.0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        bc.assign_material(breaker, mat_brass)
        bc.assign_weighted_bones(breaker, {f"clavicle_{side.lower()}": 0.5, f"upperarm_{side.lower()}": 0.5})
        created_pieces.append(breaker)
        
        # Armored Elbow Cop (Couter)
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.065, depth=0.04, location=(sign * 0.36, -0.05, 1.20), rotation=(0.0, 1.5708, 0.0))
        couter = bpy.context.active_object
        couter.name = f"Knight_Couter_{side}"
        bc.assign_material(couter, mat_brass)
        bc.assign_rigid_weight(couter, f"lowerarm_{side.lower()}")
        created_pieces.append(couter)
        
        # Full Plate Vambrace on Forearm
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.068, depth=0.24, location=(sign * 0.39, 0.07, 1.14), rotation=(0.3, sign * -0.2, 0.0))
        vambrace = bpy.context.active_object
        vambrace.name = f"Knight_Vambrace_{side}"
        bc.assign_material(vambrace, mat_steel)
        bc.assign_rigid_weight(vambrace, f"lowerarm_{side.lower()}")
        created_pieces.append(vambrace)
        
        # Hourglass Finger Gauntlet
        bpy.ops.mesh.primitive_cube_add(size=0.08, location=(sign * 0.46, -0.15, 1.04))
        gauntlet = bpy.context.active_object
        gauntlet.name = f"Knight_Gauntlet_{side}"
        gauntlet.scale = (0.9, 0.8, 0.4)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(gauntlet, mat_steel)
        bc.assign_rigid_weight(gauntlet, f"hand_{side.lower()}")
        created_pieces.append(gauntlet)
        
    # 4. FAULDS & TASSETS OVER CHAINMAIL HAUBERK
    # Segmented Faulds (Steel belt hoops)
    for i in range(2):
        z_offset = 0.98 - (i * 0.05)
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.23 + (i * 0.015), depth=0.045, location=(0.0, -0.01, z_offset))
        fauld = bpy.context.active_object
        fauld.name = f"Knight_Fauld_Hoop_{i}"
        fauld.scale = (1.1, 0.86, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(fauld, mat_steel)
        bc.assign_rigid_weight(fauld, "pelvis")
        created_pieces.append(fauld)
        
    # Twin Hanging Tassets over thighs
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.10, depth=0.02, location=(sign * 0.12, 0.17, 0.82), rotation=(1.5708, 0.0, 0.0))
        tasset = bpy.context.active_object
        tasset.name = f"Knight_Tasset_{side}"
        tasset.scale = (1.0, 1.5, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(tasset, mat_steel)
        bc.assign_weighted_bones(tasset, {"pelvis": 0.8, f"thigh_{side.lower()}": 0.2})
        created_pieces.append(tasset)
        
        # Brass border on tasset
        bpy.ops.mesh.primitive_torus_add(major_radius=0.08, minor_radius=0.008, location=(sign * 0.12, 0.18, 0.82), rotation=(1.5708, 0.0, 0.0))
        tasset_trim = bpy.context.active_object
        tasset_trim.name = f"Knight_Tasset_Trim_{side}"
        bc.assign_material(tasset_trim, mat_brass)
        bc.assign_weighted_bones(tasset_trim, {"pelvis": 0.8, f"thigh_{side.lower()}": 0.2})
        created_pieces.append(tasset_trim)
        
    # 5. POLEYNS, GREAVES & GOTHIC POINTED SABATONS
    for side, sign in [("L", 1), ("R", -1)]:
        # Pointed Poleyn (Knee cop)
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.075, radius2=0.015, depth=0.08, location=(sign * 0.12, 0.09, 0.52), rotation=(1.5708, 0.0, 0.0))
        poleyn = bpy.context.active_object
        poleyn.name = f"Knight_Poleyn_{side}"
        bc.assign_material(poleyn, mat_brass)
        bc.assign_rigid_weight(poleyn, f"calf_{side.lower()}")
        created_pieces.append(poleyn)
        
        # Anatomical Steel Greaves on Shin & Calf
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.082, depth=0.36, location=(sign * 0.12, 0.015, 0.32))
        greave = bpy.context.active_object
        greave.name = f"Knight_Greave_{side}"
        greave.scale = (0.9, 0.9, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(greave, mat_steel)
        bc.assign_rigid_weight(greave, f"calf_{side.lower()}")
        created_pieces.append(greave)
        
        # Pointed Gothic Sabaton (Armored boot with elongated steel toe)
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(sign * 0.14, -0.04, 0.04))
        sabaton = bpy.context.active_object
        sabaton.name = f"Knight_Sabaton_{side}"
        sabaton.scale = (0.9, 1.9, 0.45)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(sabaton, mat_steel)
        bc.assign_rigid_weight(sabaton, f"foot_{side.lower()}")
        created_pieces.append(sabaton)
        
        # Pointed steel toe beak
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.035, radius2=0.005, depth=0.10, location=(sign * 0.14, 0.10, 0.04), rotation=(-1.5708, 0.0, 0.0))
        toe_beak = bpy.context.active_object
        toe_beak.name = f"Knight_Toe_Beak_{side}"
        bc.assign_material(toe_beak, mat_brass)
        bc.assign_rigid_weight(toe_beak, f"foot_{side.lower()}")
        created_pieces.append(toe_beak)
        
    # Join armor pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in created_pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = created_pieces[0]
    bpy.ops.object.join()
    
    armor_mesh = created_pieces[0]
    armor_mesh.name = "Knight_Armor_Mesh"
    armor_mesh.parent = arm
    mod = armor_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    
    bc.export_fbx(out_fbx)
    return {
        "character": "MedievalWarrior",
        "output_fbx": out_fbx,
        "base_mesh": base_mesh.name,
        "armor_mesh": armor_mesh.name,
        "polys": len(armor_mesh.data.polygons) + len(base_mesh.data.polygons)
    }

if __name__ == "__main__":
    res = build_medieval_warrior()
    print("Result:", res)
