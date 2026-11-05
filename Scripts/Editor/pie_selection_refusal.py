"""G2 live recovery gate; authored only, not run by Codex.

Separate PIE sessions prove missing path refusal, bad-manifest refusal from an
unsaved transient copy of G044, and fresh empty-selection legacy startup. Takes
ShowUI screenshots on both refusals for human visual confirmation of the red
on-screen refusal text. Log prefix [SelectionRefusal].
"""
import json
import unreal

log = lambda text: unreal.log("[SelectionRefusal] " + str(text))
results = []
state = {"time": 0.0, "phase": "prepare", "case": 0, "next": 0.0, "done": False}
handle = None
transient_copy = None  # keep the unsaved transient object alive across PIE startup
CASES = ("missing", "corrupt_hash", "clear_legacy")
SELECTION = "/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter"
LEGACY_BUNDLE = ("RPGBossPhases", "RPGBossStagger", "RPGBossEncounter", "RPGBossDormantWake",
                 "RPGBossPosture", "RPGBossDeath", "RPGBossLook", "RPGBossBleed",
                 "RPGAttackTracker", "RPGBossCloseClipSwap", "RPGBossShockwave",
                 "RPGBossLowSweep", "RPGBossHealPunish", "RPGDamageResolver",
                 "RPGTraceGuard", "RPGBossHud", "RPGBossLegend", "RPGBossMusic")


def check(name, ok, detail=""):
    results.append(bool(ok))
    log(("PASS " if ok else "FAIL ") + name + (" " + str(detail) if detail else ""))


def prepare_corrupt_copy():
    global transient_copy
    source = unreal.EditorAssetLibrary.load_asset(SELECTION)
    check("G044 definition loaded", source is not None)
    if source is None:
        raise RuntimeError("required G044 source definition is missing")
    transient_copy = unreal.new_object(source.get_class(), name="G2_Transient_Manifest_Corruption")
    check("copy is transient", transient_copy is not None and "/Game/" not in transient_copy.get_path_name(),
          transient_copy.get_path_name() if transient_copy else "")
    for prop in ("schema", "encounter_instance", "stable_manifest_hash", "boss_slot", "player_slot",
                 "initial_boss_phase", "boss_definition", "player_definition"):
        transient_copy.set_editor_property(prop, source.get_editor_property(prop))
    original_hash = str(transient_copy.get_editor_property("stable_manifest_hash"))
    transient_copy.set_editor_property("stable_manifest_hash", "G" * 64)
    check("manifest hash changed only on transient copy",
          original_hash != "G" * 64 and transient_copy.get_editor_property("stable_manifest_hash") == "G" * 64)
    log("transient definition path=" + transient_copy.get_path_name() + " source asset is never modified or saved")


def world_and_snapshot():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    cls = getattr(unreal, "RPGPlayerMovesSubsystem", None)
    accessor = getattr(cls, "get_for_world", None) if cls else None
    subsystem = accessor(world) if accessor and world else None
    if subsystem is None:
        raise RuntimeError("runtime subsystem or begun PIE world unavailable")
    return world, json.loads(subsystem.build_encounter_parity_snapshot())


def begin_case():
    label = CASES[state["case"]]
    if label == "missing":
        selection = "/Game/OneBossFight/Data/DOES_NOT_EXIST_G2.DOES_NOT_EXIST_G2"
    elif label == "corrupt_hash":
        selection = transient_copy.get_path_name()
    else:
        # Lead fix (C-872): a console variable with no value only PRINTS its value; the clear needs an
        # explicit empty string (same form as the cleanup below), otherwise the previous case's path stays selected.
        selection = '""'
    unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + selection)
    log("PIE_BEGIN case=" + label + " selection=" + (selection or "<empty>"))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
    state.update(phase="observe", time=0.0)


def observe_case():
    label = CASES[state["case"]]
    world, snap = world_and_snapshot()
    activation = snap.get("activation", {})
    route = snap.get("route")
    if label in ("missing", "corrupt_hash"):
        check(label + " route remains selected", route == "data", route)
        check(label + " fail-closed HardError", activation.get("outcome") == "HardError", activation)
        expected = "EncounterSelection.AssetLoad" if label == "missing" else "EncounterDefinition.ManifestShape"
        check(label + " refusal token", expected in str(activation.get("reason", "")), activation.get("reason"))
        boss_components = snap.get("components", {}).get("boss", [])
        leaked = [name for name in LEGACY_BUNDLE if any(name in str(item) for item in boss_components)]
        check(label + " legacy boss bundle absent", not leaked, leaked)
        unreal.SystemLibrary.execute_console_command(world, "Shot ShowUI")
        log("ShowUI refusal screenshot requested; visually confirm red 'Encounter activation refused' text")
    else:
        check("fresh empty selection chooses legacy", route == "legacy" and activation.get("outcome") == "LegacyNoSelection", snap)
        boss_components = snap.get("components", {}).get("boss", [])
        check("fresh legacy route restores boss bundle", all(any(name in str(item) for item in boss_components)
                                                               for name in LEGACY_BUNDLE), boss_components)
    log("SNAPSHOT " + json.dumps(snap, sort_keys=True))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    state.update(phase="between", time=0.0)


def tick(delta):
    global handle
    if state["done"]:
        return
    state["time"] += delta
    try:
        if state["phase"] == "prepare":
            prepare_corrupt_copy()
            state.update(phase="between", time=0.0)
        elif state["phase"] == "between" and state["time"] > (2.0 if state["case"] else 0.5):
            if state["case"] >= len(CASES):
                state["done"] = True
                unreal.SystemLibrary.execute_console_command(None, 'rpg.EncounterDefinition ""')
                unreal.unregister_slate_post_tick_callback(handle)
                handle = None
                log("RESULT %d/%d passed" % (sum(results), len(results)))
                return
            begin_case()
        elif state["phase"] == "observe" and state["time"] >= 10.0:
            observe_case()
            state["case"] += 1
    except Exception as error:
        check("driver exception", False, repr(error))
        try:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        except Exception:
            pass
        state["case"] = len(CASES)
        state.update(phase="between", time=0.0)


handle = unreal.register_slate_post_tick_callback(tick)
