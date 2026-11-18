"""PIE probe: presses a key (Saved/jump_key.txt, default SpaceBar) and logs the player's height above its start for 2 s. Log prefix [JumpProbe]. Needs a warm-up PIE once."""
import os
import unreal
from pie_driver_support import FinalResult, MappingReadinessGate

log = lambda m: unreal.log("[JumpProbe] " + m)
_kf = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "jump_key.txt")
KEY = open(_kf).read().strip() if os.path.exists(_kf) else "SpaceBar"
S = {"phase": "start", "t": 0.0, "run": 0.0, "z0": None, "maxz": 0.0,
     "down": False, "done": False, "mapping_gate": MappingReadinessGate(5.0),
     "press_ok": False, "release_ok": False}
handle = None
FINAL_RESULT = FinalResult(log, "pie_jump_probe")


def finish(reason):
    global handle
    if S["done"]:
        return
    S["done"] = True
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
        if pc and S["down"]:
            unreal.RPGInputTestUtils.set_key_down(pc, KEY, False)
    except Exception:
        pass
    FINAL_RESULT.emit(reason == "probe complete" and S["press_ok"] and S["release_ok"], reason,
                      key=KEY, press_ok=S["press_ok"], release_ok=S["release_ok"],
                      max_height_cm="%.1f" % S["maxz"])
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    global handle
    s = S
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        if s["t"] > 20.0:
            finish("player unavailable")
        return
    if s["phase"] == "run" and s["t"] >= 9.0:
        s["phase"] = "mapping_ready"
        return
    if s["phase"] == "mapping_ready":
        timing = next((c for c in pawn.get_components_by_class(unreal.ActorComponent)
                       if c.get_class().get_name() == "RPGDodgeTiming"), None)
        status = s["mapping_gate"].poll(
            dt, lambda: bool(timing and timing.is_elden_ring_input_active()))
        if status in ("ready", "timeout", "readiness_error", "invalid_delta"):
            log("mapping_readiness=%s waited_s=%.3f" % (status, s["mapping_gate"].elapsed))
            if status != "ready":
                finish("input mapping " + status)
                return
            s.update(phase="measure", run=0.0)
        return
    if s["phase"] != "measure":
        return
    s["run"] += dt
    z = pawn.get_actor_location().z
    if s["z0"] is None:
        s["z0"] = z
    if 0.5 <= s["run"] < 0.6 and not s["down"]:
        s["press_ok"] = bool(unreal.RPGInputTestUtils.set_key_down(pc, KEY, True))
        if not s["press_ok"]:
            finish("input mapping refused press")
            return
        s["down"] = True
        log("pressed %s" % KEY)
    if s["run"] >= 0.6 and s["down"]:
        s["release_ok"] = bool(unreal.RPGInputTestUtils.set_key_down(pc, KEY, False))
        if not s["release_ok"]:
            finish("input mapping refused release")
            return
        s["down"] = False
    s["maxz"] = max(s["maxz"], z - s["z0"])
    if s["run"] > 2.5:
        log("max height gained %.1f cm with key %s, state %s" % (s["maxz"], KEY, pawn.character_movement.movement_mode))
        finish("probe complete")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("driver exception")


handle = unreal.register_slate_post_tick_callback(tick)
