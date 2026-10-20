"""
generate_master_builds_v2.py - Generates 6 highly detailed, visually authentic character builds
rigged to the UE5 SK_CombatMannequin 160-bone skeleton.

Characters:
1. Viking (SKM_Viking)
2. Medieval Warrior (SKM_MedievalWarrior)
3. Samurai (SKM_Samurai)
4. Indian Yoddha (SKM_IndianYoddha)
5. Indian Goddess (SKM_IndianGoddess)
6. Girl Warrior (SKM_GirlWarrior)
"""

import sys
import os
import math
import bpy
from mathutils import Vector, Euler, Matrix

# Common helper functions
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
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = color
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = roughness
    return mat

def setup_camera_and_render(output_img_path):
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.45, 0.45, 0.47, 1.0)
        bg.inputs["Strength"].default_value = 0.85

    cam_data = bpy.data.cameras.new("RenderCam")
    cam = bpy.data.objects.new("RenderCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cam.location = (0.0, -320.0, 105.0)
    cam.rotation_euler = (math.radians(88.0), 0.0, 0.0)
    cam.data.clip_end = 2500.0
    
    sun_data = bpy.data.lights.new("SunKey", 'SUN')
    sun_data.energy = 4.5
    sun = bpy.data.objects.new("SunKey", sun_data)
    sun.location = (200.0, -300.0, 350.0)
    sun.rotation_euler = (math.radians(50.0), math.radians(20.0), math.radians(-30.0))
    bpy.context.scene.collection.objects.link(sun)
    
    fill_data = bpy.data.lights.new("Fill", 'POINT')
    fill_data.energy = 60000.0
    fill = bpy.data.objects.new("Fill", fill_data)
    fill.location = (-180.0, -250.0, 120.0)
    bpy.context.scene.collection.objects.link(fill)
    
    bpy.context.scene.render.resolution_x = 720
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.filepath = output_img_path
    bpy.ops.render.render(write_still=True)

def skin_and_export(mesh_obj, arm_obj, manny_mesh, out_fbx_path):
    mesh_obj.parent = arm_obj
    mesh_obj.matrix_parent_inverse = arm_obj.matrix_world.inverted()
    
    # DataTransfer weights from manny
    dt = mesh_obj.modifiers.new("DataTransfer", 'DATA_TRANSFER')
    dt.object = manny_mesh
    dt.use_vert_data = True
    dt.data_types_verts = {'VGROUP_WEIGHTS'}
    dt.vert_mapping = 'POLYINTERP_NEAREST'
    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.datalayout_transfer(modifier="DataTransfer")
    bpy.ops.object.modifier_apply(modifier="DataTransfer")
    
    arm_mod = mesh_obj.modifiers.new("Armature", 'ARMATURE')
    arm_mod.object = arm_obj
    
    # Remove manny mesh so only character mesh is present
    bpy.data.objects.remove(manny_mesh, do_unlink=True)
    
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
# 1. VIKING WARRIOR
# =========================================================================
def build_viking():
    print("\n================== BUILDING 1/6: VIKING ==================")
    dummy = reset_scene()
    
    manny_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
    bpy.ops.import_scene.fbx(filepath=manny_fbx)
    bpy.data.objects.remove(dummy, do_unlink=True)
    
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    manny_mesh = [o for o in bpy.data.objects if o.type == 'MESH' and "LOD0" in o.name][0]
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o != manny_mesh and "CombatMannequin" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Import Greystone Tough
    dummy2 = bpy.data.objects.new("Dummy2", None)
    bpy.context.scene.collection.objects.link(dummy2)
    bpy.context.view_layer.objects.active = dummy2
    tough_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Greystone_Tough.fbx"
    bpy.ops.import_scene.fbx(filepath=tough_fbx)
    bpy.data.objects.remove(dummy2, do_unlink=True)
    
    tough_mesh = bpy.data.objects.get("Greystone_Tough_LOD0")
    for o in list(bpy.data.objects):
        if o.name.startswith("Greystone_Tough_LOD") and o != tough_mesh:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'ARMATURE' and o != arm:
            bpy.data.objects.remove(o, do_unlink=True)
            
    bpy.context.view_layer.objects.active = tough_mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='MATERIAL')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Import Fur from standard Greystone
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
    
    mat_iron = make_pbr_mat("M_Viking_Iron", (0.50, 0.52, 0.55, 1.0), metallic=0.88, roughness=0.30)
    mat_silver = make_pbr_mat("M_Viking_Silver", (0.88, 0.89, 0.92, 1.0), metallic=0.95, roughness=0.18)
    mat_leather = make_pbr_mat("M_Viking_Leather", (0.28, 0.16, 0.09, 1.0), metallic=0.04, roughness=0.68)
    mat_fur = make_pbr_mat("M_Viking_WolfFur", (0.45, 0.42, 0.38, 1.0), metallic=0.0, roughness=0.92)
    mat_beard = make_pbr_mat("M_Viking_Beard", (0.35, 0.18, 0.08, 1.0), metallic=0.0, roughness=0.80)
    mat_wood = make_pbr_mat("M_Viking_WoodPlanks", (0.42, 0.26, 0.14, 1.0), metallic=0.0, roughness=0.70)
    mat_shield_red = make_pbr_mat("M_Viking_ShieldRed", (0.65, 0.09, 0.09, 1.0), metallic=0.05, roughness=0.55)
    mat_skin = make_pbr_mat("M_Viking_Skin", (0.82, 0.64, 0.52, 1.0), metallic=0.0, roughness=0.50)
    
    body_parts = []
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o != manny_mesh:
            mname = o.data.materials[0].name if o.data.materials else ""
            if "Sword" in mname or "Hair" in mname:
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
            elif "head" in mname or "skin" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_skin)
                body_parts.append(o)
            elif o.name.startswith("Greystone_LOD"):
                bpy.data.objects.remove(o, do_unlink=True)
            else:
                body_parts.append(o)
                
    custom_pieces = []
    
    # Gjermundbu Spectacle Helmet
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=18, radius=18.5, location=(0.0, -3.5, 184.0))
    helm_dome = bpy.context.active_object
    helm_dome.scale = (1.02, 1.15, 1.05)
    bpy.ops.object.transform_apply(scale=True)
    helm_dome.data.materials.append(mat_iron)
    custom_pieces.append(helm_dome)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=18.8, minor_radius=1.6, location=(0.0, -3.5, 175.0))
    helm_rim = bpy.context.active_object
    helm_rim.scale = (1.02, 1.15, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    helm_rim.data.materials.append(mat_silver)
    custom_pieces.append(helm_rim)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.6, depth=38.0, location=(0.0, -3.5, 187.0), rotation=(math.radians(90), 0, 0))
    rib_fb = bpy.context.active_object
    rib_fb.data.materials.append(mat_silver)
    custom_pieces.append(rib_fb)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.6, depth=38.0, location=(0.0, -3.5, 187.0), rotation=(0, math.radians(90), 0))
    rib_lr = bpy.context.active_object
    rib_lr.data.materials.append(mat_silver)
    custom_pieces.append(rib_lr)
    
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=2.8, radius2=0.5, depth=7.5, location=(0.0, -3.5, 204.0))
    apex = bpy.context.active_object
    apex.data.materials.append(mat_silver)
    custom_pieces.append(apex)
    
    for eye_side, eye_x in [("L", 5.2), ("R", -5.2)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=4.5, minor_radius=1.2, location=(eye_x, -16.2, 173.0), rotation=(math.radians(90), 0, 0))
        oc = bpy.context.active_object
        oc.data.materials.append(mat_iron)
        custom_pieces.append(oc)
        
    bpy.ops.mesh.primitive_cube_add(size=6.0, location=(0.0, -17.5, 166.0))
    nasal = bpy.context.active_object
    nasal.scale = (0.32, 0.25, 2.0)
    bpy.ops.object.transform_apply(scale=True)
    nasal.data.materials.append(mat_iron)
    custom_pieces.append(nasal)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=19.5, depth=20.0, location=(0.0, -1.0, 160.0))
    aventail = bpy.context.active_object
    aventail.scale = (1.02, 1.12, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    aventail.data.materials.append(mat_iron)
    custom_pieces.append(aventail)
    
    # Norse Braided Beard (positioned over chestplate collar)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=12.0, radius2=4.0, depth=36.0, location=(0.0, -18.5, 144.0), rotation=(math.radians(18), 0, 0))
    beard = bpy.context.active_object
    beard.scale = (1.1, 0.70, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    beard.data.materials.append(mat_beard)
    custom_pieces.append(beard)
    
    for m_side, mx, rotz in [("L", 4.5, math.radians(20)), ("R", -4.5, math.radians(-20))]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=2.2, depth=12.0, location=(mx, -18.0, 163.0), rotation=(math.radians(30), math.radians(35) if m_side == "L" else math.radians(-35), rotz))
        stache = bpy.context.active_object
        stache.data.materials.append(mat_beard)
        custom_pieces.append(stache)
        
    for b_side, bx in [("L", 4.2), ("R", -4.2)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=2.4, depth=32.0, location=(bx, -17.5, 136.0), rotation=(math.radians(14), 0, 0))
        br = bpy.context.active_object
        br.data.materials.append(mat_beard)
        custom_pieces.append(br)
        for rz in [142.0, 128.0]:
            bpy.ops.mesh.primitive_torus_add(major_radius=2.8, minor_radius=0.8, location=(bx, -17.0, rz))
            ring = bpy.context.active_object
            ring.data.materials.append(mat_silver)
            custom_pieces.append(ring)
            
    for br_side, br_x in [("L", 16.0), ("R", -16.0)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=3.8, depth=1.5, location=(br_x, -14.0, 154.0), rotation=(math.radians(80), 0, 0))
        brooch = bpy.context.active_object
        brooch.data.materials.append(mat_silver)
        custom_pieces.append(brooch)
        
    # Norse Round Shield on Back
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=38.0, depth=3.2, location=(0.0, 24.0, 128.0), rotation=(math.radians(90), 0, 0))
    s_wood = bpy.context.active_object
    s_wood.data.materials.append(mat_wood)
    custom_pieces.append(s_wood)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=37.5, depth=3.4, location=(0.0, 24.2, 128.0), rotation=(math.radians(90), 0, 0))
    s_paint = bpy.context.active_object
    s_paint.scale = (0.70, 1.0, 0.70)
    bpy.ops.object.transform_apply(scale=True)
    s_paint.data.materials.append(mat_shield_red)
    custom_pieces.append(s_paint)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=38.0, minor_radius=1.8, location=(0.0, 24.0, 128.0), rotation=(math.radians(90), 0, 0))
    s_rim = bpy.context.active_object
    s_rim.data.materials.append(mat_iron)
    custom_pieces.append(s_rim)
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=7.5, location=(0.0, 27.0, 128.0))
    s_boss = bpy.context.active_object
    s_boss.scale = (1.0, 0.5, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    s_boss.data.materials.append(mat_iron)
    custom_pieces.append(s_boss)
    
    for leg_side, leg_x in [("L", 14.0), ("R", -14.0)]:
        for strap_i in range(5):
            sz = 18.0 + (strap_i * 6.5)
            bpy.ops.mesh.primitive_torus_add(major_radius=8.2, minor_radius=0.5, location=(leg_x, -2.5, sz), rotation=(math.radians(15 if strap_i % 2 == 0 else -15), 0, 0))
            st = bpy.context.active_object
            st.scale = (0.95, 1.15, 1.0)
            bpy.ops.object.transform_apply(scale=True)
            st.data.materials.append(mat_leather)
            custom_pieces.append(st)
            
    all_viking = body_parts + custom_pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_viking:
        p.select_set(True)
    bpy.context.view_layer.objects.active = all_viking[0]
    bpy.ops.object.join()
    
    master_viking = bpy.context.active_object
    master_viking.name = "SKM_Viking_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    prev_path = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\preview_viking.png"
    setup_camera_and_render(prev_path)
    
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_Viking.fbx"
    skin_and_export(master_viking, arm, manny_mesh, out_fbx)
    return {"status": "Viking Complete", "fbx": out_fbx, "preview": prev_path}


# =========================================================================
# 2. MEDIEVAL WARRIOR (GOTHIC KNIGHT PALADIN)
# =========================================================================
def build_medieval_warrior():
    print("\n================== BUILDING 2/6: MEDIEVAL WARRIOR ==================")
    dummy = reset_scene()
    
    manny_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
    bpy.ops.import_scene.fbx(filepath=manny_fbx)
    bpy.data.objects.remove(dummy, do_unlink=True)
    
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    manny_mesh = [o for o in bpy.data.objects if o.type == 'MESH' and "LOD0" in o.name][0]
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o != manny_mesh and "CombatMannequin" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)
            
    dummy2 = bpy.data.objects.new("Dummy2", None)
    bpy.context.scene.collection.objects.link(dummy2)
    bpy.context.view_layer.objects.active = dummy2
    grey_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Greystone.fbx"
    bpy.ops.import_scene.fbx(filepath=grey_fbx)
    bpy.data.objects.remove(dummy2, do_unlink=True)
    
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
    
    mat_plate = make_pbr_mat("M_Knight_PolishedSteel", (0.80, 0.82, 0.85, 1.0), metallic=0.96, roughness=0.18)
    mat_gold_trim = make_pbr_mat("M_Knight_GoldFiligree", (0.95, 0.78, 0.22, 1.0), metallic=0.95, roughness=0.22)
    mat_royal_blue = make_pbr_mat("M_Knight_RoyalBlue", (0.08, 0.16, 0.45, 1.0), metallic=0.04, roughness=0.65)
    mat_fur = make_pbr_mat("M_Knight_ErmineFur", (0.85, 0.84, 0.82, 1.0), metallic=0.0, roughness=0.90)
    mat_skin = make_pbr_mat("M_Knight_Skin", (0.82, 0.65, 0.52, 1.0), metallic=0.0, roughness=0.50)
    
    body_parts = []
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o != manny_mesh:
            mname = o.data.materials[0].name if o.data.materials else ""
            if "Hair" in mname:
                bpy.data.objects.remove(o, do_unlink=True)
            elif "Fur" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_fur)
                body_parts.append(o)
            elif "Torso" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_plate)
                body_parts.append(o)
            elif "arms" in mname or "Arms" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_plate)
                body_parts.append(o)
            elif "legs" in mname or "Legs" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_plate)
                body_parts.append(o)
            elif "shield" in mname or "Shield" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_royal_blue)
                body_parts.append(o)
            elif "head" in mname or "Flesh" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_skin)
                body_parts.append(o)
            else:
                body_parts.append(o)
                
    custom_pieces = []
    
    # High Gothic Armet Knight Helmet
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=18, radius=18.5, location=(0.0, -2.5, 185.0))
    helm_skull = bpy.context.active_object
    helm_skull.scale = (1.02, 1.14, 1.08)
    bpy.ops.object.transform_apply(scale=True)
    helm_skull.data.materials.append(mat_plate)
    custom_pieces.append(helm_skull)
    
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=16.0, radius2=2.0, depth=14.0, location=(0.0, -14.5, 175.0), rotation=(math.radians(-80), 0, 0))
    visor = bpy.context.active_object
    visor.scale = (1.02, 0.70, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    visor.data.materials.append(mat_plate)
    custom_pieces.append(visor)
    
    for slit_side, sx in [("L", 5.0), ("R", -5.0)]:
        bpy.ops.mesh.primitive_cube_add(size=3.0, location=(sx, -19.5, 178.0))
        slit = bpy.context.active_object
        slit.scale = (1.8, 0.15, 0.25)
        bpy.ops.object.transform_apply(scale=True)
        slit.data.materials.append(mat_gold_trim)
        custom_pieces.append(slit)
        
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=19.0, depth=16.0, location=(0.0, -1.0, 162.0))
    gorget = bpy.context.active_object
    gorget.scale = (1.04, 1.10, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    gorget.data.materials.append(mat_plate)
    custom_pieces.append(gorget)
    
    bpy.ops.mesh.primitive_cube_add(size=10.0, location=(0.0, -2.0, 198.0))
    crest_comb = bpy.context.active_object
    crest_comb.scale = (0.15, 2.5, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    crest_comb.data.materials.append(mat_gold_trim)
    custom_pieces.append(crest_comb)
    
    for plume_i in range(3):
        pz = 205.0 + (plume_i * 6.0)
        py = -5.0 - (plume_i * 4.0)
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=3.5 - (plume_i * 0.5), radius2=0.5, depth=14.0, location=(0.0, py, pz), rotation=(math.radians(-35 - (plume_i * 12)), 0, 0))
        feather = bpy.context.active_object
        feather.scale = (0.5, 1.0, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        feather.data.materials.append(mat_royal_blue if plume_i % 2 == 0 else mat_gold_trim)
        custom_pieces.append(feather)
        
    bpy.ops.mesh.primitive_cube_add(size=10.0, location=(0.0, -16.5, 85.0))
    tabard = bpy.context.active_object
    tabard.scale = (1.3, 0.12, 3.8)
    bpy.ops.object.transform_apply(scale=True)
    tabard.data.materials.append(mat_royal_blue)
    custom_pieces.append(tabard)
    
    bpy.ops.mesh.primitive_cube_add(size=10.0, location=(0.0, -16.7, 68.0))
    tabard_hem = bpy.context.active_object
    tabard_hem.scale = (1.34, 0.14, 0.5)
    bpy.ops.object.transform_apply(scale=True)
    tabard_hem.data.materials.append(mat_gold_trim)
    custom_pieces.append(tabard_hem)
    
    all_knight = body_parts + custom_pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_knight:
        p.select_set(True)
    bpy.context.view_layer.objects.active = all_knight[0]
    bpy.ops.object.join()
    
    master_knight = bpy.context.active_object
    master_knight.name = "SKM_MedievalWarrior_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    prev_path = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\preview_medievalwarrior.png"
    setup_camera_and_render(prev_path)
    
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_MedievalWarrior.fbx"
    skin_and_export(master_knight, arm, manny_mesh, out_fbx)
    return {"status": "Medieval Warrior Complete", "fbx": out_fbx, "preview": prev_path}


# =========================================================================
# 3. SAMURAI (BUSHI CLAN COMMANDER)
# =========================================================================
def build_samurai():
    print("\n================== BUILDING 3/6: SAMURAI ==================")
    dummy = reset_scene()
    
    manny_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
    bpy.ops.import_scene.fbx(filepath=manny_fbx)
    bpy.data.objects.remove(dummy, do_unlink=True)
    
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    manny_mesh = [o for o in bpy.data.objects if o.type == 'MESH' and "LOD0" in o.name][0]
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o != manny_mesh and "CombatMannequin" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Import Greystone WhiteTiger (Asian warrior silhouette)
    dummy2 = bpy.data.objects.new("Dummy2", None)
    bpy.context.scene.collection.objects.link(dummy2)
    bpy.context.view_layer.objects.active = dummy2
    wt_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Greystone_WhiteTiger.fbx"
    bpy.ops.import_scene.fbx(filepath=wt_fbx)
    bpy.data.objects.remove(dummy2, do_unlink=True)
    
    wt_mesh = bpy.data.objects.get("Greystone_WhiteTiger_LOD0")
    for o in list(bpy.data.objects):
        if o.name.startswith("Greystone_WhiteTiger_LOD") and o != wt_mesh:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'ARMATURE' and o != arm:
            bpy.data.objects.remove(o, do_unlink=True)
            
    bpy.context.view_layer.objects.active = wt_mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='MATERIAL')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Authentic Samurai Materials
    mat_lacquer = make_pbr_mat("M_Samurai_BlackUrushi", (0.04, 0.04, 0.05, 1.0), metallic=0.15, roughness=0.18)
    mat_gold = make_pbr_mat("M_Samurai_GoldKamon", (0.95, 0.76, 0.22, 1.0), metallic=0.96, roughness=0.20)
    mat_silk_red = make_pbr_mat("M_Samurai_OdoshiSilk", (0.75, 0.05, 0.08, 1.0), metallic=0.02, roughness=0.68)
    mat_iron = make_pbr_mat("M_Samurai_KozaneIron", (0.28, 0.29, 0.32, 1.0), metallic=0.85, roughness=0.35)
    mat_skin = make_pbr_mat("M_Samurai_Skin", (0.84, 0.68, 0.54, 1.0), metallic=0.0, roughness=0.50)
    
    body_parts = []
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o != manny_mesh:
            mname = o.data.materials[0].name if o.data.materials else ""
            if "Hair" in mname or "Fur" in mname or "shield" in mname:
                bpy.data.objects.remove(o, do_unlink=True)
            elif "Torso" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_lacquer)
                body_parts.append(o)
            elif "arms" in mname or "Arms" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_lacquer)
                body_parts.append(o)
            elif "legs" in mname or "Legs" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_lacquer)
                body_parts.append(o)
            elif "head" in mname or "Flesh" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_skin)
                body_parts.append(o)
            else:
                body_parts.append(o)
                
    custom_pieces = []
    
    # 1. KABUTO HELMET (Ribbed iron bowl at Z=185)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=18, radius=18.5, location=(0.0, -3.0, 185.0))
    kabuto_dome = bpy.context.active_object
    kabuto_dome.scale = (1.02, 1.15, 1.04)
    bpy.ops.object.transform_apply(scale=True)
    kabuto_dome.data.materials.append(mat_lacquer)
    custom_pieces.append(kabuto_dome)
    
    # Tehen (Apex Chrysanthemum brass opening)
    bpy.ops.mesh.primitive_torus_add(major_radius=3.5, minor_radius=1.0, location=(0.0, -3.0, 204.0))
    tehen = bpy.context.active_object
    tehen.data.materials.append(mat_gold)
    custom_pieces.append(tehen)
    
    # 2. SHIKORO (4-tier Flared Neck Skirt laced with silk ribbons)
    for tier_i in range(4):
        tz = 175.0 - (tier_i * 4.5)
        trad = 19.5 + (tier_i * 2.2)
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=trad, depth=3.8, location=(0.0, 0.0, tz))
        shikoro_tier = bpy.context.active_object
        shikoro_tier.scale = (1.04, 1.12, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        shikoro_tier.data.materials.append(mat_silk_red if tier_i % 2 == 1 else mat_lacquer)
        custom_pieces.append(shikoro_tier)
        
    # 3. FUKIGAESHI (Wing-like Turnbacks on helmet sides with Gold Clan Mon)
    for f_side, fx, frot in [("L", 18.5, math.radians(35)), ("R", -18.5, math.radians(-35))]:
        bpy.ops.mesh.primitive_cube_add(size=8.0, location=(fx, -10.0, 180.0))
        fuki = bpy.context.active_object
        fuki.scale = (0.25, 1.2, 1.5)
        fuki.rotation_euler = (0, 0, frot)
        bpy.ops.object.transform_apply(rotation=True, scale=True)
        fuki.data.materials.append(mat_lacquer)
        custom_pieces.append(fuki)
        
        # Gold Mon Crest
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=2.2, depth=0.6, location=(fx * 1.08, -10.0, 180.0), rotation=(0, math.radians(90), 0))
        mon = bpy.context.active_object
        mon.data.materials.append(mat_gold)
        custom_pieces.append(mon)
        
    # 4. MAEDATE CREST (Sweeping Golden Crescent Horns on Brow)
    for horn_side, hx, hrot in [("L", 6.5, math.radians(-25)), ("R", -6.5, math.radians(25))]:
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=2.8, radius2=0.4, depth=22.0, location=(hx, -18.5, 198.0), rotation=(math.radians(25), hrot, 0))
        horn = bpy.context.active_object
        horn.scale = (0.35, 1.0, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        horn.data.materials.append(mat_gold)
        custom_pieces.append(horn)
        
    # Central Sunburst Crest Disc
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=4.5, depth=1.2, location=(0.0, -19.5, 188.0), rotation=(math.radians(90), 0, 0))
    crest_sun = bpy.context.active_object
    crest_sun.data.materials.append(mat_gold)
    custom_pieces.append(crest_sun)
    
    # 5. MENPO (Demonic Iron War Mask covering lower face with Bared Teeth & Moustache)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=11.5, location=(0.0, -15.5, 166.0))
    menpo = bpy.context.active_object
    menpo.scale = (0.95, 0.85, 0.95)
    bpy.ops.object.transform_apply(scale=True)
    menpo.data.materials.append(mat_lacquer)
    custom_pieces.append(menpo)
    
    # Fierce golden warrior moustache
    for ms, mx in [("L", 4.0), ("R", -4.0)]:
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.5, radius2=0.2, depth=9.0, location=(mx, -22.5, 166.0), rotation=(math.radians(35), math.radians(45 if ms=="L" else -45), 0))
        moust = bpy.context.active_object
        moust.data.materials.append(mat_gold)
        custom_pieces.append(moust)
        
    # 6. Ō-SODE (Rectangular Layered Shoulder Defense Shields)
    for sode_side, sx in [("L", 34.0), ("R", -34.0)]:
        for tier in range(4):
            sz = 152.0 - (tier * 6.5)
            bpy.ops.mesh.primitive_cube_add(size=10.0, location=(sx, -2.0, sz))
            sode = bpy.context.active_object
            sode.scale = (0.25, 2.2, 0.6)
            bpy.ops.object.transform_apply(scale=True)
            sode.data.materials.append(mat_lacquer if tier % 2 == 0 else mat_silk_red)
            custom_pieces.append(sode)
            
            # Gold ornamental corner brackets (Kanamono)
            for by in [-8.5, 8.5]:
                bpy.ops.mesh.primitive_cube_add(size=2.0, location=(sx * 1.04, by, sz))
                bracket = bpy.context.active_object
                bracket.data.materials.append(mat_gold)
                custom_pieces.append(bracket)
                
    # 7. KUSAZURI (Multi-panel hanging skirt tassets over Hakama)
    for panel_side, px, py in [("FL", 12.0, -14.0), ("FR", -12.0, -14.0), ("SL", 20.0, -2.0), ("SR", -20.0, -2.0), ("BL", 12.0, 14.0), ("BR", -12.0, 14.0)]:
        bpy.ops.mesh.primitive_cube_add(size=10.0, location=(px, py, 88.0))
        tasset = bpy.context.active_object
        tasset.scale = (1.1, 0.18, 2.8)
        bpy.ops.object.transform_apply(scale=True)
        tasset.data.materials.append(mat_lacquer)
        custom_pieces.append(tasset)
        
        # Red silk odoshi trim
        bpy.ops.mesh.primitive_cube_add(size=10.0, location=(px, py * 1.02, 75.0))
        t_trim = bpy.context.active_object
        t_trim.scale = (1.12, 0.20, 0.5)
        bpy.ops.object.transform_apply(scale=True)
        t_trim.data.materials.append(mat_silk_red)
        custom_pieces.append(t_trim)
        
    all_samurai = body_parts + custom_pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_samurai:
        p.select_set(True)
    bpy.context.view_layer.objects.active = all_samurai[0]
    bpy.ops.object.join()
    
    master_samurai = bpy.context.active_object
    master_samurai.name = "SKM_Samurai_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    prev_path = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\preview_samurai.png"
    setup_camera_and_render(prev_path)
    
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_Samurai.fbx"
    skin_and_export(master_samurai, arm, manny_mesh, out_fbx)
    return {"status": "Samurai Complete", "fbx": out_fbx, "preview": prev_path}


# =========================================================================
# 4. INDIAN YODDHA (KSHATRIYA WARRIOR)
# =========================================================================
def build_indian_yoddha():
    print("\n================== BUILDING 4/6: INDIAN YODDHA ==================")
    dummy = reset_scene()
    
    manny_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
    bpy.ops.import_scene.fbx(filepath=manny_fbx)
    bpy.data.objects.remove(dummy, do_unlink=True)
    
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    manny_mesh = [o for o in bpy.data.objects if o.type == 'MESH' and "LOD0" in o.name][0]
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o != manny_mesh and "CombatMannequin" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Import Greystone Novaborn (athletic sculpted torso, abs, legs)
    dummy2 = bpy.data.objects.new("Dummy2", None)
    bpy.context.scene.collection.objects.link(dummy2)
    bpy.context.view_layer.objects.active = dummy2
    nb_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Greystone_Novaborn.fbx"
    bpy.ops.import_scene.fbx(filepath=nb_fbx)
    bpy.data.objects.remove(dummy2, do_unlink=True)
    
    nb_mesh = bpy.data.objects.get("Greystone_Novaborn_LOD0")
    for o in list(bpy.data.objects):
        if o.name.startswith("Greystone_Novaborn_LOD") and o != nb_mesh:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'ARMATURE' and o != arm:
            bpy.data.objects.remove(o, do_unlink=True)
            
    bpy.context.view_layer.objects.active = nb_mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='MATERIAL')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Import Shiva Head and Hair for authentic sculpted Indian face and warrior top-knot
    dummy3 = bpy.data.objects.new("Dummy3", None)
    bpy.context.scene.collection.objects.link(dummy3)
    bpy.context.view_layer.objects.active = dummy3
    shiva_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Shiva_Statue_Project\Lord_Shiva_Statue.fbx"
    bpy.ops.import_scene.fbx(filepath=shiva_fbx)
    bpy.data.objects.remove(dummy3, do_unlink=True)
    
    shiva_head = bpy.data.objects.get("Shiva_Head")
    shiva_hair = bpy.data.objects.get("Shiva_Hair")
    
    for s_obj in [shiva_head, shiva_hair]:
        if s_obj:
            bpy.ops.object.select_all(action='DESELECT')
            s_obj.select_set(True)
            bpy.context.view_layer.objects.active = s_obj
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            
    for o in list(bpy.data.objects):
        if o.name.startswith("Shiva_") and o not in (shiva_head, shiva_hair):
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Scale and place Shiva Head & Hair in centimeter space (head at Z=176, Y=-4.0)
    for obj in [shiva_head, shiva_hair]:
        if obj:
            for v in obj.data.vertices:
                v.co.x *= 50.0 # 0.50 scale in cm (x100)
                v.co.y = ((v.co.y - (-0.079)) * 50.0) - 4.0
                v.co.z = ((v.co.z - 3.47) * 50.0) + 176.0
            obj.data.update()
            
    # Materials
    mat_skin = make_pbr_mat("M_Yoddha_Skin", (0.75, 0.54, 0.38, 1.0), metallic=0.0, roughness=0.52)
    mat_hair = make_pbr_mat("M_Yoddha_Hair", (0.05, 0.03, 0.02, 1.0), metallic=0.0, roughness=0.80)
    mat_gold = make_pbr_mat("M_Yoddha_Gold", (0.96, 0.76, 0.22, 1.0), metallic=0.96, roughness=0.20)
    mat_steel = make_pbr_mat("M_Yoddha_WootzSteel", (0.68, 0.70, 0.73, 1.0), metallic=0.92, roughness=0.25)
    mat_saffron = make_pbr_mat("M_Yoddha_Saffron", (0.96, 0.42, 0.06, 1.0), metallic=0.02, roughness=0.75)
    mat_maroon = make_pbr_mat("M_Yoddha_Maroon", (0.48, 0.05, 0.08, 1.0), metallic=0.02, roughness=0.80)
    mat_ruby = make_pbr_mat("M_Yoddha_Ruby", (0.85, 0.02, 0.08, 1.0), metallic=0.2, roughness=0.10)
    
    shiva_head.data.materials.clear()
    shiva_head.data.materials.append(mat_skin)
    shiva_hair.data.materials.clear()
    shiva_hair.data.materials.append(mat_hair)
    
    body_parts = [shiva_head, shiva_hair]
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o != manny_mesh and o not in body_parts:
            mname = o.data.materials[0].name if o.data.materials else ""
            if "head" in mname or "Hair" in mname or "Eye" in mname or "Sword" in mname:
                bpy.data.objects.remove(o, do_unlink=True)
            elif "Torso" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_gold)
                body_parts.append(o)
            elif "Leg" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_saffron)
                body_parts.append(o)
            elif "Weapons" in mname:
                o.data.materials.clear()
                o.data.materials.append(mat_maroon)
                body_parts.append(o)
            else:
                body_parts.append(o)
                
    custom_pieces = []
    
    # 1. MARTIAL PAGRI (Turban) with Royal Sarpech and Tilak
    for i in range(4):
        z_offset = 176.0 + (i * 3.5)
        rad = 17.5 + (i * 0.8)
        bpy.ops.mesh.primitive_torus_add(major_radius=rad, minor_radius=2.6, location=(0.0, -3.5, z_offset))
        fold = bpy.context.active_object
        fold.scale = (1.02, 1.15, 0.75)
        fold.rotation_euler = (0.04 * (i - 1.5), 0.03 * (i - 1.5), 0.0)
        bpy.ops.object.transform_apply(rotation=True, scale=True)
        fold.data.materials.append(mat_saffron if i % 2 == 0 else mat_maroon)
        custom_pieces.append(fold)
        
    # Golden Sarpech Brooch
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=3.2, depth=1.2, location=(0.0, -18.5, 184.0), rotation=(math.radians(90), 0, 0))
    sarpech = bpy.context.active_object
    sarpech.data.materials.append(mat_gold)
    custom_pieces.append(sarpech)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=1.8, depth=1.6, location=(0.0, -19.2, 184.0), rotation=(math.radians(90), 0, 0))
    ruby = bpy.context.active_object
    ruby.data.materials.append(mat_ruby)
    custom_pieces.append(ruby)
    
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=2.5, radius2=0.5, depth=14.0, location=(0.0, -18.5, 193.0), rotation=(math.radians(-10), 0, 0))
    kalgi = bpy.context.active_object
    kalgi.scale = (0.35, 1.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    kalgi.data.materials.append(mat_saffron)
    custom_pieces.append(kalgi)
    
    # Forehead Tilak
    bpy.ops.mesh.primitive_cube_add(size=4.0, location=(0.0, -17.5, 175.0))
    tilak = bpy.context.active_object
    tilak.scale = (0.25, 0.15, 1.2)
    bpy.ops.object.transform_apply(scale=True)
    tilak.data.materials.append(mat_ruby)
    custom_pieces.append(tilak)
    
    # 2. CHAR-AINA (Surya Kavacha) with Embossed Sun God on chest
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=7.5, depth=1.5, location=(0.0, -19.5, 134.0), rotation=(math.radians(90), 0, 0))
    surya = bpy.context.active_object
    surya.data.materials.append(mat_gold)
    custom_pieces.append(surya)
    
    for beam_i in range(8):
        angle = beam_i * (math.pi / 4.0)
        bx = 9.0 * math.cos(angle)
        bz = 134.0 + (9.0 * math.sin(angle))
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=1.4, radius2=0.2, depth=5.0, location=(bx, -19.5, bz), rotation=(math.radians(90), 0, -angle + math.radians(90)))
        ray = bpy.context.active_object
        ray.data.materials.append(mat_gold)
        custom_pieces.append(ray)
        
    # 3. KAMARBANDH & EMBROIDERED PATKA SASH
    bpy.ops.mesh.primitive_torus_add(major_radius=20.0, minor_radius=2.2, location=(0.0, -1.0, 98.0))
    belt = bpy.context.active_object
    belt.scale = (1.06, 0.88, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    belt.data.materials.append(mat_gold)
    custom_pieces.append(belt)
    
    bpy.ops.mesh.primitive_cube_add(size=10.0, location=(0.0, -16.5, 65.0))
    patka = bpy.context.active_object
    patka.scale = (1.1, 0.12, 3.2)
    bpy.ops.object.transform_apply(scale=True)
    patka.data.materials.append(mat_maroon)
    custom_pieces.append(patka)
    
    bpy.ops.mesh.primitive_cube_add(size=10.0, location=(0.0, -16.8, 50.0))
    patka_hem = bpy.context.active_object
    patka_hem.scale = (1.12, 0.14, 0.4)
    bpy.ops.object.transform_apply(scale=True)
    patka_hem.data.materials.append(mat_gold)
    custom_pieces.append(patka_hem)
    
    # 4. TRADITIONAL CURVED-TOE MOJARI SHOES
    for leg_side, leg_x in [("L", 14.0), ("R", -14.0)]:
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=3.5, radius2=0.5, depth=7.0, location=(leg_x, -18.0, 8.0), rotation=(math.radians(65), 0, 0))
        toe = bpy.context.active_object
        toe.data.materials.append(mat_gold)
        custom_pieces.append(toe)
        
    # 5. AUTHENTIC DHAL SHIELD ON BACK
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=28.0, depth=2.8, location=(0.0, 24.0, 128.0), rotation=(math.radians(90), 0, 0))
    dhal = bpy.context.active_object
    dhal.data.materials.append(mat_steel)
    custom_pieces.append(dhal)
    
    for bx, bz in [(-10.0, 138.0), (10.0, 138.0), (-10.0, 118.0), (10.0, 118.0)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=2.4, location=(bx, 26.5, bz))
        boss = bpy.context.active_object
        boss.data.materials.append(mat_gold)
        custom_pieces.append(boss)
        
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=4.5, depth=1.5, location=(0.0, 26.5, 128.0), rotation=(math.radians(90), 0, 0))
    dhal_c = bpy.context.active_object
    dhal_c.data.materials.append(mat_gold)
    custom_pieces.append(dhal_c)
    
    all_yoddha = body_parts + custom_pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_yoddha:
        p.select_set(True)
    bpy.context.view_layer.objects.active = all_yoddha[0]
    bpy.ops.object.join()
    
    master_yoddha = bpy.context.active_object
    master_yoddha.name = "SKM_IndianYoddha_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    prev_path = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\preview_indianyoddha.png"
    setup_camera_and_render(prev_path)
    
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_IndianYoddha.fbx"
    skin_and_export(master_yoddha, arm, manny_mesh, out_fbx)
    return {"status": "Indian Yoddha Complete", "fbx": out_fbx, "preview": prev_path}


# =========================================================================
# 5. INDIAN GODDESS (DEVI / DURGA WARRIOR)
# =========================================================================
def build_indian_goddess():
    print("\n================== BUILDING 5/6: INDIAN GODDESS ==================")
    dummy = reset_scene()
    
    quinn_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_Quinn.fbx"
    bpy.ops.import_scene.fbx(filepath=quinn_fbx)
    bpy.data.objects.remove(dummy, do_unlink=True)
    
    quinn_mesh = [o for o in bpy.data.objects if o.type == 'MESH' and "LOD0" in o.name][0]
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o != quinn_mesh and "Quinn" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'ARMATURE':
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Unparent Quinn so its coordinates are in true centimeters (0 to 180 cm)
    quinn_mesh.parent = None
    quinn_mesh.matrix_world = Matrix.Identity(4)
    bpy.context.view_layer.objects.active = quinn_mesh
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # Import Shiva Head for sculpted divine facial features
    dummy2 = bpy.data.objects.new("Dummy2", None)
    bpy.context.scene.collection.objects.link(dummy2)
    bpy.context.view_layer.objects.active = dummy2
    shiva_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Shiva_Statue_Project\Lord_Shiva_Statue.fbx"
    bpy.ops.import_scene.fbx(filepath=shiva_fbx)
    bpy.data.objects.remove(dummy2, do_unlink=True)
    
    shiva_head = bpy.data.objects.get("Shiva_Head")
    if shiva_head:
        bpy.ops.object.select_all(action='DESELECT')
        shiva_head.select_set(True)
        bpy.context.view_layer.objects.active = shiva_head
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
    for o in list(bpy.data.objects):
        if o.name.startswith("Shiva_") and o != shiva_head:
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Scale Shiva Head to Quinn female proportions (Z=168, Y=-3.0)
    if shiva_head:
        for v in shiva_head.data.vertices:
            v.co.x *= 44.0
            v.co.y = ((v.co.y - (-0.079)) * 44.0) - 3.0
            v.co.z = ((v.co.z - 3.47) * 44.0) + 168.0
        shiva_head.data.update()
        
    mat_gold = make_pbr_mat("M_Goddess_Gold", (0.98, 0.78, 0.20, 1.0), metallic=0.96, roughness=0.18)
    mat_crimson = make_pbr_mat("M_Goddess_Crimson", (0.65, 0.04, 0.08, 1.0), metallic=0.02, roughness=0.65)
    mat_skin = make_pbr_mat("M_Goddess_Skin", (0.76, 0.54, 0.40, 1.0), metallic=0.0, roughness=0.50)
    mat_ruby = make_pbr_mat("M_Goddess_Ruby", (0.88, 0.02, 0.08, 1.0), metallic=0.2, roughness=0.10)
    mat_emerald = make_pbr_mat("M_Goddess_Emerald", (0.02, 0.65, 0.25, 1.0), metallic=0.2, roughness=0.10)
    
    if shiva_head:
        shiva_head.data.materials.clear()
        shiva_head.data.materials.append(mat_skin)
    
    quinn_mesh.data.materials.clear()
    quinn_mesh.data.materials.append(mat_crimson)
    
    custom_pieces = [shiva_head] if shiva_head else []
    
    # 1. PRABHAVALI HALO (Radiating 16-ray celestial sunburst arch behind head)
    bpy.ops.mesh.primitive_torus_add(major_radius=28.0, minor_radius=1.6, location=(0.0, 6.0, 168.0), rotation=(math.radians(90), 0, 0))
    halo_ring = bpy.context.active_object
    halo_ring.data.materials.append(mat_gold)
    custom_pieces.append(halo_ring)
    
    for ray_i in range(16):
        angle = ray_i * (math.pi / 8.0)
        rx = 30.0 * math.cos(angle)
        rz = 168.0 + (30.0 * math.sin(angle))
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=1.6, radius2=0.2, depth=7.0, location=(rx, 6.0, rz), rotation=(math.radians(90), 0, -angle + math.radians(90)))
        ray = bpy.context.active_object
        ray.data.materials.append(mat_gold)
        custom_pieces.append(ray)
        
    # 2. KIRITAMUKUTA (Tiered Temple Crown)
    for tier in range(3):
        cz = 176.0 + (tier * 5.5)
        crad = 13.5 - (tier * 2.5)
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=crad, depth=5.0, location=(0.0, -2.5, cz))
        c_tier = bpy.context.active_object
        c_tier.data.materials.append(mat_gold)
        custom_pieces.append(c_tier)
        
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=1.6, depth=1.2, location=(0.0, -2.5 - crad, cz), rotation=(math.radians(90), 0, 0))
        gem = bpy.context.active_object
        gem.data.materials.append(mat_ruby if tier % 2 == 0 else mat_emerald)
        custom_pieces.append(gem)
        
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=2.2, radius2=0.4, depth=9.0, location=(0.0, -2.5, 196.0))
    finial = bpy.context.active_object
    finial.data.materials.append(mat_gold)
    custom_pieces.append(finial)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=1.8, depth=0.6, location=(0.0, -15.5, 168.0), rotation=(math.radians(90), 0, 0))
    tikka = bpy.context.active_object
    tikka.data.materials.append(mat_ruby)
    custom_pieces.append(tikka)
    
    for ear_side, ex in [("L", 10.5), ("R", -10.5)]:
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=2.0, radius2=0.5, depth=3.8, location=(ex, -2.5, 160.0), rotation=(math.radians(180), 0, 0))
        jhumka = bpy.context.active_object
        jhumka.data.materials.append(mat_gold)
        custom_pieces.append(jhumka)
        
    # 3. SWARNA KAVACHA (Golden Lotus Cuirass over chest)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=15.5, depth=24.0, location=(0.0, -1.0, 126.0))
    kavacha = bpy.context.active_object
    kavacha.scale = (1.04, 0.82, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    kavacha.data.materials.append(mat_gold)
    custom_pieces.append(kavacha)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=5.0, depth=1.5, location=(0.0, -14.0, 128.0), rotation=(math.radians(90), 0, 0))
    lotus = bpy.context.active_object
    lotus.data.materials.append(mat_gold)
    custom_pieces.append(lotus)
    
    # 4. TEMPLE JEWELRY
    for arm_side, ax in [("L", 22.0), ("R", -22.0)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=5.8, minor_radius=0.9, location=(ax, -2.0, 132.0))
        baju = bpy.context.active_object
        baju.data.materials.append(mat_gold)
        custom_pieces.append(baju)
        
        for kz in [102.0, 99.0]:
            bpy.ops.mesh.primitive_torus_add(major_radius=4.2, minor_radius=0.7, location=(ax * 1.5, -4.0, kz))
            kada = bpy.context.active_object
            kada.data.materials.append(mat_gold)
            custom_pieces.append(kada)
            
    # 5. ODDIYANAM WAIST BELT & PLEATED KACHHA DRAPE
    bpy.ops.mesh.primitive_torus_add(major_radius=15.5, minor_radius=1.8, location=(0.0, -0.5, 96.0))
    belt = bpy.context.active_object
    belt.scale = (1.05, 0.85, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    belt.data.materials.append(mat_gold)
    custom_pieces.append(belt)
    
    bpy.ops.mesh.primitive_cube_add(size=10.0, location=(0.0, -13.5, 68.0))
    pleats = bpy.context.active_object
    pleats.scale = (1.1, 0.15, 3.2)
    bpy.ops.object.transform_apply(scale=True)
    pleats.data.materials.append(mat_crimson)
    custom_pieces.append(pleats)
    
    bpy.ops.mesh.primitive_cube_add(size=10.0, location=(0.0, -13.7, 52.0))
    zari = bpy.context.active_object
    zari.scale = (1.12, 0.17, 0.5)
    bpy.ops.object.transform_apply(scale=True)
    zari.data.materials.append(mat_gold)
    custom_pieces.append(zari)
    
    for leg_side, lx in [("L", 11.0), ("R", -11.0)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=4.8, minor_radius=0.8, location=(lx, -0.5, 14.0))
        ghungroo = bpy.context.active_object
        ghungroo.data.materials.append(mat_gold)
        custom_pieces.append(ghungroo)
        
    all_goddess = [quinn_mesh] + custom_pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_goddess:
        p.select_set(True)
    bpy.context.view_layer.objects.active = all_goddess[0]
    bpy.ops.object.join()
    
    master_goddess = bpy.context.active_object
    master_goddess.name = "SKM_IndianGoddess_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    prev_path = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\preview_indiangoddess.png"
    setup_camera_and_render(prev_path)
    
    # Target skeleton is SK_CombatMannequin (centimeter scale)
    dummy_m = bpy.data.objects.new("DummyM", None)
    bpy.context.scene.collection.objects.link(dummy_m)
    bpy.context.view_layer.objects.active = dummy_m
    manny_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
    bpy.ops.import_scene.fbx(filepath=manny_fbx)
    bpy.data.objects.remove(dummy_m, do_unlink=True)
    
    manny_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    manny_mesh = [o for o in bpy.data.objects if o.type == 'MESH' and "LOD0" in o.name and "CombatMannequin" in o.name][0]
    
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_IndianGoddess.fbx"
    skin_and_export(master_goddess, manny_arm, manny_mesh, out_fbx)
    return {"status": "Indian Goddess Complete", "fbx": out_fbx, "preview": prev_path}


# =========================================================================
# 6. GIRL WARRIOR (VALKYRIE / AMAZON CHAMPION)
# =========================================================================
def build_girl_warrior():
    print("\n================== BUILDING 6/6: GIRL WARRIOR (VALKYRIE) ==================")
    dummy = reset_scene()
    
    quinn_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_Quinn.fbx"
    bpy.ops.import_scene.fbx(filepath=quinn_fbx)
    bpy.data.objects.remove(dummy, do_unlink=True)
    
    quinn_mesh = [o for o in bpy.data.objects if o.type == 'MESH' and "LOD0" in o.name][0]
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o != quinn_mesh and "Quinn" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'ARMATURE':
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Unparent Quinn so its coordinates are in true centimeters (0 to 180 cm)
    quinn_mesh.parent = None
    quinn_mesh.matrix_world = Matrix.Identity(4)
    bpy.context.view_layer.objects.active = quinn_mesh
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    mat_silver = make_pbr_mat("M_Valkyrie_Silver", (0.86, 0.88, 0.90, 1.0), metallic=0.96, roughness=0.18)
    mat_sapphire = make_pbr_mat("M_Valkyrie_Sapphire", (0.08, 0.35, 0.85, 1.0), metallic=0.2, roughness=0.10)
    mat_leather = make_pbr_mat("M_Valkyrie_Leather", (0.24, 0.14, 0.08, 1.0), metallic=0.04, roughness=0.70)
    mat_cape = make_pbr_mat("M_Valkyrie_Cape", (0.12, 0.08, 0.28, 1.0), metallic=0.02, roughness=0.75)
    mat_gold = make_pbr_mat("M_Valkyrie_GoldTrim", (0.92, 0.75, 0.25, 1.0), metallic=0.92, roughness=0.25)
    
    quinn_mesh.data.materials.clear()
    quinn_mesh.data.materials.append(mat_leather)
    
    custom_pieces = [quinn_mesh]
    
    # 1. WINGED VALKYRIE TIARA / CIRCLET
    bpy.ops.mesh.primitive_torus_add(major_radius=14.5, minor_radius=1.2, location=(0.0, -2.0, 172.0))
    circlet = bpy.context.active_object
    circlet.scale = (1.02, 1.14, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    circlet.data.materials.append(mat_silver)
    custom_pieces.append(circlet)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=2.2, depth=1.0, location=(0.0, -16.5, 173.0), rotation=(math.radians(90), 0, 0))
    gem = bpy.context.active_object
    gem.data.materials.append(mat_sapphire)
    custom_pieces.append(gem)
    
    for wing_side, wx, wrot in [("L", 14.5, math.radians(-25)), ("R", -14.5, math.radians(25))]:
        for feather_i in range(3):
            fz = 175.0 + (feather_i * 6.5)
            fy = -2.0 - (feather_i * 4.5)
            bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=2.8 - (feather_i * 0.4), radius2=0.4, depth=16.0, location=(wx, fy, fz), rotation=(math.radians(-40 - (feather_i * 8)), wrot, 0))
            feather = bpy.context.active_object
            feather.scale = (0.35, 1.0, 1.0)
            bpy.ops.object.transform_apply(scale=True)
            feather.data.materials.append(mat_silver if feather_i % 2 == 0 else mat_gold)
            custom_pieces.append(feather)
            
    # High Warrior Ponytail
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=3.5, radius2=0.8, depth=28.0, location=(0.0, 12.0, 168.0), rotation=(math.radians(-65), 0, 0))
    tail = bpy.context.active_object
    tail.scale = (0.8, 1.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    tail.data.materials.append(mat_leather)
    custom_pieces.append(tail)
    
    # 2. SCULPTED FORM-FITTED TITANIUM BREASTPLATE
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=15.5, depth=24.0, location=(0.0, -1.0, 126.0))
    breastplate = bpy.context.active_object
    breastplate.scale = (1.04, 0.82, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    breastplate.data.materials.append(mat_silver)
    custom_pieces.append(breastplate)
    
    for wing_s, ex in [("L", 7.0), ("R", -7.0)]:
        bpy.ops.mesh.primitive_cube_add(size=6.0, location=(ex, -14.0, 128.0))
        wing_plate = bpy.context.active_object
        wing_plate.scale = (1.2, 0.12, 1.5)
        wing_plate.rotation_euler = (0, 0, math.radians(25 if wing_s=="L" else -25))
        bpy.ops.object.transform_apply(rotation=True, scale=True)
        wing_plate.data.materials.append(mat_gold)
        custom_pieces.append(wing_plate)
        
    # 3. FALCON-WING PAULDRONS & VAMBRACES
    for p_side, px in [("L", 24.0), ("R", -24.0)]:
        for tier in range(3):
            pz = 142.0 - (tier * 4.5)
            bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=7.0 - (tier * 0.8), depth=4.0, location=(px, -1.5, pz))
            pauldron = bpy.context.active_object
            pauldron.scale = (1.1, 1.25, 1.0)
            bpy.ops.object.transform_apply(scale=True)
            pauldron.data.materials.append(mat_silver if tier % 2 == 0 else mat_gold)
            custom_pieces.append(pauldron)
            
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=5.0, depth=18.0, location=(px * 1.35, -3.0, 108.0))
        vambrace = bpy.context.active_object
        vambrace.data.materials.append(mat_silver)
        custom_pieces.append(vambrace)
        
    # 4. LAYERED LEATHER TASSET BATTLE SKIRT
    bpy.ops.mesh.primitive_torus_add(major_radius=15.5, minor_radius=1.6, location=(0.0, -0.5, 96.0))
    belt = bpy.context.active_object
    belt.scale = (1.05, 0.85, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    belt.data.materials.append(mat_gold)
    custom_pieces.append(belt)
    
    for t_side, tx, ty in [("FL", 9.5, -11.5), ("FR", -9.5, -11.5), ("SL", 15.0, -1.5), ("SR", -15.0, -1.5)]:
        bpy.ops.mesh.primitive_cube_add(size=8.0, location=(tx, ty, 84.0))
        tasset = bpy.context.active_object
        tasset.scale = (1.1, 0.16, 2.5)
        bpy.ops.object.transform_apply(scale=True)
        tasset.data.materials.append(mat_leather)
        custom_pieces.append(tasset)
        
    # 5. WINGED GREAVES & BOOTS
    for leg_s, lx in [("L", 11.0), ("R", -11.0)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=6.2, depth=26.0, location=(lx, -1.0, 32.0))
        greave = bpy.context.active_object
        greave.scale = (0.95, 1.15, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        greave.data.materials.append(mat_silver)
        custom_pieces.append(greave)
        
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.8, radius2=0.3, depth=10.0, location=(lx * 1.35, 2.0, 18.0), rotation=(math.radians(35), 0, 0))
        flair = bpy.context.active_object
        flair.data.materials.append(mat_gold)
        custom_pieces.append(flair)
        
    # 6. BATTLE CAPELET
    bpy.ops.mesh.primitive_cube_add(size=12.0, location=(0.0, 14.0, 115.0))
    cape = bpy.context.active_object
    cape.scale = (2.0, 0.12, 4.0)
    cape.rotation_euler = (math.radians(-10), 0, 0)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    cape.data.materials.append(mat_cape)
    custom_pieces.append(cape)
    
    all_valkyrie = custom_pieces
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_valkyrie:
        p.select_set(True)
    bpy.context.view_layer.objects.active = all_valkyrie[0]
    bpy.ops.object.join()
    
    master_valkyrie = bpy.context.active_object
    master_valkyrie.name = "SKM_GirlWarrior_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    prev_path = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\preview_girlwarrior.png"
    setup_camera_and_render(prev_path)
    
    dummy_m = bpy.data.objects.new("DummyM", None)
    bpy.context.scene.collection.objects.link(dummy_m)
    bpy.context.view_layer.objects.active = dummy_m
    manny_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\SKM_CombatMannequin.fbx"
    bpy.ops.import_scene.fbx(filepath=manny_fbx)
    bpy.data.objects.remove(dummy_m, do_unlink=True)
    
    manny_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    manny_mesh = [o for o in bpy.data.objects if o.type == 'MESH' and "LOD0" in o.name and "CombatMannequin" in o.name][0]
    
    out_fbx = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Characters\Builds\SKM_GirlWarrior.fbx"
    skin_and_export(master_valkyrie, manny_arm, manny_mesh, out_fbx)
    return {"status": "Girl Warrior Complete", "fbx": out_fbx, "preview": prev_path}


# =========================================================================
# MASTER BATCH RUNNER
# =========================================================================
def build_all():
    print("="*60)
    print("STARTING FULL PROCEDURAL BUILD OF ALL 6 CHARACTERS")
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
