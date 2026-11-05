"""Read-only probe for the active PIE encounter snapshot; Lead-run after a build."""
import json
import os
import unreal

log = lambda message: unreal.log("[EncounterSnapshotProbe] " + message)
handle = None
state = {"ticks": 0, "done": False, "started": False}


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    if state["started"]:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def tick(_delta):
    if state["done"]:
        return
    state["ticks"] += 1
    if not state["started"]:
        if state["ticks"] < 20:
            return
        selection = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
        if not selection:
            state["done"] = True
            log("FAIL H019_ENCOUNTER_DEFINITION is required for selected-route probe")
            finish()
            return
        unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + selection)
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
        state["started"] = True
        state["ticks"] = 0
        log("PIE requested for selected definition " + selection)
        return
    if state["ticks"] < 20:
        return
    # Lead fix (C-834): the wait for the PIE world must stay outside try/finally, otherwise the
    # finally block ends PIE and unregisters the tick on the first retry.
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if world is None and state["ticks"] < 120:
        return
    state["done"] = True
    try:
        if world is None:
            log("FAIL no active PIE game world after 120 Slate ticks")
            return
        subsystem_type = getattr(unreal, "RPGPlayerMovesSubsystem", None)
        accessor = getattr(subsystem_type, "get_for_world", None) if subsystem_type else None
        if accessor is None:
            log("FAIL reflected get_for_world accessor unavailable; rebuild project")
            return
        subsystem = accessor(world)
        if subsystem is None:
            log("FAIL player moves world subsystem unavailable")
            return
        snapshot_text = subsystem.build_encounter_parity_snapshot()
        snapshot = json.loads(snapshot_text)
        if snapshot.get("schema") != "onebossfight.encounter-runtime-snapshot/v1":
            log("FAIL unexpected snapshot schema %s" % snapshot.get("schema"))
            return
        log("SNAPSHOT_JSON " + snapshot_text)
        if snapshot.get("route") != "data" or not snapshot.get("selection", {}).get("selected"):
            log("FAIL selected route was not active: route=%s" % snapshot.get("route"))
            return
        log("PASS snapshot schema=%s route=%s" % (snapshot["schema"], snapshot.get("route")))
    except Exception as exc:
        log("FAIL %s" % exc)
    finally:
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
