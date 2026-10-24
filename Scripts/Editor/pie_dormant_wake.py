"""B11: authored dormant loop and wake gate. Exercises normal wake, direct attack veto, reset during wake, and death during wake. Log prefix [DormantWake]."""
import unreal

log = lambda message: unreal.log("[DormantWake] " + message)
results = []
state = {"phase": "start", "time": 0.0, "index": 0, "next": 0.0}
handle = None


def check(name, ok, detail=""):
    results.append(bool(ok))
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def component(actor, class_name):
    return next((item for item in actor.get_components_by_class(unreal.ActorComponent) if item.get_class().get_name() == class_name), None)


def parts(pawn, boss):
    return component(boss, "RPGBossEncounter"), component(boss, "RPGBossDormantWake"), component(boss, "RPGAttackTracker"), component(boss, "RPGCombatDebug"), component(boss, "RPGBossDeath")


def montage(debug):
    return debug.debug_boss_montage_anim_name() if debug else ""


def place_far(pawn, boss):
    origin = boss.get_actor_location()
    pawn.set_actor_location_and_rotation(origin + unreal.Vector(1600.0, 0.0, 20.0), unreal.Rotator(0.0, 0.0, 180.0), False, True)


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    log("RESULT %d/%d passed" % (sum(results), len(results)))


def run_step(pawn, boss):
    encounter, clips, tracker, debug, death = parts(pawn, boss)
    if not all((encounter, clips, tracker, debug, death)):
        check("B11 components attach", False, "enc=%s clips=%s tracker=%s debug=%s death=%s" % (encounter, clips, tracker, debug, death))
        return -1
    index = state["index"]
    state["index"] += 1
    if index == 0:
        place_far(pawn, boss)
        encounter.reset_for_test()
        return 0.5
    if index == 1:
        check("D1 reset enters dormant", encounter.is_dormant())
        check("D2 dormant loop plays authored idle", clips.get_stage_name() == "dormant" and montage(debug) == "AN_Boss01_DormantIdle", "%s / %s" % (clips.get_stage_name(), montage(debug)))
        encounter.wake()
        check("W1 wake gate starts", encounter.is_waking() and clips.get_stage_name() == "wake", "%s" % clips.get_stage_name())
        check("W2 a direct close start is rejected during wake", not tracker.start_move("Close"))
        return 4.0
    if index == 2:
        check("W3 wake completes", not encounter.is_waking() and clips.get_stage_name() != "wake", "%s" % clips.get_stage_name())
        place_far(pawn, boss)
        encounter.reset_for_test()
        return 0.5
    if index == 3:
        encounter.wake()
        return 0.15
    if index == 4:
        check("I1 reset reaches a live wake", encounter.is_waking())
        encounter.reset_for_test()
        return 0.4
    if index == 5:
        check("I2 reset cancels wake", not encounter.is_waking() and encounter.is_dormant(), "%s / %s" % (encounter.is_waking(), clips.get_stage_name()))
        check("I3 reset restores only the dormant loop", clips.get_stage_name() == "dormant" and montage(debug) == "AN_Boss01_DormantIdle", montage(debug))
        encounter.wake()
        return 0.15
    if index == 6:
        check("I4 death scenario starts while waking", encounter.is_waking())
        debug.debug_kill_boss()
        return 0.5
    check("I5 death cancels wake", not encounter.is_waking() and clips.get_stage_name() != "wake", "%s / %s" % (death.get_death_state_name(), clips.get_stage_name()))
    check("I6 death state is active", death.get_death_state_name() in ("dying", "dead"), death.get_death_state_name())
    return -1


def tick(delta):
    try:
        state["time"] += delta
        if state["phase"] == "start":
            if state["time"] > 0.5:
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                state.update(phase="play", time=0.0, next=8.0)
            return
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        controller = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
        pawn = controller.get_controlled_pawn() if controller else None
        boss = next((actor for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character) if actor.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if world else None
        if not pawn or not boss:
            if state["time"] > 35.0:
                check("PIE actors arrive", False)
                finish()
            return
        if state["time"] < state["next"]:
            return
        delay = run_step(pawn, boss)
        if delay < 0:
            finish()
            return
        state["time"] = 0.0
        state["next"] = delay
    except Exception:
        import traceback
        check("driver step", False, traceback.format_exc())
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
