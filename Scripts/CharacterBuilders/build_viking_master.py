"""
build_viking_master.py - Generates an authentic, highly detailed Viking Warrior.
Combines AAA rugged warrior body/head/fur with authentic Gjermundbu spectacle helmet,
massive braided Norse beard with silver rings, cross-gartered boots, and slung Norse round shield.
"""

import sys
import os
import math
import bpy
from mathutils import Vector, Euler, Matrix

def build():
    # 1. Reset scene cleanly
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
        
    dummy = bpy.data.objects.new("Dummy", None)
    bpy.context.scene.collection.objects.link(dummy)
    bpy.context.view_layer.objects.active = dummy
    
    # 2. Import Manny base (for skeleton and weight transfer)
    manny_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
    bpy.ops.import_scene.fbx(filepath=manny_fbx)
    if dummy.name in bpy.data.objects:
        bpy.data.objects.remove(dummy, do_unlink=True)
        
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    manny_mesh = [o for o in bpy.data.objects if o.type == 'MESH' and "LOD0" in o.name][0]
    
    # Remove extra Manny LODs
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o != manny_mesh and "CombatMannequin" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)
            
    # 3. Import Greystone Tough (rugged warrior body, head, arms, legs)
    dummy2 = bpy.data.objects.new("Dummy2", None)
    bpy.context.scene.collection.objects.link(dummy2)
    bpy.context.view_layer.objects.active = dummy2
    
    tough_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Greystone_Tough.fbx"
    bpy.ops.import_scene.fbx(filepath=tough_fbx)
    bpy.data.objects.remove(dummy2, do_unlink=True)
    
    # Keep only Greystone_Tough_LOD0 and delete other LODs / armatures
    tough_mesh = bpy.data.objects.get("Greystone_Tough_LOD0")
    for o in list(bpy.data.objects):
        if o.name.startswith("Greystone_Tough_LOD") and o != tough_mesh:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'ARMATURE' and o != arm:
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Separate Tough by material to isolate components
    bpy.context.view_layer.objects.active = tough_mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='MATERIAL')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Identify Tough parts
    tough_parts = []
    for o in bpy.data.objects:
        if o.type == 'MESH' and o != manny_mesh:
            mat_name = o.data.materials[0].name if o.data.materials else ""
            if "Sword" in mat_name:
                # Remove default sword mesh
                bpy.data.objects.remove(o, do_unlink=True)
            else:
                tough_parts.append(o)
                
    # 4. Import Greystone standard (for heavy fur pelt mantle)
    dummy3 = bpy.data.objects.new("Dummy3", None)
    bpy.context.scene.collection.objects.link(dummy3)
    bpy.context.view_layer.objects.active = dummy3
    
    grey_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Greystone.fbx"
    bpy.ops.import_scene.fbx(filepath=grey_fbx)
    bpy.data.objects.remove(dummy3, do_unlink=True)
    
    grey_mesh = bpy.data.objects.get("Greystone_LOD0")
    for o in list(bpy.data.objects):
        if o.name.startswith("Greystone_LOD") and o != grey_mesh:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'ARMATURE' and o != arm:
            bpy.data.objects.remove(o, do_unlink=True)
            
    bpy.context.view_layer.objects.active = grey_mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='MATERIAL')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    fur_parts = []
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o != manny_mesh and o not in tough_parts:
            mat_name = o.data.materials[0].name if o.data.materials else ""
            if "Fur" in mat_name:
                fur_parts.append(o)
            else:
                bpy.data.objects.remove(o, do_unlink=True)
                
    # 5. CREATE AUTHENTIC VIKING PBR MATERIALS
    def make_pbr(name, color, metallic=0.0, roughness=0.5):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        b = mat.node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = color
        b.inputs["Metallic"].default_value = metallic
        b.inputs["Roughness"].default_value = roughness
        return mat
        
    mat_iron = make_pbr("M_Viking_Iron", (0.50, 0.52, 0.55, 1.0), metallic=0.88, roughness=0.30)
    mat_silver = make_pbr("M_Viking_Silver", (0.88, 0.89, 0.92, 1.0), metallic=0.95, roughness=0.18)
    mat_leather = make_pbr("M_Viking_Leather", (0.28, 0.16, 0.09, 1.0), metallic=0.04, roughness=0.68)
    mat_fur = make_pbr("M_Viking_WolfFur", (0.45, 0.42, 0.38, 1.0), metallic=0.0, roughness=0.92)
    mat_beard = make_pbr("M_Viking_Beard", (0.35, 0.18, 0.08, 1.0), metallic=0.0, roughness=0.80)
    mat_shield_wood = make_pbr("M_Viking_WoodPlanks", (0.42, 0.26, 0.14, 1.0), metallic=0.0, roughness=0.70)
    mat_shield_red = make_pbr("M_Viking_ShieldRed", (0.65, 0.09, 0.09, 1.0), metallic=0.05, roughness=0.55)
    mat_skin = make_pbr("M_Viking_Skin", (0.82, 0.64, 0.52, 1.0), metallic=0.0, roughness=0.50)
    
    # Assign custom materials to tough body parts
    active_tough = []
    for tp in tough_parts:
        mname = tp.data.materials[0].name if tp.data.materials else ""
        tp.data.materials.clear()
        if "Hair" in mname:
            # Hide top hair that would clip through helmet
            bpy.data.objects.remove(tp, do_unlink=True)
        else:
            if "Torso" in mname:
                tp.data.materials.append(mat_leather)
            elif "Arms" in mname:
                tp.data.materials.append(mat_iron)
            elif "Legs" in mname:
                tp.data.materials.append(mat_leather)
            elif "head" in mname or "skin" in mname:
                tp.data.materials.append(mat_skin)
            else:
                tp.data.materials.append(mat_leather)
            active_tough.append(tp)
            
    # Assign fur material to fur parts
    for fp in fur_parts:
        fp.data.materials.clear()
        fp.data.materials.append(mat_fur)
        
    custom_pieces = []
    
    # 6. MODEL AUTHENTIC VIKING ELEMENTS (True centimeter scale: head at Z=176, front is -Y)
    
    # --- A. Gjermundbu Spectacle Helmet ---
    # Iron Spangenhelm Dome fitted snugly over head (Z=175 to 204 cm)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=18, radius=18.5, location=(0.0, -3.5, 184.0))
    helm_dome = bpy.context.active_object
    helm_dome.name = "Viking_Helm_Dome"
    helm_dome.scale = (1.02, 1.15, 1.05)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    helm_dome.data.materials.append(mat_iron)
    custom_pieces.append(helm_dome)
    
    # Helmet Brow Band
    bpy.ops.mesh.primitive_torus_add(major_radius=18.8, minor_radius=1.6, location=(0.0, -3.5, 175.0))
    helm_rim = bpy.context.active_object
    helm_rim.name = "Viking_Helm_Rim"
    helm_rim.scale = (1.02, 1.15, 0.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    helm_rim.data.materials.append(mat_silver)
    custom_pieces.append(helm_rim)
    
    # Cross Ribs (Spangenhelm construction)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.6, depth=38.0, location=(0.0, -3.5, 187.0), rotation=(math.radians(90), 0, 0))
    rib_fb = bpy.context.active_object
    rib_fb.name = "Viking_Rib_FB"
    rib_fb.data.materials.append(mat_silver)
    custom_pieces.append(rib_fb)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.6, depth=38.0, location=(0.0, -3.5, 187.0), rotation=(0, math.radians(90), 0))
    rib_lr = bpy.context.active_object
    rib_lr.name = "Viking_Rib_LR"
    rib_lr.data.materials.append(mat_silver)
    custom_pieces.append(rib_lr)
    
    # Apex Spike
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=2.8, radius2=0.5, depth=7.5, location=(0.0, -3.5, 204.0))
    apex_spike = bpy.context.active_object
    apex_spike.name = "Viking_Apex_Spike"
    apex_spike.data.materials.append(mat_silver)
    custom_pieces.append(apex_spike)
    
    # Spectacle Ocular Eye Guards (Iconic Viking Mask over eyes and nose bridge - Front is -Y!)
    for eye_side, eye_x in [("L", 5.2), ("R", -5.2)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=4.5, minor_radius=1.2, location=(eye_x, -16.2, 173.0), rotation=(math.radians(90), 0, 0))
        ocular = bpy.context.active_object
        ocular.name = f"Viking_Ocular_{eye_side}"
        ocular.data.materials.append(mat_iron)
        custom_pieces.append(ocular)
        
    # Nasal Guard Bar
    bpy.ops.mesh.primitive_cube_add(size=6.0, location=(0.0, -17.5, 166.0))
    nasal = bpy.context.active_object
    nasal.name = "Viking_Nasal_Bar"
    nasal.scale = (0.32, 0.25, 2.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    nasal.data.materials.append(mat_iron)
    custom_pieces.append(nasal)
    
    # Chainmail Aventail (Neck drape behind helmet)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=19.5, depth=20.0, location=(0.0, -1.0, 160.0))
    aventail = bpy.context.active_object
    aventail.name = "Viking_Mail_Aventail"
    aventail.scale = (1.02, 1.12, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    aventail.data.materials.append(mat_iron)
    custom_pieces.append(aventail)
    
    # --- B. Massive Braided Norse Warrior Beard ---
    # Central beard volume cascading down chest from chin (Z=162 down to Z=130)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=12.0, radius2=4.0, depth=34.0, location=(0.0, -15.5, 146.0), rotation=(math.radians(18), 0, 0))
    beard_main = bpy.context.active_object
    beard_main.name = "Viking_Beard_Main"
    beard_main.scale = (1.1, 0.70, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    beard_main.data.materials.append(mat_beard)
    custom_pieces.append(beard_main)
    
    # Moustache
    for m_side, mx, rotz in [("L", 4.5, math.radians(20)), ("R", -4.5, math.radians(-20))]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=2.2, depth=12.0, location=(mx, -17.0, 163.0), rotation=(math.radians(30), math.radians(35) if m_side == "L" else math.radians(-35), rotz))
        stache = bpy.context.active_object
        stache.name = f"Viking_Moustache_{m_side}"
        stache.data.materials.append(mat_beard)
        custom_pieces.append(stache)
    
    # Braided Beard Strands with Silver Beard-Rings
    for b_side, bx in [("L", 4.2), ("R", -4.2)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=2.4, depth=30.0, location=(bx, -14.5, 138.0), rotation=(math.radians(14), 0, 0))
        braid = bpy.context.active_object
        braid.name = f"Viking_Braid_{b_side}"
        braid.data.materials.append(mat_beard)
        custom_pieces.append(braid)
        
        # Silver Beard Ring clasps
        for r_z in [142.0, 128.0]:
            bpy.ops.mesh.primitive_torus_add(major_radius=2.8, minor_radius=0.8, location=(bx, -14.0, r_z))
            ring = bpy.context.active_object
            ring.name = f"Viking_BeardRing_{b_side}_{r_z}"
            ring.data.materials.append(mat_silver)
            custom_pieces.append(ring)
            
    # Twin Silver Raven Brooches on Fur Mantle
    for br_side, br_x in [("L", 16.0), ("R", -16.0)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=3.8, depth=1.5, location=(br_x, -14.0, 154.0), rotation=(math.radians(80), 0, 0))
        brooch = bpy.context.active_object
        brooch.name = f"Viking_RavenBrooch_{br_side}"
        brooch.data.materials.append(mat_silver)
        custom_pieces.append(brooch)

    # --- C. Iconic Norse Round Shield Slung on Back ---
    # Large 32-inch circular wooden shield (Z=128, Y=+24 behind shoulders)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=38.0, depth=3.2, location=(0.0, 24.0, 128.0), rotation=(math.radians(90), 0, 0))
    shield_wood = bpy.context.active_object
    shield_wood.name = "Viking_RoundShield_Wood"
    shield_wood.data.materials.append(mat_shield_wood)
    custom_pieces.append(shield_wood)
    
    # Red-painted quadrant planks
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=37.5, depth=3.4, location=(0.0, 24.2, 128.0), rotation=(math.radians(90), 0, 0))
    shield_paint = bpy.context.active_object
    shield_paint.name = "Viking_RoundShield_RedQuarters"
    shield_paint.scale = (0.70, 1.0, 0.70)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    shield_paint.data.materials.append(mat_shield_red)
    custom_pieces.append(shield_paint)
    
    # Heavy Forged Iron Outer Rim
    bpy.ops.mesh.primitive_torus_add(major_radius=38.0, minor_radius=1.8, location=(0.0, 24.0, 128.0), rotation=(math.radians(90), 0, 0))
    shield_rim = bpy.context.active_object
    shield_rim.name = "Viking_RoundShield_IronRim"
    shield_rim.data.materials.append(mat_iron)
    custom_pieces.append(shield_rim)
    
    # Central Domed Iron Boss
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=7.5, location=(0.0, 27.0, 128.0))
    shield_boss = bpy.context.active_object
    shield_boss.name = "Viking_RoundShield_Boss"
    shield_boss.scale = (1.0, 0.5, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    shield_boss.data.materials.append(mat_iron)
    custom_pieces.append(shield_boss)
    
    # --- D. Cross-gartered Boot Rawhide Straps ---
    for leg_side, leg_x in [("L", 14.0), ("R", -14.0)]:
        for strap_i in range(5):
            sz = 18.0 + (strap_i * 6.5)
            s_rot = math.radians(15 if strap_i % 2 == 0 else -15)
            bpy.ops.mesh.primitive_torus_add(major_radius=8.2, minor_radius=0.5, location=(leg_x, -1.0, sz), rotation=(s_rot, 0, 0))
            strap = bpy.context.active_object
            strap.name = f"Viking_Garter_{leg_side}_{strap_i}"
            strap.scale = (0.95, 1.15, 1.0)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            strap.data.materials.append(mat_leather)
            custom_pieces.append(strap)

    # 7. JOIN ALL VIKING PARTS INTO MASTER MESH
    all_parts = active_tough + fur_parts + custom_pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = all_parts[0]
    bpy.ops.object.join()
    
    viking_mesh = bpy.context.active_object
    viking_mesh.name = "Viking_Character_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # 8. SKINNING & RIGGING TO UE5 SKELETON
    viking_mesh.parent = arm
    viking_mesh.matrix_parent_inverse = arm.matrix_world.inverted()
    
    # DataTransfer weights from Manny LOD0
    dt = viking_mesh.modifiers.new("DataTransfer", 'DATA_TRANSFER')
    dt.object = manny_mesh
    dt.use_vert_data = True
    dt.data_types_verts = {'VGROUP_WEIGHTS'}
    dt.vert_mapping = 'POLYINTERP_NEAREST'
    bpy.context.view_layer.objects.active = viking_mesh
    bpy.ops.object.datalayout_transfer(modifier="DataTransfer")
    bpy.ops.object.modifier_apply(modifier="DataTransfer")
    
    arm_mod = viking_mesh.modifiers.new("Armature", 'ARMATURE')
    arm_mod.object = arm
    
    # Remove mannequin body so only Viking is present
    bpy.data.objects.remove(manny_mesh, do_unlink=True)
    
    # 9. RENDER FRONT PREVIEW
    cam_data = bpy.data.cameras.new("RenderCam")
    cam = bpy.data.objects.new("RenderCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cam.location = (0.0, -320.0, 105.0)
    cam.rotation_euler = (math.radians(88.0), 0.0, 0.0)
    cam.data.clip_end = 2000.0
    
    sun_data = bpy.data.lights.new("SunKey", 'SUN')
    sun_data.energy = 4.0
    sun = bpy.data.objects.new("SunKey", sun_data)
    sun.location = (200.0, -300.0, 350.0)
    sun.rotation_euler = (math.radians(50.0), math.radians(20.0), math.radians(-30.0))
    bpy.context.scene.collection.objects.link(sun)
    
    fill_data = bpy.data.lights.new("Fill", 'POINT')
    fill_data.energy = 50000.0
    fill = bpy.data.objects.new("Fill", fill_data)
    fill.location = (-180.0, -250.0, 120.0)
    bpy.context.scene.collection.objects.link(fill)
    
    preview_img = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\preview_viking.png"
    bpy.context.scene.render.resolution_x = 720
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.filepath = preview_img
    bpy.ops.render.render(write_still=True)
    
    # 10. EXPORT FBX
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_Viking.fbx"
    os.makedirs(os.path.dirname(out_fbx), exist_ok=True)
    bpy.ops.export_scene.fbx(
        filepath=out_fbx,
        use_selection=False,
        object_types={'ARMATURE', 'MESH'},
        use_armature_deform_only=True,
        add_leaf_bones=False,
        mesh_smooth_type='FACE',
        bake_anim=False
    )
    
    return {
        "status": "success",
        "fbx_path": out_fbx,
        "fbx_size": os.path.getsize(out_fbx),
        "preview_path": preview_img,
        "total_vertices": len(viking_mesh.data.vertices),
        "vertex_groups": len(viking_mesh.vertex_groups)
    }

if __name__ == "__main__":
    res = build()
    print("Result:", res)
