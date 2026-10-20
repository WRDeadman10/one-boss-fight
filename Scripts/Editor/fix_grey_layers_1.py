"""Greystone layer repair, step 1: the layer ABPs were saved with their parent at /Game/ABP_CombatAnimLayersBase_Grey (its location before it was moved),
so they cannot load. Put a temporary copy of the real base at that path so they load; step 2 re-parents them and removes the copy."""
import unreal
log = lambda m: unreal.log("[GreyFix1] " + m)
REAL = "/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/LinkedLayers/ABP_CombatAnimLayersBase_Grey"
if unreal.load_asset("/Game/ABP_CombatAnimLayersBase_Grey") is None:
    copy = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset("ABP_CombatAnimLayersBase_Grey", "/Game", unreal.load_asset(REAL))
    unreal.EditorAssetLibrary.save_loaded_asset(copy)
    log("temporary base copy created: %s" % copy)
else:
    log("temporary base copy already there")
