"""Screenshots the fog gate from the arena side: sleeping boss (thin mist), then awake (closed). Log prefix [GateLook]."""
import unreal

log = lambda m: unreal.log("[GateLook] " + m)
state = {"phase": "start", "t": 0.0, "step": 0, "wait": 0.0}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def _tick(dt):
    global handle
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0, wait=9.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    gate = next(iter(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.RPGFogGate)), None) if w else None
    if pawn is None or boss is None or gate is None or s["t"] < s["wait"]:
        return
    gl = gate.get_actor_location()
    gf = gate.get_actor_forward_vector()
    if s["step"] == 0:
        log("gate at %s forward %s state %s amount %.2f" % (gl, gf, gate.get_state_name(), gate.get_amount()))
        for d in (-1200,):
            p = unreal.Vector(gl.x + gf.x * d, gl.y + gf.y * d, gl.z + 20)
            yaw = unreal.MathLibrary.find_look_at_rotation(p, gl).yaw
            pawn.set_actor_location_and_rotation(p, unreal.Rotator(0, 0, yaw), False, True)
            pc.set_control_rotation(unreal.Rotator(roll=0, pitch=-4, yaw=yaw))
        s["step"] = 1
        s["wait"] = s["t"] + 1.5
        return
    if s["step"] == 1:
        unreal.SystemLibrary.execute_console_command(w, "Shot ShowUI")
        log("shot idle: state %s amount %.2f" % (gate.get_state_name(), gate.get_amount()))
        comp(boss, "RPGBossEncounter").wake()
        comp(boss, "RPGBossEncounter").hold_for_test(True)
        s["step"] = 2
        s["wait"] = s["t"] + 3.5
        return
    if s["step"] == 2:
        unreal.SystemLibrary.execute_console_command(w, "Shot ShowUI")
        log("shot closed: state %s amount %.2f" % (gate.get_state_name(), gate.get_amount()))
        d = -500
        p = unreal.Vector(gl.x + gf.x * d, gl.y + gf.y * d, gl.z + 20)
        yaw = unreal.MathLibrary.find_look_at_rotation(p, gl).yaw
        pawn.set_actor_location_and_rotation(p, unreal.Rotator(0, 0, yaw), False, True)
        pc.set_control_rotation(unreal.Rotator(roll=0, pitch=-4, yaw=yaw))
        s["step"] = 3
        s["wait"] = s["t"] + 1.2
        return
    if s["step"] == 3:
        unreal.SystemLibrary.execute_console_command(w, "Shot ShowUI")
        log("shot closed near")
        s["step"] = 4
        s["wait"] = s["t"] + 1.0
        return
    if s["step"] == 4:
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
