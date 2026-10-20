import unreal
log = lambda m: unreal.log("[CamProbe] " + m)
state = {"phase": "start", "t": 0.0}
handle = None


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def tick(dt):
    global handle
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait", t=0.0)
        return
    w = world()
    if w is None:
        return
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None or s["t"] < 22.0:
        return
    for c in pawn.get_components_by_class(unreal.SceneComponent):
        extra = ""
        if isinstance(c, unreal.SpringArmComponent):
            extra = " arm=%.0f socket=%s lag=%s probe=%s" % (c.get_editor_property("target_arm_length"), c.get_editor_property("socket_offset"), c.get_editor_property("enable_camera_lag"), c.get_editor_property("do_collision_test"))
        log("%-22s %-24s world=%s%s" % (c.get_name(), c.get_class().get_name(), c.get_world_location(), extra))
    cam = pc.player_camera_manager
    log("view target %s camera loc %s rot %s fov %s" % (cam.get_view_target().get_name(), cam.get_camera_location(), cam.get_camera_rotation(), cam.get_fov_angle()))
    log("pawn loc %s rot %s control rot %s" % (pawn.get_actor_location(), pawn.get_actor_rotation(), pc.get_control_rotation()))
    unreal.unregister_slate_post_tick_callback(handle)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


handle = unreal.register_slate_post_tick_callback(tick)
