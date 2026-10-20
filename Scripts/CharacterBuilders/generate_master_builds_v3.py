"""
generate_master_builds_v3.py - Generates 6 highly detailed, visually authentic character builds
rigged to the UE5 SK_CombatMannequin 160-bone skeleton.

Characters:
1. Viking (SKM_Viking) - Norse Jarl with Gjermundbu spectacle helmet, wolf fur mantle, braided beard, round shield
2. Medieval Warrior (SKM_MedievalWarrior) - High Gothic Knight Paladin with full plate, Armet bellows visor, heraldic plume, tabard
3. Samurai (SKM_Samurai) - Bushi Commander with Kabuto helmet, crescent Maedate, Menpo war mask, O-Sode pauldrons
4. Indian Yoddha (SKM_IndianYoddha) - Kshatriya Warrior with sculpted Indian anatomy, turban Sarpech, Surya armor, Dhoti, Dhal shield
5. Indian Goddess (SKM_IndianGoddess) - Durga/Devi Warrior with Kiritamukuta crown, Prabhavali halo, Swarna Kavacha, temple jewelry, warrior saree
6. Girl Warrior (SKM_GirlWarrior) - Valkyrie Champion with winged tiara, ponytail, sculpted cuirass, falcon pauldrons, pteruges skirt, capelet
"""

import sys
import os
import math
import bpy
import mathutils
from mathutils import Vector, Euler, Matrix

# =========================================================================
# HELPER FUNCTIONS
# =========================================================================
def reset_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    dummy = bpy.data.objects.new("Dummy", None)
    bpy.context.scene.collection.objects.link(dummy)
    bpy.context.view_layer.objects.active = dummy
    return dummy

def make_pbr_mat(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = color
        b.inputs["Metallic"].default_value = metallic
        b.inputs["Roughness"].default_value = roughness
    return mat

def normalize_object(obj):
    """Unparents obj and normalizes its transforms to world identity (centimeter space)."""
    obj.parent = None
    obj.matrix_world = Matrix.Identity(4)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

def setup_camera_and_render(output_img_path, target_z=115.0, cam_dist=290.0):
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.42, 0.42, 0.45, 1.0)
        bg.inputs["Strength"].default_value = 0.90

    cam = bpy.data.objects.get("RenderCam")
    if not cam:
        cam_data = bpy.data.cameras.new("RenderCam")
        cam = bpy.data.objects.new("RenderCam", cam_data)
        bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cam.location = (0.0, -cam_dist, target_z)
    cam.rotation_euler = (math.radians(88.0), 0.0, 0.0)
    cam.data.clip_end = 2500.0
    
    sun = bpy.data.objects.get("SunKey")
    if not sun:
        sun_data = bpy.data.lights.new("SunKey", 'SUN')
        sun = bpy.data.objects.new("SunKey", sun_data)
        bpy.context.scene.collection.objects.link(sun)
    sun.data.energy = 5.0
    sun.location = (150.0, -250.0, 320.0)
    sun.rotation_euler = (math.radians(45.0), math.radians(25.0), math.radians(-30.0))
    
    fill = bpy.data.objects.get("FillLight")
    if not fill:
        fill_data = bpy.data.lights.new("FillLight", 'POINT')
        fill = bpy.data.objects.new("FillLight", fill_data)
        bpy.context.scene.collection.objects.link(fill)
    fill.data.energy = 50000.0
    fill.location = (-150.0, -200.0, 130.0)
    
    rim = bpy.data.objects.get("RimLight")
    if not rim:
        rim_data = bpy.data.lights.new("RimLight", 'POINT')
        rim = bpy.data.objects.new("RimLight", rim_data)
        bpy.context.scene.collection.objects.link(rim)
    rim.data.energy = 35000.0
    rim.location = (0.0, 200.0, 180.0)
    
    bpy.context.scene.render.resolution_x = 720
    bpy.context.scene.render.resolution_y = 1080
    os.makedirs(os.path.dirname(output_img_path), exist_ok=True)
    bpy.context.scene.render.filepath = output_img_path
    bpy.ops.render.render(write_still=True)
    print(f"[RENDER] Saved preview to {output_img_path}")

def skin_and_export(mesh_obj, out_fbx_path):
    # Import reference CombatMannequin for rig and weights
    dummy_m = bpy.data.objects.new("DummyM", None)
    bpy.context.scene.collection.objects.link(dummy_m)
    bpy.context.view_layer.objects.active = dummy_m
    manny_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
    bpy.ops.import_scene.fbx(filepath=manny_fbx)
    bpy.data.objects.remove(dummy_m, do_unlink=True)
    
    manny_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    manny_mesh = [o for o in bpy.data.objects if o.type == 'MESH' and "LOD0" in o.name and "CombatMannequin" in o.name][0]
    
    # Normalize manny_arm so its world transform matches mesh_obj in centimeters
    manny_arm.parent = None
    manny_arm.matrix_world = Matrix.Identity(4)
    bpy.ops.object.select_all(action='DESELECT')
    manny_arm.select_set(True)
    bpy.context.view_layer.objects.active = manny_arm
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    manny_mesh.parent = None
    manny_mesh.matrix_world = Matrix.Identity(4)
    bpy.ops.object.select_all(action='DESELECT')
    manny_mesh.select_set(True)
    bpy.context.view_layer.objects.active = manny_mesh
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    mesh_obj.parent = manny_arm
    mesh_obj.matrix_parent_inverse = manny_arm.matrix_world.inverted()
    
    # Transfer vertex weights from manny
    dt = mesh_obj.modifiers.new("DataTransfer", 'DATA_TRANSFER')
    dt.object = manny_mesh
    dt.use_vert_data = True
    dt.data_types_verts = {'VGROUP_WEIGHTS'}
    dt.vert_mapping = 'POLYINTERP_NEAREST'
    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.datalayout_transfer(modifier="DataTransfer")
    bpy.ops.object.modifier_apply(modifier="DataTransfer")
    
    arm_mod = mesh_obj.modifiers.new("Armature", 'ARMATURE')
    arm_mod.object = manny_arm
    
    # Clean up manny mesh and helper empties
    bpy.data.objects.remove(manny_mesh, do_unlink=True)
    for o in list(bpy.data.objects):
        if o.type == 'EMPTY' or (o.type == 'MESH' and o != mesh_obj):
            bpy.data.objects.remove(o, do_unlink=True)
            
    os.makedirs(os.path.dirname(out_fbx_path), exist_ok=True)
    bpy.ops.export_scene.fbx(
        filepath=out_fbx_path,
        use_selection=False,
        object_types={'ARMATURE', 'MESH'},
        use_armature_deform_only=True,
        add_leaf_bones=False,
        mesh_smooth_type='FACE',
        bake_anim=False
    )
    print(f"[EXPORT] Successfully wrote {out_fbx_path} ({os.path.getsize(out_fbx_path)} bytes)")


# =========================================================================
# 1. VIKING WARRIOR (SKM_Viking)
# =========================================================================
def build_viking():
    print("\n" + "="*50)
    print("BUILDING 1/6: VIKING WARRIOR")
    print("="*50)
    dummy = reset_scene()
    
    tough_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Greystone_Tough.fbx"
    bpy.ops.import_scene.fbx(filepath=tough_fbx)
    bpy.data.objects.remove(dummy, do_unlink=True)
    
    tough_mesh = bpy.data.objects.get("Greystone_Tough_LOD0")
    for o in list(bpy.data.objects):
        if o.name.startswith("Greystone_Tough_LOD") and o != tough_mesh:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'EMPTY':
            bpy.data.objects.remove(o, do_unlink=True)
            
    normalize_object(tough_mesh)
    bpy.context.view_layer.objects.active = tough_mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='MATERIAL')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Import sculpted fur from Greystone
    dummy_f = bpy.data.objects.new("DummyF", None)
    bpy.context.scene.collection.objects.link(dummy_f)
    bpy.context.view_layer.objects.active = dummy_f
    grey_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Greystone.fbx"
    bpy.ops.import_scene.fbx(filepath=grey_fbx)
    bpy.data.objects.remove(dummy_f, do_unlink=True)
    
    grey_mesh = bpy.data.objects.get("Greystone_LOD0")
    for o in list(bpy.data.objects):
        if o.name.startswith("Greystone_LOD") and o != grey_mesh:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'EMPTY':
            bpy.data.objects.remove(o, do_unlink=True)
            
    normalize_object(grey_mesh)
    bpy.context.view_layer.objects.active = grey_mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='MATERIAL')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    mat_iron = make_pbr_mat("M_Viking_Iron", (0.48, 0.50, 0.53, 1.0), metallic=0.90, roughness=0.28)
    mat_silver = make_pbr_mat("M_Viking_Silver", (0.88, 0.89, 0.92, 1.0), metallic=0.95, roughness=0.18)
    mat_leather = make_pbr_mat("M_Viking_Leather", (0.24, 0.14, 0.08, 1.0), metallic=0.04, roughness=0.68)
    mat_fur = make_pbr_mat("M_Viking_WolfFur", (0.32, 0.28, 0.25, 1.0), metallic=0.0, roughness=0.95)
    mat_beard = make_pbr_mat("M_Viking_Beard", (0.35, 0.18, 0.07, 1.0), metallic=0.0, roughness=0.80)
    mat_wood = make_pbr_mat("M_Viking_WoodPlanks", (0.36, 0.22, 0.12, 1.0), metallic=0.0, roughness=0.72)
    mat_shield_red = make_pbr_mat("M_Viking_ShieldRed", (0.62, 0.06, 0.06, 1.0), metallic=0.05, roughness=0.55)
    mat_skin = make_pbr_mat("M_Viking_Skin", (0.82, 0.65, 0.53, 1.0), metallic=0.0, roughness=0.48)
    
    body_parts = []
    for o in list(bpy.data.objects):
        if o.type == 'MESH':
            mname = o.data.materials[0].name if o.data.materials else ""
            if "Sword" in mname or "shield" in mname:
                bpy.data.objects.remove(o, do_unlink=True)
            elif "Fur" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_fur)
                body_parts.append(o)
            elif "Torso" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_leather)
                body_parts.append(o)
            elif "Arms" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_iron)
                body_parts.append(o)
            elif "Legs" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_leather)
                body_parts.append(o)
            elif "head" in mname or "skin" in mname or "Flesh" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_skin)
                body_parts.append(o)
            elif "Hair" in mname and "Tough" in o.name:
                o.data.materials.clear()
                o.data.materials.append(mat_beard)
                body_parts.append(o)
            elif o.name.startswith("Greystone_LOD"):
                bpy.data.objects.remove(o, do_unlink=True)
            else:
                body_parts.append(o)
                
    custom_pieces = []
    
    # Spangenhelm Skull Cap Dome
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=14, radius=10.6, location=(0.0, -1.0, 197.5))
    dome = bpy.context.active_object
    dome.scale = (0.95, 1.08, 0.95)
    bpy.ops.object.transform_apply(scale=True)
    dome.data.materials.append(mat_iron)
    custom_pieces.append(dome)

    # Brow band rim around forehead
    bpy.ops.mesh.primitive_torus_add(major_radius=10.4, minor_radius=0.85, location=(0.0, -1.0, 193.5))
    rim = bpy.context.active_object
    rim.scale = (0.95, 1.08, 0.75)
    bpy.ops.object.transform_apply(scale=True)
    rim.data.materials.append(mat_silver)
    custom_pieces.append(rim)

    # Cross ribs
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.85, depth=21.0, location=(0.0, -1.0, 201.5), rotation=(math.radians(90), 0, 0))
    rib_fb = bpy.context.active_object
    rib_fb.data.materials.append(mat_silver)
    custom_pieces.append(rib_fb)

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.85, depth=20.0, location=(0.0, -1.0, 201.5), rotation=(0, math.radians(90), 0))
    rib_lr = bpy.context.active_object
    rib_lr.data.materials.append(mat_silver)
    custom_pieces.append(rib_lr)

    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.4, radius2=0.25, depth=5.5, location=(0.0, -1.0, 209.5))
    apex = bpy.context.active_object
    apex.data.materials.append(mat_silver)
    custom_pieces.append(apex)

    # Spectacle oculars framing eyes
    for ex in [-4.8, 4.8]:
        bpy.ops.mesh.primitive_torus_add(major_radius=3.1, minor_radius=0.50, location=(ex, -11.2, 191.0), rotation=(math.radians(85), 0, 0))
        oc = bpy.context.active_object
        oc.data.materials.append(mat_silver)
        custom_pieces.append(oc)

    # Nasal guard
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -13.0, 187.0))
    nasal = bpy.context.active_object
    nasal.scale = (0.35, 0.35, 3.2)
    bpy.ops.object.transform_apply(scale=True)
    nasal.data.materials.append(mat_silver)
    custom_pieces.append(nasal)

    # Braided Norse Beard
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=8.0, radius2=3.0, depth=14.0, location=(0.0, -10.5, 175.0), rotation=(math.radians(16), 0, 0))
    beard_top = bpy.context.active_object
    beard_top.scale = (1.05, 0.70, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    beard_top.data.materials.append(mat_beard)
    custom_pieces.append(beard_top)

    for bx in [-3.2, 3.2]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=1.6, depth=26.0, location=(bx, -11.5, 160.0), rotation=(math.radians(12), 0, 0))
        braid = bpy.context.active_object
        braid.data.materials.append(mat_beard)
        custom_pieces.append(braid)
        for rz in [165.0, 152.0]:
            bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.45, location=(bx, -11.0, rz))
            ring = bpy.context.active_object
            ring.data.materials.append(mat_silver)
            custom_pieces.append(ring)

    for mx, rotz in [(-3.0, math.radians(-22)), (3.0, math.radians(22))]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.1, depth=7.5, location=(mx, -12.5, 183.5), rotation=(math.radians(35), math.radians(-30 if mx < 0 else 30), rotz))
        stache = bpy.context.active_object
        stache.data.materials.append(mat_beard)
        custom_pieces.append(stache)

    # Shoulder Brooches
    for br_x in [-18.0, 18.0]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=2.8, depth=1.2, location=(br_x, -8.0, 169.0), rotation=(math.radians(75), 0, 0))
        brooch = bpy.context.active_object
        brooch.data.materials.append(mat_silver)
        custom_pieces.append(brooch)

    # Norse Round Shield on Back
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=35.0, depth=2.8, location=(0.0, 24.0, 135.0), rotation=(math.radians(90), 0, 0))
    s_wood = bpy.context.active_object
    s_wood.data.materials.append(mat_wood)
    custom_pieces.append(s_wood)

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=34.6, depth=3.0, location=(0.0, 24.1, 135.0), rotation=(math.radians(90), 0, 0))
    s_paint = bpy.context.active_object
    s_paint.scale = (0.75, 1.0, 0.75)
    bpy.ops.object.transform_apply(scale=True)
    s_paint.data.materials.append(mat_shield_red)
    custom_pieces.append(s_paint)

    bpy.ops.mesh.primitive_torus_add(major_radius=35.0, minor_radius=1.5, location=(0.0, 24.0, 135.0), rotation=(math.radians(90), 0, 0))
    s_rim = bpy.context.active_object
    s_rim.data.materials.append(mat_iron)
    custom_pieces.append(s_rim)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=18, ring_count=10, radius=6.5, location=(0.0, 26.5, 135.0))
    s_boss = bpy.context.active_object
    s_boss.scale = (1.0, 0.5, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    s_boss.data.materials.append(mat_iron)
    custom_pieces.append(s_boss)

    all_pieces = body_parts + custom_pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = all_pieces[0]
    bpy.ops.object.join()
    
    master_mesh = bpy.context.active_object
    master_mesh.name = "SKM_Viking_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    prev_path = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\preview_viking.png"
    setup_camera_and_render(prev_path)
    
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_Viking.fbx"
    skin_and_export(master_mesh, out_fbx)
    return {"status": "Viking Complete", "fbx": out_fbx, "preview": prev_path}


# =========================================================================
# 2. MEDIEVAL WARRIOR (HIGH GOTHIC KNIGHT PALADIN)
# =========================================================================
def build_medieval_warrior():
    print("\n" + "="*50)
    print("BUILDING 2/6: MEDIEVAL WARRIOR (KNIGHT PALADIN)")
    print("="*50)
    dummy = reset_scene()
    
    grey_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Greystone.fbx"
    bpy.ops.import_scene.fbx(filepath=grey_fbx)
    bpy.data.objects.remove(dummy, do_unlink=True)
    
    grey_mesh = bpy.data.objects.get("Greystone_LOD0")
    for o in list(bpy.data.objects):
        if o.name.startswith("Greystone_LOD") and o != grey_mesh:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'EMPTY':
            bpy.data.objects.remove(o, do_unlink=True)
            
    normalize_object(grey_mesh)
    bpy.context.view_layer.objects.active = grey_mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='MATERIAL')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    mat_plate = make_pbr_mat("M_Knight_SteelPlate", (0.75, 0.77, 0.80, 1.0), metallic=0.92, roughness=0.18)
    mat_gold_trim = make_pbr_mat("M_Knight_GoldTrim", (0.95, 0.78, 0.22, 1.0), metallic=0.95, roughness=0.22)
    mat_tabard = make_pbr_mat("M_Knight_TabardAzure", (0.06, 0.18, 0.45, 1.0), metallic=0.08, roughness=0.55)
    mat_leather = make_pbr_mat("M_Knight_Leather", (0.22, 0.14, 0.09, 1.0), metallic=0.04, roughness=0.68)
    mat_plume = make_pbr_mat("M_Knight_Plume", (0.12, 0.35, 0.85, 1.0), metallic=0.0, roughness=0.85)
    mat_skin = make_pbr_mat("M_Knight_Skin", (0.84, 0.68, 0.56, 1.0), metallic=0.0, roughness=0.48)
    mat_hair = make_pbr_mat("M_Knight_Hair", (0.45, 0.30, 0.18, 1.0), metallic=0.0, roughness=0.75)
    
    body_parts = []
    for o in list(bpy.data.objects):
        if o.type == 'MESH':
            mname = o.data.materials[0].name if o.data.materials else ""
            if "Fur" in mname or "shield" in mname or "RockHair" in mname:
                bpy.data.objects.remove(o, do_unlink=True)
            elif "Torso" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_tabard)
                body_parts.append(o)
            elif "arms" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_plate)
                body_parts.append(o)
            elif "legs" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_plate)
                body_parts.append(o)
            elif "head" in mname or "skin" in mname or "Flesh" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_skin)
                body_parts.append(o)
            elif "Hair" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_hair)
                body_parts.append(o)
            else:
                body_parts.append(o)
                
    custom_pieces = []
    
    # 1. High Gothic Armet Skull Dome (Z=198, radius 11.0)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=26, ring_count=16, radius=11.0, location=(0.0, -0.5, 198.0))
    dome = bpy.context.active_object
    dome.scale = (0.95, 1.10, 0.98)
    bpy.ops.object.transform_apply(scale=True)
    dome.data.materials.append(mat_plate)
    custom_pieces.append(dome)
    
    # Gold rim band around base of helmet dome
    bpy.ops.mesh.primitive_torus_add(major_radius=10.6, minor_radius=0.85, location=(0.0, -0.5, 193.0))
    rim = bpy.context.active_object
    rim.scale = (0.95, 1.10, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    rim.data.materials.append(mat_gold_trim)
    custom_pieces.append(rim)
    
    # Fluted Gothic Comb along crest
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -0.5, 207.5))
    comb = bpy.context.active_object
    comb.scale = (0.35, 9.5, 2.0)
    bpy.ops.object.transform_apply(scale=True)
    comb.data.materials.append(mat_gold_trim)
    custom_pieces.append(comb)
    
    # 2. Gothic Pointed Bellows Visor
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=9.8, radius2=2.0, depth=11.0, location=(0.0, -9.5, 187.0), rotation=(math.radians(82), 0, 0))
    visor = bpy.context.active_object
    visor.scale = (0.88, 0.85, 1.15)
    bpy.ops.object.transform_apply(scale=True)
    visor.data.materials.append(mat_plate)
    custom_pieces.append(visor)
    
    # Vision slit
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -13.5, 190.5))
    slit = bpy.context.active_object
    slit.scale = (10.0, 0.6, 0.50)
    bpy.ops.object.transform_apply(scale=True)
    slit.data.materials.append(mat_gold_trim)
    custom_pieces.append(slit)
    
    # 3. Flowing Azure & Gold Knight Plume
    for pi, (py, pz, ps) in enumerate([(1.0, 212.0, 1.0), (4.5, 210.0, 0.85), (8.0, 206.0, 0.70), (11.0, 200.0, 0.55)]):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=3.2 * ps, location=(0.0, py, pz))
        pl = bpy.context.active_object
        pl.scale = (0.50, 1.3, 0.9)
        bpy.ops.object.transform_apply(scale=True)
        pl.data.materials.append(mat_plume if pi % 2 == 0 else mat_gold_trim)
        custom_pieces.append(pl)
        
    # 4. Golden Cross on Tabard
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -12.5, 142.0))
    cross_v = bpy.context.active_object
    cross_v.scale = (2.2, 0.4, 16.0)
    bpy.ops.object.transform_apply(scale=True)
    cross_v.data.materials.append(mat_gold_trim)
    custom_pieces.append(cross_v)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -12.5, 145.0))
    cross_h = bpy.context.active_object
    cross_h.scale = (11.0, 0.4, 2.2)
    bpy.ops.object.transform_apply(scale=True)
    cross_h.data.materials.append(mat_gold_trim)
    custom_pieces.append(cross_h)

    all_pieces = body_parts + custom_pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = all_pieces[0]
    bpy.ops.object.join()
    
    master_mesh = bpy.context.active_object
    master_mesh.name = "SKM_MedievalWarrior_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    prev_path = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\preview_medievalwarrior.png"
    setup_camera_and_render(prev_path)
    
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_MedievalWarrior.fbx"
    skin_and_export(master_mesh, out_fbx)
    return {"status": "Medieval Warrior Complete", "fbx": out_fbx, "preview": prev_path}


# =========================================================================
# 3. SAMURAI (JAPANESE BUSHI COMMANDER)
# =========================================================================
def build_samurai():
    print("\n" + "="*50)
    print("BUILDING 3/6: SAMURAI COMMANDER")
    print("="*50)
    dummy = reset_scene()
    
    wt_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Greystone_WhiteTiger.fbx"
    bpy.ops.import_scene.fbx(filepath=wt_fbx)
    bpy.data.objects.remove(dummy, do_unlink=True)
    
    wt_mesh = bpy.data.objects.get("Greystone_WhiteTiger_LOD0")
    for o in list(bpy.data.objects):
        if o.name.startswith("Greystone_WhiteTiger_LOD") and o != wt_mesh:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'EMPTY':
            bpy.data.objects.remove(o, do_unlink=True)
            
    normalize_object(wt_mesh)
    bpy.context.view_layer.objects.active = wt_mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='MATERIAL')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    mat_urushi = make_pbr_mat("M_Samurai_BlackUrushi", (0.05, 0.05, 0.06, 1.0), metallic=0.75, roughness=0.22)
    mat_gold = make_pbr_mat("M_Samurai_ImperialGold", (0.95, 0.78, 0.18, 1.0), metallic=0.96, roughness=0.18)
    mat_crimson = make_pbr_mat("M_Samurai_CrimsonSilk", (0.68, 0.06, 0.06, 1.0), metallic=0.08, roughness=0.52)
    mat_iron = make_pbr_mat("M_Samurai_ForgedIron", (0.35, 0.36, 0.38, 1.0), metallic=0.88, roughness=0.32)
    mat_skin = make_pbr_mat("M_Samurai_Skin", (0.84, 0.67, 0.54, 1.0), metallic=0.0, roughness=0.48)
    mat_hair = make_pbr_mat("M_Samurai_Hair", (0.05, 0.04, 0.04, 1.0), metallic=0.0, roughness=0.85)
    
    body_parts = []
    for o in list(bpy.data.objects):
        if o.type == 'MESH':
            mname = o.data.materials[0].name if o.data.materials else ""
            if "shield" in mname or "Fur" in mname:
                bpy.data.objects.remove(o, do_unlink=True)
            elif "Torso" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_urushi)
                body_parts.append(o)
            elif "arms" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_urushi)
                body_parts.append(o)
            elif "legs" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_urushi)
                body_parts.append(o)
            elif "head" in mname or "skin" in mname or "Flesh" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_skin)
                body_parts.append(o)
            elif "Hair" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_hair)
                body_parts.append(o)
            else:
                body_parts.append(o)
                
    custom_pieces = []
    
    # 1. Hoshi-Kabuto Helmet Dome (Z=198, radius 10.8)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=26, ring_count=16, radius=10.8, location=(0.0, -0.8, 198.0))
    dome = bpy.context.active_object
    dome.scale = (0.96, 1.08, 0.95)
    bpy.ops.object.transform_apply(scale=True)
    dome.data.materials.append(mat_urushi)
    custom_pieces.append(dome)
    
    # Tehen Kanamono apex grommet
    bpy.ops.mesh.primitive_torus_add(major_radius=2.6, minor_radius=0.6, location=(0.0, -0.8, 208.5))
    tehen = bpy.context.active_object
    tehen.data.materials.append(mat_gold)
    custom_pieces.append(tehen)
    
    # 2. Golden Crescent Moon Maedate (Facing forward on front brow)
    bpy.ops.mesh.primitive_torus_add(major_radius=7.5, minor_radius=0.75, location=(0.0, -11.5, 200.0), rotation=(math.radians(90), 0, 0))
    crescent = bpy.context.active_object
    crescent.scale = (1.2, 0.30, 0.9)
    bpy.ops.object.transform_apply(scale=True)
    crescent.data.materials.append(mat_gold)
    custom_pieces.append(crescent)
    
    # Maedate Central Sun Disk
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=2.2, depth=0.6, location=(0.0, -11.8, 196.0), rotation=(math.radians(90), 0, 0))
    sun_disk = bpy.context.active_object
    sun_disk.data.materials.append(mat_crimson)
    custom_pieces.append(sun_disk)
    
    # Fukigaeshi winglets
    for fx, f_rot in [(-9.5, math.radians(-35)), (9.5, math.radians(35))]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, -8.0, 195.0), rotation=(math.radians(15), 0, f_rot))
        fk = bpy.context.active_object
        fk.scale = (3.2, 4.5, 0.8)
        bpy.ops.object.transform_apply(scale=True)
        fk.data.materials.append(mat_gold)
        custom_pieces.append(fk)
        
    # 3. Shikoro Neck Guard (Curving only along BACK and SIDES)
    for ti in range(3):
        tz = 188.0 - (ti * 4.0)
        ty = 4.0 + (ti * 1.5)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, ty, tz), rotation=(math.radians(-15), 0, 0))
        tier = bpy.context.active_object
        tier.scale = (22.0 + (ti * 3.0), 3.0, 3.2)
        bpy.ops.object.transform_apply(scale=True)
        tier.data.materials.append(mat_urushi if ti % 2 == 0 else mat_crimson)
        custom_pieces.append(tier)
        
    # 4. Menpo Demonic War Mask (covering jaw and mouth)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=7.5, radius2=3.5, depth=8.0, location=(0.0, -10.5, 178.0), rotation=(math.radians(75), 0, 0))
    menpo = bpy.context.active_object
    menpo.scale = (0.95, 0.65, 1.1)
    bpy.ops.object.transform_apply(scale=True)
    menpo.data.materials.append(mat_iron)
    custom_pieces.append(menpo)
    
    # Menpo Flared Mustache
    for mx, mz in [(-3.2, math.radians(-25)), (3.2, math.radians(25))]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.8, depth=6.0, location=(mx, -13.5, 180.0), rotation=(math.radians(25), 0, mz))
        sm = bpy.context.active_object
        sm.data.materials.append(mat_urushi)
        custom_pieces.append(sm)
        
    # 5. Ō-Sode Shoulder Guards
    for sx, sy in [(-25.0, math.radians(-12)), (25.0, math.radians(12))]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, -1.0, 158.0), rotation=(0, sy, 0))
        sode = bpy.context.active_object
        sode.scale = (2.2, 14.0, 20.0)
        bpy.ops.object.transform_apply(scale=True)
        sode.data.materials.append(mat_urushi)
        custom_pieces.append(sode)
        
        # Golden crest on O-Sode
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=3.2, depth=0.6, location=(sx * 1.05, -1.0, 160.0), rotation=(0, math.radians(90), 0))
        crest = bpy.context.active_object
        crest.data.materials.append(mat_gold)
        custom_pieces.append(crest)

    all_pieces = body_parts + custom_pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = all_pieces[0]
    bpy.ops.object.join()
    
    master_mesh = bpy.context.active_object
    master_mesh.name = "SKM_Samurai_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    prev_path = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\preview_samurai.png"
    setup_camera_and_render(prev_path)
    
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_Samurai.fbx"
    skin_and_export(master_mesh, out_fbx)
    return {"status": "Samurai Complete", "fbx": out_fbx, "preview": prev_path}


# =========================================================================
# 4. INDIAN YODDHA (ANCIENT KSHATRIYA WARRIOR)
# =========================================================================
def build_indian_yoddha():
    print("\n" + "="*50)
    print("BUILDING 4/6: INDIAN YODDHA (KSHATRIYA WARRIOR)")
    print("="*50)
    dummy = reset_scene()
    
    # Novaborn athletic muscular body
    nova_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Greystone_Novaborn.fbx"
    bpy.ops.import_scene.fbx(filepath=nova_fbx)
    bpy.data.objects.remove(dummy, do_unlink=True)
    
    nova_mesh = bpy.data.objects.get("Greystone_Novaborn_LOD0")
    for o in list(bpy.data.objects):
        if o.name.startswith("Greystone_Novaborn_LOD") and o != nova_mesh:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'EMPTY':
            bpy.data.objects.remove(o, do_unlink=True)
            
    normalize_object(nova_mesh)
    bpy.context.view_layer.objects.active = nova_mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='MATERIAL')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    body_parts = []
    for o in list(bpy.data.objects):
        if o.type == 'MESH':
            mname = o.data.materials[0].name if o.data.materials else ""
            if any(k in mname.lower() for k in ["weapon", "head", "hair", "eye", "mouth"]):
                bpy.data.objects.remove(o, do_unlink=True)
            else:
                body_parts.append(o)
                
    # Authentic Indian sculpted head from Shiva Statue
    dummy_s = bpy.data.objects.new("DummyS", None)
    bpy.context.scene.collection.objects.link(dummy_s)
    bpy.context.view_layer.objects.active = dummy_s
    shiva_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Shiva_Statue_Project\Lord_Shiva_Statue.fbx"
    bpy.ops.import_scene.fbx(filepath=shiva_fbx)
    bpy.data.objects.remove(dummy_s, do_unlink=True)
    
    shiva_head = bpy.data.objects.get("Shiva_Head")
    shiva_hair = bpy.data.objects.get("Shiva_Hair")
    
    for o in list(bpy.data.objects):
        if o.name.startswith("Shiva_") and o not in [shiva_head, shiva_hair]:
            bpy.data.objects.remove(o, do_unlink=True)
            
    scale_factor = 35.71
    for obj in [shiva_head, shiva_hair]:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(rotation=True)
        for v in obj.data.vertices:
            v.co.x = v.co.x * scale_factor * 1.05
            v.co.y = (v.co.y - (-0.08)) * scale_factor - 4.5
            v.co.z = (v.co.z - 3.47) * scale_factor * 0.90 + 185.0
            
    mat_gold = make_pbr_mat("M_Yoddha_VedicGold", (0.95, 0.78, 0.18, 1.0), metallic=0.96, roughness=0.18)
    mat_bronze = make_pbr_mat("M_Yoddha_CharAina", (0.80, 0.50, 0.22, 1.0), metallic=0.90, roughness=0.25)
    mat_saffron = make_pbr_mat("M_Yoddha_SaffronSilk", (0.92, 0.42, 0.08, 1.0), metallic=0.08, roughness=0.60)
    mat_crimson = make_pbr_mat("M_Yoddha_RoyalCrimson", (0.65, 0.08, 0.08, 1.0), metallic=0.08, roughness=0.55)
    mat_indian_skin = make_pbr_mat("M_Yoddha_Skin", (0.76, 0.54, 0.38, 1.0), metallic=0.0, roughness=0.50)
    mat_hair_black = make_pbr_mat("M_Yoddha_Hair", (0.05, 0.04, 0.04, 1.0), metallic=0.0, roughness=0.85)
    mat_tilak_red = make_pbr_mat("M_Yoddha_Tilak", (0.85, 0.04, 0.04, 1.0), metallic=0.0, roughness=0.70)
    mat_dhal = make_pbr_mat("M_Yoddha_DhalLeather", (0.12, 0.10, 0.09, 1.0), metallic=0.15, roughness=0.50)
    
    shiva_head.data.materials.clear()
    shiva_head.data.materials.append(mat_indian_skin)
    shiva_hair.data.materials.clear()
    shiva_hair.data.materials.append(mat_hair_black)
    body_parts.extend([shiva_head, shiva_hair])
    
    for o in body_parts:
        if o not in [shiva_head, shiva_hair]:
            mname = o.data.materials[0].name if o.data.materials else ""
            if "Torso" in mname or "Flesh" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_indian_skin)
            elif "Legs" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_saffron)
                
    custom_pieces = []
    
    # 1. Royal Kshatriya Warrior Pagri (Turban wrapped around head cranium)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=11.2, location=(0.0, -1.0, 192.0))
    pagri = bpy.context.active_object
    pagri.scale = (1.05, 1.15, 0.65)
    bpy.ops.object.transform_apply(scale=True)
    pagri.data.materials.append(mat_saffron)
    custom_pieces.append(pagri)
    
    # Pagri pleated fold band
    bpy.ops.mesh.primitive_torus_add(major_radius=11.5, minor_radius=1.2, location=(0.0, -1.0, 191.0), rotation=(math.radians(12), 0, 0))
    pband = bpy.context.active_object
    pband.scale = (1.02, 1.12, 0.75)
    bpy.ops.object.transform_apply(scale=True)
    pband.data.materials.append(mat_crimson)
    custom_pieces.append(pband)
    
    # Golden Sarpech (Royal Brooch with Jewel Plume on front of turban)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=2.2, depth=0.8, location=(0.0, -12.5, 194.0), rotation=(math.radians(85), 0, 0))
    sarpech = bpy.context.active_object
    sarpech.data.materials.append(mat_gold)
    custom_pieces.append(sarpech)
    
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.4, radius2=0.2, depth=7.0, location=(0.0, -12.2, 199.0), rotation=(math.radians(12), 0, 0))
    sarpech_plume = bpy.context.active_object
    sarpech_plume.data.materials.append(mat_crimson)
    custom_pieces.append(sarpech_plume)
    
    # Vermilion Tilak (Tripundra marking on brow)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -12.0, 185.0))
    tilak = bpy.context.active_object
    tilak.scale = (1.8, 0.2, 3.2)
    bpy.ops.object.transform_apply(scale=True)
    tilak.data.materials.append(mat_tilak_red)
    custom_pieces.append(tilak)
    
    # 2. Char-Aina ("Four Mirrors") Circular Surya Cuirass on chest
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=12.5, depth=2.2, location=(0.0, -11.5, 142.0), rotation=(math.radians(85), 0, 0))
    surya = bpy.context.active_object
    surya.data.materials.append(mat_gold)
    custom_pieces.append(surya)
    
    # Surya 12 Radiating Sun Rays
    for ray_i in range(12):
        angle = (ray_i / 12.0) * math.pi * 2.0
        rx = math.cos(angle) * 14.5
        rz = 142.0 + math.sin(angle) * 14.5
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.6, radius2=0.1, depth=5.5, location=(rx, -11.0, rz), rotation=(math.radians(85), 0, -angle + math.pi/2))
        ray = bpy.context.active_object
        ray.data.materials.append(mat_bronze)
        custom_pieces.append(ray)
        
    # Back Char-Aina plate
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=12.0, depth=2.0, location=(0.0, 12.0, 142.0), rotation=(math.radians(95), 0, 0))
    surya_b = bpy.context.active_object
    surya_b.data.materials.append(mat_bronze)
    custom_pieces.append(surya_b)
    
    # 3. Kshatriya War Kamarbandh (Belt & Sash)
    bpy.ops.mesh.primitive_torus_add(major_radius=16.0, minor_radius=2.2, location=(0.0, 0.0, 108.0))
    kamar = bpy.context.active_object
    kamar.scale = (1.05, 0.85, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    kamar.data.materials.append(mat_gold)
    custom_pieces.append(kamar)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -12.0, 85.0))
    sash = bpy.context.active_object
    sash.scale = (7.5, 0.6, 26.0)
    bpy.ops.object.transform_apply(scale=True)
    sash.data.materials.append(mat_crimson)
    custom_pieces.append(sash)
    
    # 4. Traditional Indian Dhal Shield on back
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=32.0, location=(0.0, 20.0, 132.0))
    dhal = bpy.context.active_object
    dhal.scale = (1.0, 0.15, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    dhal.data.materials.append(mat_dhal)
    custom_pieces.append(dhal)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=32.0, minor_radius=1.2, location=(0.0, 20.0, 132.0), rotation=(math.radians(90), 0, 0))
    drim = bpy.context.active_object
    drim.data.materials.append(mat_gold)
    custom_pieces.append(drim)
    
    for b_angle in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
        dbx = math.cos(b_angle) * 14.0
        dbz = 132.0 + math.sin(b_angle) * 14.0
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=3.2, location=(dbx, 24.5, dbz))
        boss = bpy.context.active_object
        boss.data.materials.append(mat_gold)
        custom_pieces.append(boss)

    all_pieces = body_parts + custom_pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = all_pieces[0]
    bpy.ops.object.join()
    
    master_mesh = bpy.context.active_object
    master_mesh.name = "SKM_IndianYoddha_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    prev_path = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\preview_indianyoddha.png"
    setup_camera_and_render(prev_path)
    
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_IndianYoddha.fbx"
    skin_and_export(master_mesh, out_fbx)
    return {"status": "Indian Yoddha Complete", "fbx": out_fbx, "preview": prev_path}


# =========================================================================
# 5. INDIAN GODDESS (DEVI / DURGA WARRIOR)
# =========================================================================
def build_indian_goddess():
    print("\n" + "="*50)
    print("BUILDING 5/6: INDIAN GODDESS (DEVI / DURGA WARRIOR)")
    print("="*50)
    dummy = reset_scene()
    
    quinn_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_Quinn.fbx"
    bpy.ops.import_scene.fbx(filepath=quinn_fbx)
    bpy.data.objects.remove(dummy, do_unlink=True)
    
    quinn_mesh = bpy.data.objects.get("SKM_Quinn_LOD0")
    for o in list(bpy.data.objects):
        if o.name.startswith("SKM_Quinn_LOD") and o != quinn_mesh:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'EMPTY':
            bpy.data.objects.remove(o, do_unlink=True)
            
    normalize_object(quinn_mesh)
    
    # Cut off Quinn's featureless robot head so real Indian Goddess face takes its place
    bpy.context.view_layer.objects.active = quinn_mesh
    bpy.ops.object.mode_set(mode='EDIT')
    import bmesh
    bm = bmesh.from_edit_mesh(quinn_mesh.data)
    verts_to_delete = [v for v in bm.verts if v.co.z > 148.0]
    bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')
    bmesh.update_edit_mesh(quinn_mesh.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Sculpted Indian Goddess face from Shiva Statue
    dummy_s = bpy.data.objects.new("DummyS", None)
    bpy.context.scene.collection.objects.link(dummy_s)
    bpy.context.view_layer.objects.active = dummy_s
    shiva_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Shiva_Statue_Project\Lord_Shiva_Statue.fbx"
    bpy.ops.import_scene.fbx(filepath=shiva_fbx)
    bpy.data.objects.remove(dummy_s, do_unlink=True)
    
    shiva_head = bpy.data.objects.get("Shiva_Head")
    shiva_hair = bpy.data.objects.get("Shiva_Hair")
    
    for o in list(bpy.data.objects):
        if o.name.startswith("Shiva_") and o not in [shiva_head, shiva_hair]:
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Scale to graceful feminine proportions and place right on neck
    scale_factor = 28.5
    for obj in [shiva_head, shiva_hair]:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(rotation=True)
        for v in obj.data.vertices:
            v.co.x = v.co.x * scale_factor * 0.88
            v.co.y = (v.co.y - (-0.08)) * scale_factor * 0.88 - 3.2
            v.co.z = (v.co.z - 3.47) * scale_factor * 0.82 + 164.0
            
    mat_gold = make_pbr_mat("M_Goddess_24kGold", (0.98, 0.82, 0.22, 1.0), metallic=0.98, roughness=0.15)
    mat_crimson = make_pbr_mat("M_Goddess_DeviCrimson", (0.75, 0.04, 0.08, 1.0), metallic=0.08, roughness=0.48)
    mat_emerald = make_pbr_mat("M_Goddess_Emerald", (0.05, 0.65, 0.22, 1.0), metallic=0.20, roughness=0.25)
    mat_skin = make_pbr_mat("M_Goddess_RadiantSkin", (0.82, 0.62, 0.48, 1.0), metallic=0.0, roughness=0.45)
    mat_hair = make_pbr_mat("M_Goddess_HairBlack", (0.04, 0.03, 0.03, 1.0), metallic=0.0, roughness=0.85)
    
    quinn_mesh.data.materials.clear()
    quinn_mesh.data.materials.append(mat_crimson)
    shiva_head.data.materials.clear()
    shiva_head.data.materials.append(mat_skin)
    shiva_hair.data.materials.clear()
    shiva_hair.data.materials.append(mat_hair)
    
    custom_pieces = []
    
    # 1. Radiant 16-Ray Prabhavali (Sacred Solar Halo centered behind head at Z=168)
    bpy.ops.mesh.primitive_torus_add(major_radius=18.0, minor_radius=1.0, location=(0.0, 4.0, 168.0), rotation=(math.radians(90), 0, 0))
    halo_ring = bpy.context.active_object
    halo_ring.data.materials.append(mat_gold)
    custom_pieces.append(halo_ring)
    
    for r_i in range(16):
        r_angle = (r_i / 16.0) * math.pi * 2.0
        rx = math.cos(r_angle) * 19.5
        rz = 168.0 + math.sin(r_angle) * 19.5
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.2, radius2=0.1, depth=5.5, location=(rx, 4.0, rz), rotation=(math.radians(90), 0, -r_angle + math.pi/2))
        h_ray = bpy.context.active_object
        h_ray.data.materials.append(mat_gold)
        custom_pieces.append(h_ray)
        
    # 2. Multi-Tiered Golden Kiritamukuta (Goddess Crown on brow Z=172)
    for c_i, (cz, cr, ch) in enumerate([(172.0, 8.8, 4.0), (176.0, 7.2, 4.5), (180.5, 5.2, 4.5), (185.0, 3.2, 4.5)]):
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=cr, radius2=cr*0.75, depth=ch, location=(0.0, -1.0, cz))
        c_tier = bpy.context.active_object
        c_tier.scale = (0.95, 1.08, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        c_tier.data.materials.append(mat_gold if c_i % 2 == 0 else mat_emerald)
        custom_pieces.append(c_tier)
        
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=2.0, location=(0.0, -1.0, 189.5))
    kalas = bpy.context.active_object
    kalas.scale = (0.8, 0.8, 1.4)
    bpy.ops.object.transform_apply(scale=True)
    kalas.data.materials.append(mat_gold)
    custom_pieces.append(kalas)
    
    # 3. Swarna Kavacha (Golden Embossed Lotus Cuirass over bust Z=126)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=12.0, location=(0.0, -5.5, 126.0))
    kavacha = bpy.context.active_object
    kavacha.scale = (1.02, 0.60, 0.85)
    bpy.ops.object.transform_apply(scale=True)
    kavacha.data.materials.append(mat_gold)
    custom_pieces.append(kavacha)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=3.8, depth=0.8, location=(0.0, -11.5, 126.0), rotation=(math.radians(82), 0, 0))
    lotus = bpy.context.active_object
    lotus.data.materials.append(mat_gold)
    custom_pieces.append(lotus)
    
    # 4. Golden Oddiyanam (Waistbelt Z=96)
    bpy.ops.mesh.primitive_torus_add(major_radius=13.5, minor_radius=1.4, location=(0.0, 0.0, 96.0))
    oddiyanam = bpy.context.active_object
    oddiyanam.scale = (1.08, 0.85, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    oddiyanam.data.materials.append(mat_gold)
    custom_pieces.append(oddiyanam)
    
    # Warrior Saree Pleats
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -9.0, 72.0))
    saree_pleats = bpy.context.active_object
    saree_pleats.scale = (7.5, 0.8, 28.0)
    bpy.ops.object.transform_apply(scale=True)
    saree_pleats.data.materials.append(mat_crimson)
    custom_pieces.append(saree_pleats)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -9.5, 59.0))
    zari = bpy.context.active_object
    zari.scale = (7.8, 0.9, 2.2)
    bpy.ops.object.transform_apply(scale=True)
    zari.data.materials.append(mat_gold)
    custom_pieces.append(zari)

    all_pieces = [quinn_mesh, shiva_head, shiva_hair] + custom_pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = all_pieces[0]
    bpy.ops.object.join()
    
    master_mesh = bpy.context.active_object
    master_mesh.name = "SKM_IndianGoddess_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    prev_path = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\preview_indiangoddess.png"
    setup_camera_and_render(prev_path)
    
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_IndianGoddess.fbx"
    skin_and_export(master_mesh, out_fbx)
    return {"status": "Indian Goddess Complete", "fbx": out_fbx, "preview": prev_path}


# =========================================================================
# 6. GIRL WARRIOR (VALKYRIE / AMAZON CHAMPION)
# =========================================================================
def build_girl_warrior():
    print("\n" + "="*50)
    print("BUILDING 6/6: GIRL WARRIOR (VALKYRIE CHAMPION)")
    print("="*50)
    dummy = reset_scene()
    
    quinn_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_Quinn.fbx"
    bpy.ops.import_scene.fbx(filepath=quinn_fbx)
    bpy.data.objects.remove(dummy, do_unlink=True)
    
    quinn_mesh = bpy.data.objects.get("SKM_Quinn_LOD0")
    for o in list(bpy.data.objects):
        if o.name.startswith("SKM_Quinn_LOD") and o != quinn_mesh:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'EMPTY':
            bpy.data.objects.remove(o, do_unlink=True)
            
    normalize_object(quinn_mesh)
    
    # Cut off robot head and replace with sculpted face
    bpy.context.view_layer.objects.active = quinn_mesh
    bpy.ops.object.mode_set(mode='EDIT')
    import bmesh
    bm = bmesh.from_edit_mesh(quinn_mesh.data)
    verts_to_delete = [v for v in bm.verts if v.co.z > 148.0]
    bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')
    bmesh.update_edit_mesh(quinn_mesh.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Import sculpted face from Shiva Statue
    dummy_s = bpy.data.objects.new("DummyS", None)
    bpy.context.scene.collection.objects.link(dummy_s)
    bpy.context.view_layer.objects.active = dummy_s
    shiva_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Shiva_Statue_Project\Lord_Shiva_Statue.fbx"
    bpy.ops.import_scene.fbx(filepath=shiva_fbx)
    bpy.data.objects.remove(dummy_s, do_unlink=True)
    
    shiva_head = bpy.data.objects.get("Shiva_Head")
    for o in list(bpy.data.objects):
        if o.name.startswith("Shiva_") and o != shiva_head:
            bpy.data.objects.remove(o, do_unlink=True)
            
    scale_factor = 27.5
    bpy.ops.object.select_all(action='DESELECT')
    shiva_head.select_set(True)
    bpy.context.view_layer.objects.active = shiva_head
    bpy.ops.object.transform_apply(rotation=True)
    for v in shiva_head.data.vertices:
        v.co.x = v.co.x * scale_factor * 0.88
        v.co.y = (v.co.y - (-0.08)) * scale_factor * 0.88 - 3.0
        v.co.z = (v.co.z - 3.47) * scale_factor * 0.82 + 158.0
        
    mat_mithril = make_pbr_mat("M_Valkyrie_Mithril", (0.85, 0.88, 0.92, 1.0), metallic=0.95, roughness=0.18)
    mat_azure = make_pbr_mat("M_Valkyrie_AzureSteel", (0.12, 0.35, 0.72, 1.0), metallic=0.88, roughness=0.25)
    mat_gold = make_pbr_mat("M_Valkyrie_GoldTrim", (0.95, 0.80, 0.22, 1.0), metallic=0.95, roughness=0.20)
    mat_leather = make_pbr_mat("M_Valkyrie_Leather", (0.24, 0.15, 0.10, 1.0), metallic=0.04, roughness=0.68)
    mat_cape = make_pbr_mat("M_Valkyrie_CapeAzure", (0.08, 0.18, 0.45, 1.0), metallic=0.06, roughness=0.60)
    mat_skin = make_pbr_mat("M_Valkyrie_FairSkin", (0.86, 0.70, 0.60, 1.0), metallic=0.0, roughness=0.45)
    mat_hair_blonde = make_pbr_mat("M_Valkyrie_HairBlonde", (0.85, 0.72, 0.42, 1.0), metallic=0.0, roughness=0.75)
    mat_gem = make_pbr_mat("M_Valkyrie_Sapphire", (0.05, 0.25, 0.95, 1.0), metallic=0.20, roughness=0.10)
    
    quinn_mesh.data.materials.clear()
    quinn_mesh.data.materials.append(mat_mithril)
    shiva_head.data.materials.clear()
    shiva_head.data.materials.append(mat_skin)
    
    custom_pieces = []
    
    # 1. Valkyrie Winged War Tiara on brow (Z=164)
    bpy.ops.mesh.primitive_torus_add(major_radius=8.2, minor_radius=0.65, location=(0.0, -1.0, 164.0))
    tiara = bpy.context.active_object
    tiara.scale = (0.95, 1.08, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    tiara.data.materials.append(mat_gold)
    custom_pieces.append(tiara)
    
    # Forehead Sapphire Gem
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.2, depth=0.6, location=(0.0, -9.5, 165.0), rotation=(math.radians(82), 0, 0))
    gem = bpy.context.active_object
    gem.data.materials.append(mat_gem)
    custom_pieces.append(gem)
    
    # Swept Falcon Wings above temples
    for wx, wy_rot in [(-8.0, math.radians(-25)), (8.0, math.radians(25))]:
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=2.2, radius2=0.35, depth=11.0, location=(wx, 0.5, 171.0), rotation=(math.radians(35), math.radians(-35 if wx < 0 else 35), wy_rot))
        wing = bpy.context.active_object
        wing.scale = (0.4, 0.8, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        wing.data.materials.append(mat_mithril)
        custom_pieces.append(wing)
        
    # 2. High Ponytail Hairstyle flowing behind
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=2.5, depth=26.0, location=(0.0, 7.5, 154.0), rotation=(math.radians(-28), 0, 0))
    pony = bpy.context.active_object
    pony.data.materials.append(mat_hair_blonde)
    custom_pieces.append(pony)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=2.5, minor_radius=0.50, location=(0.0, 3.2, 166.0), rotation=(math.radians(-28), 0, 0))
    htie = bpy.context.active_object
    htie.data.materials.append(mat_gold)
    custom_pieces.append(htie)
    
    # 3. Falcon Pauldrons on Shoulders
    for px in [-17.0, 17.0]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=7.0, location=(px, -1.0, 142.0))
        pld = bpy.context.active_object
        pld.scale = (0.95, 1.20, 0.70)
        bpy.ops.object.transform_apply(scale=True)
        pld.data.materials.append(mat_azure)
        custom_pieces.append(pld)
        
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=2.8, radius2=0.45, depth=9.5, location=(px * 1.15, -1.0, 147.0), rotation=(0, math.radians(-45 if px < 0 else 45), 0))
        pflange = bpy.context.active_object
        pflange.data.materials.append(mat_gold)
        custom_pieces.append(pflange)
        
    # 4. Sculpted Mithril Breastplate
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=11.0, location=(0.0, -5.0, 126.0))
    bplate = bpy.context.active_object
    bplate.scale = (1.05, 0.55, 0.85)
    bpy.ops.object.transform_apply(scale=True)
    bplate.data.materials.append(mat_mithril)
    custom_pieces.append(bplate)
    
    # 5. Gladiator Pteruges over hips
    for sk_i in range(8):
        sk_angle = (sk_i / 8.0) * math.pi * 2.0
        sk_x = math.cos(sk_angle) * 13.5
        sk_y = math.sin(sk_angle) * 10.5
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sk_x, sk_y, 88.0), rotation=(math.radians(10), 0, -sk_angle))
        pteruge = bpy.context.active_object
        pteruge.scale = (3.8, 0.6, 14.0)
        bpy.ops.object.transform_apply(scale=True)
        pteruge.data.materials.append(mat_leather if sk_i % 2 == 0 else mat_azure)
        custom_pieces.append(pteruge)
        
    # 6. Azure Valkyrie Capelet
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 9.0, 112.0))
    cape = bpy.context.active_object
    cape.scale = (18.0, 0.6, 44.0)
    cape.rotation_euler = (math.radians(-8), 0, 0)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    cape.data.materials.append(mat_cape)
    custom_pieces.append(cape)

    all_pieces = [quinn_mesh, shiva_head] + custom_pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = all_pieces[0]
    bpy.ops.object.join()
    
    master_mesh = bpy.context.active_object
    master_mesh.name = "SKM_GirlWarrior_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    prev_path = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\preview_girlwarrior.png"
    setup_camera_and_render(prev_path)
    
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_GirlWarrior.fbx"
    skin_and_export(master_mesh, out_fbx)
    return {"status": "Girl Warrior Complete", "fbx": out_fbx, "preview": prev_path}


# =========================================================================
# MASTER BATCH RUNNER
# =========================================================================
def build_all():
    print("="*60)
    print("STARTING FULL PROCEDURAL BUILD OF ALL 6 CHARACTERS (V3 REFINED)")
    print("="*60)
    
    results = {}
    results["viking"] = build_viking()
    results["medieval_warrior"] = build_medieval_warrior()
    results["samurai"] = build_samurai()
    results["indian_yoddha"] = build_indian_yoddha()
    results["indian_goddess"] = build_indian_goddess()
    results["girl_warrior"] = build_girl_warrior()
    
    print("\n" + "="*60)
    print("ALL 6 CHARACTERS GENERATED SUCCESSFULLY!")
    print("="*60)
    return results

if __name__ == "__main__":
    res = build_all()
    print("Results:", res)
