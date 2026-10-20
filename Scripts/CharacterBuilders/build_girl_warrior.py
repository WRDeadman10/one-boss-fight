"""
build_girl_warrior.py - Generates the Girl Warrior (Valkyrie / Amazon Champion) build rigged to UE5 Mannequin armature.
"""

import sys
import os
import math
sys.path.append(r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Scripts\CharacterBuilders")

import bpy
import builder_common as bc

def build_girl_warrior():
    fbx_base = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_Quinn.fbx"
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_GirlWarrior.fbx"
    
    arm, base_mesh = bc.load_base_model(fbx_base)
    base_mesh.name = "GirlWarrior_BaseBody"
    
    # Materials
    mat_titanium = bc.create_pbr_material("M_Girl_Titanium", base_color=(0.84, 0.86, 0.90, 1.0), metallic=0.96, roughness=0.20) # Titanium Silver
    mat_leather = bc.create_pbr_material("M_Girl_Leather", base_color=(0.07, 0.07, 0.09, 1.0), metallic=0.04, roughness=0.65) # Tactical Black Leather
    mat_gold = bc.create_pbr_material("M_Girl_Gold", base_color=(0.92, 0.74, 0.45, 1.0), metallic=0.92, roughness=0.25) # Pale Gold Trim
    mat_amethyst = bc.create_pbr_material("M_Girl_Amethyst", base_color=(0.65, 0.10, 0.85, 1.0), metallic=0.10, roughness=0.10, emissive=(0.3, 0.05, 0.45, 1.0)) # Glowing Amethyst
    mat_hair = bc.create_pbr_material("M_Girl_Hair", base_color=(0.18, 0.09, 0.05, 1.0), metallic=0.0, roughness=0.80) # Dark Auburn Ponytail
    mat_cape = bc.create_pbr_material("M_Girl_Cape", base_color=(0.15, 0.05, 0.22, 1.0), metallic=0.02, roughness=0.75) # Twilight Violet
    
    bc.assign_material(base_mesh, mat_leather)
    created_pieces = []
    
    # 1. VALKYRIE WINGED DIADEM & HIGH PONYTAIL
    # Diadem Brow Band
    bpy.ops.mesh.primitive_torus_add(major_radius=0.142, minor_radius=0.012, location=(0.0, -0.01, 1.73))
    diadem = bpy.context.active_object
    diadem.name = "Girl_Diadem_Band"
    diadem.scale = (1.0, 1.10, 0.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(diadem, mat_titanium)
    bc.assign_rigid_weight(diadem, "head")
    created_pieces.append(diadem)
    
    # Amethyst Forehead Gem
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.022, depth=0.012, location=(0.0, 0.138, 1.73), rotation=(1.5708, 0.0, 0.0))
    gem = bpy.context.active_object
    gem.name = "Girl_Diadem_Gem"
    bc.assign_material(gem, mat_amethyst)
    bc.assign_rigid_weight(gem, "head")
    created_pieces.append(gem)
    
    # Winged Side Fins on Temples
    for w_side, w_sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cube_add(size=0.08, location=(w_sign * 0.14, 0.02, 1.78), rotation=(0.3, w_sign * 0.4, 0.0))
        wing_fin = bpy.context.active_object
        wing_fin.name = f"Girl_Wing_Fin_{w_side}"
        wing_fin.scale = (0.2, 1.8, 0.8)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(wing_fin, mat_titanium)
        bc.assign_rigid_weight(wing_fin, "head")
        created_pieces.append(wing_fin)
        
    # High Ponytail flowing backwards
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.035, depth=0.42, location=(0.0, -0.22, 1.62), rotation=(0.55, 0.0, 0.0))
    ponytail = bpy.context.active_object
    ponytail.name = "Girl_Ponytail"
    bc.assign_material(ponytail, mat_hair)
    bc.assign_rigid_weight(ponytail, "head")
    created_pieces.append(ponytail)
    
    # Gold Hair Tie Ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.038, minor_radius=0.010, location=(0.0, -0.12, 1.76), rotation=(0.55, 0.0, 0.0))
    hair_tie = bpy.context.active_object
    hair_tie.name = "Girl_Hair_Tie"
    bc.assign_material(hair_tie, mat_gold)
    bc.assign_rigid_weight(hair_tie, "head")
    created_pieces.append(hair_tie)
    
    # 2. SCULPTED TITANIUM PLATE CUIRASS & CORSET
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.20, depth=0.36, location=(0.0, -0.01, 1.25))
    cuirass = bpy.context.active_object
    cuirass.name = "Girl_Titanium_Cuirass"
    cuirass.scale = (1.06, 0.82, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(cuirass, mat_titanium)
    bc.assign_weighted_bones(cuirass, {
        "spine_01": 0.15,
        "spine_02": 0.25,
        "spine_03": 0.35,
        "spine_04": 0.15,
        "spine_05": 0.10
    })
    created_pieces.append(cuirass)
    
    # Amethyst Sternum Core Medallion
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.045, depth=0.015, location=(0.0, 0.155, 1.32), rotation=(1.5708, 0.0, 0.0))
    core_medallion = bpy.context.active_object
    core_medallion.name = "Girl_Core_Medallion"
    bc.assign_material(core_medallion, mat_amethyst)
    bc.assign_weighted_bones(core_medallion, {"spine_03": 0.7, "spine_04": 0.3})
    created_pieces.append(core_medallion)
    
    # Gold Collar Rim
    bpy.ops.mesh.primitive_torus_add(major_radius=0.14, minor_radius=0.015, location=(0.0, 0.02, 1.45))
    collar_rim = bpy.context.active_object
    collar_rim.name = "Girl_Collar_Rim"
    collar_rim.scale = (1.05, 0.85, 0.6)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(collar_rim, mat_gold)
    bc.assign_weighted_bones(collar_rim, {"neck_01": 0.5, "spine_05": 0.5})
    created_pieces.append(collar_rim)
    
    # 3. FALCON WING PAULDRONS
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.12, location=(sign * 0.21, 0.01, 1.44))
        pauldron = bpy.context.active_object
        pauldron.name = f"Girl_Pauldron_{side}"
        pauldron.scale = (0.8, 1.25, 0.75)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(pauldron, mat_titanium)
        bc.assign_weighted_bones(pauldron, {f"clavicle_{side.lower()}": 0.4, f"upperarm_{side.lower()}": 0.6})
        created_pieces.append(pauldron)
        
        # Feather Blade Fin on Pauldron
        bpy.ops.mesh.primitive_cube_add(size=0.10, location=(sign * 0.25, -0.04, 1.48), rotation=(0.2, sign * -0.3, 0.0))
        pauldron_blade = bpy.context.active_object
        pauldron_blade.name = f"Girl_PauldronBlade_{side}"
        pauldron_blade.scale = (0.2, 1.5, 0.6)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(pauldron_blade, mat_gold)
        bc.assign_weighted_bones(pauldron_blade, {f"clavicle_{side.lower()}": 0.4, f"upperarm_{side.lower()}": 0.6})
        created_pieces.append(pauldron_blade)
        
        # Sleek Pointed Forearm Bracer
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.060, depth=0.22, location=(sign * 0.36, 0.06, 1.16), rotation=(0.3, sign * -0.2, 0.0))
        bracer = bpy.context.active_object
        bracer.name = f"Girl_Bracer_{side}"
        bc.assign_material(bracer, mat_titanium)
        bc.assign_rigid_weight(bracer, f"lowerarm_{side.lower()}")
        created_pieces.append(bracer)
        
        # Parrying Elbow Blade
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.03, radius2=0.005, depth=0.08, location=(sign * 0.33, -0.04, 1.22), rotation=(-1.2, 0.0, 0.0))
        elbow_blade = bpy.context.active_object
        elbow_blade.name = f"Girl_ElbowBlade_{side}"
        bc.assign_material(elbow_blade, mat_titanium)
        bc.assign_rigid_weight(elbow_blade, f"lowerarm_{side.lower()}")
        created_pieces.append(elbow_blade)
        
        # Armored Combat Glove
        bpy.ops.mesh.primitive_cube_add(size=0.065, location=(sign * 0.44, -0.14, 1.05))
        glove = bpy.context.active_object
        glove.name = f"Girl_Glove_{side}"
        glove.scale = (0.9, 0.7, 0.35)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(glove, mat_titanium)
        bc.assign_rigid_weight(glove, f"hand_{side.lower()}")
        created_pieces.append(glove)
        
    # 4. ASYMMETRICAL BATTLE SKIRT & COMBAT FAULDS
    bpy.ops.mesh.primitive_torus_add(major_radius=0.19, minor_radius=0.032, location=(0.0, -0.01, 0.98))
    war_belt = bpy.context.active_object
    war_belt.name = "Girl_War_Belt"
    war_belt.scale = (1.08, 0.84, 0.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(war_belt, mat_titanium)
    bc.assign_rigid_weight(war_belt, "pelvis")
    created_pieces.append(war_belt)
    
    # Asymmetrical Left Hip Combat Tasset
    bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.11, depth=0.02, location=(0.19, 0.0, 0.82), rotation=(0.0, 1.5708, 0.0))
    tasset_l = bpy.context.active_object
    tasset_l.name = "Girl_Tasset_L"
    tasset_l.scale = (1.0, 1.6, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(tasset_l, mat_titanium)
    bc.assign_weighted_bones(tasset_l, {"pelvis": 0.8, "thigh_l": 0.2})
    created_pieces.append(tasset_l)
    
    # Violet Capelet draped over back
    bpy.ops.mesh.primitive_cube_add(size=0.16, location=(0.0, -0.15, 1.30))
    capelet = bpy.context.active_object
    capelet.name = "Girl_Combat_Capelet"
    capelet.scale = (1.4, 0.1, 2.2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bc.assign_material(capelet, mat_cape)
    bc.assign_weighted_bones(capelet, {"spine_04": 0.4, "spine_03": 0.4, "spine_02": 0.2})
    created_pieces.append(capelet)
    
    # 5. HIGH-CALF GREAVES & COMBAT BOOTS
    for side, sign in [("L", 1), ("R", -1)]:
        # Pointed Knee Guard
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.065, radius2=0.015, depth=0.06, location=(sign * 0.12, 0.08, 0.50), rotation=(1.5708, 0.0, 0.0))
        knee_guard = bpy.context.active_object
        knee_guard.name = f"Girl_KneeGuard_{side}"
        bc.assign_material(knee_guard, mat_titanium)
        bc.assign_rigid_weight(knee_guard, f"calf_{side.lower()}")
        created_pieces.append(knee_guard)
        
        # Sleek High Greave on Shin
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.076, depth=0.34, location=(sign * 0.12, 0.015, 0.32))
        greave = bpy.context.active_object
        greave.name = f"Girl_Greave_{side}"
        greave.scale = (0.9, 0.9, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(greave, mat_titanium)
        bc.assign_rigid_weight(greave, f"calf_{side.lower()}")
        created_pieces.append(greave)
        
        # Reinforced Combat Boot
        bpy.ops.mesh.primitive_cube_add(size=0.09, location=(sign * 0.14, -0.03, 0.04))
        boot = bpy.context.active_object
        boot.name = f"Girl_Boot_{side}"
        boot.scale = (0.85, 1.8, 0.45)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bc.assign_material(boot, mat_titanium)
        bc.assign_rigid_weight(boot, f"foot_{side.lower()}")
        created_pieces.append(boot)
        
    # Join armor pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in created_pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = created_pieces[0]
    bpy.ops.object.join()
    
    armor_mesh = created_pieces[0]
    armor_mesh.name = "Girl_Armor_Mesh"
    armor_mesh.parent = arm
    mod = armor_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    
    bc.export_fbx(out_fbx)
    return {
        "character": "GirlWarrior",
        "output_fbx": out_fbx,
        "base_mesh": base_mesh.name,
        "armor_mesh": armor_mesh.name,
        "polys": len(armor_mesh.data.polygons) + len(base_mesh.data.polygons)
    }

if __name__ == "__main__":
    res = build_girl_warrior()
    print("Result:", res)
