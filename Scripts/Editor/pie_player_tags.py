"""PIE probe: presses the pack's dodge key and logs the player's owned gameplay tags whenever they change (to find the i-frame state). Log prefix [PlayerTags]. Needs a warm-up PIE once."""
import unreal

log = lambda m: unreal.log("[PlayerTags] " + m)
S = {"phase": "start", "t": 0.0, "last": None, "down": False, "run": 0.0}
handle = None
KEY = "Gamepad_FaceButton_Right"


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
    if 1.0 <= s["run"] < 1.12 and not s["down"]:
        unreal.RPGInputTestUtils.set_key_down(pc, KEY, True)
        s["down"] = True
    if s["run"] >= 1.12 and s["down"]:
        unreal.RPGInputTestUtils.set_key_down(pc, KEY, False)
        s["down"] = False
    try:
        tags = str(sorted(str(x.get_editor_property("tag_name")) for x in pawn.call_method("GetOwnedGameplayTags").get_editor_property("gameplay_tags")))
    except Exception as e:
        tags = "ERR %s" % e
    if tags != s["last"]:
        log("t=%.2f tags %s" % (s["run"], tags[:300]))
        s["last"] = tags
    if s["run"] > 4.0:
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
