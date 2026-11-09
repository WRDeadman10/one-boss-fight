"""Gate 2 / G2-10, Freeze S11 and L09: the player dies in the middle of a boss action and respawns; both combatants must be reset correctly. Scenarios: during a stance break, during a riposte, during the A4 sweep,
with an A5 javelin in flight. After the respawn (a new pawn) the boss must be back at its start, dormant, with full health and posture, not staggered, with no montage, no blade, no javelin and a new encounter generation,
and the new player must be at full health (nothing from the old fight hurts the new one). Run pie_debug_overlay.py once after an editor start first. Log prefix [DeathReset].
"""
import math
import os
import unreal

log = lambda m: unreal.log("[DeathReset] " + m)
USE_MELEE = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_NormalAttack"
results = []
S = {"phase": "start", "t": 0.0, "i": 0, "stage": "wake", "st": 0.0, "now": 0.0, "mem": {}, "press_until": 0.0, "pawn_name": None}
handle = None


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def attr(actor, tag):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    try:
        return c.call_method("Get Current Attribute Value", args=(t,))
    except Exception:
        return None


def max_attr(actor, tag):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    try:
        return c.call_method("GetMaxAttributeValue", args=(t,))
    except Exception:
        return None


def has_tag(actor, name):
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % name)
    try:
        return bool(actor.call_method("HasMatchingGameplayTag", args=(t,)))
    except Exception:
        return None


def place(pawn, boss, dist, ang_deg):
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw + ang_deg)
    p = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(p, bl).yaw
    pawn.set_actor_location_and_rotation(p, unreal.Rotator(0, 0, look), False, True)


def parts(boss):
    return {n: comp(boss, c) for n, c in (("enc", "RPGBossEncounter"), ("tr", "RPGAttackTracker"), ("dbg", "RPGCombatDebug"), ("stg", "RPGBossStagger"), ("sw", "RPGBossLowSweep"), ("pu", "RPGBossHealPunish"))}


def javelins(w):
    return [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "RPGBossJavelin"]


# name, setup(w, pc, pawn, boss), action time after the setup, kill time after the setup
def setup_break(w, pc, pawn, boss):
    p = parts(boss)
    p["stg"].force_break_for_test()
    place(pawn, boss, 110, 0)


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def setup_riposte(w, pc, pawn, boss):
    p = parts(boss)
    p["stg"].force_break_for_test()
    place(pawn, boss, 110, 0)
    pc.set_control_rotation(unreal.Rotator(0, 0, pawn.get_actor_rotation().yaw))
    S["mem"]["riposte0"] = p["stg"].get_riposte_count()


def act_riposte(w, pc, pawn, boss):
    S["press_until"] = S["now"] + 0.12


def setup_a4(w, pc, pawn, boss):
    place(pawn, boss, 250, 0)
    S["mem"]["start_ok"] = parts(boss)["tr"].start_move("A4", True)


def setup_a5(w, pc, pawn, boss):
    place(pawn, boss, 1000, 0)
    parts(boss)["pu"].notify_heal_started_for_test()


def setup_parry_lifecycle(w, pc, pawn, boss):
    """Open a real player parry window immediately before the death-reset path."""
    place(pawn, boss, 120, 0)
    parry = comp(pawn, "RPGPlayerParry")
    if parry is None:
        raise RuntimeError("player pawn has no RPGPlayerParry component")
    window_seconds = float(parry.get_editor_property("window_seconds"))
    cooldown_seconds = float(parry.get_editor_property("cooldown_seconds"))
    press_before = int(parry.get_press_count())
    parried_before = int(parry.get_parried_count())
    opened = bool(parry.press())
    active = bool(parry.is_window_open())
    tag = has_tag(pawn, "Status.ParryActive")
    S["mem"].update(parry_window_seconds=window_seconds, parry_cooldown_seconds=cooldown_seconds,
                     parry_press_before=press_before, parry_press_after=int(parry.get_press_count()),
                     parry_count_before=parried_before, parry_opened_before_reset=opened,
                     parry_active_before_reset=active, parry_tag_before_reset=tag)
    log("PARRY_LIFECYCLE stage=before_reset pawn=%s opened=%s parry_window=%s status_parry_active=%s parried_count=%d press_count=%d cooldown_seconds=%.3f" %
        (pawn.get_name(), opened, active, tag, parried_before, int(parry.get_press_count()), cooldown_seconds))


def noop(w, pc, pawn, boss):
    pass


_BASE_SCENARIOS = [
    ("parry window lifecycle", setup_parry_lifecycle, noop, 0.0, 0.0),
    ("stance break", setup_break, noop, 0.0, 1.0),
    ("riposte", setup_riposte, act_riposte, 1.0, 2.3),  # the press waits for the kneel (the interaction opens when the 0.7 s fall clip is over); the paired clips start at once and the impact lands 0.8 s later: the player dies 1.3 s after the press, with the clips still running
    ("A4 sweep", setup_a4, noop, 0.0, 0.8),
    ("A5 javelin in flight", setup_a5, noop, 0.0, 1.0),
]
_repeat_count = int(os.environ.get("A5_DEATH_RESET_REPETITIONS", "1"))
if _repeat_count not in (1, 3):
    raise ValueError("A5_DEATH_RESET_REPETITIONS must be 1 or 3")
SCENARIOS = [
    ("%s (cycle %d)" % (scenario[0], cycle + 1),) + scenario[1:]
    for cycle in range(_repeat_count)
    for scenario in _BASE_SCENARIOS
]


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("RESULT %d/%d passed" % (sum(1 for r in results if r), len(results)))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = S
    s["t"] += dt
    s["now"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            selection = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
            if selection:
                unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + selection)
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0, st=9.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if boss is None or (pawn is None and s["stage"] != "respawn"):
        return
    if pc is not None and pawn is not None and s["now"] < s["press_until"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(USE_MELEE), unreal.Vector(1, 0, 0))
    p = parts(boss)
    if s["t"] < s["st"]:
        return
    if s["i"] >= len(SCENARIOS):
        finish()
        return
    name, setup, act, act_t, kill_t = SCENARIOS[s["i"]]
    if s["stage"] == "wake":
        p["enc"].wake()
        p["enc"].hold_for_test(True)
        p["dbg"].debug_refill_player()
        p["tr"].enter_combat()
        comp(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))  # the riposte needs the player in combat
        s.update(stage="setup", t=0.0, st=3.0)
    elif s["stage"] == "setup":
        p["dbg"].debug_refill_player()
        s["pawn_name"] = pawn.get_name()
        s["mem"] = {"gen": int(p["enc"].get_participant_generation_text()), "resets": p["enc"].get_reset_count(), "jav": 0,
                    "pawn_class": pawn.get_class().get_name()}
        setup(w, pc, pawn, boss)
        s.update(stage="act", t=0.0, st=act_t)
    elif s["stage"] == "act":
        act(w, pc, pawn, boss)
        s.update(stage="kill", t=0.0, st=max(0.0, kill_t - act_t))
    elif s["stage"] == "kill":
        extra = ""
        if name.startswith("riposte"):
            extra = " (riposte count %d -> %d)" % (s["mem"]["riposte0"], p["stg"].get_riposte_count())
            check("riposte: the riposte was accepted, its impact has landed and the execution is still running when the player dies", p["stg"].get_riposte_count() == s["mem"]["riposte0"] + 1 and p["stg"].is_staggered() and p["stg"].is_riposte_executing(), extra)
        if name.startswith("A5"):
            extra = " (javelins in flight %d)" % len(javelins(w))
        log("== %s: killing the player%s" % (name, extra))
        health_before = attr(pawn, "Attribute.Health")
        p["dbg"].debug_set_player_health(0.0)
        try:
            health_after = attr(pawn, "Attribute.Health")
        except Exception as error:
            health_after = "unreadable:%s" % error
        s["mem"].update(death_health_before=health_before, death_health_after=health_after,
                        respawn_log_at=s["now"])
        log("PARRY_LIFECYCLE stage=death_request pawn=%s class=%s health_before=%s health_after=%s controller_pawn=%s" %
            (pawn.get_name(), pawn.get_class().get_name(), health_before, health_after,
             pc.get_controlled_pawn().get_name() if pc and pc.get_controlled_pawn() else "None"))
        s.update(stage="respawn", t=0.0, st=0.0, kill_at=s["now"])
    elif s["stage"] == "respawn":
        elapsed = s["now"] - s["kill_at"]
        candidate_names = [actor.get_name() for actor in
                           unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)
                           if actor.get_name() != s["pawn_name"] and
                           actor.get_class().get_name() == s["mem"].get("pawn_class")]
        is_new_expected_pawn = (pawn is not None and pawn.get_name() != s["pawn_name"] and
                                pawn.get_class().get_name() == s["mem"].get("pawn_class"))
        if is_new_expected_pawn and elapsed > 0.5:
            log("== %s: controller repossessed %s class=%s after %.1f s; spawned candidates=%s" %
                (name, pawn.get_name(), pawn.get_class().get_name(), elapsed, candidate_names))
            s["mem"]["respawn_pawn_class"] = pawn.get_class().get_name()
            s.update(stage="check", t=0.0, st=2.5)
        else:
            if s["now"] >= s["mem"].get("respawn_log_at", s["kill_at"]):
                log("RESPAWN_WAIT elapsed=%.1f controller_pawn=%s class=%s matching_spawned_candidates=%s health_after_request=%s" %
                    (elapsed, pawn.get_name() if pawn else "None",
                     pawn.get_class().get_name() if pawn else "None", candidate_names,
                     s["mem"].get("death_health_after")))
                s["mem"]["respawn_log_at"] = s["now"] + 5.0
            if elapsed > 45.0:
                check("%s: player respawn/repossess observed within 45 s" % name, False,
                      "controller pawn=%s, spawned candidates=%s, health_after_request=%s" %
                      (pawn.get_name() if pawn else "None", candidate_names,
                       s["mem"].get("death_health_after")))
                finish()
    elif s["stage"] == "check":
        enc, stg, dbg = p["enc"], p["stg"], p["dbg"]
        home = enc.get_home_transform().translation
        away = (boss.get_actor_location() - home).length()
        mesh = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0]
        inst = mesh.get_anim_instance()
        montage = inst.get_current_active_montage() if inst else None
        php = attr(pawn, "Attribute.Health")
        generation = int(enc.get_participant_generation_text())
        check("%s: encounter reset once (generation +1)" % name, generation == s["mem"]["gen"] + 1 and enc.get_reset_count() == s["mem"]["resets"] + 1, "generation %d -> %d" % (s["mem"]["gen"], generation))
        check("%s: boss back at its start, dormant" % name, away < 10.0 and enc.is_dormant(), "%.1f cm from home, dormant %s" % (away, enc.is_dormant()))
        check("%s: boss not staggered, no montage left" % name, (not stg.is_staggered()) and (montage is None or (dbg.debug_boss_montage_anim_name() or "") == "AN_Boss01_DormantIdle"), "staggered %s, montage %s, anim %s" % (stg.is_staggered(), montage.get_name() if montage else None, dbg.debug_boss_montage_anim_name() if montage else None))  # since B11 a dormant boss plays its idle loop (2026-10-25)
        health, maximum = attr(boss, "Attribute.Health"), max_attr(boss, "Attribute.Health")
        check("%s: boss health and poise full" % name, health is not None and maximum is not None and abs(health - maximum) <= 0.5 and (attr(boss, "Attribute.Poise") or 0) >= 99.0 and comp(boss, "RPGBossPosture").get_posture() >= 99.0, "health %s/%s poise %s" % (health, maximum, attr(boss, "Attribute.Poise")))
        check("%s: no blade, no pending punish, no javelin" % name, (not p["sw"].is_blade_active()) and (not p["pu"].is_pending()) and len(javelins(w)) == 0, "blade %s pending %s javelins %d" % (p["sw"].is_blade_active(), p["pu"].is_pending(), len(javelins(w))))
        check("%s: the new player starts at full health" % name, php is not None and php >= 99.0, "health %s" % php)
        if name.startswith("parry window lifecycle"):
            parry = comp(pawn, "RPGPlayerParry")
            if parry is None:
                check("parry lifecycle: new pawn has RPGPlayerParry", False)
            else:
                new_window = bool(parry.is_window_open())
                new_tag = has_tag(pawn, "Status.ParryActive")
                new_parried = int(parry.get_parried_count())
                press_before = int(parry.get_press_count())
                cooldown_ready = bool(parry.press())
                press_after = int(parry.get_press_count())
                log("PARRY_LIFECYCLE stage=after_respawn pawn=%s parry_window_before_probe=%s status_parry_active_before_probe=%s parried_count=%d press_count_before=%d press_cooldown_ready=%s press_count_after=%d window_seconds=%.3f cooldown_seconds=%.3f" %
                    (pawn.get_name(), new_window, new_tag, new_parried, press_before, cooldown_ready,
                     press_after, S["mem"]["parry_window_seconds"], S["mem"]["parry_cooldown_seconds"]))
                check("parry lifecycle: active window and tag do not carry across respawn",
                      not new_window and new_tag is False,
                      "window=%s Status.ParryActive=%s" % (new_window, new_tag))
                check("parry lifecycle: new pawn has fresh counters and cooldown",
                      new_parried == 0 and press_before == 0 and cooldown_ready and press_after == 1,
                      "ParriedCount=%d PressCount=%d->%d cooldown_ready=%s" %
                      (new_parried, press_before, press_after, cooldown_ready))
                check("parry lifecycle: pre-death control opened a live window",
                      S["mem"].get("parry_opened_before_reset") is True and
                      S["mem"].get("parry_active_before_reset") is True and
                      S["mem"].get("parry_tag_before_reset") is True,
                      "opened=%s window=%s Status.ParryActive=%s" %
                      (S["mem"].get("parry_opened_before_reset"),
                       S["mem"].get("parry_active_before_reset"),
                       S["mem"].get("parry_tag_before_reset")))
        s["i"] += 1
        s.update(stage="wake", t=0.0, st=1.0)


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        check("tick raised", False)
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
