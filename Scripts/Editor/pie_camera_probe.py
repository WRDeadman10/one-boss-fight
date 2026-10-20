"""
PIE probe of the pack player's camera: prints the spring arm and camera component settings, then samples camera height above the floor, camera pitch and the control
pitch every 0.2 s through three phases next to the pack boss: free camera (walking and dodging close to the boss), lock-on (IA_LockOn toggled), lock-on with dodges.
Reports min / max per phase so "the camera goes to the ground" shows up as a number. Log prefix [CamPie]. Open L_SevarogArena first; run with Scripts/run_in_editor.py
(editor throttling off).
"""
import unreal

log = lambda m: unreal.log("[CamPie] " + m)
ACTIONS = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
state = {"phase": "start", "t": 0.0, "stage": 0, "stage_t0": 0.0, "samples": [], "sample_t": 0.0, "heal_t": 0.0, "dumped": False, "lock_pressed": False, "key": {}}
handle = None
# (name, seconds, distance to the boss in cm or None to keep the fight distance)
STAGES = [("lock-on at 250 cm", 5.0, 250), ("lock-on at 450 cm", 5.0, 450), ("lock-on at 800 cm", 5.0, 800), ("lock-on, dodging near the boss", 8.0, None)]


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def key(pc, name, down):
    if state["key"].get(name, False) != down:
        state["key"][name] = down
        unreal.RPGInputTestUtils.set_key_down(pc, name, down)


def finish(reason):
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def dump(pawn):
    for c in pawn.get_components_by_class(unreal.SpringArmComponent):
        log("spring arm %s: arm length %.0f, socket offset %s, target offset %s, collision test %s, probe size %.1f, pawn control rotation %s, lag %s speed %.1f, rotation lag %s speed %.1f, rel loc %s rel rot %s" % (
            c.get_name(), c.get_editor_property("target_arm_length"), c.get_editor_property("socket_offset"), c.get_editor_property("target_offset"), c.get_editor_property("do_collision_test"),
            c.get_editor_property("probe_size"), c.get_editor_property("use_pawn_control_rotation"), c.get_editor_property("enable_camera_lag"), c.get_editor_property("camera_lag_speed"),
            c.get_editor_property("enable_camera_rotation_lag"), c.get_editor_property("camera_rotation_lag_speed"), c.get_editor_property("relative_location"), c.get_editor_property("relative_rotation")))
    for c in pawn.get_components_by_class(unreal.CameraComponent):
        log("camera %s: fov %.0f rel loc %s rel rot %s" % (c.get_name(), c.get_editor_property("field_of_view"), c.get_editor_property("relative_location"), c.get_editor_property("relative_rotation")))


def report(name):
    s = state["samples"]
    if not s:
        return
    hs = [x[0] for x in s]
    ps = [x[1] for x in s]
    cp = [x[2] for x in s]
    log("[%s] camera height above floor: min %.0f max %.0f cm; camera pitch: min %.1f max %.1f; control pitch: min %.1f max %.1f; samples %d" % (name, min(hs), max(hs), min(ps), max(ps), min(cp), max(cp), len(s)))
    head = [x[3] for x in s]
    feet = [x[4] for x in s]
    log("   boss head (3 m) vertical angle from the screen centre: %.1f to %.1f deg; boss feet: %.1f to %.1f deg; the view reaches +-29 deg (16:9, 90 deg wide)" % (min(head), max(head), min(feet), max(feet)))


def _tick(dt):
    s = state
    s["t"] += dt
    if s["t"] > 120:
        finish("timeout")
        return
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait", t=0.0)
        return
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next(iter([a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"]), None) if w else None
    if pawn is None or boss is None:
        return
    cam = unreal.GameplayStatics.get_player_camera_manager(w, 0)
    if not s["dumped"]:
        s["dumped"] = True
        dump(pawn)
    s["heal_t"] += dt
    if s["heal_t"] > 0.4:
        s["heal_t"] = 0.0
        t = unreal.GameplayTag()
        t.import_text('(TagName="Attribute.Health")')
        comp(pawn, "BP_AttributesComponent_C").call_method("Set Current Attribute Value", args=(t, 100.0))
    if s["phase"] == "wait":
        if s["t"] > 9.0:
            s.update(phase="run", t=0.0, stage=0, stage_t0=0.0)
            log("== stage: %s" % STAGES[0][0])
        return
    d = boss.get_actor_location() - pawn.get_actor_location()
    flat = unreal.Vector(d.x, d.y, 0)
    name, length, dist = STAGES[s["stage"]]
    if dist is not None:
        # stand dist cm from the boss, on the side the player came from, once at the start of the stage and then hold the position
        if s["t"] - s["stage_t0"] < 0.2 or s.get("hold_stage") != s["stage"]:
            s["hold_stage"] = s["stage"]
            side = (pawn.get_actor_location() - boss.get_actor_location())
            side = unreal.Vector(side.x, side.y, 0).normal()
            pawn.set_actor_location(boss.get_actor_location() + side * dist + unreal.Vector(0, 0, 10 - boss.get_actor_location().z + 100), False, True)
    elif flat.length() > 260:
        pawn.add_movement_input(flat.normal(), 1.0, False)
    # the control rotation looks at the boss in the free stage so the camera sits behind the player
    name, length, dist = STAGES[s["stage"]]
    if name.startswith("lock-on") and not s["lock_pressed"]:
        s["lock_pressed"] = True
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(ACTIONS + "IA_LockOn"), unreal.Vector(1, 0, 0))
        log("   lock-on pressed")
    if s["lock_pressed"] and s["t"] - s["stage_t0"] < 0.3:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(ACTIONS + "IA_LockOn"), unreal.Vector(1, 0, 0))
    if "dodging" in name:
        ts = (s["t"] - s["stage_t0"]) % 2.0
        key(pc, "Gamepad_FaceButton_Right", 0.0 <= ts < 0.08)
    s["sample_t"] += dt
    if s["sample_t"] >= 0.2:
        s["sample_t"] = 0.0
        loc = cam.get_camera_location()
        rot = cam.get_camera_rotation()
        floor_z = 0.0  # the arena floor top sits at z = 0
        import math
        def vangle(point):  # vertical angle of a world point relative to the camera's pitch, degrees (positive = above the screen centre)
            v = point - loc
            horiz = math.hypot(v.x, v.y)
            return math.degrees(math.atan2(v.z, horiz)) - rot.pitch
        b = boss.get_actor_location()
        s["samples"].append((loc.z - floor_z, rot.pitch, pc.get_control_rotation().pitch, vangle(unreal.Vector(b.x, b.y, 300.0)), vangle(unreal.Vector(b.x, b.y, 0.0))))
    if s["t"] - s["stage_t0"] > length:
        unreal.SystemLibrary.execute_console_command(w, "HighResShot 960x540")
        report(name)
        s["samples"] = []
        s["stage"] += 1
        if s["stage"] >= len(STAGES):
            finish("done")
            return
        s["stage_t0"] = s["t"]
        log("== stage: %s" % STAGES[s["stage"]][0])


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
handle = unreal.register_slate_post_tick_callback(tick)
