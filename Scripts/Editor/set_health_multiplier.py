"""
Writes the health damage multiplier (KI-097) of the starter sword into the weapon attack table asset /Game/OneBossFight/Data/DA_WeaponAttacks (log prefix [HealthMultiplier]). Run in the open editor, no PIE.
Idempotent: a row that already has the value is left as it is; rows of other weapons are never touched. The asset holds what the owner tunes, so the script only fills the rows named below.

Number: the pack's starter sword deals 41 health per light and 57.4 per strong hit, the builds' weapons 16 and 22.4 (nine bot runs, 2026-10-23): 16 / 41 and 22.4 / 57.4 are both 0.39.
Keep it in step with FillDefaults in Player/RPGWeaponAttackTable.cpp.
"""
import unreal

log = lambda m: unreal.log("[HealthMultiplier] " + m)
PATH = "/Game/OneBossFight/Data/DA_WeaponAttacks"
VALUES = {"SwordCombatStyle": 0.39}

table = unreal.EditorAssetLibrary.load_asset(PATH)
if table is None:
    log("FAILED: %s does not exist (run make_weapon_table.py first)" % PATH)
else:
    rows = list(table.get_editor_property("rows"))  # copies of the structs: edited here, written back below
    changed = 0
    for row in rows:
        weapon = str(row.get_editor_property("weapon"))
        if weapon not in VALUES:
            continue
        value = VALUES[weapon]
        if abs(row.get_editor_property("health_damage_multiplier") - value) < 1e-4:
            continue
        row.set_editor_property("health_damage_multiplier", value)
        changed += 1
        log("%s %s: %.2f written" % (weapon, row.get_editor_property("kind").name, value))
    if changed:
        table.modify()
        table.set_editor_property("rows", rows)
        log("%d row(s) changed, saved: %s" % (changed, unreal.EditorAssetLibrary.save_loaded_asset(table)))
    else:
        log("nothing to change")
    table = unreal.EditorAssetLibrary.load_asset(PATH)
    for row in table.get_editor_property("rows"):
        if abs(row.get_editor_property("health_damage_multiplier") - 1.0) > 1e-4:
            log("   %-22s %-10s multiplier %.2f" % (row.get_editor_property("weapon"), row.get_editor_property("kind").name, row.get_editor_property("health_damage_multiplier")))
log("done")
