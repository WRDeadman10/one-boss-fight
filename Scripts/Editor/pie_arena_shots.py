"""
PIE arena stills: teleports the idle player to a few vantage points and raises Saved/m7_flag.txt with the shot name so
Scripts/CaptureLoop.ps1 grabs frames. Prefix [ArenaShots]. Needs -unattended and the editor in the foreground.
"""
import os

import unreal

LOG = "[ArenaShots] "
SAVED = unreal.Paths.project_saved_dir()
FLAG = os.path.join(SAVED, "m7_flag.txt")
# name, location, yaw (the camera sits behind the player, so the yaw is the viewing direction)
SHOTS = [
    ("spawn_to_center", (-1800.0, 0.0, 120.0), 0.0),
    ("wall_and_pillars", (0.0, 1500.0, 120.0), 90.0),
    ("arch_from_inside", (-2000.0, 0.0, 120.0), 180.0),
    ("pillar_closeup", (1900.0, 600.0, 120.0), 20.0),
]
state = {"phase": "start", "t": 0.0, "i": 0}
handle = None


def log(msg):
    unreal.log(LOG + msg)


def set_flag(tag):
    if tag is None:
        if os.path.exists(FLAG):
            os.remove(FLAG)
    else:
        with open(FLAG, "w") as f:
            f.write(tag)


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def finish(reason):
    global handle
    set_flag(None)
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    q = {"n": 0, "h": None}

    def quit_tick(_dt):
        q["n"] += 1
        if q["n"] > 120:
            unreal.unregister_slate_post_tick_callback(q["h"])
            unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")

    q["h"] = unreal.register_slate_post_tick_callback(quit_tick)


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error: " + traceback.format_exc())
        finish("error")


def _tick(dt):
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait", t=0.0)
        return
    w = world()
    if w is None:
        if s["phase"] != "wait":
            finish("PIE ended")
        return
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        return
    if s["phase"] == "wait":
        if s["t"] > 25.0:  # shader warm-up for the new materials
            s.update(phase="go", t=0.0)
        return
    if s["phase"] == "go":
        if s["i"] >= len(SHOTS):
            finish("all shots")
            return
        name, loc, yaw = SHOTS[s["i"]]
        pawn.set_actor_location_and_rotation(unreal.Vector(*loc), unreal.Rotator(0.0, yaw, 0.0), False, True)
        pc.set_control_rotation(unreal.Rotator(-8.0, yaw, 0.0))
        s.update(phase="settle", t=0.0)
        return
    if s["phase"] in ("settle", "hold"):
        yaw = SHOTS[s["i"]][2]
        pc.set_control_rotation(unreal.Rotator(-8.0, yaw, 0.0))  # the player's camera logic would otherwise recentre
    if s["phase"] == "settle":
        if s["t"] > 1.0:
            set_flag(SHOTS[s["i"]][0])
            s.update(phase="hold", t=0.0)
        return
    if s["phase"] == "hold":
        if s["t"] > 1.4:
            set_flag(None)
            s["i"] += 1
            s.update(phase="go", t=0.0)


handle = unreal.register_slate_post_tick_callback(tick)
log("registered")
