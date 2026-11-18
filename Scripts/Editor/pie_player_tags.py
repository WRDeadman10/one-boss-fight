"""PIE probe: presses the pack's dodge key and logs the player's owned gameplay tags whenever they change (to find the i-frame state). Log prefix [PlayerTags]. Needs a warm-up PIE once."""
import unreal
from pie_driver_support import FinalResult, MappingReadinessGate

log = lambda m: unreal.log("[PlayerTags] " + m)
S = {"phase": "start", "t": 0.0, "last": None, "down": False, "run": 0.0}
S.update(done=False, mapping_checked=False, press_ok=False, release_ok=False,
         mapping_gate=MappingReadinessGate(5.0))
handle = None
KEY = "Gamepad_FaceButton_Right"
FINAL_RESULT = FinalResult(log, "pie_player_tags")


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
                      press_ok=S["press_ok"], release_ok=S["release_ok"])
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
    if s["phase"] == "run" and s["t"] >= 9.0 and not s["mapping_checked"]:
        s.update(phase="mapping_ready")
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
            s.update(phase="run", mapping_checked=True, run=0.0)
        return
    if s["phase"] != "run" or s["t"] < 9.0:
        return
    s["run"] += dt
    if 1.0 <= s["run"] < 1.12 and not s["down"]:
        s["press_ok"] = bool(unreal.RPGInputTestUtils.set_key_down(pc, KEY, True))
        if not s["press_ok"]:
            finish("input mapping refused press")
            return
        s["down"] = True
    if s["run"] >= 1.12 and s["down"]:
        s["release_ok"] = bool(unreal.RPGInputTestUtils.set_key_down(pc, KEY, False))
        if not s["release_ok"]:
            finish("input mapping refused release")
            return
        s["down"] = False
    try:
        tags = str(sorted(str(x.get_editor_property("tag_name")) for x in pawn.call_method("GetOwnedGameplayTags").get_editor_property("gameplay_tags")))
    except Exception as e:
        tags = "ERR %s" % e
    if tags != s["last"]:
        log("t=%.2f tags %s" % (s["run"], tags[:300]))
        s["last"] = tags
    if s["run"] > 4.0:
        finish("probe complete")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("driver exception")


handle = unreal.register_slate_post_tick_callback(tick)
