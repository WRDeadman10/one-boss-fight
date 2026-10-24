"""Q13: close-stage telegraph coverage (rpg.CloseTelegraph, default 0.4 since 2026-10-24). Logs [Telegraph] and restores the value the session had at the start."""
import unreal

log = lambda message: unreal.log("[Telegraph] " + message)
results = []
S = {"phase": "start", "now": 0.0, "wake": 0.0, "t": 0.0, "finished": False, "initial": 0.4}
handle = None


def check(name, ok, detail=""):
    results.append(bool(ok))
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def close(a, b, tolerance):
    return abs(a - b) <= tolerance


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def console(command):
    w = world()
    if w:
        unreal.SystemLibrary.execute_console_command(w, command)


def component(actor, name):
    if actor is None:
        return None
    return next((item for item in actor.get_components_by_class(unreal.ActorComponent)
                 if item.get_class().get_name() == name), None)


def parts():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((actor for actor in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)
                 if actor.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return (component(boss, "RPGAttackTracker"), component(boss, "RPGBossEncounter"),
            component(boss, "RPGCombatDebug"), pawn, boss)


def front(pawn, boss):
    # A1b and A3b are branch stages: the tracker stops them unless the player stands in the boss's frontal cone and in range at the stage start
    place = boss.get_actor_location() + boss.get_actor_forward_vector() * 180.0
    pawn.set_actor_location_and_rotation(unreal.Vector(place.x, place.y, boss.get_actor_location().z), unreal.Rotator(0, 0, 0), False, True)


def start(tracker, move):
    ok = tracker.play_move_montage_for_test(move)
    check("%s montage starts" % move, ok)
    return ok


def settle(seconds):
    yield seconds


def scenario():
    yield 3.0
    tracker, encounter, debug, pawn, boss = parts()
    check("T0 tracker component exists", tracker is not None)
    check("T0 encounter component exists", encounter is not None)
    check("T0 debug component exists", debug is not None)
    S["initial"] = unreal.SystemLibrary.get_console_variable_float_value("rpg.CloseTelegraph")
    check("T0 the default is 0.4 (the Freeze's A3 windup, owner 2026-10-24)", close(S["initial"], 0.4, 0.001), "value %.3f" % S["initial"])
    if tracker is None or encounter is None or debug is None:
        return
    encounter.wake()
    encounter.hold_for_test(True)
    debug.debug_refill_player()
    yield 0.3

    console("rpg.CloseTelegraph 0")
    if start(tracker, "A3a"):
        yield 0.05
        check("T1 cvar zero keeps A3a rate one", close(tracker.get_telegraph_rate(), 1.0, 0.01), "rate %.3f" % tracker.get_telegraph_rate())
        yield from settle(0.35)
        windup = tracker.get_last_stage_windup_seconds()
        check("T1 cvar zero keeps the authored A3a windup (0.40 s since the authored clips, B10)", close(windup, 0.40, 0.06), "windup %.3f" % windup)
    yield from settle(0.8)

    console("rpg.CloseTelegraph 0.4")
    if start(tracker, "A3a"):
        yield 0.05
        rate = tracker.get_telegraph_rate()
        check("T2 authored A3a is not stretched by the cvar (its own windup is already 0.40 s)", close(rate, 1.0, 0.01), "rate %.3f" % rate)
        yield from settle(0.55)
        windup = tracker.get_last_stage_windup_seconds()
        check("T2 authored A3a windup stays 0.40 seconds", close(windup, 0.40, 0.06), "windup %.3f" % windup)
        check("T2 authored A3a rate is one after active", close(tracker.get_telegraph_rate(), 1.0, 0.01), "rate %.3f" % tracker.get_telegraph_rate())
    yield from settle(0.8)

    # A1b is still the pack montage (no authored clip yet): the cvar stretches it to the 0.35 s cap
    front(pawn, boss)
    yield 0.1
    if start(tracker, "A1b"):
        yield 0.05
        rate = tracker.get_telegraph_rate()
        check("T2b pack A1b slows before active", rate < 1.0, "rate %.3f" % rate)
        yield from settle(0.55)
        windup = tracker.get_last_stage_windup_seconds()
        check("T2b pack A1b reaches the 0.35 second cap", close(windup, 0.35, 0.06), "windup %.3f" % windup)
        check("T2b pack A1b restores rate after active", close(tracker.get_telegraph_rate(), 1.0, 0.01), "rate %.3f" % tracker.get_telegraph_rate())
    yield from settle(1.0)

    if start(tracker, "A1"):
        yield 0.50
        windup = tracker.get_last_stage_windup_seconds()
        check("T3 A1 caps at 0.35 seconds", close(windup, 0.35, 0.06), "windup %.3f" % windup)
        check("T3 A1 restores its rate", close(tracker.get_telegraph_rate(), 1.0, 0.01), "rate %.3f" % tracker.get_telegraph_rate())
    yield from settle(1.0)

    if start(tracker, "A2"):
        yield 2.20
        windup = tracker.get_last_stage_windup_seconds()
        check("T4 A2 keeps its un-stretched windup", close(windup, 1.93, 0.12), "windup %.3f" % windup)
        check("T4 A2 never changes telegraph rate", close(tracker.get_telegraph_rate(), 1.0, 0.01), "rate %.3f" % tracker.get_telegraph_rate())
    yield from settle(1.0)

    front(pawn, boss)
    yield 0.1
    if start(tracker, "A1b"):
        yield 0.05
        check("T5 pack A1b is slowed before cvar reset", tracker.get_telegraph_rate() < 1.0, "rate %.3f" % tracker.get_telegraph_rate())
        console("rpg.CloseTelegraph 0")
        yield 0.15
        check("T5 cvar reset restores rate within 0.2 seconds", close(tracker.get_telegraph_rate(), 1.0, 0.01), "rate %.3f" % tracker.get_telegraph_rate())
    yield from settle(1.0)

    console("rpg.CloseTelegraph 0")
    if start(tracker, "A3a"):
        yield 0.05
        check("T6 final cvar reset leaves rate one", close(tracker.get_telegraph_rate(), 1.0, 0.01), "rate %.3f" % tracker.get_telegraph_rate())


def finish():
    global handle
    if S["finished"]:
        return
    S["finished"] = True
    try:
        console("rpg.CloseTelegraph %s" % S["initial"])  # the value the session had at the start (the default), never a silent 0 for the drivers that run after this one
    except Exception as error:
        log("cleanup console reset failed: %s" % error)
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    log("RESULT %d/%d passed" % (sum(1 for result in results if result), len(results)))


def tick(delta_seconds):
    try:
        S["now"] += delta_seconds
        if S["phase"] == "start":
            S["t"] += delta_seconds
            if S["t"] > 0.5:
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                S["phase"] = "wait"
            return
        if S["phase"] == "wait":
            tracker, encounter, debug, pawn, boss = parts()
            if tracker is None or encounter is None or debug is None or pawn is None or boss is None:
                return
            S["phase"] = "run"
            S["wake"] = S["now"]
            return
        if S["phase"] == "run" and S["now"] >= S["wake"]:
            try:
                wait_seconds = next(generator)
                S["wake"] = S["now"] + (float(wait_seconds) if wait_seconds else 0.0)
            except StopIteration:
                finish()
            except Exception:
                import traceback
                check("scenario raised", False, traceback.format_exc())
                finish()
    except Exception:
        import traceback
        check("tick raised", False, traceback.format_exc())
        finish()


generator = scenario()
handle = unreal.register_slate_post_tick_callback(tick)
