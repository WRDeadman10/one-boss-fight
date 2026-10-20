"""Starts PIE, switches the combat debug overlay on (rpg.Debug 2), lets it log for a few seconds, stops PIE. Log lines appear under LogRPGDebug. Log prefix [DebugOverlay]."""
import unreal

log = lambda m: unreal.log("[DebugOverlay] " + m)
state = {"t": 0.0, "phase": "start", "on": False}
handle = None


def _tick(dt):
    global handle
    s = state
    s["t"] += dt
    if s["phase"] == "start" and s["t"] > 0.5:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
        s.update(phase="play", t=0.0)
        return
    if s["phase"] != "play":
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if w is None:
        return
    if not s["on"] and s["t"] > 8.0:
        unreal.SystemLibrary.execute_console_command(w, "rpg.Debug 2")
        s["on"] = True
        log("rpg.Debug 2 set")
    if s["t"] > 13.0:
        unreal.SystemLibrary.execute_console_command(w, "rpg.Debug 0")
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("done")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
