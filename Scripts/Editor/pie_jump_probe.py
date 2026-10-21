"""PIE probe: presses a key (Saved/jump_key.txt, default SpaceBar) and logs the player's height above its start for 2 s. Log prefix [JumpProbe]. Needs a warm-up PIE once."""
import os
import unreal

log = lambda m: unreal.log("[JumpProbe] " + m)
_kf = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "jump_key.txt")
KEY = open(_kf).read().strip() if os.path.exists(_kf) else "SpaceBar"
S = {"phase": "start", "t": 0.0, "run": 0.0, "z0": None, "maxz": 0.0, "down": False}
handle = None


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
    if pawn is None or s["t"] < 9.0:
        return
    s["run"] += dt
    z = pawn.get_actor_location().z
    if s["z0"] is None:
        s["z0"] = z
    if 0.5 <= s["run"] < 0.6 and not s["down"]:
        unreal.RPGInputTestUtils.set_key_down(pc, KEY, True)
        s["down"] = True
        log("pressed %s" % KEY)
    if s["run"] >= 0.6 and s["down"]:
        unreal.RPGInputTestUtils.set_key_down(pc, KEY, False)
        s["down"] = False
    s["maxz"] = max(s["maxz"], z - s["z0"])
    if s["run"] > 2.5:
        log("max height gained %.1f cm with key %s, state %s" % (s["maxz"], KEY, pawn.character_movement.movement_mode))
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
