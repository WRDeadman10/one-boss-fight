"""
Writes the hyperarmor windows of the Strength build (M13/M14) into the weapon attack table asset /Game/OneBossFight/Data/DA_WeaponAttacks (log prefix [WeaponWindows]). Run in the open editor, no PIE.
Idempotent: a row that already has the window is left as it is; rows of other weapons are never touched. The asset holds what the owner tunes, so the script only fills the windows of the rows named below and says what it did.

Numbers (seconds of MONTAGE position, measured by g3_probe_montages.py on 2026-10-22, Documentation/M13_BUILDS_PLAN.md appendix): the window opens 0.08 s before the first weapon trace window of the montage and closes with the last one.
  Claymore Strong and JumpHeavy: the pack plays the same montage Ability_E_Anim_Montage for both (trace 0.432 to 0.618)  -> 0.352 to 0.618
  Claymore Charged: ChargedAttack_Montage (trace 0.503 to 1.005)                                                      -> 0.423 to 1.005
The Starter sword, the dual swords and the twinblades get none (Freeze 5 and 20.1 name the Strength build's downswing only). Keep the numbers in step with FillDefaults in Player/RPGWeaponAttackTable.cpp.
"""
import unreal

log = lambda m: unreal.log("[WeaponWindows] " + m)
PATH = "/Game/OneBossFight/Data/DA_WeaponAttacks"
KIND = unreal.RPGAttackKind
WINDOWS = {
    ("ClaymoreCombatStyle", KIND.STRONG): (0.352, 0.618, "Ability_E_Anim_Montage: trace 0.432-0.618, window opens 0.08 s before the first trace"),
    ("ClaymoreCombatStyle", KIND.JUMP_HEAVY): (0.352, 0.618, "Ability_E_Anim_Montage (the jump heavy is the strong montage): trace 0.432-0.618, window opens 0.08 s before the first trace"),
    ("ClaymoreCombatStyle", KIND.CHARGED): (0.423, 1.005, "ChargedAttack_Montage: trace 0.503-1.005, window opens 0.08 s before the first trace"),
}

table = unreal.EditorAssetLibrary.load_asset(PATH)
if table is None:
    log("FAILED: %s does not exist (run make_weapon_table.py first)" % PATH)
else:
    rows = list(table.get_editor_property("rows"))  # copies of the structs: edited here, written back below
    changed = 0
    found = set()
    for row in rows:
        key = (str(row.get_editor_property("weapon")), row.get_editor_property("kind"))
        if key not in WINDOWS:
            continue
        found.add(key)
        start, end, note = WINDOWS[key]
        if abs(row.get_editor_property("hyper_armor_start") - start) < 1e-4 and abs(row.get_editor_property("hyper_armor_end") - end) < 1e-4:
            log("%s %s already has %.3f to %.3f" % (key[0], key[1].name, start, end))
            continue
        row.set_editor_property("hyper_armor_start", start)
        row.set_editor_property("hyper_armor_end", end)
        old = str(row.get_editor_property("note"))
        row.set_editor_property("note", (old + "; " if old else "") + "hyperarmor " + note)
        changed += 1
        log("%s %s: window %.3f to %.3f written" % (key[0], key[1].name, start, end))
    for key in WINDOWS:
        if key not in found:
            log("WARNING: no row for %s %s in the table: nothing written for it (the lookup would fall back to another row)" % (key[0], key[1].name))
    if changed:
        table.modify()
        table.set_editor_property("rows", rows)
        saved = unreal.EditorAssetLibrary.save_loaded_asset(table)
        log("%d row(s) changed, saved: %s" % (changed, saved))
    else:
        log("nothing to change")
    # read back from the saved asset
    table = unreal.EditorAssetLibrary.load_asset(PATH)
    for row in table.get_editor_property("rows"):
        if row.get_editor_property("hyper_armor_start") >= 0:
            log("   %-22s %-10s hyperarmor %.3f to %.3f   %s" % (row.get_editor_property("weapon"), row.get_editor_property("kind").name, row.get_editor_property("hyper_armor_start"), row.get_editor_property("hyper_armor_end"), str(row.get_editor_property("note"))[:90]))
log("done")
