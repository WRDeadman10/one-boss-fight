"""C-1286 Lead: remove the five C-1282 Greystone ER assets so author_greystone_player.py can recreate them
on the root-motion-corrected *_Fit_GreystoneRM sequences.

Safety: deletes ONLY the five listed assets under /Game/OneBossFight/Player/Greystone/, and only when every
referencer of each one is inside that same set (they reference each other and nothing else references them:
the mannequin stays the default player). Default = dry-run; --write deletes. Log prefix [GreystoneReplace];
ends with "[GreystoneReplace] RESULT=PASS|FAIL".
"""
import traceback

import unreal

PREFIX = "[GreystoneReplace] "
ROOT = "/Game/OneBossFight/Player/Greystone/"
ASSETS = [
    ROOT + "BP_GreystoneERPlayer",
    ROOT + "AM_ER_Backstep_Mixamo_V2_Fit_Greystone",
    ROOT + "AM_ER_Attack_Air_Light_Fit_Greystone",
    ROOT + "AM_ER_Attack_Air_Heavy_Plunge_Fit_Greystone",
    ROOT + "AM_ER_Attack_GuardCounter_Fit_Greystone",
]


def log(m):
    unreal.log(PREFIX + str(m))


def main():
    write = "--write" in unreal.SystemLibrary.get_command_line().split()
    log("MODE=%s" % ("WRITE" if write else "DRY_RUN"))
    eal = unreal.EditorAssetLibrary
    allowed = set(ASSETS)
    plan = []
    for path in ASSETS:
        if not path.startswith(ROOT):
            raise RuntimeError("path escaped the allowlist: " + path)
        if not eal.does_asset_exist(path):
            log("ABSENT " + path)
            continue
        referencers = [str(r) for r in eal.find_package_referencers_for_asset(path, False)]
        outside = [r for r in referencers if r not in allowed]
        log("ASSET %s referencers=%s outside=%s" % (path, referencers, outside))
        if outside:
            raise RuntimeError("refusing to delete %s: referenced outside the set by %s" % (path, outside))
        plan.append(path)
    if not write:
        log("RESULT=PASS dry_run=1 would_delete=%d" % len(plan))
        return
    deleted = 0
    for path in plan:
        if not eal.delete_asset(path) or eal.does_asset_exist(path):
            raise RuntimeError("delete failed: " + path)
        deleted += 1
        log("DELETED " + path)
    log("RESULT=PASS deleted=%d" % deleted)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log("ERROR " + repr(exc))
        traceback.print_exc()
        log("RESULT=FAIL")
