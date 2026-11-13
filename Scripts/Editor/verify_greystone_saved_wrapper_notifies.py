"""BQ-51 (Queue BQ batch 11; B5): read-only notify readback of the SAVED Greystone _Fit wrapper montages.

verify_greystone_wrapper_readback.py (C-1275a) proves the C++ wrapper copies notifies correctly into a TRANSIENT montage.
This script closes the B5 gap: it reads the four wrappers that author_greystone_player.py SAVED under
/Game/OneBossFight/Player/Greystone/ and compares their native notify rows (class, trigger, duration, track, slots, segment
path@length) against each source montage, through the same author helpers (source_readback, wrapper_notify_rows,
compare_wrapper_notify_rows). Each saved package is reloaded from disk first (EditorLoadingAndSavingUtils.reload_packages,
ASSUME_POSITIVE), so the check reads the saved state, not a resident in-memory object (the X-2359 lesson).

Never sets, saves, creates or deletes anything. Run in the full Editor under the C-1155 lock (ENG).
Output: "WRAPPER PASS|FAIL name=..." per wrapper and a terminal "RESULT=PASS wrappers=4 saves=0" or "RESULT=FAIL ...".
"""
import os
import sys
import traceback

PREFIX = "[GreystoneSavedWrapperNotifies] "


def saved_path(allowlist, name):
    """Package path of a saved wrapper (pure; pinned by the contract)."""
    return allowlist + name


def reload_from_disk(unreal, path, require):
    eal = unreal.EditorAssetLibrary
    require(eal.does_asset_exist(path), "saved wrapper is absent: " + path)
    asset = unreal.load_asset(path)
    require(asset is not None, "saved wrapper failed to load: " + path)
    loading = getattr(unreal, "EditorLoadingAndSavingUtils", None)
    modes = getattr(unreal, "ReloadPackagesInteractionMode", None)
    mode = getattr(modes, "ASSUME_POSITIVE", None) if modes is not None else None
    require(loading is not None and mode is not None and hasattr(loading, "reload_packages"),
            "UE 5.5 package reload API is unavailable; refusing to read a possibly resident object")
    result = loading.reload_packages([asset.get_outermost()], mode)
    ok = bool(result[0]) if isinstance(result, tuple) else bool(result)
    require(ok, "package reload failed: " + path)
    reloaded = unreal.load_asset(path)
    require(reloaded is not None and reloaded.get_class().get_name() == "AnimMontage",
            "reloaded wrapper is missing or not an AnimMontage: " + path)
    return reloaded


def main():
    import unreal  # Editor only
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import author_greystone_player as author

    passed, failures = 0, []
    for spec in author.MONTAGES:
        path = saved_path(author.ALLOWLIST, spec["name"])
        try:
            source, sequence, _info, _desc, _slot, _sections = author.source_readback(spec)
            saved = reload_from_disk(unreal, path, author.require)
            first = saved.get_first_anim_reference()
            author.require(first is not None and first.get_path_name() == sequence.get_path_name(),
                           "%s saved wrapper does not reference the Fit sequence %s" % (spec["name"], sequence.get_path_name()))
            source_rows = author.wrapper_notify_rows(source)
            saved_rows = author.wrapper_notify_rows(saved)
            matched = author.compare_wrapper_notify_rows(spec, source_rows, saved_rows, sequence)
            for source_row, saved_row in zip(source_rows, saved_rows):
                unreal.log(PREFIX + "SOURCE " + source_row)
                unreal.log(PREFIX + "SAVED  " + saved_row)
            unreal.log(PREFIX + "WRAPPER PASS name=%s notifies=%d path=%s" % (spec["name"], matched, path))
            passed += 1
        except Exception as error:  # per-wrapper fail-closed; keep checking the rest for a complete receipt
            failures.append("%s: %s" % (spec["name"], error))
            unreal.log_error(PREFIX + "WRAPPER FAIL name=%s reason=%s" % (spec["name"], error))
    if failures or passed != len(author.MONTAGES):
        unreal.log_error(PREFIX + "RESULT=FAIL wrappers=%d passed=%d first=%s saves=0" %
                         (len(author.MONTAGES), passed, failures[0] if failures else "count mismatch"))
    else:
        unreal.log(PREFIX + "RESULT=PASS wrappers=%d saves=0" % passed)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import unreal
        unreal.log_error(PREFIX + "RESULT=FAIL " + str(error))
        unreal.log_error(traceback.format_exc())
