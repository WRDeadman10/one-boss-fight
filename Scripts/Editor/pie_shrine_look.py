"""Shoots the Shiva shrine in PIE from three pawn positions (log prefix [ShrineLook]): from the player start, from 600 cm and from 350 cm in front of the face. The pawn is hidden (the third-person camera sits behind it). Screenshots land in Saved/Screenshots/WindowsEditor."""
import math
import unreal

log = lambda m: unreal.log("[ShrineLook] " + m)
S = {"phase": "start", "t": 0.0, "step": 0, "wait": 9.0}
handle = None
VIEWS = [("start", None), ("600", 600.0), ("350", 350.0)]


def _tick(dt):
    global handle
    S["t"] += dt
    if S["phase"] == "start":
        if S["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase="run", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    shrine = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.StaticMeshActor) if a.get_actor_label() == "ShivaShrine"), None) if w else None
    if pawn is None or shrine is None or S["t"] < S["wait"]:
        return
    i = S["step"] // 2
    if i >= len(VIEWS):
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("done")
        return
    name, dist = VIEWS[i]
    sl = shrine.get_actor_location()
    if S["step"] % 2 == 0:
        pawn.set_actor_hidden_in_game(True)
        if dist is not None:
            # in front of the face: the face is the mesh's -Y, i.e. the actor's negative right vector direction rotated: use the vector towards the player start from the shrine
            to = unreal.Vector(-1800 - sl.x, 0 - sl.y, 0)
            n = math.hypot(to.x, to.y)
            p = unreal.Vector(sl.x + to.x / n * dist, sl.y + to.y / n * dist, 150.0)
            yaw = unreal.MathLibrary.find_look_at_rotation(p, unreal.Vector(sl.x, sl.y, 200.0)).yaw
            pawn.set_actor_location_and_rotation(p, unreal.Rotator(0, 0, yaw), False, True)
            pc.set_control_rotation(unreal.Rotator(roll=0, pitch=0, yaw=yaw))
        else:
            pc.set_control_rotation(unreal.Rotator(roll=0, pitch=0, yaw=unreal.MathLibrary.find_look_at_rotation(pawn.get_actor_location(), sl).yaw))
        S["wait"] = S["t"] + 2.0
    else:
        unreal.SystemLibrary.execute_console_command(w, "Shot ShowUI")
        log("shot %s" % name)
        S["wait"] = S["t"] + 1.5
    S["step"] += 1


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
