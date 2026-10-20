"""Loads every retargeted animation Blueprint of GreystonePack and reports whether it compiled and its parent."""
import unreal
log = lambda m: unreal.log("[GreyLayers] " + m)
reg = unreal.AssetRegistryHelpers.get_asset_registry()
for a in reg.get_assets_by_path("/Game/OneBossFight/GreystonePack", recursive=True):
    if str(a.asset_class_path.asset_name) != "AnimBlueprint":
        continue
    bp = a.get_asset()
    gc = bp.generated_class() if bp else None
    try:
        status = unreal.BlueprintEditorLibrary.get_blueprint_status(bp) if hasattr(unreal.BlueprintEditorLibrary, "get_blueprint_status") else "?"
    except Exception:
        status = "?"
    log("%s generated=%s parent=%s" % (a.asset_name, gc.get_name() if gc else None, gc.get_super_class().get_name() if gc and hasattr(gc, "get_super_class") else "?"))
