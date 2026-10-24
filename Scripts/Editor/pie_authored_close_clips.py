"""B10 authored close clips: validates the live pack-ability swap and the A1/A3 tracker timing source. Log prefix [AuthoredClose]."""
import unreal

log = lambda text: unreal.log("[AuthoredClose] " + text)
results = []
state = {"phase": "start", "now": 0.0, "wake": 0.0, "t": 0.0, "finished": False}
handle = None


def check(name, ok, detail=""):
    results.append(bool(ok))
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def component(actor, name):
    return next((item for item in actor.get_components_by_class(unreal.ActorComponent)
                 if item.get_class().get_name() == name), None) if actor else None


def parts():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    boss = next((actor for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                 if actor.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if world else None
    return (component(boss, "RPGBossCloseClipSwap"), component(boss, "RPGAttackTracker"),
            component(boss, "RPGBossEncounter"), component(boss, "RPGCombatDebug"), boss)


def scenario():
    yield 3.0
    swap, tracker, encounter, debug, boss = parts()
    check("A0 live swap component exists", swap is not None)
    check("A0 tracker exists", tracker is not None)
    check("A0 encounter and debug exist", encounter is not None and debug is not None)
    if not swap or not tracker or not encounter or not debug or not boss:
        return
    encounter.wake()
    encounter.hold_for_test(True)
    debug.debug_refill_player()
    tracker.enter_combat()
    yield 1.0
    detail = swap.apply_now_for_test()
    check("A1 swap applies to the validated live pack ability", swap.is_applied(), detail)
    check("A1 exactly A1, A3a and A3b swap", swap.get_applied_entry_count() == 3, "entries %d" % swap.get_applied_entry_count())
    check("A1 result identifies the retained pack A1b", "A1b remains pack" in swap.get_last_result(), swap.get_last_result())

    expected = {"A1": (0.33, 0.35, 0.50, 1.20), "A3a": (0.38, 0.40, 0.60, 0.80), "A3b": (0.13, 0.15, 0.40, 1.3333)}
    for move, values in expected.items():
        # UFUNCTIONs: PlayMoveMontageForTest, GetCommitCount, GetLastCommitPosition and GetLastActiveStartPosition (RPGAttackTracker.h).
        commits = tracker.get_commit_count()
        # A3b is a branch stage: the tracker denies it (and stops the montage) unless the player stands in the boss's frontal cone and in range at its start, so the player is put 180 cm in front of the boss for every move
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
        front = boss.get_actor_location() + boss.get_actor_forward_vector() * 180.0
        pawn.set_actor_location_and_rotation(unreal.Vector(front.x, front.y, boss.get_actor_location().z), unreal.Rotator(0, 0, 0), False, True)
        yield 0.1
        started = tracker.play_move_montage_for_test(move)
        check("A2 %s authored montage starts" % move, started)
        yield 0.05
        check("A2 %s keeps authored windup unscaled" % move, abs(tracker.get_telegraph_rate() - 1.0) < 0.01,
              "rate %.3f" % tracker.get_telegraph_rate())
        yield values[0] + 0.05
        check("A2 %s commits at authored %.2f seconds" % (move, values[0]), tracker.get_commit_count() == commits + 1 and abs(tracker.get_last_commit_position() - values[0]) < 0.12,
              "commit %.3f" % tracker.get_last_commit_position())
        yield max(0.05, values[1] - values[0]) + 0.08
        check("A2 %s opens at authored %.2f seconds" % (move, values[1]), abs(tracker.get_last_active_start_position() - values[1]) < 0.12,
              "active %.3f, recovery %.4f" % (tracker.get_last_active_start_position(), values[3]))
        yield max(0.10, values[3] - values[1]) + 0.25

    restores = swap.get_restore_count()
    swap.set_enabled_for_test(False)
    yield 0.1
    check("A3 test disable restores the pack entries", not swap.is_applied() and swap.get_restore_count() == restores + 1, "restores %d" % swap.get_restore_count())
    swap.set_enabled_for_test(True)
    detail = swap.apply_now_for_test()
    check("A3 enable safely reapplies", swap.is_applied() and swap.get_applied_entry_count() == 3, detail)


def finish():
    global handle
    if state["finished"]:
        return
    state["finished"] = True
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    log("RESULT %d/%d passed" % (sum(results), len(results)))


def tick(delta):
    try:
        state["now"] += delta
        if state["phase"] == "start":
            state["t"] += delta
            if state["t"] > 0.5:
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                state["phase"] = "wait"
            return
        if state["phase"] == "wait":
            if all(parts()[:4]):
                state["phase"] = "run"
            return
        if state["phase"] == "run" and state["now"] >= state["wake"]:
            try:
                state["wake"] = state["now"] + float(next(generator) or 0.0)
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
