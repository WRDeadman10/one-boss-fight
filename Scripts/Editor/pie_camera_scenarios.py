"""Camera scenarios after the rig (log prefix [CamScn]): C1 death and ragdoll, C2 dodge roll with the camera low, C3 standing against the arena wall with the camera behind towards the wall, C4 jump and land with the
camera low. A camera is clipped when the floor clearance below it is under the probe size (34 cm) or its sphere sits inside blocking geometry. The boss is held so it cannot interfere. Needs a warm-up PIE first."""
import math
import unreal

log = lambda m: unreal.log("[CamScn] " + m)
PROBE = 34.0
results = []
S = {"phase": "start", "t": 0.0, "i": 0, "next": 0.0, "min": 1e9, "clipped": 0, "n": 0, "mem": {}}
handle = None


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def trace(w, a, b):
    hit = unreal.SystemLibrary.line_trace_single(w, a, b, unreal.TraceTypeQuery.TRACE_TYPE_QUERY2, False, [], unreal.DrawDebugTrace.NONE, True)
    if hit is None:
        return None
    t = hit.to_tuple()
    return t[5] if t[0] else None


def inside(w, loc, r):
    hit = unreal.SystemLibrary.sphere_trace_single(w, loc, unreal.Vector(loc.x, loc.y, loc.z + 0.1), r, unreal.TraceTypeQuery.TRACE_TYPE_QUERY2, False, [], unreal.DrawDebugTrace.NONE, True)
    if hit is None:
        return False
    t = hit.to_tuple()
    return bool(t[0] and t[1])


def sampler_reset():
    S.update(min=1e9, clipped=0, n=0)


def sampler(w, pc, pawn):
    cam = pc.player_camera_manager.get_camera_location()
    fl = trace(w, unreal.Vector(cam.x, cam.y, cam.z + 300), unreal.Vector(cam.x, cam.y, cam.z - 2000))
    clear = cam.z - fl.z if fl is not None else None
    S["n"] += 1
    if S["mem"].get("verbose") and S["n"] % 8 == 0:
        hit = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(cam.x, cam.y, cam.z + 300), unreal.Vector(cam.x, cam.y, cam.z - 2000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY2, False, [], unreal.DrawDebugTrace.NONE, True)
        who = hit.to_tuple()[9].get_name() if hit is not None and hit.to_tuple()[9] else None
        arm = pawn.get_components_by_class(unreal.SpringArmComponent)[0]
        log("  sample %d: camera z %.0f, floor hit %s by %s, arm origin z %.0f, actor z %.0f, arm parent %s probe %.0f len %.0f socket %s collision %s pitch %.0f" % (S["n"], cam.z, "%.0f" % fl.z if fl is not None else None, who, arm.get_world_location().z, pawn.get_actor_location().z, arm.get_attach_parent().get_name(), arm.get_editor_property("probe_size"), arm.get_editor_property("target_arm_length"), arm.get_editor_property("socket_offset").z, arm.get_editor_property("do_collision_test"), pc.player_camera_manager.get_camera_rotation().pitch))
    if clear is not None:
        S["min"] = min(S["min"], clear)
    # 2 cm tolerance: the arm parks the sphere exactly one probe radius off the surface
    if (clear is not None and clear < PROBE - 2.0) or inside(w, cam, PROBE - 4.0):
        S["clipped"] += 1


def parts(boss):
    return comp(boss, "RPGBossEncounter"), comp(boss, "RPGCombatDebug")


def s_setup(w, pc, pawn, boss):
    enc, dbg = parts(boss)
    enc.hold_for_test(True)
    dbg.debug_refill_player()
    pawn.set_actor_location_and_rotation(unreal.Vector(900, 0, 120), unreal.Rotator(0, 0, 0), False, True)
    pc.set_control_rotation(unreal.Rotator(roll=0, pitch=20, yaw=0))


def s_c1_start(w, pc, pawn, boss):
    sampler_reset()
    S["mem"]["on"] = True
    S["mem"]["verbose"] = True
    parts(boss)[1].debug_set_player_health(0.0)


def s_c1_check(w, pc, pawn, boss):
    S["mem"]["on"] = False
    S["mem"]["verbose"] = False
    check("C1 death: camera stays clear of the floor for 5 s (%d samples)" % S["n"], S["clipped"] == 0 and S["n"] > 20, "clipped %d, minimum clearance %.0f cm" % (S["clipped"], S["min"]))


def s_c2_prep(w, pc, pawn, boss):
    enc, dbg = parts(boss)
    dbg.debug_refill_player()
    pawn.set_actor_location_and_rotation(unreal.Vector(900, 0, 120), unreal.Rotator(0, 0, 0), False, True)
    pc.set_control_rotation(unreal.Rotator(roll=0, pitch=20, yaw=0))


def s_c2_start(w, pc, pawn, boss):
    sampler_reset()
    S["mem"]["on"] = True
    unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_FaceButton_Right", True)


def s_c2_release(w, pc, pawn, boss):
    unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_FaceButton_Right", False)


def s_c2_check(w, pc, pawn, boss):
    S["mem"]["on"] = False
    check("C2 dodge roll with the camera low (%d samples)" % S["n"], S["clipped"] == 0 and S["n"] > 20, "clipped %d, minimum clearance %.0f cm" % (S["clipped"], S["min"]))


def s_c3_start(w, pc, pawn, boss):
    # find the wall: trace along +Y from the middle of the arena at head height
    wall = trace(w, unreal.Vector(0, 0, 120), unreal.Vector(0, 6000, 120))
    S["mem"]["wall"] = wall
    check("C3 a wall exists along +Y", wall is not None, str(wall))
    if wall is None:
        return
    # the player stands 70 cm in front of the wall, looking away from it (towards -Y), so the camera, behind the player, points into the wall
    pawn.set_actor_location_and_rotation(unreal.Vector(wall.x, wall.y - 70, 120), unreal.Rotator(0, 0, -90), False, True)
    pc.set_control_rotation(unreal.Rotator(roll=0, pitch=10, yaw=-90))
    sampler_reset()
    S["mem"]["on"] = True


def s_c3_check(w, pc, pawn, boss):
    S["mem"]["on"] = False
    wall = S["mem"].get("wall")
    if wall is None:
        return
    cam = pc.player_camera_manager.get_camera_location()
    dist_to_wall = wall.y - cam.y
    check("C3 camera stays in front of the wall", dist_to_wall >= PROBE - 4.0, "camera %.0f cm from the wall plane (probe %.0f)" % (dist_to_wall, PROBE))
    check("C3 no clipping next to the wall (%d samples)" % S["n"], S["clipped"] == 0, "clipped %d, minimum clearance %.0f cm" % (S["clipped"], S["min"]))


def s_c4_prep(w, pc, pawn, boss):
    parts(boss)[1].debug_refill_player()
    pawn.set_actor_location_and_rotation(unreal.Vector(900, 0, 120), unreal.Rotator(0, 0, 0), False, True)
    pc.set_control_rotation(unreal.Rotator(roll=0, pitch=25, yaw=0))


def s_c4_start(w, pc, pawn, boss):
    sampler_reset()
    S["mem"]["on"] = True
    unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_FaceButton_Bottom", True)


def s_c4_release(w, pc, pawn, boss):
    unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_FaceButton_Bottom", False)


def s_c4_check(w, pc, pawn, boss):
    S["mem"]["on"] = False
    check("C4 jump and landing with the camera low (%d samples)" % S["n"], S["clipped"] == 0 and S["n"] > 20, "clipped %d, minimum clearance %.0f cm" % (S["clipped"], S["min"]))


STEPS = [
    (9.0, s_setup), (1.5, s_c1_start), (5.0, s_c1_check),
    (4.0, s_c2_prep), (1.5, s_c2_start), (0.12, s_c2_release), (2.0, s_c2_check),
    (0.5, s_c3_start), (2.0, s_c3_check),
    (0.5, s_c4_prep), (1.5, s_c4_start), (0.12, s_c4_release), (2.0, s_c4_check),
]


def _tick(dt):
    global handle
    s = S
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0, next=STEPS[0][0])
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is None or boss is None:
        return
    if s["mem"].get("on"):
        sampler(w, pc, pawn)
    if s["t"] < s["next"]:
        return
    if s["i"] >= len(STEPS):
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("RESULT %d/%d passed" % (sum(1 for r in results if r), len(results)))
        return
    _, fn = STEPS[s["i"]]
    try:
        fn(w, pc, pawn, boss)
    except Exception:
        import traceback
        check("step %d (%s) raised" % (s["i"], fn.__name__), False, traceback.format_exc())
    s["i"] += 1
    s["t"] = 0.0
    s["next"] = STEPS[s["i"]][0] if s["i"] < len(STEPS) else 0.5


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
