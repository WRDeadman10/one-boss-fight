"""
PIE look check: plays the arena and takes high resolution screenshots from the player's own camera at a few spots (player start, mid arena facing the boss,
near a brazier, near the wall, boss close up). Files land in Saved/Screenshots/WindowsEditor/ (HighresScreenshotNNNNN.png); the log prefix [LookPie] lists the order.
Open L_SevarogArena first; run with Scripts/run_in_editor.py (turn off throttling first: Scripts/Editor/no_throttle.py).
"""
import unreal

log = lambda m: unreal.log("[LookPie] " + m)
# (seconds after PIE start, label, player location or None, yaw)
STEPS = [
    (9.0, "start", None, 0.0),
    (12.0, "mid arena toward boss", (-900.0, 0.0, 110.0), 0.0),
    (15.0, "near brazier", (1500.0, 700.0, 110.0), 25.0),
    (18.0, "west wall looking out", (-1900.0, 600.0, 110.0), 200.0),
    (21.0, "boss close", (-250.0, 0.0, 110.0), 0.0),
]
state = {"phase": "start", "t": 0.0, "i": 0, "shots": 0}
handle = None


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def finish(reason):
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = state
    s["t"] += dt
    if s["t"] > 60.0:
        finish("timeout")
        return
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        return
    if s["i"] < len(STEPS) and s["t"] >= STEPS[s["i"]][0]:
        _, label, loc, yaw = STEPS[s["i"]]
        if loc:
            pawn.set_actor_location_and_rotation(unreal.Vector(*loc), unreal.Rotator(0, 0, yaw), False, True)
            pc.set_control_rotation(unreal.Rotator(roll=0, pitch=-6, yaw=yaw))
        unreal.SystemLibrary.execute_console_command(w, "HighResShot 1280x720")
        s["shots"] += 1
        log("shot %d: %s" % (s["shots"], label))
        s["i"] += 1
    elif s["i"] >= len(STEPS) and s["t"] > STEPS[-1][0] + 3.0:
        finish("done")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
handle = unreal.register_slate_post_tick_callback(tick)
