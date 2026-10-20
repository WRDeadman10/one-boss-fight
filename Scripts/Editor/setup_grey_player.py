"""Gives BP_GreystonePlayer Greystone's mesh and the retargeted pack animation Blueprint. Run in the editor."""
import unreal

log = lambda m: unreal.log("[GreyPlayer] " + m)
bp = unreal.load_asset("/Game/OneBossFight/GreystonePack/BP_GreystonePlayer")
parent_bp = unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter")
pm = unreal.get_default_object(parent_bp.generated_class()).get_editor_property("mesh")
log("parent mesh: %s anim %s loc %s rot %s" % (pm.get_editor_property("skeletal_mesh_asset"), pm.get_editor_property("anim_class"), pm.get_editor_property("relative_location"), pm.get_editor_property("relative_rotation")))
cdo = unreal.get_default_object(bp.generated_class())
mesh = cdo.get_editor_property("mesh")
mesh.set_editor_property("skeletal_mesh_asset", unreal.load_asset("/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone"))
mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
mesh.set_editor_property("anim_class", unreal.load_object(None, "/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/ABP_CombatCharacter_Grey.ABP_CombatCharacter_Grey_C"))
log("child mesh set: %s anim %s" % (mesh.get_editor_property("skeletal_mesh_asset").get_name(), mesh.get_editor_property("anim_class").get_name()))
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
log("saved")
