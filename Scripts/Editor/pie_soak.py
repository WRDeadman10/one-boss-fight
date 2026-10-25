"""Gate 4 G4-4: deterministic 30-encounter soak.
Six PIE sessions run natural, break, roar, player-death and boss-death scenarios.
Boss death is last because the pack destroys that boss; every result is out of 213.
Run pie_debug_overlay.py once after an editor start first (KI-081).
"""
import math
import traceback
import unreal

log = lambda message: unreal.log("[Soak] " + message)
BOSS_CLASS = "BP_ExampleGreatSwordBoss_C"
SCENARIOS = ("natural", "break", "roar", "player_death", "boss_death")
TOTAL = 30
PER_ENCOUNTER = 7
EXPECTED = TOTAL * PER_ENCOUNTER + 3
WARMUP = 9.0
PER_ENCOUNTER_LIMIT = 60.0
TOTAL_LIMIT = 3900.0
NO_PAWN_LIMIT = 40.0
HEARTBEAT = 15.0

S = {"phase": "start", "now": 0.0, "phase_time": 0.0, "wait": 0.0,
     "runner": None, "encounter": 0, "started": 0.0, "checks": 0,
     "results": [], "tick_error": False, "hung": False, "no_pawn": 0.0,
     "heartbeat": -HEARTBEAT, "stop_at": 0.0, "restart": False,
     "finished": False, "moves": []}
handle = None

def check(name, passed, detail=""):
    S["results"].append(bool(passed))
    if S["encounter"] and S["checks"] < PER_ENCOUNTER:
        S["checks"] += 1
    log("%s %s %s" % ("PASS" if passed else "FAIL", name, detail))

def comp(actor, class_name):
    if actor is None:
        return None
    return next((item for item in actor.get_components_by_class(unreal.ActorComponent)
                 if item.get_class().get_name() == class_name), None)

def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()

def actors():
    game_world = world()
    controller = unreal.GameplayStatics.get_player_controller(game_world, 0) if game_world else None
    pawn = controller.get_controlled_pawn() if controller else None
    boss = next((actor for actor in unreal.GameplayStatics.get_all_actors_of_class(game_world, unreal.Character)
                 if actor.get_class().get_name() == BOSS_CLASS), None) if game_world else None
    return game_world, controller, pawn, boss

def parts(boss):
    return {"enc": comp(boss, "RPGBossEncounter"),
            "tracker": comp(boss, "RPGAttackTracker"),
            "stagger": comp(boss, "RPGBossStagger"),
            "phase": comp(boss, "RPGBossPhases"),
            "posture": comp(boss, "RPGBossPosture"),
            "debug": comp(boss, "RPGCombatDebug"),
            "wave": comp(boss, "RPGBossShockwave")}

def attr(actor, tag_name):
    attributes = comp(actor, "BP_AttributesComponent_C")
    if attributes is None:
        return None
    tag = unreal.GameplayTag()
    tag.import_text('(TagName="%s")' % tag_name)
    try:
        return attributes.call_method("Get Current Attribute Value", args=(tag,))
    except Exception:
        return None


def max_attr(actor, tag_name):
    attributes = comp(actor, "BP_AttributesComponent_C")
    if attributes is None:
        return None
    tag = unreal.GameplayTag()
    tag.import_text('(TagName="%s")' % tag_name)
    try:
        return attributes.call_method("GetMaxAttributeValue", args=(tag,))
    except Exception:
        return None

def place(pawn, boss, distance=220.0):
    origin = boss.get_actor_location()
    radians = math.radians(boss.get_actor_rotation().yaw)
    location = unreal.Vector(origin.x + math.cos(radians) * distance,
                             origin.y + math.sin(radians) * distance, origin.z + 20.0)
    pawn.set_actor_location_and_rotation(
        location, unreal.Rotator(0.0, 0.0,
        unreal.MathLibrary.find_look_at_rotation(location, origin).yaw), False, True)

def snapshot(p):
    tracker = p["tracker"]
    stagger = p["stagger"]
    return {"generation": p["enc"].get_generation(), "resets": p["enc"].get_reset_count(),
            "illegal": tracker.get_illegal_start_count(), "double": tracker.get_double_launch_count(),
            "attacks": tracker.get_attack_instance(), "commits": tracker.get_commit_count(),
            "interrupted": tracker.get_interrupted_count(), "stagger": stagger.get_stagger_count(),
            "riposte": stagger.get_riposte_count()}

def leftovers(game_world):
    class_names = [actor.get_class().get_name()
                   for actor in unreal.GameplayStatics.get_all_actors_of_class(game_world, unreal.Actor)] if game_world else []
    return {"boss": sum(name == BOSS_CLASS for name in class_names),
            "javelin": sum(name == "RPGBossJavelin" for name in class_names),
            "wave_actor": sum("Shockwave" in name or "Wave" in name for name in class_names)}

def remember(p):
    move = str(p["tracker"].get_current_move())
    if move != "None" and (not S["moves"] or S["moves"][-1] != move):
        S["moves"] = (S["moves"] + [move])[-5:]

def wait_until(predicate, timeout, step=0.1):
    started = S["now"]
    while not predicate():
        if S["now"] - started > timeout:
            return False
        yield step
    return True

def prepare(held):
    game_world, controller, pawn, boss = actors()
    if pawn is None or boss is None:
        return None
    p = parts(boss)
    if any(value is None for value in p.values()):
        return None
    p["enc"].reset_for_test()
    yield 1.2
    game_world, controller, pawn, boss = actors()
    if pawn is None or boss is None:
        return None
    p = parts(boss)
    p["enc"].wake()
    p["enc"].hold_for_test(held)
    p["debug"].debug_refill_player()
    place(pawn, boss)
    yield 1.5
    return game_world, controller, pawn, boss, p

def begin(scenario):
    S["encounter"] += 1
    S["checks"] = 0
    S["started"] = S["now"]
    S["moves"] = []
    log("ENCOUNTER %02d scenario %s begin" % (S["encounter"], scenario))

def fill(scenario, reason):
    while S["checks"] < PER_ENCOUNTER:
        check("%02d %s required check %d" % (S["encounter"], scenario, S["checks"] + 1),
              False, reason + "; last moves " + str(S["moves"]))

def finalize_reset(scenario, goal, goal_ok, baseline, expected_resets=1):
    yield 1.5
    game_world, _, pawn, boss = actors()
    if boss is None or pawn is None:
        check("%02d %s scenario goal" % (S["encounter"], scenario), False, goal + "; reset state unavailable")
        fill(scenario, "missing boss or pawn after reset")
        return
    p = parts(boss)
    counters = snapshot(p)
    home = p["enc"].get_home_transform().translation
    health = attr(boss, "Attribute.Health")
    maximum_health = max_attr(boss, "Attribute.Health")
    player_before = attr(pawn, "Attribute.Health")
    stale = leftovers(game_world)
    wave_active = p["wave"].is_wave_active()
    start_ok = ((boss.get_actor_location() - home).length() < 10.0 and p["enc"].is_dormant() and
                health is not None and maximum_health is not None and abs(health - maximum_health) <= 0.5 and p["posture"].get_posture() >= 99.0 and
                not p["stagger"].is_staggered() and (p["debug"].debug_boss_montage_anim_name() or "") in ("", "AN_Boss01_DormantIdle"))  # since B11 a dormant boss plays its authored idle loop (2026-10-25)
    generation_ok = (counters["generation"] == baseline["generation"] + expected_resets and
                     p["enc"].get_reset_count() == baseline["resets"] + expected_resets)
    yield 1.5
    _, _, late_pawn, late_boss = actors()
    player_after = attr(late_pawn, "Attribute.Health") if late_pawn else None
    late_ok = (late_boss is not None and player_before is not None and player_after is not None and
               player_after >= player_before - 0.01)
    log("ENCOUNTER %02d scenario %s generation %d reset %d phase2 %s health %s posture %.1f "
        "stagger %d riposte %d delta(illegal=%+d double=%+d attack=%+d commit=%+d interrupted=%+d) "
        "outcome dormant=%s start=%s montage='%s' leftovers=%s player_hp=(%s,%s) moves=%s" %
        (S["encounter"], scenario, counters["generation"], p["enc"].get_reset_count(),
         p["phase"].is_phase_two(), health, p["posture"].get_posture(),
         counters["stagger"], counters["riposte"],
         counters["illegal"] - baseline["illegal"], counters["double"] - baseline["double"],
         counters["attacks"] - baseline["attacks"], counters["commits"] - baseline["commits"],
         counters["interrupted"] - baseline["interrupted"], p["enc"].is_dormant(), start_ok,
         p["debug"].debug_boss_montage_anim_name(), stale, player_before, player_after, S["moves"]))
    check("%02d %s scenario goal" % (S["encounter"], scenario), goal_ok, goal)
    check("%02d %s reset start state" % (S["encounter"], scenario), start_ok)
    check("%02d %s no illegal start" % (S["encounter"], scenario), counters["illegal"] == baseline["illegal"])
    check("%02d %s no double launch" % (S["encounter"], scenario), counters["double"] == baseline["double"])
    check("%02d %s generation/reset count" % (S["encounter"], scenario), generation_ok)
    check("%02d %s no stale boss/projectile/wave" % (S["encounter"], scenario),
          stale["boss"] == 1 and stale["javelin"] == 0 and stale["wave_actor"] == 0 and not wave_active, str(stale))
    check("%02d %s no damage after reset" % (S["encounter"], scenario), late_ok, str((player_before, player_after)))

def natural():
    begin("natural")
    prepared = yield from prepare(False)
    if prepared is None:
        fill("natural", "setup failed")
        return
    _, _, pawn, boss, p = prepared
    baseline = snapshot(p)
    survived = True
    for _ in range(40):
        _, _, current_pawn, current_boss = actors()
        if current_pawn is None or current_boss is None:
            survived = False
            break
        current = parts(current_boss)
        current["debug"].debug_refill_player()
        remember(current)
        yield 0.5
    _, _, current_pawn, boss = actors()
    if boss is not None:
        if current_pawn is not None:
            # a real respawn puts the player far from the boss: with the player 220 cm away the boss, which is not held here, wakes again at once and the start state cannot be read (soak run 1, 6 of 6 natural encounters)
            far = boss.get_actor_location() + unreal.Vector(0.0, 2500.0, 20.0)
            current_pawn.set_actor_location_and_rotation(far, unreal.Rotator(0, 0, 0), False, True)
        parts(boss)["enc"].reset_for_test()
    yield from finalize_reset("natural", "20-second awake fight with player refilled", survived, baseline)

def break_scenario():
    begin("break")
    prepared = yield from prepare(True)
    if prepared is None:
        fill("break", "setup failed")
        return
    _, _, pawn, boss, p = prepared
    baseline = snapshot(p)
    p["stagger"].set_cooldown_for_test(0.0)
    request = p["stagger"].force_break_for_test()
    reached = yield from wait_until(lambda: actors()[3] is not None and parts(actors()[3])["stagger"].is_staggered(), 4.0)
    p["enc"].reset_for_test()
    yield from finalize_reset("break", "ForceBreakForTest=%s staggered=%s" % (request, reached),
                              request == "started" and reached, baseline)

def roar():
    begin("roar")
    prepared = yield from prepare(True)
    if prepared is None:
        fill("roar", "setup failed")
        return
    _, _, pawn, boss, p = prepared
    baseline = snapshot(p)
    p["debug"].debug_set_boss_health_fraction(0.55)
    reached = yield from wait_until(lambda: actors()[3] is not None and parts(actors()[3])["phase"].is_in_transition(), 4.0)
    p["enc"].reset_for_test()
    yield from finalize_reset("roar", "phase transition observed before reset", reached, baseline)

def player_death():
    begin("player_death")
    prepared = yield from prepare(True)
    if prepared is None:
        fill("player_death", "setup failed")
        return
    _, _, pawn, boss, p = prepared
    baseline = snapshot(p)
    old_name = pawn.get_name()
    p["debug"].debug_set_player_health(0.0)
    respawned = yield from wait_until(lambda: actors()[2] is not None and actors()[2].get_name() != old_name, 25.0)
    yield from finalize_reset("player_death", "player respawned after DebugSetPlayerHealth(0)", respawned, baseline)

def boss_death():
    begin("boss_death")
    prepared = yield from prepare(True)
    if prepared is None:
        fill("boss_death", "setup failed")
        S["restart"] = True
        return
    game_world, _, pawn, boss, p = prepared
    baseline = snapshot(p)
    terminal = snapshot(p)
    phase_two = p["phase"].is_phase_two()
    player_before = attr(pawn, "Attribute.Health")
    p["debug"].debug_kill_boss()
    destroyed = yield from wait_until(lambda: actors()[3] is None, 8.0)
    yield 1.5
    game_world, _, late_pawn, late_boss = actors()
    player_after = attr(late_pawn, "Attribute.Health") if late_pawn else None
    stale = leftovers(game_world)
    late_ok = (player_before is not None and player_after is not None and player_after >= player_before - 0.01)
    log("ENCOUNTER %02d scenario boss_death generation %d reset %d phase2 %s health dead posture unavailable "
        "stagger %d riposte %d delta(illegal=%+d double=%+d attack=%+d commit=%+d interrupted=%+d) "
        "outcome destroyed=%s leftovers=%s player_hp=(%s,%s) moves=%s" %
        (S["encounter"], baseline["generation"], baseline["resets"], phase_two,
         terminal["stagger"], terminal["riposte"],
         terminal["illegal"] - baseline["illegal"],
         terminal["double"] - baseline["double"],
         terminal["attacks"] - baseline["attacks"],
         terminal["commits"] - baseline["commits"],
         terminal["interrupted"] - baseline["interrupted"],
         destroyed, stale, player_before, player_after, S["moves"]))
    check("%02d boss_death scenario goal" % S["encounter"], destroyed)
    check("%02d boss_death intentional terminal state" % S["encounter"], destroyed and late_boss is None)
    check("%02d boss_death no illegal start" % S["encounter"], terminal["illegal"] == baseline["illegal"])
    check("%02d boss_death no double launch" % S["encounter"], terminal["double"] == baseline["double"])
    check("%02d boss_death generation unchanged" % S["encounter"], terminal["generation"] == baseline["generation"])
    check("%02d boss_death no stale projectile/wave" % S["encounter"],
          stale["boss"] == 0 and stale["javelin"] == 0 and stale["wave_actor"] == 0, str(stale))
    check("%02d boss_death no late player damage" % S["encounter"], late_ok, str((player_before, player_after)))
    S["restart"] = True

def run_batch():
    while S["encounter"] < TOTAL:
        scenario = SCENARIOS[S["encounter"] % len(SCENARIOS)]
        if scenario == "natural":
            yield from natural()
        elif scenario == "break":
            yield from break_scenario()
        elif scenario == "roar":
            yield from roar()
        elif scenario == "player_death":
            yield from player_death()
        else:
            yield from boss_death()
        if S["restart"]:
            return "restart"
    return "done"

def abort_remaining(reason):
    if S["encounter"] and S["checks"] < PER_ENCOUNTER:
        fill(SCENARIOS[(S["encounter"] - 1) % len(SCENARIOS)], reason)
    while S["encounter"] < TOTAL:
        S["encounter"] += 1
        S["checks"] = 0
        scenario = SCENARIOS[(S["encounter"] - 1) % len(SCENARIOS)]
        log("ENCOUNTER %02d scenario %s skipped: %s" % (S["encounter"], scenario, reason))
        fill(scenario, reason)

def finish():
    global handle
    if S["finished"]:
        return
    S["finished"] = True
    S["encounter"] = min(S["encounter"], TOTAL)
    in_encounter = S["encounter"]
    S["encounter"] = 0
    check("all 30 encounters ran", in_encounter == TOTAL)
    check("no tick error", not S["tick_error"])
    check("no watchdog hang", not S["hung"])
    S["encounter"] = in_encounter
    while len(S["results"]) < EXPECTED:
        S["results"].append(False)
        log("FAIL accounting filler")
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("RESULT %d/%d passed" % (sum(1 for result in S["results"] if result), EXPECTED))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()

def request_restart():
    S["restart"] = False
    S["phase"] = "stopping"
    S["stop_at"] = S["now"]
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()

def _tick(dt):
    S["now"] += dt
    S["phase_time"] += dt
    if S["now"] > TOTAL_LIMIT:
        S["hung"] = True
        abort_remaining("total watchdog %.0f s" % TOTAL_LIMIT)
        finish()
        return
    if S["now"] - S["heartbeat"] >= HEARTBEAT:
        S["heartbeat"] = S["now"]
        log("heartbeat encounter %d/%d phase %s elapsed %.0f s" %
            (S["encounter"], TOTAL, S["phase"], S["now"]))
    if S["phase"] == "start":
        if S["phase_time"] >= 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S["phase"], S["phase_time"] = "warming", 0.0
        return
    if S["phase"] == "warming":
        if S["phase_time"] >= WARMUP:
            S["phase"], S["phase_time"], S["runner"] = "run", 0.0, run_batch()
        return
    if S["phase"] == "stopping":
        if world() is None and S["now"] - S["stop_at"] > 1.5:
            if S["encounter"] >= TOTAL:
                finish()
            else:
                S["phase"], S["phase_time"] = "start", 0.0
        elif S["now"] - S["stop_at"] > 20.0:
            S["hung"] = True
            abort_remaining("PIE teardown watchdog")
            finish()
        return
    _, _, pawn, boss = actors()
    if pawn is None:
        S["no_pawn"] += dt
        if S["no_pawn"] > NO_PAWN_LIMIT:
            S["hung"] = True
            abort_remaining("no player pawn for %.0f s" % NO_PAWN_LIMIT)
            finish()
        return
    S["no_pawn"] = 0.0
    if S["encounter"] and S["now"] - S["started"] > PER_ENCOUNTER_LIMIT:
        S["hung"] = True
        abort_remaining("encounter watchdog %.0f s" % PER_ENCOUNTER_LIMIT)
        finish()
        return
    if S["wait"] > 0.0:
        S["wait"] -= dt
        return
    if boss is not None:
        remember(parts(boss))
    try:
        S["wait"] = float(next(S["runner"]))
    except StopIteration as stop:
        if stop.value == "restart":
            request_restart()
        else:
            finish()

def tick(dt):
    try:
        _tick(dt)
    except Exception:
        S["tick_error"] = True
        log("tick error " + traceback.format_exc())
        abort_remaining("tick error")
        finish()

handle = unreal.register_slate_post_tick_callback(tick)

