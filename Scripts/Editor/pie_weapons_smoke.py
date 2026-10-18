"""
Play-in-editor smoke test for M5 weapons: walks the player into the boss fight, then for each of the player's
weapons swaps to it and attacks the boss for a few seconds, logging the boss health lost, the weapon name and
that time dilation returns to 1. Editor must be started with -unattended and be in the foreground.
Results: [M5Drive] lines in the Output Log.
"""

import unreal

LOG = "[M5Drive] "
TRIGGER_POINT = unreal.Vector(-1100.0, 0.0, 120.0)
ATTACK_SECONDS = 6.0
state = {"phase": "start", "t": 0.0, "weapon": 0, "hp_start": 0.0, "press": 0.0, "hits": 0}
handle = None


def log(msg):
    unreal.log(LOG + msg)


def game_world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def first(world, class_path):
    actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.load_class(None, class_path))
    return actors[0] if actors else None


def finish(reason):
    global handle
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception:
        pass
    log("finished: " + reason)


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error: " + traceback.format_exc())
        finish("error")


def _tick(dt):
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait_pie", t=0.0)
        return

    world = game_world()
    if world is None:
        if s["phase"] != "wait_pie":
            finish("PIE ended unexpectedly")
        return
    player = first(world, "/Script/OneBossFight.RPGPlayerCharacter")
    boss = first(world, "/Script/OneBossFight.RPGBossCharacter")
    if player is None or boss is None:
        if s["t"] > 20.0:
            finish("player or boss missing")
        return

    combat = player.get_components_by_class(unreal.RPGCombatComponent)[0]
    p_attr = player.get_components_by_class(unreal.RPGAttributeComponent)[0]
    b_attr = boss.get_components_by_class(unreal.RPGAttributeComponent)[0]
    brain = boss.get_components_by_class(unreal.RPGBossCombatComponent)[0]

    if s["phase"] == "wait_pie":
        if s["t"] > 3.0:
            p_attr.set_editor_property("max_health", 100000.0)
            p_attr.reset_attributes()
            player.set_actor_location(TRIGGER_POINT, False, True)
            log("player entered the trigger")
            s.update(phase="wait_combat", t=0.0)
        return

    if s["phase"] == "wait_combat":
        if brain.get_boss_state() == unreal.RPGBossState.COMBAT:
            # Stand right in front of the boss, facing it.
            player.set_actor_location_and_rotation(unreal.Vector(-235.0, 0.0, 120.0), unreal.Rotator(0.0, 0.0, 0.0), False, True)
            s.update(phase="attack", t=0.0, hp_start=b_attr.get_health(), press=0.0)
            log("weapon %d: %s" % (s["weapon"], combat.get_editor_property("weapon").get_editor_property("display_name")))
        elif s["t"] > 30.0:
            finish("boss never reached combat")
        return

    if s["phase"] == "attack":
        s["press"] += dt
        if s["press"] > 0.1:
            s["press"] = 0.0
            combat.request_light_attack()
            # keep the player alive and in front of the boss
            if p_attr.get_health() < 50000.0:
                p_attr.heal(100000.0)
        if s["t"] > ATTACK_SECONDS:
            lost = s["hp_start"] - b_attr.get_health()
            log("weapon %d done: boss lost %.0f HP in %.0fs, boss phase %d, player time dilation %.2f, boss time dilation %.2f" % (
                s["weapon"], lost, ATTACK_SECONDS, brain.get_phase(), player.get_editor_property("custom_time_dilation"),
                boss.get_editor_property("custom_time_dilation")))
            s["phase"] = "switch"
            s["t"] = 0.0
        return

    if s["phase"] == "switch":
        # Wait until the player is free to act, then cycle.
        if combat.get_state() == unreal.RPGCombatState.LOCOMOTION or s["t"] > 3.0:
            s["weapon"] += 1
            if s["weapon"] >= 3:
                finish("all weapons tried")
                return
            changed = player.cycle_weapon()
            log("cycle_weapon -> %s" % changed)
            s.update(phase="wait_combat", t=0.0)


handle = unreal.register_slate_post_tick_callback(tick)
log("driver registered")
