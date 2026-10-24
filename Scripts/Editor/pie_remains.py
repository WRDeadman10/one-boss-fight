"""Death-remains driver: kill through debug_kill_boss (health 0 and the pack's Ability.Dead, the path pie_boss_death uses; a single injected light attack is not reliable here: the boss has to be fully awake first), wait for the pack to destroy the boss, verify the statue forms, then retry. Log prefix [Remains]."""
import unreal

log = lambda text: unreal.log("[Remains] " + text)
state = {"phase": "start", "time": 0.0, "checks": [], "world": None, "released": False}
handle = None


def check(name, passed, detail=""):
    state["checks"].append(passed)
    log("%s %s %s" % ("PASS" if passed else "FAIL", name, detail))


def component(actor, class_name):
    return next((item for item in actor.get_components_by_class(unreal.ActorComponent)
                 if item.get_class().get_name() == class_name), None)


def boss(world):
    return next((actor for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                 if actor.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)


def remains(world):
    return [actor for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
            if actor.get_class().get_name() == "RPGBossRemains"]


def tags(*names):
    value = unreal.GameplayTagContainer()
    value.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % name for name in names))
    return value


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    passed = sum(1 for value in state["checks"] if value)
    log("RESULT %d/%d passed" % (passed, len(state["checks"])))


def tick(delta):
    try:
        state["time"] += delta
        if state["phase"] == "start":
            if state["time"] >= 0.5:
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                state.update(phase="warm", time=0.0)
            return

        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        controller = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
        pawn = controller.get_controlled_pawn() if controller else None
        target = boss(world) if world else None
        if not pawn:
            return

        if state["phase"] == "warm":
            if target and state["time"] >= 9.0:
                encounter = component(target, "RPGBossEncounter")
                debug = component(target, "RPGCombatDebug")
                encounter.wake()
                encounter.hold_for_test(True)
                debug.debug_refill_player()
                component(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
                state.update(phase="kill", time=0.0, world=str(world))
                log("boss awake and held; killing it with debug_kill_boss in 2.5 s")
            return

        if state["phase"] == "kill":
            if state["time"] >= 2.5:
                component(target, "RPGCombatDebug").debug_kill_boss()
                state.update(phase="wait_remains", time=0.0)
            return

        statues = remains(world)
        if state["phase"] == "wait_remains":
            if target is None and statues:
                statue = statues[0]
                check("R1 exactly one remains actor spawns after the boss is destroyed", len(statues) == 1, str(len(statues)))
                check("R2 remains has the three authored material slots", statue.get_slot_count() == 3, str(statue.get_slot_count()))
                state.update(phase="form", time=0.0)
            elif state["time"] > 15.0:
                check("R1 remains appears after the boss is destroyed", False, "boss=%s remains=%d" % (target is not None, len(statues)))
                check("R2 remains has the three authored material slots", False, "no remains")
                state.update(phase="form", time=0.0)
            return

        if state["phase"] == "form":
            if statues and (statues[0].is_fully_formed() or state["time"] > 3.5):
                statue = statues[0]
                check("R3 remains reaches Dissolve 1.0", statue.is_fully_formed() and statue.get_dissolve() >= 0.999, "%.3f" % statue.get_dissolve())
                unreal.RPGInputTestUtils.set_key_down(controller, "R", True)
                state.update(phase="retry", time=0.0)
            elif state["time"] > 5.0:
                check("R3 remains reaches Dissolve 1.0", False, "no formed remains")
                unreal.RPGInputTestUtils.set_key_down(controller, "R", True)
                state.update(phase="retry", time=0.0)
            return

        if state["phase"] == "retry":
            if not state["released"] and state["time"] >= 0.15:
                unreal.RPGInputTestUtils.set_key_down(controller, "R", False)
                state["released"] = True
            if str(world) != state["world"]:
                check("R4 retry resets the level with no remains actor", len(statues) == 0, str(len(statues)))
                finish()
            elif state["time"] > 12.0:
                check("R4 retry resets the level with no remains actor", False, "level did not reload")
                finish()
    except Exception:
        import traceback
        check("driver did not raise", False, traceback.format_exc())
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
