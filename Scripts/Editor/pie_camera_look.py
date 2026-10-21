"""Screenshots the player's own camera at three pitches (32 up, 0, -60 down) on the arena floor. Log prefix [CamLook]. Needs a warm-up PIE first."""
import unreal

log = lambda m: unreal.log("[CamLook] " + m)
PITCHES = [32, 0, -60]
S = {"phase": "start", "t": 0.0, "i": 0, "wait": 0.0, "step": 0}
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
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is None or boss is None or s["t"] < 9.0 or s["t"] < s["wait"]:
        return
    next(c for c in boss.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == "RPGBossEncounter").hold_for_test(True)
    if s["i"] >= len(PITCHES):
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("done")
        return
    if s["step"] == 0:
        pawn.set_actor_location_and_rotation(unreal.Vector(900, 0, 120), unreal.Rotator(0, 0, 0), False, True)
        pc.set_control_rotation(unreal.Rotator(roll=0, pitch=PITCHES[s["i"]], yaw=0))
        s["step"] = 1
        s["wait"] = s["t"] + 2.0
        return
    unreal.SystemLibrary.execute_console_command(w, "HighResShot 1280x720")
    log("shot at pitch %d" % PITCHES[s["i"]])
    s["i"] += 1
    s["step"] = 0
    s["wait"] = s["t"] + 1.0


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
