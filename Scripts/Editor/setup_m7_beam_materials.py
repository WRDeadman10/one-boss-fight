"""
The Niagara Energy Beam Pack as downloaded lacks four materials that NS_Thunder_Beam7 references
(/Game/BeamPack/Materials/M_Dirt, M_Dirt_2, M_Mesh, M_Mesh_7), so its meshes and ribbon fall back to the grey default
material. This creates replacements under the same names: an additive emissive blue-white lightning material for the
mesh/ribbon parts and an invisible additive material for the dirt parts. Idempotent.

  UnrealEditor-Cmd.exe OneBossFight.uproject -run=pythonscript -script=Scripts/Editor/setup_m7_beam_materials.py -unattended -nullrhi
"""

import unreal

FOLDER = "/Game/BeamPack/Materials"
# name -> (emissive colour, additive intensity multiplier)
MATERIALS = {
    "M_Mesh": (unreal.LinearColor(0.35, 0.6, 1.0, 1.0), 12.0),
    "M_Mesh_7": (unreal.LinearColor(0.35, 0.6, 1.0, 1.0), 12.0),
    "M_Dirt": (unreal.LinearColor(0.0, 0.0, 0.0, 1.0), 0.0),
    "M_Dirt_2": (unreal.LinearColor(0.0, 0.0, 0.0, 1.0), 0.0),
}


def log(msg):
    unreal.log("[BeamMaterials] " + msg)


def build(name, color, intensity):
    path = FOLDER + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, FOLDER, unreal.Material, unreal.MaterialFactoryNew())
    material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
    material.set_editor_property("two_sided", True)
    for flag in ("used_with_niagara_mesh_particles", "used_with_niagara_ribbons", "used_with_niagara_sprites"):
        material.set_editor_property(flag, True)
    lib = unreal.MaterialEditingLibrary
    constant = lib.create_material_expression(material, unreal.MaterialExpressionConstant3Vector, -300, 0)
    constant.set_editor_property("constant", unreal.LinearColor(color.r * intensity, color.g * intensity, color.b * intensity, 1.0))
    lib.connect_material_property(constant, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    lib.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material, False)
    log("created %s" % path)


for material_name, (material_color, material_intensity) in MATERIALS.items():
    build(material_name, material_color, material_intensity)
