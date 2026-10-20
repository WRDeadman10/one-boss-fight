"""Starts PIE and logs the player's position, camera yaw, combat state and stamina every 0.4 s for DURATION seconds.
Used with real keyboard input sent from outside (see Scripts/SendKeys.ps1) to check key mappings. Log prefix [PosLog]."""
import unreal

DURATION = 32.0
state = {"phase": "start", "t": 0.0, "next": 0.0}
handle = None


def log(msg):
    unreal.log("[PosLog] " + msg)


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def finish(reason):
    global handle
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception:
        pass
    log("finished: " + reason)


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
        if s["phase"] == "run":
            finish("PIE ended")
        return
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        return
    if s["phase"] == "wait":
        s.update(phase="run", t=0.0, next=0.0)
        log("PIE ready")
        return
    if s["t"] >= s["next"]:
        s["next"] += 0.4
        combat = pawn.get_components_by_class(unreal.RPGCombatComponent)[0]
        attr = pawn.get_components_by_class(unreal.RPGAttributeComponent)[0]
        loc = pawn.get_actor_location()
        log("t=%.1f x=%.0f y=%.0f camYaw=%.0f state=%s stamina=%.0f" % (
            s["t"], loc.x, loc.y, pc.get_control_rotation().yaw, str(combat.get_state()).split(".")[-1].split(":")[0], attr.get_stamina()))
    if s["t"] > DURATION:
        finish("done")


handle = unreal.register_slate_post_tick_callback(tick)
log("driver registered")
