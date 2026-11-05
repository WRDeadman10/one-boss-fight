"""Run one registered A5 PIE driver in a fresh process, with gate preconditions, then quit."""
import importlib.util
import json
import os
import unreal

ROOT = unreal.Paths.project_dir()
SCRIPTS = os.path.join(ROOT, "Scripts", "Editor")
ALLOWED = {
    "pie_dormant_wake": 600.0,
    "pie_damage_path": 900.0,
    "pie_player_death_reset": 1200.0,
    "pie_telegraph": 600.0,
    "pie_boss_hud": 900.0,
    "pie_phase_reset": 420.0,
    "pie_boss_death": 300.0,
    "pie_boss_death_states": 600.0,
    "pie_victory_lock": 420.0,
    "pie_transition_rules": 900.0,
    "pie_a5_heal_punish": 420.0,
    "pie_bleed": 900.0,
    "pie_leap_wave": 420.0,
    "pie_posture_hits": 1100.0,
    "pie_hyperarmor": 900.0,
    "pie_close_attacks": 420.0,
    "pie_authored_close_clips": 600.0,
    "pie_boss_clips": 600.0,
    "pie_attack_rules": 420.0,
    "pie_boss_look": 300.0,
    "pie_riposte": 420.0,
    "pie_riposte_exec": 700.0,
    "pie_riposte_lethal": 300.0,
    "pie_trace_audit": 1500.0,
    "pie_hit_intake": 600.0,
    "pie_iframes": 1500.0,
    "pie_fog_gate": 420.0,
    "pie_remains": 600.0,
    "pie_soak": 900.0,
    "pie_legend": 900.0,
    "pie_selection_refusal": 600.0,  # lead (C-872): single-arm G2 recovery run through the same preconditions
}
log = lambda message: unreal.log("[A5ParityRunner] " + message)
driver_name = os.environ.get("A5_PARITY_DRIVER", "").strip()
state = {"phase": "warmup", "elapsed": 0.0, "driver_elapsed": 0.0, "after": 0,
         "module": None, "snapshot": False, "done": False}
handle = None


def load(name):
    path = os.path.join(SCRIPTS, name + ".py")
    spec = importlib.util.spec_from_file_location("onebossfight_" + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def quit_editor(reason):
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    if not state["done"]:
        state["done"] = True
        log(reason + "; quitting editor")
        unreal.SystemLibrary.quit_editor()


if driver_name not in ALLOWED:
    raise RuntimeError("A5_PARITY_DRIVER must be one of: " + ", ".join(sorted(ALLOWED)))

# Match Scripts/RunDrivers.ps1 preconditions and its first-PIE warm-up.
load("no_throttle")
load("wake_clip_off")
load("legend_off")
load("build_off")
warmup = load("pie_debug_overlay")


def tick(delta):
    global handle
    state["elapsed"] += delta
    if state["phase"] == "warmup":
        if warmup.handle is not None:
            if state["elapsed"] > 90.0:
                quit_editor("first-PIE warm-up timed out")
            return
        state["phase"] = "settle"
        state["elapsed"] = 0.0
        log("first-PIE warm-up complete; settling 40 seconds")
        return
    if state["phase"] == "settle":
        if state["elapsed"] < 40.0:
            return
        try:
            state["module"] = load(driver_name)
            state["phase"] = "driver"
            state["elapsed"] = 0.0
            log("driver_started=" + driver_name)
        except Exception as exc:
            quit_editor("driver import failed: " + repr(exc))
        return
    if state["phase"] != "driver":
        state["after"] += 1
        if state["after"] < 60:
            return
        state["done"] = True
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        log("driver terminal; quitting editor")
        unreal.SystemLibrary.quit_editor()
        return

    state["driver_elapsed"] += delta
    if not state["snapshot"]:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        subsystem_type = getattr(unreal, "RPGPlayerMovesSubsystem", None)
        accessor = getattr(subsystem_type, "get_for_world", None) if subsystem_type else None
        subsystem = accessor(world) if accessor and world else None
        if subsystem:
            # Lead fix (C-835): BuildEncounterParitySnapshot() returns pretty-printed JSON, which the log
            # splits over many lines; write_a4_parity_receipt.py reads one line, so log it compact.
            snapshot_text = json.dumps(json.loads(subsystem.build_encounter_parity_snapshot()),
                                       sort_keys=True, separators=(",", ":"))
            log("SNAPSHOT_JSON " + snapshot_text)
            state["snapshot"] = True
    if state["module"].handle is None:
        state["phase"] = "shutdown_settle"
        state["elapsed"] = 0.0
    elif state["driver_elapsed"] > ALLOWED[driver_name]:
        quit_editor("driver timeout=" + driver_name)


handle = unreal.register_slate_post_tick_callback(tick)
