"""C-1286 Lead: remove the C-1254 Sevarog draft data assets so author_sevarog_draft_cards.py (X26) can recreate
the full S1-S8 set (S1/S2 90-120 cm rows, AdditionalPhaseIds, S6/S7/S8, PhaseTwoFraction 0.6) in one authoring pass.

Safety: deletes ONLY the listed assets under /Game/OneBossFight/Data/Sevarog/, and only when every referencer of
each one is inside that same set. If anything else (the arena map, DA_Sevarog_G044_Encounter, a Blueprint) references
one of them, the script refuses and lists the referencer; nothing is deleted. Default = dry-run; --write deletes.
Log prefix [SevarogReplace]; ends with "[SevarogReplace] RESULT=PASS|FAIL".
"""
import traceback

import unreal

PREFIX = "[SevarogReplace] "
ROOT = "/Game/OneBossFight/Data/Sevarog/"
ASSETS = [
    ROOT + "DA_Boss_Sevarog_Draft",
    ROOT + "DA_Boss_Sevarog_FrameworkProfile_Draft",
    ROOT + "DA_Move_Sevarog_Swing1_Medium_C1247",
    ROOT + "DA_Move_Sevarog_Swing2_Medium_C1247",
    ROOT + "DA_Move_Sevarog_Swing3_Slow_C1247",
    ROOT + "DA_Move_Sevarog_Speedburst_C1247",
    ROOT + "DA_Move_Sevarog_Swing1_FAST_v2_C1247",
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
