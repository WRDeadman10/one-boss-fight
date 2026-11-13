"""BQ-46..49 (Queue BQ batch 10; B2): repoint the Greystone child's dodge montages to the _RM roll copies.

Context: C-1289 left the Greystone quick roll at 0.00 cm (pelvis-baked travel, C-1285). BK-1's
retarget_greystone_pack_rolls_rm.py --write creates root-motion copies under
/Game/OneBossFight/Player/Greystone/RootMotion/Montages/{quick,full}/<name>_RM. This script is the next step: it
points BP_GreystoneERPlayer's URPGDodgeTiming QuickMontage / FullMontage at those copies, so the RM4 driver
(pie_greystone_root_motion.py, which reads the child's montage names) measures the _RM rolls.

Default: read-only DRY RUN (prints the current and planned values, writes nothing). Pass -RMRepointWrite on the Editor
command line to write. Write mode refuses unless BOTH _RM montages exist and are AnimMontages (their root-motion travel
is proven by the BK-1 manifest and RM4, not re-checked here), and the child still points at the expected _Grey montages (or already at the _RM ones: idempotent no-op). It changes
only those two fields on the child Blueprint, compiles, saves, reloads and reads back. It never edits the _Grey assets,
the pack, the parent Blueprint, or deletes anything. Rollback = run the inverse (set the two _Grey paths) by hand,
recorded in the receipt line. Run only in the full Editor under the C-1155 lock (ENG).
"""
import traceback

PREFIX = "[GreystoneRMRepoint] "
WRITE_TOKEN = "-RMRepointWrite"
CHILD_PATH = "/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer"
RM_ROOT = "/Game/OneBossFight/Player/Greystone/RootMotion"

# Field -> (current _Grey montage, _RM copy). The _RM paths follow retarget_greystone_pack_rolls_rm.py:
# OUT_ROOT + "/Montages/" + kind + "/" + <grey montage name> + "_RM" (the contract test pins this derivation).
REPOINTS = {
    "QuickMontage": (
        "/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey",
        RM_ROOT + "/Montages/quick/Dodge_Small_Forward_Roll_Montage_Grey_RM",
    ),
    "FullMontage": (
        "/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage_Grey",
        RM_ROOT + "/Montages/full/Dodge_To_Idle_Montage_Grey_RM",
    ),
}


def plan(current_by_field):
    """Pure decision per field: 'repoint', 'already' (idempotent) or 'refuse' (unexpected current value, never overwritten)."""
    decisions = {}
    for field, (grey, rm) in REPOINTS.items():
        current = current_by_field.get(field)
        if current == rm:
            decisions[field] = "already"
        elif current == grey:
            decisions[field] = "repoint"
        else:
            decisions[field] = "refuse"
    return decisions


def python_name(field):
    """C++ UPROPERTY name -> the snake_case name UE Python documents for get/set_editor_property (QuickMontage -> quick_montage)."""
    out = []
    for i, ch in enumerate(field):
        if ch.isupper() and i:
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


def package_path(obj):
    return str(obj.get_path_name()).split(".", 1)[0] if obj is not None else None


def main():
    import unreal  # Editor only; the static contract imports this module without Unreal

    def log(message):
        unreal.log(PREFIX + message)

    def require(condition, message):
        if not condition:
            raise RuntimeError(message)

    write = WRITE_TOKEN in unreal.SystemLibrary.get_command_line().split()
    eal = unreal.EditorAssetLibrary
    bp = unreal.load_asset(CHILD_PATH)
    require(bp is not None, "child Blueprint missing: " + CHILD_PATH)
    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    lib = unreal.SubobjectDataBlueprintFunctionLibrary
    timing = None
    for handle in list(subsystem.k2_gather_subobject_data_for_blueprint(bp)):
        component = lib.get_object(lib.get_data(handle))
        if component is not None and component.get_class().get_name() == "RPGDodgeTiming":
            require(timing is None, "child has more than one URPGDodgeTiming; refusing")
            timing = component
    require(timing is not None, "child has no URPGDodgeTiming component")

    current = {field: package_path(timing.get_editor_property(python_name(field))) for field in REPOINTS}
    decisions = plan(current)
    for field, (grey, rm) in REPOINTS.items():
        log("PLAN field=%s current=%s target=%s decision=%s" % (field, current[field], rm, decisions[field]))
    require("refuse" not in decisions.values(), "unexpected current montage; refusing to overwrite: %r" % current)

    rm_assets = {}
    for field, (_, rm) in REPOINTS.items():
        asset = unreal.load_asset(rm) if eal.does_asset_exist(rm) else None
        exists = asset is not None and asset.get_class().get_name() == "AnimMontage"
        # Root-motion travel is proven by the BK-1 retarget manifest (nonzero output displacement) and by RM4; it is not
        # re-derived here, to avoid guessing a reflected montage flag name.
        log("RM_ASSET field=%s path=%s exists=%d anim_montage=%d" % (field, rm, int(asset is not None), int(exists)))
        rm_assets[field] = asset if exists else None

    if not write:
        log("RESULT=DRY_RUN would_repoint=%d already=%d saves=0" %
            (sum(d == "repoint" for d in decisions.values()), sum(d == "already" for d in decisions.values())))
        return
    require(all(rm_assets.values()), "an _RM montage is missing or not an AnimMontage; run the BK-1 retarget --write first")
    if all(d == "already" for d in decisions.values()):
        log("RESULT=PASS repointed=0 already=2 saves=0")
        return
    for field, decision in decisions.items():
        if decision == "repoint":
            timing.set_editor_property(python_name(field), rm_assets[field])
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    require(eal.save_loaded_asset(bp), "failed to save the child Blueprint")
    loading = getattr(unreal, "EditorLoadingAndSavingUtils", None)
    reload_modes = getattr(unreal, "ReloadPackagesInteractionMode", None)
    require(loading is not None and reload_modes is not None and hasattr(loading, "reload_packages"),
            "UE package reload API is unavailable; saved readback cannot be proven")
    reload_mode = getattr(reload_modes, "ASSUME_POSITIVE", None)
    require(reload_mode is not None, "non-interactive package reload mode is unavailable")
    reload_result = loading.reload_packages([bp.get_outermost()], reload_mode)
    reload_ok = bool(reload_result[0]) if isinstance(reload_result, tuple) else bool(reload_result)
    reload_error = str(reload_result[1]) if isinstance(reload_result, tuple) and len(reload_result) > 1 else ""
    require(reload_ok, "saved child package reload failed: " + reload_error)
    reloaded = unreal.load_asset(CHILD_PATH)
    readback = None
    for handle in list(subsystem.k2_gather_subobject_data_for_blueprint(reloaded)):
        component = lib.get_object(lib.get_data(handle))
        if component is not None and component.get_class().get_name() == "RPGDodgeTiming":
            readback = component
    require(readback is not None, "reloaded child lost its URPGDodgeTiming")
    for field, (grey, rm) in REPOINTS.items():
        actual = package_path(readback.get_editor_property(python_name(field)))
        require(actual == rm, "readback mismatch for %s: %s" % (field, actual))
        log("READBACK field=%s asset=%s rollback_to=%s" % (field, actual, grey))
    log("RESULT=PASS repointed=%d saves=1" % sum(d == "repoint" for d in decisions.values()))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import unreal
        unreal.log_error(PREFIX + "RESULT=FAIL " + str(error))
        unreal.log_error(traceback.format_exc())
