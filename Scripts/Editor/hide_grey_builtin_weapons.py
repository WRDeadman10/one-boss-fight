"""Greystone ships with a sword, shield and some fur baked into material slot 3 (M03_SwordShieldFur). The pack's own weapons are attached at runtime, so the built-in
ones show twice. Creates M_GreyHiddenSlot (masked, opacity 0) and uses it as the override for slot 3 on BP_GreystonePlayer's mesh."""
import traceback
import unreal

try:
    DIR = "/Game/OneBossFight/GreystonePack"
    path = DIR + "/M_GreyHiddenSlot"
    mat = unreal.load_asset(path)
    if mat is None:
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_GreyHiddenSlot", DIR, unreal.Material, unreal.MaterialFactoryNew())
        mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
        zero = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 0)
        zero.set_editor_property("r", 0.0)
        unreal.MaterialEditingLibrary.connect_material_property(zero, "", unreal.MaterialProperty.MP_OPACITY_MASK)
        unreal.MaterialEditingLibrary.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
    bp = unreal.load_asset(DIR + "/BP_GreystonePlayer")
    cdo = unreal.get_default_object(bp.generated_class())
    mesh = cdo.get_editor_property("mesh")
    slots = [None, None, None, mat]
    mesh.set_editor_property("override_materials", slots)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    print("[Hide] slot 3 hidden: %s" % [x.get_name() if x else None for x in mesh.get_editor_property("override_materials")])
except Exception:
    print("[Hide] " + traceback.format_exc())
