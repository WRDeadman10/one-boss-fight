"""PIE probe of the player's camera setup: spring arm and camera component properties, the camera manager's pitch limits, what the camera trace channel hits on the arena floor. Log prefix [CamProbe]."""
import unreal

log = lambda m: unreal.log("[CamProbe] " + m)
S = {"phase": "start", "t": 0.0}
handle = None


def props(obj, names):
    for n in names:
        try:
            log("   %s = %s" % (n, obj.get_editor_property(n)))
        except Exception as e:
            log("   %s ERR %s" % (n, str(e)[:60]))


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
    log("pawn %s, controller %s" % (pawn.get_class().get_name(), pc.get_class().get_name()))
    for c in pawn.get_components_by_class(unreal.SceneComponent):
        log("component %s (%s) parent %s rel loc %s" % (c.get_name(), c.get_class().get_name(), c.get_attach_parent().get_name() if c.get_attach_parent() else None, c.get_editor_property("relative_location")))
    arm = pawn.get_components_by_class(unreal.SpringArmComponent)
    log("spring arms: %d" % len(arm))
    for a in arm:
        log("SPRING ARM %s" % a.get_name())
        props(a, ["target_arm_length", "do_collision_test", "probe_size", "probe_channel", "socket_offset", "target_offset", "use_pawn_control_rotation", "inherit_pitch", "inherit_yaw", "inherit_roll",
                  "enable_camera_lag", "camera_lag_speed", "camera_lag_max_distance", "enable_camera_rotation_lag", "camera_rotation_lag_speed", "use_camera_lag_substepping", "lag_max_time_step", "do_collision_test"])
        props(a, ["primary_component_tick"])
    for c in pawn.get_components_by_class(unreal.CameraComponent):
        log("CAMERA %s" % c.get_name())
        props(c, ["field_of_view", "use_pawn_control_rotation", "relative_location", "relative_rotation"])
    cm = pc.player_camera_manager
    log("camera manager %s" % cm.get_class().get_name())
    props(cm, ["view_pitch_min", "view_pitch_max", "view_yaw_min", "view_yaw_max"])
    log("control rotation %s" % pc.get_control_rotation())
    log("camera location %s rotation %s" % (cm.get_camera_location(), cm.get_camera_rotation()))
    pl = pawn.get_actor_location()
    for ch_name, ch in (("Visibility", unreal.TraceTypeQuery.TRACE_TYPE_QUERY1), ("Camera", unreal.TraceTypeQuery.TRACE_TYPE_QUERY2)):
        hit = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(pl.x, pl.y, pl.z + 300), unreal.Vector(pl.x, pl.y, pl.z - 600), ch, False, [], unreal.DrawDebugTrace.NONE, True)
        log("floor trace on %s: %s" % (ch_name, hit))
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
