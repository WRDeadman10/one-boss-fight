"""Greystone layer repair, step 2: re-parent every layer ABP to the real retargeted base, compile and save, then remove the temporary copy at /Game
when nothing references it any more."""
import unreal
log = lambda m: unreal.log("[GreyFix2] " + m)
REAL = "/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/LinkedLayers/ABP_CombatAnimLayersBase_Grey"
TEMP = "/Game/ABP_CombatAnimLayersBase_Grey"
real = unreal.load_asset(REAL)
real_cls = real.generated_class()
reg = unreal.AssetRegistryHelpers.get_asset_registry()
for a in reg.get_assets_by_path("/Game/OneBossFight/GreystonePack", recursive=True):
    name = str(a.asset_name)
    if str(a.asset_class_path.asset_name) != "AnimBlueprint" or name in ("ABP_CombatAnimLayersBase_Grey", "ABP_CombatCharacter_Grey"):
        continue
    bp = a.get_asset()
    ok = unreal.BlueprintEditorLibrary.reparent_blueprint(bp, real_cls)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    log("%s reparent=%s" % (name, ok))
refs = unreal.EditorAssetLibrary.find_package_referencers_for_asset(TEMP, False)
log("referencers of the temporary copy: %s" % [str(r) for r in refs])
if not refs:
    log("delete temporary copy: %s" % unreal.EditorAssetLibrary.delete_asset(TEMP))
