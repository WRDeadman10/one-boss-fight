"""
builder_common.py - Common utilities for procedural character generation in Blender.
"""

import bpy
import math
import os
from mathutils import Vector, Euler, Matrix

def reset_scene_with_dummy():
    """Clears all objects while ensuring Blender context remains valid for FBX operators."""
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    for arm in list(bpy.data.armatures):
        bpy.data.armatures.remove(arm, do_unlink=True)
        
    dummy = bpy.data.objects.new("DummyContext", None)
    bpy.context.scene.collection.objects.link(dummy)
    bpy.context.view_layer.objects.active = dummy
    return dummy

def load_base_model(fbx_path):
    """Imports the base FBX mannequin and removes the dummy object."""
    dummy = reset_scene_with_dummy()
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    if dummy.name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[dummy.name], do_unlink=True)
        
    arm = None
    base_mesh = None
    for o in bpy.data.objects:
        if o.type == 'ARMATURE' and not arm:
            arm = o
        elif o.type == 'MESH':
            if "LOD0" in o.name:
                base_mesh = o
            elif "LOD" in o.name:
                bpy.data.objects.remove(o, do_unlink=True)
                
    if not base_mesh:
        meshes = [o for o in bpy.data.objects if o.type == 'MESH']
        if meshes:
            base_mesh = meshes[0]
            
    return arm, base_mesh

def create_pbr_material(name, base_color=(0.8, 0.8, 0.8, 1.0), metallic=0.0, roughness=0.5, specular=0.5, emissive=(0,0,0,1)):
    """Creates a Principled BSDF material with given PBR properties."""
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        output = nodes.get("Material Output")
        mat.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
        
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = specular
    elif "Specular" in bsdf.inputs:
        bsdf.inputs["Specular"].default_value = specular
        
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = emissive
    elif "Emission" in bsdf.inputs:
        bsdf.inputs["Emission"].default_value = emissive
        
    return mat

def assign_material(obj, mat):
    """Assigns material to object, replacing or appending slot 0."""
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def assign_rigid_weight(obj, bone_name, weight=1.0):
    """Assigns all vertices of obj to a single bone vertex group."""
    vg = obj.vertex_groups.get(bone_name)
    if not vg:
        vg = obj.vertex_groups.new(name=bone_name)
    vert_indices = [v.index for v in obj.data.vertices]
    if vert_indices:
        vg.add(vert_indices, weight, 'REPLACE')

def assign_weighted_bones(obj, weights_dict):
    """Assigns specific weights to multiple bone vertex groups (e.g. {'spine_02': 0.5, 'spine_03': 0.5})."""
    vert_indices = [v.index for v in obj.data.vertices]
    for bone_name, weight in weights_dict.items():
        vg = obj.vertex_groups.get(bone_name)
        if not vg:
            vg = obj.vertex_groups.new(name=bone_name)
        if vert_indices:
            vg.add(vert_indices, weight, 'REPLACE')

def bind_to_armature(obj, arm, use_auto_weights=False, source_mesh=None):
    """Parents object to armature with Armature modifier and skinning."""
    obj.parent = arm
    mod = obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    
    if use_auto_weights:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    elif source_mesh:
        dt = obj.modifiers.new(name="DataTransfer", type='DATA_TRANSFER')
        dt.object = source_mesh
        dt.use_vert_data = True
        dt.data_types_verts = {'VGROUP_WEIGHTS'}
        dt.vert_mapping = 'POLYINTERP_NEAREST'
        bpy.context.view_layer.objects.active = obj
        try:
            bpy.ops.object.datalayout_transfer(modifier="DataTransfer")
            bpy.ops.object.modifier_apply(modifier="DataTransfer")
        except Exception as e:
            print("DataTransfer fallback:", e)

def export_fbx(output_path):
    """Exports all meshes and armatures to FBX with optimal UE5 settings."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    bpy.ops.export_scene.fbx(
        filepath=output_path,
        use_selection=False,
        object_types={'ARMATURE', 'MESH'},
        use_armature_deform_only=True,
        add_leaf_bones=False,
        mesh_smooth_type='FACE',
        bake_anim=False
    )
    print(f"Exported to {output_path}, size={os.path.getsize(output_path)} bytes")
