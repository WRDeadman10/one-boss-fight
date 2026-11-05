"""U-C05: one PIE run per route, natural combat exposure and fifty encounter resets.

Run with the editor open using Scripts/run_in_editor.py. Set
H019_ENCOUNTER_DEFINITION before launching the editor for the selected route;
leave it unset for the legacy route. Restart the editor between route arms.
"""
import ctypes
import math
import os
import traceback
import unreal


BOSS_CLASS = "BP_ExampleGreatSwordBoss_C"
SELECTED = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
ROUTE = "selected" if SELECTED else "legacy"
CYCLES = 50
WARMUP_SECONDS = 9.0
FIGHT_SECONDS = 10.0
RESET_WAIT_SECONDS = 15.0
TOTAL_TIMEOUT_SECONDS = 1800.0
HEARTBEAT_SECONDS = 15.0
S = {"time": 0.0, "phase": "start", "phase_time": 0.0, "cycle": 0,
     "generation": None, "reset_count": None, "results": [], "tick_error": False,
     "last_heartbeat": -HEARTBEAT_SECONDS, "finished": False, "world_ready": False}
handle = None


def log(message):
    unreal.log("[MemorySoak] " + message)


def process_memory_mb():
    """Return current UnrealEditor working/private bytes when Win32 exposes them."""
    try:
        class Counters(ctypes.Structure):
            _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
                        ("PrivateUsage", ctypes.c_size_t)]
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        psapi.GetProcessMemoryInfo.argtypes = (ctypes.c_void_p, ctypes.POINTER(Counters), ctypes.c_ulong)
        psapi.GetProcessMemoryInfo.restype = ctypes.c_bool
        current = kernel.GetCurrentProcess()
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        if not psapi.GetProcessMemoryInfo(current, ctypes.byref(counters), counters.cb):
            return None
        scale = 1024.0 * 1024.0
        return {"working_set_mb": round(counters.WorkingSetSize / scale, 1),
                "private_mb": round(counters.PrivateUsage / scale, 1)}
    except Exception as exc:
        return {"unavailable": type(exc).__name__}


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def actors():
    game_world = world()
    controller = unreal.GameplayStatics.get_player_controller(game_world, 0) if game_world else None
    pawn = controller.get_controlled_pawn() if controller else None
    boss = next((actor for actor in unreal.GameplayStatics.get_all_actors_of_class(game_world, unreal.Character)
                 if actor.get_class().get_name() == BOSS_CLASS), None) if game_world else None
    return game_world, pawn, boss


def component(actor, class_name):
    if actor is None:
        return None
    return next((item for item in actor.get_components_by_class(unreal.ActorComponent)
                 if item.get_class().get_name() == class_name), None)


def census(game_world):
    all_actors = unreal.GameplayStatics.get_all_actors_of_class(game_world, unreal.Actor) if game_world else []
    names = [actor.get_class().get_name() for actor in all_actors]
    return {"actors": len(names), "bosses": names.count(BOSS_CLASS),
            "javelins": names.count("RPGBossJavelin"),
            "wave_or_projectile": sum("Wave" in name or "Projectile" in name for name in names)}


def generation(encounter):
    try:
        return int(encounter.get_participant_generation_text()), int(encounter.get_reset_count())
    except Exception:
        return None, None


def place_player(pawn, boss):
    origin = boss.get_actor_location()
    radians = math.radians(boss.get_actor_rotation().yaw)
    location = unreal.Vector(origin.x + math.cos(radians) * 450.0,
                             origin.y + math.sin(radians) * 450.0, origin.z + 20.0)
    facing = unreal.MathLibrary.find_look_at_rotation(location, origin)
    pawn.set_actor_location_and_rotation(location, facing, False, True)


def sample(stage):
    game_world, pawn, boss = actors()
    if game_world is None:
        raise RuntimeError("cannot sample lifetime evidence without an active PIE world")
    log("gc_before_sample stage=%s command=obj gc" % stage)
    unreal.SystemLibrary.execute_console_command(game_world, "obj gc")
    log("gc_before_sample_completed stage=%s" % stage)
    encounter = component(boss, "RPGBossEncounter")
    gen, resets = generation(encounter) if encounter else (None, None)
    record = {"route": ROUTE, "cycle": S["cycle"], "stage": stage, "gc_before_sample": True,
              "generation": gen, "reset_count": resets,
              "objects": census(game_world), "memory": process_memory_mb()}
    log("sample " + repr(record))
    return record


def finish(reason):
    global handle
    if S["finished"]:
        return
    S["finished"] = True
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    passed = reason == "complete" and S["cycle"] == CYCLES and not S["tick_error"]
    log("RESULT route=%s resets=%d/%d status=%s reason=%s" %
        (ROUTE, S["cycle"], CYCLES, "PASS" if passed else "INCOMPLETE", reason))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def tick(delta_seconds):
    S["time"] += max(0.0, float(delta_seconds))
    S["phase_time"] += max(0.0, float(delta_seconds))
    if S["time"] > TOTAL_TIMEOUT_SECONDS:
        finish("total watchdog")
        return
    if S["time"] - S["last_heartbeat"] >= HEARTBEAT_SECONDS:
        S["last_heartbeat"] = S["time"]
        log("heartbeat route=%s phase=%s cycle=%d/%d elapsed=%.1f" %
            (ROUTE, S["phase"], S["cycle"], CYCLES, S["time"]))
    if S["phase"] == "start":
        if S["phase_time"] >= 0.5:
            if SELECTED:
                unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + SELECTED)
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S["phase"], S["phase_time"] = "warming", 0.0
        return
    game_world, pawn, boss = actors()
    if boss is None or pawn is None:
        if S["phase_time"] > 90.0:
            finish("player/boss unavailable after PIE start")
        return
    encounter = component(boss, "RPGBossEncounter")
    if encounter is None:
        finish("RPGBossEncounter component missing")
        return
    if S["phase"] == "warming":
        if not S["world_ready"]:
            S["world_ready"] = True
            S["phase_time"] = 0.0
            log("PIE world ready; warmup timer started")
            return
        if S["phase_time"] >= WARMUP_SECONDS:
            place_player(pawn, boss)
            S["phase"] = "fighting"
            S["phase_time"] = 0.0
            S["cycle"] = 1
            S["generation"], S["reset_count"] = generation(encounter)
            sample("baseline_after_warmup")
        return
    if S["phase"] == "fighting":
        if S["phase_time"] >= FIGHT_SECONDS:
            S["generation"], S["reset_count"] = generation(encounter)
            sample("before_reset")
            try:
                encounter.reset_for_test()
            except Exception as exc:
                S["tick_error"] = True
                finish("reset_for_test failed: %s" % exc)
                return
            S["phase"], S["phase_time"] = "resetting", 0.0
        return
    if S["phase"] == "resetting":
        gen, resets = generation(encounter)
        if gen is not None and gen > S["generation"] and resets > S["reset_count"]:
            sample("after_reset")
            if S["cycle"] >= CYCLES:
                finish("complete")
                return
            S["cycle"] += 1
            place_player(pawn, boss)
            S["phase"], S["phase_time"] = "fighting", 0.0
        elif S["phase_time"] > RESET_WAIT_SECONDS:
            S["tick_error"] = True
            finish("reset did not advance generation/count")


def on_tick(delta_seconds):
    try:
        tick(delta_seconds)
    except Exception:
        S["tick_error"] = True
        log("tick exception: " + traceback.format_exc())
        finish("tick exception")


# Lead fix (C-906): register at module level like every other registered driver; the fresh-process runner imports this file as a
# module (__name__ != "__main__"), so the old __main__ guard never started the soak.
log("start route=%s selected_definition=%s cycles=%d warmup=%.1fs fight=%.1fs" %
    (ROUTE, SELECTED or "<unset>", CYCLES, WARMUP_SECONDS, FIGHT_SECONDS))
handle = unreal.register_slate_post_tick_callback(on_tick)
