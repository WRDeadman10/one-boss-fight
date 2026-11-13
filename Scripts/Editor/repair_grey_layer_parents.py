"""BQ-56 (Queue BQ batch 12; B8, KI-040): guarded repair of the Greystone layer AnimBlueprints' missing parent.

The retargeted layer ABPs were saved with their parent at /Game/ABP_CombatAnimLayersBase_Grey (the base's old location),
so they log "CreateExport: Failed to load". The real base is REAL below. The older fix_grey_layers_1/2.py scripts repair
this but have no dry run, re-parent EVERY AnimBlueprint under GreystonePack without checking its parent, and delete the
temporary copy; this script replaces them with a closed, verified procedure. Do not run the old scripts.

Default: read-only DRY RUN. It reads each layer's ParentClass from the asset registry (no load needed) and prints the plan.
Write needs -GreyLayerRepairWrite on the Editor command line and then:
  1. only if a layer still names the stale parent: duplicate REAL to STALE so those layers can load (logged as TEMP_CREATED);
  2. re-parent ONLY the layers in LAYERS whose registry parent is STALE (never REAL-parented ones, never other ABPs);
  3. compile each, refuse to save one whose compile status reports an error, save, reload, and read the parent back;
  4. delete the temporary copy only if it was created by this run AND nothing references it (else it stays, logged).
Never touches the base, ABP_CombatCharacter_Grey, the pack originals, or any other asset. Run under C-1155 (ENG).
"""
import traceback

PREFIX = "[GreyLayerRepair] "
WRITE_TOKEN = "-GreyLayerRepairWrite"
REAL = "/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/LinkedLayers/ABP_CombatAnimLayersBase_Grey"
STALE = "/Game/ABP_CombatAnimLayersBase_Grey"
GP = "/Game/OneBossFight/GreystonePack"
# Closed list: the layer ABPs found on disk (KI-040 names four of them, "and others").
LAYERS = (
    GP + "/Characters/Heroes/Mannequins/Animations/LinkedLayers/ABP_UnarmedLayer_Grey",
    GP + "/MagicCombatSystem/Blueprints/Animation/ABP_MagicStaffLayer_Grey",
    GP + "/MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_2HandedSwordLayer_Grey",
    GP + "/MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_DualSwordLayer_Grey",
    GP + "/MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_SwordLayer_Grey",
    GP + "/MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_SwordnShieldLayer_Grey",
    GP + "/MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_TwinbladeLayer_Grey",
    GP + "/MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_UnarmednShieldLayer_Grey",
)


def classify(parent_tag):
    """Pure: registry ParentClass tag -> 'stale' (needs repair), 'ok' (already the real base) or 'unknown' (left alone)."""
    # The tag looks like "/Script/Engine.AnimBlueprintGeneratedClass'/Game/ABP_CombatAnimLayersBase_Grey.ABP_..._C'".
    # STALE ("/Game/ABP_...") is never a substring of REAL ("/Game/OneBossFight/.../ABP_..."), so the checks are disjoint.
    text = str(parent_tag or "")
    if REAL + "." in text:
        return "ok"
    if STALE + "." in text:
        return "stale"
    return "unknown"


def main():
    import unreal  # Editor only

    def log(message):
        unreal.log(PREFIX + message)

    def require(condition, message):
        if not condition:
            raise RuntimeError(message)

    write = WRITE_TOKEN in unreal.SystemLibrary.get_command_line().split()
    eal = unreal.EditorAssetLibrary
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    require(eal.does_asset_exist(REAL), "real base is missing: " + REAL)

    plan = {}
    for path in LAYERS:
        data = registry.get_asset_by_object_path(path + "." + path.rsplit("/", 1)[-1])
        parent = data.get_tag_value("ParentClass") if data and data.is_valid() else None
        plan[path] = classify(parent)
        log("PLAN layer=%s parent=%s decision=%s" % (path, parent, plan[path]))
    stale = [p for p, d in plan.items() if d == "stale"]
    if not write:
        log("RESULT=DRY_RUN stale=%d ok=%d unknown=%d saves=0" %
            (len(stale), sum(d == "ok" for d in plan.values()), sum(d == "unknown" for d in plan.values())))
        return
    if not stale:
        log("RESULT=PASS repaired=0 saves=0 (nothing names the stale parent)")
        return

    created_temp = False
    if not eal.does_asset_exist(STALE):
        copy = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(STALE.rsplit("/", 1)[-1], "/Game", unreal.load_asset(REAL))
        require(copy is not None and eal.save_loaded_asset(copy), "could not create the temporary parent copy at " + STALE)
        created_temp = True
        log("TEMP_CREATED path=%s" % STALE)
    real_class = unreal.load_asset(REAL).generated_class()
    repaired = []
    for path in stale:
        bp = unreal.load_asset(path)
        require(bp is not None, "layer still fails to load: " + path)
        require(unreal.BlueprintEditorLibrary.reparent_blueprint(bp, real_class), "reparent refused: " + path)
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        status = str(bp.get_editor_property("status"))
        require("ERROR" not in status.upper(), "compile error after reparent, not saved: %s (%s)" % (path, status))
        require(eal.save_loaded_asset(bp), "save failed: " + path)
        repaired.append(path)
        log("REPARENTED layer=%s status=%s" % (path, status))
    loading = getattr(unreal, "EditorLoadingAndSavingUtils", None)
    reload_modes = getattr(unreal, "ReloadPackagesInteractionMode", None)
    require(loading is not None and reload_modes is not None and hasattr(loading, "reload_packages"),
            "UE package reload API is unavailable; refusing to claim saved readback")
    reload_mode = getattr(reload_modes, "ASSUME_POSITIVE", None)
    require(reload_mode is not None, "non-interactive package reload mode is unavailable")
    for path in repaired:
        saved_asset = unreal.load_asset(path)
        require(saved_asset is not None, "saved layer could not be loaded for package reload: " + path)
        reload_result = loading.reload_packages([saved_asset.get_outermost()], reload_mode)
        reload_ok = bool(reload_result[0]) if isinstance(reload_result, tuple) else bool(reload_result)
        reload_error = str(reload_result[1]) if isinstance(reload_result, tuple) and len(reload_result) > 1 else ""
        require(reload_ok, "saved layer package reload failed: %s %s" % (path, reload_error))
        reloaded = unreal.load_asset(path)
        require(reloaded is not None, "layer failed to load after package reload: " + path)
        data = registry.get_asset_by_object_path(path + "." + path.rsplit("/", 1)[-1])
        require(data is not None and data.is_valid() and classify(data.get_tag_value("ParentClass")) == "ok",
                "readback: parent is not the real base: " + path)
        log("READBACK layer=%s parent=real" % path)
    if created_temp:
        referencers = list(eal.find_package_referencers_for_asset(STALE, False))
        if referencers:
            log("TEMP_KEPT path=%s referencers=%s" % (STALE, [str(r) for r in referencers]))
        else:
            removed = bool(eal.delete_asset(STALE))
            log("TEMP_REMOVED path=%s ok=%s" % (STALE, removed))
            require(removed, "temporary parent is unreferenced but could not be removed: " + STALE)
    log("RESULT=PASS repaired=%d saves=%d" % (len(repaired), len(repaired)))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import unreal
        unreal.log_error(PREFIX + "RESULT=FAIL " + str(error))
        unreal.log_error(traceback.format_exc())
