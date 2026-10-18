"""
Play-in-editor smoke test for M4 (boss and encounter loop). Run inside the open editor with L_Greybox loaded,
editor started with -unattended and in the foreground.

The player stands still and takes hits. The driver walks the player into the encounter trigger, damages the boss
to force phase 2 once, lets the boss kill the player, waits for the automatic retry, and repeats for CYCLES rounds.
Results are in the Output Log: [M4Drive] lines from here, plus the game's own encounter and boss state logs.
"""

import unreal

CYCLES = 2
TRIGGER_POINT = unreal.Vector(-1100.0, 0.0, 120.0)
LOG = "[M4Drive] "
state = {"phase": "start", "t": 0.0, "cycle": 0, "since_combat": 0.0, "phase2_done": False, "hb": 0.0, "total": 0.0}
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
    s["total"] += dt
    s["hb"] += dt

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

    brain = boss.get_components_by_class(unreal.RPGBossCombatComponent)[0]
    boss_attr = boss.get_components_by_class(unreal.RPGAttributeComponent)[0]
    p_attr = player.get_components_by_class(unreal.RPGAttributeComponent)[0]
    boss_state = brain.get_boss_state()

    if s["hb"] > 2.0:
        s["hb"] = 0.0
        log("t=%.0f cycle=%d phase=%s boss=%s statetree=%s (enters=%d) phase#=%d bossHP=%.0f playerHP=%.0f dist=%.0f" % (
            s["total"], s["cycle"], s["phase"], boss_state, brain.get_mirrored_state(), brain.get_state_tree_enter_count(),
            brain.get_phase(), boss_attr.get_health(), p_attr.get_health(),
            (player.get_actor_location() - boss.get_actor_location()).length()))

    if s["phase"] == "wait_pie":
        if s["t"] > 3.0:
            s.update(phase="enter", t=0.0)
        return

    if s["phase"] == "enter":
        player.set_actor_location(TRIGGER_POINT, False, True)
        log("cycle %d: player teleported into the trigger" % s["cycle"])
        s.update(phase="fight", t=0.0, since_combat=0.0, phase2_done=False)
        return

    if s["phase"] == "fight":
        if boss_state == unreal.RPGBossState.COMBAT:
            s["since_combat"] += dt
            if not s["phase2_done"] and s["since_combat"] > 6.0:
                s["phase2_done"] = True
                boss_attr.apply_damage(800.0)
                log("forced damage on the boss: HP now %.0f" % boss_attr.get_health())
        # Player dead and boss reset to dormant means the retry finished.
        if s["t"] > 8.0 and boss_state == unreal.RPGBossState.DORMANT and p_attr.get_health() >= p_attr.max_health - 0.1:
            s["cycle"] += 1
            log("cycle %d complete (retry reset seen)" % s["cycle"])
            if s["cycle"] >= CYCLES:
                finish("%d cycles done" % CYCLES)
            else:
                s.update(phase="enter", t=0.0)
        elif s["t"] > 120.0:
            finish("timeout in cycle %d" % s["cycle"])


handle = unreal.register_slate_post_tick_callback(tick)
log("driver registered")
