"""C-1172: PIE-only per-frame visual sword/hand/pack trace alignment probe.
Run only in L_SevarogArena under the C-1155 engine lock after AG socket authoring.
"""
import os
import unreal

PREFIX = "[EmberSwordProbe]"
SEQUENCE = [("IDLE", None, "none", 1.5), ("A1", "A1", "montage", 2.5),
            ("A2", "A2", "ability", 2.5), ("A3", "A3a", "montage", 2.5)]
S = {"phase": "start", "elapsed": 0.0, "index": 0, "rows": 0, "move_started": False,
     "missing": 0.0, "encounter_started": False, "combat_entered": False, "ready_at": None}
HANDLE = None

def log(message):
    unreal.log("%s %s" % (PREFIX, message))

def comp(actor, class_name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent)
                 if c.get_class().get_name() == class_name), None)

def vec(v):
    return "%.2f,%.2f,%.2f" % (v.x, v.y, v.z)

def dist(a, b):
    dx, dy, dz = a.x - b.x, a.y - b.y, a.z - b.z
    return (dx * dx + dy * dy + dz * dz) ** 0.5

def names_for_guard(guard):
    try:
        return list(guard.get_trace_socket_names())
    except Exception:
        out = unreal.Array(unreal.Name)
        guard.get_trace_socket_names(out)
        return list(out)

def fallback_names_for_guard(guard):
    try:
        return list(guard.get_fallback_trace_socket_names())
    except Exception:
        out = unreal.Array(unreal.Name)
        guard.get_fallback_trace_socket_names(out)
        return list(out)

def finish():
    global HANDLE
    if HANDLE:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    log("RESULT frames=%d" % S["rows"])
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    unreal.SystemLibrary.quit_editor()

def tick(dt):
    S["elapsed"] += dt
    if S["phase"] == "start":
        if S["elapsed"] >= 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase="sample", elapsed=0.0)
        return
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if not world:
        return
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                 if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)
    if not boss:
        S["missing"] += dt
        if S["missing"] > 30.0:
            log("FAIL missing BP_ExampleGreatSwordBoss_C after 30s")
            finish()
        return
    look = comp(boss, "RPGBossLook")
    tracker = comp(boss, "RPGAttackTracker")
    guard = comp(boss, "RPGTraceGuard")
    encounter = comp(boss, "RPGBossEncounter")
    if not (look and tracker and guard and encounter and look.get_sword_component()):
        S["missing"] += dt
        if S["missing"] > 30.0:
            log("FAIL missing RPGBossLook sword/RPGAttackTracker/RPGTraceGuard/RPGBossEncounter after 30s")
            finish()
        return
    S["missing"] = 0.0
    if not S["encounter_started"]:
        encounter.wake()
        encounter.hold_for_test(True)
        S["encounter_started"] = True
        log("ENCOUNTER_WAKE requested hold_for_test=true")
        return
    if encounter.is_dormant() or encounter.is_waking():
        return
    if not S["combat_entered"]:
        entered = tracker.enter_combat()
        S["combat_entered"] = True
        S["ready_at"] = S["elapsed"] + 1.0
        log("ENTER_COMBAT result=%s; waiting 1s before sampling" % entered)
        return
    if S["elapsed"] < S["ready_at"]:
        return
    stage, move, start_method, duration = SEQUENCE[S["index"]]
    if not S["move_started"]:
        log("STAGE %s move=%s" % (stage, move or "none"))
        if move:
            if start_method == "ability":
                started = tracker.start_move(move, True)
            else:
                started = tracker.play_move_montage_for_test(move)
            log("MOVE_REQUEST %s method=%s started=%s" % (move, start_method, started))
        S["move_started"] = True
    sword = look.get_sword_component()
    body = look.get_body_component()
    pack_body = next(iter(boss.get_components_by_class(unreal.SkeletalMeshComponent)), None)
    hand = pack_body.get_socket_location(unreal.Name("hand_r")) if pack_body else boss.get_actor_location()
    grip_socket = next((n for n in ("Grip", "grip", "SwordGrip", "Sword_Grip") if sword.does_socket_exist(unreal.Name(n))), None)
    source = guard.get_trace_source_component()
    live_names = names_for_guard(guard)
    fallback_source = guard.get_fallback_trace_source_component()
    fallback_names = fallback_names_for_guard(guard)
    trace_names = [n for n in live_names if str(n).startswith("Trace_")] if source and source.get_name() == sword.get_name() else []
    trace_names.sort(key=lambda n: int(str(n).split("_", 1)[1]) if str(n).split("_", 1)[1].isdigit() else -1)
    grip = sword.get_socket_location(unreal.Name(grip_socket)) if grip_socket else sword.get_world_location()
    tip_socket = "BladeEnd" if sword.does_socket_exist(unreal.Name("BladeEnd")) else (str(trace_names[-1]) if trace_names else None)
    tip = sword.get_socket_location(unreal.Name(tip_socket)) if tip_socket else sword.get_world_location()
    source_name = source.get_name() if source else "None"
    if S["rows"] == 0:
        try:
            static_mesh = sword.get_editor_property("static_mesh")
            socket_names = [str(n) for n in sword.get_all_socket_names()]
            log("ASSET_SOCKETS count=%d names=%s" % (len(socket_names), ",".join(socket_names)))
        except Exception as error:
            log("ASSET_SOCKETS unavailable=%s" % error)
    pack_points = []
    for n in live_names:
        if source and source.does_socket_exist(n):
            pack_points.append((str(n), source.get_socket_location(n)))
    fallback_points = []
    for n in fallback_names:
        if fallback_source and fallback_source.does_socket_exist(n):
            fallback_points.append((str(n), fallback_source.get_socket_location(n)))
    pairs = (("BladeStart", "BladeStart", "Trace_0"),
             ("MiddleSocket", "MiddleSocket", "Trace_1"),
             ("BladeEnd", "BladeEnd", "Trace_2"))
    baseline_offsets = ["%s=%.2f" % (old_name, dist(old_point, sword.get_socket_location(unreal.Name(visual_name))))
                        for old_name, old_point in fallback_points
                        for source_name, visual_name, _ in pairs if old_name == source_name and sword.does_socket_exist(unreal.Name(visual_name))]
    live_offsets = ["%s=%.2f" % (live_name, dist(source.get_socket_location(unreal.Name(live_name)), sword.get_socket_location(unreal.Name(visual_name))))
                    for _, visual_name, live_name in pairs if source and source.get_name() == sword.get_name()
                    and source.does_socket_exist(unreal.Name(live_name)) and sword.does_socket_exist(unreal.Name(visual_name))]
    try:
        hand_rot = pack_body.get_socket_rotation(unreal.Name("hand_r")) if pack_body else unreal.Rotator()
        grip_rot = sword.get_socket_rotation(unreal.Name(grip_socket)) if grip_socket else sword.get_world_rotation()
        delta_rot = unreal.MathLibrary.normalized_delta_rotator(grip_rot, hand_rot)
        angles = "%.2f,%.2f,%.2f" % (delta_rot.roll, delta_rot.pitch, delta_rot.yaw)
    except Exception as error:
        angles = "UNAVAILABLE:%s" % error
    nearest = min((dist(hand, p), name, p) for name, p in pack_points) if pack_points else (float("nan"), "none", hand)
    pack_points_text = ";".join("%s=(%s)" % (name, vec(point)) for name, point in pack_points)
    tip_to_trace = min((dist(tip, point) for _, point in pack_points), default=float("nan"))
    fallback_text = ";".join("%s=(%s)" % (name, vec(point)) for name, point in fallback_points)
    log("WORLD stage=%s frame=%d hand_component=%s hand_r=(%s) grip_socket=%s grip=(%s) tip_socket=%s tip=(%s) trace_source=%s trace_sockets=%s trace_world=%s fallback_source=%s fallback_sockets=%s fallback_world=%s baseline_pair_cm=%s live_pair_cm=%s nearest_trace=%s nearest_hand_cm=%.2f OFFSET_CM hand_to_grip=%.2f tip_to_trace=%.2f hand_grip_rot_delta_rpy=(%s)" %
        (stage, S["rows"], pack_body.get_name() if pack_body else "None", vec(hand), grip_socket or "pivot", vec(grip), tip_socket or "pivot", vec(tip), source_name, ",".join(map(str, live_names)),
         pack_points_text, fallback_source.get_name() if fallback_source else "None", ",".join(map(str, fallback_names)), fallback_text,
         ";".join(baseline_offsets), ";".join(live_offsets), nearest[1], nearest[0], dist(hand, grip), tip_to_trace, angles))
    S["rows"] += 1
    if S["elapsed"] >= duration:
        S["index"] += 1
        if S["index"] >= len(SEQUENCE):
            finish()
        else:
            S.update(elapsed=0.0, move_started=False)

def safe_tick(dt):
    try:
        tick(dt)
    except Exception as error:
        import traceback
        log("FAIL exception=%s\n%s" % (error, traceback.format_exc()))
        finish()

HANDLE = unreal.register_slate_post_tick_callback(safe_tick)
