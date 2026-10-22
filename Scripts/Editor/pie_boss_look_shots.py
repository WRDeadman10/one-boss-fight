"""
Pictures of the boss with its final look (G2-15) in PIE, for the owner's eye: standing (front, side), in the kneel of a stance break (front, side) and in the death clip (front, 1.0 s and 3.0 s after the kill). The boss is held awake and
rotated to yaw 0, the player (hidden) stands 330 cm in front of it (or beside it), the camera 300 cm behind the player and looks at it. Files: Saved/Screenshots/WindowsEditor/ (HighResShot 1280x720); log prefix [LookShots] lists the order and the time of each shot. No checks.
Run pie_debug_overlay.py once after an editor start first.
"""
import unreal

log = lambda m: unreal.log("[LookShots] " + m)
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None, "shots": 0}
handle = None
VIEWS = {"front": (200.0, 0.0, 180.0), "side": (0.0, 200.0, -90.0)}  # the third person camera sits about 300 cm behind the pawn; the pawn is hidden for the shots


def comp(actor, name):
    if actor is None:
        return None
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def actors():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return w, pc, pawn, boss


def look_from(view, boss_pos):
    w, pc, pawn, boss = actors()
    dx, dy, yaw = VIEWS[view]
    pawn.set_actor_location_and_rotation(unreal.Vector(boss_pos.x + dx, boss_pos.y + dy, boss_pos.z), unreal.Rotator(0, 0, yaw), False, True)
    pc.set_control_rotation(unreal.Rotator(roll=0, pitch=-4, yaw=yaw))
    pawn.set_actor_hidden_in_game(True)
    for attached in pawn.get_attached_actors():
        attached.set_actor_hidden_in_game(True)


def shoot(label):
    w, pc, pawn, boss = actors()
    unreal.SystemLibrary.execute_console_command(w, "HighResShot 1280x720")
    S["shots"] += 1
    log("shot %d: %s" % (S["shots"], label))


def script():
    w, pc, pawn, boss = actors()
    enc = comp(boss, "RPGBossEncounter")
    enc.reset_for_test()
    yield 0.8
    w, pc, pawn, boss = actors()
    enc = comp(boss, "RPGBossEncounter")
    enc.wake()
    enc.hold_for_test(True)
    comp(boss, "RPGCombatDebug").debug_refill_player()
    comp(boss, "RPGAttackTracker").enter_combat()
    yield 2.5
    w, pc, pawn, boss = actors()
    boss.set_actor_rotation(unreal.Rotator(0, 0, 0), False)
    pos = boss.get_actor_location()
    for view in ("front", "side"):
        look_from(view, pos)
        yield 0.7
        shoot("standing %s" % view)
        yield 0.7
    # the kneel
    comp(boss, "RPGBossStagger").set_cooldown_for_test(0.0)
    comp(boss, "RPGBossStagger").force_break_for_test()
    t0 = S["now"]
    while comp(actors()[3], "RPGBossStagger").get_clip_stage_name() != "down" and S["now"] - t0 < 4.0:
        yield 0.1
    yield 0.8
    for view in ("front", "side"):
        look_from(view, pos)
        yield 0.7
        shoot("kneel %s" % view)
        yield 0.7
    # the get-up ends, then the death
    t0 = S["now"]
    while comp(actors()[3], "RPGBossStagger").is_staggered() and S["now"] - t0 < 9.0:
        yield 0.2
    yield 0.8
    look_from("front", pos)
    yield 0.5
    comp(actors()[3], "RPGCombatDebug").debug_kill_boss()
    t_kill = S["now"]
    for at in (1.0, 3.0):
        while S["now"] - t_kill < at:
            yield 0.05
        look_from("front", pos)
        yield 0.3
        shoot("death clip %.1f s after the kill" % (S["now"] - t_kill))


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("done, %d shots" % S["shots"])
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = S
    s["t"] += dt
    s["now"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w, pc, pawn, boss = actors()
    if s["gen"] is not None and (pawn is None) and s["now"] > 5.0:
        pass
    if s["wait"] > 0:
        s["wait"] -= dt
        return
    if s["gen"] is None:
        if pawn is None or boss is None or s["t"] < 9.0:
            return
        s["gen"] = script()
    try:
        s["wait"] = float(next(s["gen"]))
    except StopIteration:
        finish()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
