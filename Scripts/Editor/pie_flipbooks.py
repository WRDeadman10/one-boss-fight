"""Combat-flipbook driver: observes the real bleed, weapon-hit and dodge start edges. Log prefix [Flipbook]."""
import math
import traceback
import unreal

log = lambda text: unreal.log("[Flipbook] " + text)
state = {"phase": "start", "time": 0.0, "checks": [], "seen": {}, "ready": False}
handle = None


def check(name, passed, detail=""):
    state["checks"].append(bool(passed))
    log("%s %s %s" % ("PASS" if passed else "FAIL", name, detail))


def component(actor, name):
    return next((item for item in actor.get_components_by_class(unreal.ActorComponent)
                 if item.get_class().get_name() == name), None)


def tags(*names):
    value = unreal.GameplayTagContainer()
    value.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % name for name in names))
    return value


def place(pawn, target, controller):
    origin = target.get_actor_location()
    yaw = math.radians(target.get_actor_rotation().yaw)
    location = unreal.Vector(origin.x + math.cos(yaw) * 110.0, origin.y + math.sin(yaw) * 110.0, origin.z + 20.0)
    facing = unreal.MathLibrary.find_look_at_rotation(location, origin).yaw
    pawn.set_actor_location_and_rotation(location, unreal.Rotator(0, 0, facing), False, True)
    controller.set_control_rotation(unreal.Rotator(0, 0, facing))


def boss(world):
    return next((actor for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                 if actor.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)


def effects(world):
    return [actor for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
            if actor.get_class().get_name() == "RPGFlipbookEffect"]


def observe(world):
    for actor in effects(world):
        name = actor.get_effect_name()
        prior = state["seen"].get(name)
        state["seen"][name] = {"frame": actor.get_frame_index(), "duration": actor.get_playback_seconds(),
                               "advanced": (prior or {}).get("advanced", False) or actor.get_frame_index() > 0}


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
        if not world or not controller or not pawn or not target:
            return
        observe(world)
        if state["phase"] == "warm":
            if state["time"] >= 8.0:
                encounter = component(target, "RPGBossEncounter")
                encounter.wake()
                encounter.hold_for_test(True)
                component(target, "RPGCombatDebug").debug_refill_player()
                component(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
                place(pawn, target, controller)
                state.update(phase="blood", time=0.0)
            return
        if state["phase"] == "blood":
            if state["time"] >= 0.5:
                component(target, "RPGBossBleed").add_buildup_for_test(100.0)
                state.update(phase="dodge_press", time=0.0)
            return
        if state["phase"] == "dodge_press":
            if state["time"] >= 0.8:
                unreal.RPGInputTestUtils.set_key_down(controller, "SpaceBar", True)
                state.update(phase="dodge_release", time=0.0)
            return
        if state["phase"] == "dodge_release":
            if state["time"] >= 0.08:
                unreal.RPGInputTestUtils.set_key_down(controller, "SpaceBar", False)
                state.update(phase="spark", time=0.0)
            return
        if state["phase"] == "spark":
            if state["time"] >= 1.0:
                # Uses the normal weapon path: this driver does not spawn an effect directly.
                place(pawn, target, controller)
                action = unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_NormalAttack")
                unreal.RPGInputTestUtils.inject_action(controller, action, unreal.Vector(1.0, 0.0, 0.0))
                state.update(phase="observe", time=0.0)
            return
        if state["phase"] == "observe":
            if state["time"] >= 1.2:
                expected = {"blood": 0.6, "spark": 0.25, "dust": 0.8}
                for name, duration in expected.items():
                    item = state["seen"].get(name)
                    check("F%s %s effect spawns from its production edge" % (len(state["checks"]) + 1, name), item is not None, str(item))
                    check("F%s %s has the authored duration and advances a frame" % (len(state["checks"]) + 1, name),
                          item is not None and abs(item["duration"] - duration) < 0.02 and item["advanced"], str(item))
                state.update(phase="expired", time=0.0)
            return
        if state["phase"] == "expired" and state["time"] >= 1.0:
            check("F7 effects self-destroy after their authored lifetimes", len(effects(world)) == 0, str(len(effects(world))))
            finish()
    except Exception:
        check("F0 driver did not raise", False, traceback.format_exc())
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
