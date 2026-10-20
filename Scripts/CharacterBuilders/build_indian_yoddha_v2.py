"""
build_indian_yoddha_v2.py - Generates authentic, high-detail Indian Yoddha (Kshatriya Warrior).
Uses sculpted Indian anatomy (Lord_Shiva_Statue.fbx) + authentic historical Kshatriya gear:
- Sculpted Indian head, hair top-knot (Jata/Juda), athletic torso, arms, and jewelry.
- Royal martial Pagri (turban) with jeweled golden Sarpech and red Tilak.
- Char-Aina mirror chestplate with embossed golden Surya (sunburst) emblem.
- Pleated silk Dhoti (Kachha warrior drape) with Kamarbandh and hanging Patka sash.
- Traditional curved-toe Mojari warrior shoes.
- Authentic convex Dhal shield on back with 4 golden bosses.
- Skinned to UE5 SK_CombatMannequin (160 bones).
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
    
    # 2. Import Manny base
    manny_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
    bpy.ops.import_scene.fbx(filepath=manny_fbx)
    if dummy.name in bpy.data.objects:
        bpy.data.objects.remove(dummy, do_unlink=True)
        
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    manny_mesh = [o for o in bpy.data.objects if o.type == 'MESH' and "LOD0" in o.name][0]
    
    # Remove extra LODs
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o != manny_mesh and "LOD" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)
            
    # 3. Import Shiva Sculpted Assets
    dummy2 = bpy.data.objects.new("Dummy2", None)
    bpy.context.scene.collection.objects.link(dummy2)
    bpy.context.view_layer.objects.active = dummy2
    
    shiva_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Shiva_Statue_Project\Lord_Shiva_Statue.fbx"
    bpy.ops.import_scene.fbx(filepath=shiva_fbx)
    bpy.data.objects.remove(dummy2, do_unlink=True)
    
    # Apply initial FBX transforms on Shiva objects
    shiva_names = ["Shiva_Head", "Shiva_Hair", "Shiva_Torso", "Shiva_Arms", "Shiva_Jewelry_Ornaments"]
    shiva_objs = []
    for s_name in shiva_names:
        o = bpy.data.objects.get(s_name)
        if o:
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            shiva_objs.append(o)
            
    # Delete unused Shiva parts (rock base, seated crossed legs, etc.)
    for o in list(bpy.data.objects):
        if o.name.startswith("Shiva_") and o not in shiva_objs:
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Materials
    def make_mat(name, color, metallic=0.0, roughness=0.5):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        b = mat.node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = color
        b.inputs["Metallic"].default_value = metallic
        b.inputs["Roughness"].default_value = roughness
        return mat
        
    mat_skin = make_mat("M_Yoddha_Skin", (0.74, 0.52, 0.38, 1.0), metallic=0.0, roughness=0.52)
    mat_hair = make_mat("M_Yoddha_Hair", (0.05, 0.03, 0.02, 1.0), metallic=0.0, roughness=0.8)
    mat_gold = make_mat("M_Yoddha_Gold", (0.96, 0.76, 0.22, 1.0), metallic=0.95, roughness=0.22)
    mat_steel = make_mat("M_Yoddha_Steel", (0.65, 0.67, 0.70, 1.0), metallic=0.92, roughness=0.28)
    mat_saffron = make_mat("M_Yoddha_Saffron", (0.96, 0.42, 0.06, 1.0), metallic=0.02, roughness=0.75)
    mat_maroon = make_mat("M_Yoddha_Maroon", (0.48, 0.05, 0.08, 1.0), metallic=0.02, roughness=0.80)
    mat_gem = make_mat("M_Yoddha_Ruby", (0.85, 0.02, 0.08, 1.0), metallic=0.2, roughness=0.1)
    
    # 4. Transform sculpted Shiva parts to fit Manny rig (scale 0.50, aligned with Manny bones)
    # Head and Hair: original center (0.0, -0.079, 3.47) -> target Manny head (0.0, -0.02, 1.63)
    head = bpy.data.objects.get("Shiva_Head")
    hair = bpy.data.objects.get("Shiva_Hair")
    if head:
        head.data.materials.clear()
        head.data.materials.append(mat_skin)
        for v in head.data.vertices:
            v.co.x *= 0.50
            v.co.y = ((v.co.y - (-0.079)) * 0.50) - 0.02
            v.co.z = ((v.co.z - 3.47) * 0.50) + 1.63
        head.data.update()
        
    if hair:
        hair.data.materials.clear()
        hair.data.materials.append(mat_hair)
        for v in hair.data.vertices:
            v.co.x *= 0.50
            v.co.y = ((v.co.y - (-0.079)) * 0.50) - 0.02
            v.co.z = ((v.co.z - 3.47) * 0.50) + 1.63
        hair.data.update()
        
    # Torso: original center (0.0, 0.0, 2.40) -> target Manny chest (0.0, -0.03, 1.25)
    torso = bpy.data.objects.get("Shiva_Torso")
    if torso:
        torso.data.materials.clear()
        torso.data.materials.append(mat_skin)
        for v in torso.data.vertices:
            v.co.x *= 0.51
            v.co.y = (v.co.y * 0.50) - 0.03
            v.co.z = ((v.co.z - 2.40) * 0.50) + 1.25
        torso.data.update()
        
    # Arms: original center (0.0, 0.0, 2.70) -> target Manny arms
    arms = bpy.data.objects.get("Shiva_Arms")
    if arms:
        arms.data.materials.clear()
        arms.data.materials.append(mat_skin)
        for v in arms.data.vertices:
            v.co.x *= 0.51
            v.co.y = (v.co.y * 0.50) - 0.04
            v.co.z = ((v.co.z - 2.70) * 0.50) + 1.28
        arms.data.update()
        
    # Jewelry:
    jewel = bpy.data.objects.get("Shiva_Jewelry_Ornaments")
    if jewel:
        jewel.data.materials.clear()
        jewel.data.materials.append(mat_gold)
        for v in jewel.data.vertices:
            v.co.x *= 0.51
            v.co.y = (v.co.y * 0.50) - 0.04
            v.co.z = ((v.co.z - 2.70) * 0.50) + 1.28
        jewel.data.update()

    custom_pieces = []
    
    # 5. AUTHENTIC KSHATRIYA GEAR MODELING
    
    # --- A. Martial Pagri (Turban) with Gold Sarpech & Tilak ---
    # Turban folds wrapping the brow and base of top-knot
    for i in range(4):
        z_offset = 1.68 + (i * 0.032)
        rad = 0.155 + (i * 0.008)
        bpy.ops.mesh.primitive_torus_add(major_radius=rad, minor_radius=0.026, location=(0.0, -0.015, z_offset))
        fold = bpy.context.active_object
        fold.name = f"Yoddha_Pagri_Fold_{i}"
        fold.scale = (1.02, 1.14, 0.75)
        fold.rotation_euler = (0.04 * (i - 1.5), 0.03 * (i - 1.5), 0.0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        fold.data.materials.append(mat_saffron if i % 2 == 0 else mat_maroon)
        custom_pieces.append(fold)
        
    # Sarpech: Golden royal brooch mounted dead-center on turban brow
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.032, depth=0.012, location=(0.0, -0.165, 1.74), rotation=(math.radians(90), 0, 0))
    sarpech_base = bpy.context.active_object
    sarpech_base.name = "Yoddha_Sarpech_Base"
    sarpech_base.data.materials.append(mat_gold)
    custom_pieces.append(sarpech_base)
    
    # Ruby inside Sarpech
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.018, depth=0.016, location=(0.0, -0.172, 1.74), rotation=(math.radians(90), 0, 0))
    sarpech_ruby = bpy.context.active_object
    sarpech_ruby.name = "Yoddha_Sarpech_Ruby"
    sarpech_ruby.data.materials.append(mat_gem)
    custom_pieces.append(sarpech_ruby)
    
    # Feather Plume / Kalgi extending upward from Sarpech
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.025, radius2=0.005, depth=0.14, location=(0.0, -0.165, 1.83), rotation=(math.radians(-10), 0, 0))
    sarpech_feather = bpy.context.active_object
    sarpech_feather.name = "Yoddha_Sarpech_Feather"
    sarpech_feather.scale = (0.35, 1.0, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    sarpech_feather.data.materials.append(mat_saffron)
    custom_pieces.append(sarpech_feather)
    
    # Red Sandalwood Tilak on Forehead
    bpy.ops.mesh.primitive_cube_add(size=0.04, location=(0.0, -0.155, 1.67))
    tilak = bpy.context.active_object
    tilak.name = "Yoddha_Tilak"
    tilak.scale = (0.25, 0.15, 1.2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    tilak.data.materials.append(mat_gem)
    custom_pieces.append(tilak)
    
    # --- B. Char-Aina (Surya Kavacha) Chestplate ---
    # Front polished plate over chest
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.22, depth=0.34, location=(0.0, -0.02, 1.25))
    kavacha = bpy.context.active_object
    kavacha.name = "Yoddha_CharAina_Plates"
    kavacha.scale = (1.08, 0.85, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    kavacha.data.materials.append(mat_steel)
    custom_pieces.append(kavacha)
    
    # Golden Surya (Solar Sunburst Disc) on chest center
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.075, depth=0.015, location=(0.0, -0.195, 1.32), rotation=(math.radians(90), 0, 0))
    surya_disc = bpy.context.active_object
    surya_disc.name = "Yoddha_Surya_Disc"
    surya_disc.data.materials.append(mat_gold)
    custom_pieces.append(surya_disc)
    
    # 8 radiating sunbeams
    for beam_i in range(8):
        angle = beam_i * (math.pi / 4.0)
        bx = 0.09 * math.cos(angle)
        bz = 1.32 + (0.09 * math.sin(angle))
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.014, radius2=0.002, depth=0.05, location=(bx, -0.195, bz), rotation=(math.radians(90), 0, -angle + math.radians(90)))
        ray = bpy.context.active_object
        ray.name = f"Yoddha_Surya_Ray_{beam_i}"
        ray.data.materials.append(mat_gold)
        custom_pieces.append(ray)
        
    # Golden Char-Aina borders and straps
    bpy.ops.mesh.primitive_torus_add(major_radius=0.225, minor_radius=0.014, location=(0.0, -0.02, 1.40))
    rim_top = bpy.context.active_object
    rim_top.scale = (1.08, 0.85, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    rim_top.data.materials.append(mat_gold)
    custom_pieces.append(rim_top)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=0.215, minor_radius=0.014, location=(0.0, -0.02, 1.09))
    rim_bot = bpy.context.active_object
    rim_bot.scale = (1.08, 0.85, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    rim_bot.data.materials.append(mat_gold)
    custom_pieces.append(rim_bot)
    
    # --- C. Pleated Dhoti (Warrior Kachha Style) & Kamarbandh Sash ---
    # Kamarbandh: heavy royal gold belt at waist
    bpy.ops.mesh.primitive_torus_add(major_radius=0.20, minor_radius=0.022, location=(0.0, -0.01, 0.98))
    belt = bpy.context.active_object
    belt.name = "Yoddha_Kamarbandh_Belt"
    belt.scale = (1.06, 0.88, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    belt.data.materials.append(mat_gold)
    custom_pieces.append(belt)
    
    # Hanging central Patka sash down the front
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0.0, -0.165, 0.65))
    patka = bpy.context.active_object
    patka.name = "Yoddha_Patka_Sash"
    patka.scale = (1.1, 0.12, 3.2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    patka.data.materials.append(mat_maroon)
    custom_pieces.append(patka)
    
    # Golden border at the bottom of the Patka
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0.0, -0.168, 0.50))
    patka_hem = bpy.context.active_object
    patka_hem.name = "Yoddha_Patka_GoldHem"
    patka_hem.scale = (1.12, 0.14, 0.4)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    patka_hem.data.materials.append(mat_gold)
    custom_pieces.append(patka_hem)
    
    # Pleated Dhoti warrior wrap around each leg (Kachha combat drape)
    for leg_side, leg_x in [("L", 0.14), ("R", -0.14)]:
        # Upper thigh wrap
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.135, depth=0.48, location=(leg_x, -0.01, 0.74))
        thigh_wrap = bpy.context.active_object
        thigh_wrap.name = f"Yoddha_Dhoti_{leg_side}"
        thigh_wrap.scale = (0.95, 1.05, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        thigh_wrap.data.materials.append(mat_saffron)
        custom_pieces.append(thigh_wrap)
        
        # Calf wrap
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.095, depth=0.44, location=(leg_x, -0.01, 0.32))
        calf_wrap = bpy.context.active_object
        calf_wrap.name = f"Yoddha_CalfWrap_{leg_side}"
        calf_wrap.scale = (0.95, 1.05, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        calf_wrap.data.materials.append(mat_maroon)
        custom_pieces.append(calf_wrap)
        
        # Golden Mojari warrior shoes
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(leg_x, -0.06, 0.06))
        shoe = bpy.context.active_object
        shoe.name = f"Yoddha_Mojari_{leg_side}"
        shoe.scale = (0.95, 2.2, 0.65)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        shoe.data.materials.append(mat_gold)
        custom_pieces.append(shoe)
        
        # Upward curved toe tip of Mojari
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.035, radius2=0.005, depth=0.07, location=(leg_x, -0.18, 0.08), rotation=(math.radians(65), 0, 0))
        toe_curl = bpy.context.active_object
        toe_curl.name = f"Yoddha_MojariToe_{leg_side}"
        toe_curl.data.materials.append(mat_gold)
        custom_pieces.append(toe_curl)

    # --- D. Traditional Indian Dhal Shield on Back ---
    # Convex circular steel shield slung across upper back
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.28, location=(0.0, 0.20, 1.28))
    dhal = bpy.context.active_object
    dhal.name = "Yoddha_Dhal_Shield"
    dhal.scale = (1.0, 0.22, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    dhal.data.materials.append(mat_steel)
    custom_pieces.append(dhal)
    
    # 4 Golden Bosses (rivets arranged in square)
    for bx, bz in [(-0.10, 1.38), (0.10, 1.38), (-0.10, 1.18), (0.10, 1.18)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.024, location=(bx, 0.24, bz))
        boss = bpy.context.active_object
        boss.name = "Yoddha_Dhal_Boss"
        boss.data.materials.append(mat_gold)
        custom_pieces.append(boss)
        
    # Center golden crescent/starburst on shield
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.045, depth=0.015, location=(0.0, 0.25, 1.28), rotation=(math.radians(90), 0, 0))
    dhal_center = bpy.context.active_object
    dhal_center.name = "Yoddha_Dhal_Center"
    dhal_center.data.materials.append(mat_gold)
    custom_pieces.append(dhal_center)
    
    # 6. JOIN ALL YODDHA CHARACTER PARTS INTO A SINGLE MASTER CHARACTER MESH
    all_yoddha_parts = shiva_objs + custom_pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_yoddha_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = all_yoddha_parts[0]
    bpy.ops.object.join()
    
    yoddha_mesh = bpy.context.active_object
    yoddha_mesh.name = "Yoddha_Character_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # 7. SKINNING & RIGGING TO UE5 SKELETON
    # Parent to arm with identity parent inverse
    yoddha_mesh.parent = arm
    yoddha_mesh.matrix_parent_inverse = arm.matrix_world.inverted()
    
    # Transfer all 110 vertex groups from Manny LOD0
    dt = yoddha_mesh.modifiers.new("DataTransfer", 'DATA_TRANSFER')
    dt.object = manny_mesh
    dt.use_vert_data = True
    dt.data_types_verts = {'VGROUP_WEIGHTS'}
    dt.vert_mapping = 'POLYINTERP_NEAREST'
    bpy.context.view_layer.objects.active = yoddha_mesh
    bpy.ops.object.datalayout_transfer(modifier="DataTransfer")
    bpy.ops.object.modifier_apply(modifier="DataTransfer")
    
    # Armature modifier
    arm_mod = yoddha_mesh.modifiers.new("Armature", 'ARMATURE')
    arm_mod.object = arm
    
    # Remove the robot mannequin body so only the Yoddha is in the character!
    bpy.data.objects.remove(manny_mesh, do_unlink=True)
    
    # 8. RENDER FRONT PREVIEW
    cam_data = bpy.data.cameras.new("RenderCam")
    cam = bpy.data.objects.new("RenderCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cam.location = (0.0, -3.1, 0.98)
    cam.rotation_euler = (math.radians(88.0), 0.0, 0.0)
    
    # Studio lighting
    sun_data = bpy.data.lights.new("SunKey", 'SUN')
    sun_data.energy = 4.0
    sun = bpy.data.objects.new("SunKey", sun_data)
    sun.location = (2.0, -3.0, 3.5)
    sun.rotation_euler = (math.radians(50.0), math.radians(20.0), math.radians(-30.0))
    bpy.context.scene.collection.objects.link(sun)
    
    fill_data = bpy.data.lights.new("Fill", 'POINT')
    fill_data.energy = 300.0
    fill = bpy.data.objects.new("Fill", fill_data)
    fill.location = (-1.8, -2.5, 1.2)
    bpy.context.scene.collection.objects.link(fill)
    
    preview_img = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\preview_indianyoddha.png"
    bpy.context.scene.render.resolution_x = 720
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.filepath = preview_img
    bpy.ops.render.render(write_still=True)
    
    # 9. EXPORT FBX
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_IndianYoddha.fbx"
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
        "total_vertices": len(yoddha_mesh.data.vertices),
        "vertex_groups": len(yoddha_mesh.vertex_groups)
    }

if __name__ == "__main__":
    res = build()
    print("Result:", res)
