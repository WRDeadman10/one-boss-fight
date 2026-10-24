"""G3-5 flask overlay. Reads only the reflected live HealthPotion stack; one real IA_UseTool press consumes it after the boss debug helper lowers player health. Log prefix [FlaskHud]."""
import unreal

log = lambda message: unreal.log("[FlaskHud] " + message)
results = []
state = {"phase": "start", "elapsed": 0.0, "step": 0, "next": 0.0, "before": -1, "maximum": 0, "pressed": False}
handle = None
MEL = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/"


def check(name, ok, detail=""):
    results.append(bool(ok))
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def component(actor, class_name):
    return next((item for item in actor.get_components_by_class(unreal.ActorComponent) if item.get_class().get_name() == class_name), None)


def expected_fill(count, maximum):
    if count < 0 or maximum <= 0:
        return "Unavailable"
    if count == 0:
        return "Empty"
    return "Full" if count * 3 > maximum * 2 else "Half"


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    log("RESULT %d/%d passed" % (sum(results), len(results)))


def step(world, player, boss):
    hud = component(player, "RPGFlaskHud")
    debug = component(boss, "RPGCombatDebug")
    if not hud or not debug:
        check("components attach", False, "hud=%s debug=%s" % (hud, debug))
        return -1
    hud.refresh_for_test()
    index = state["step"]
    state["step"] += 1
    if index == 0:
        count, maximum = hud.get_flask_count(), hud.get_flask_maximum()
        state.update(before=count, maximum=maximum)
        check("overlay appears when pack HealthPotion is found", hud.is_overlay_shown(), "count %d max %d state %s" % (count, maximum, hud.get_flask_fill_state()))
        check("the recorded maximum is the initial live count", count > 0 and maximum == count, "%d / %d" % (count, maximum))
        check("initial fill state is derived from count and maximum", hud.get_flask_fill_state() == expected_fill(count, maximum))
        debug.debug_set_player_health(1.0)
        state["pressed"] = True
        return 0.15
    if index == 1:
        return 2.0
    count, maximum = hud.get_flask_count(), hud.get_flask_maximum()
    check("the real use-tool drink lowers the pack stack", count >= 0 and count < state["before"], "%d -> %d" % (state["before"], count))
    check("a drink does not change the recorded starting maximum", maximum == state["maximum"], "%d" % maximum)
    check("displayed fill state follows the live stack", hud.get_flask_fill_state() == expected_fill(count, maximum), "%s for %d/%d" % (hud.get_flask_fill_state(), count, maximum))
    check("overlay remains visible after the drink", hud.is_overlay_shown())
    return -1


def tick(delta):
    try:
        state["elapsed"] += delta
        if state["phase"] == "start":
            if state["elapsed"] > 0.5:
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                state.update(phase="play", elapsed=0.0, next=8.0)
            return
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        controller = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
        player = controller.get_controlled_pawn() if controller else None
        boss = next((actor for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character) if actor.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if world else None
        if not player or not boss:
            if state["elapsed"] > 35.0:
                check("PIE actors arrive", False)
                finish()
            return
        if state["pressed"] and state["step"] == 1 and state["elapsed"] < state["next"] + 0.2:
            action = unreal.load_asset(MEL + "Input/InputActions/IA_UseTool")
            unreal.RPGInputTestUtils.inject_action(controller, action, unreal.Vector(1.0, 0.0, 0.0))
        if state["elapsed"] < state["next"]:
            return
        delay = step(world, player, boss)
        if delay < 0:
            finish()
            return
        state["elapsed"] = 0.0
        state["next"] = delay
    except Exception:
        import traceback
        check("driver step", False, traceback.format_exc())
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
