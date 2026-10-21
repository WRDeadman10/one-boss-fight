"""Gate 2 / M4 (SPEC_M4_transition.md): stance break versus phase transition and the boss's own moves. The boss is frozen awake (hold_for_test) and every scenario starts from fresh() (reset, wake, hold).
Generator style: each `yield seconds` waits, `yield 0.0` polls on the next tick. Mode from Saved/transition_mode.txt: main (default, spec trial counts) or quick (3 trials). Log prefix [Transition].
S00 the roar's immunity effect ends with the roar; S01 a break asked during the roar is dropped (and the heal punish is discarded); S02 posture is pinned during the roar; S03 regeneration restarts 6 s after the roar;
S04 a transition queued behind a stance break starts in the same instant the break ends (gap <= 0.02 s); S05 the same behind an accepted riposte; S06 behind the get-up; S07 five breaks in one frame make one break and the transition waits;
S09 an A4 blade is cut at once by a break or a transition; S10 a pending A5 punish; S11 a javelin in flight; S12 an A6 wave; S14 a reset in the roar; S15 a reset in a break with a queued transition; S16 the stance break cooldown;
S19 posture is held at 0 during a break and refills at the end. INV1 never staggered and transitioning at once; INV2 the posture hold matches the state. Run pie_debug_overlay.py once after an editor start first.
"""
import math
import os
import unreal

log = lambda m: unreal.log("[Transition] " + m)
IA_NORMAL = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_NormalAttack"
_mf = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "transition_mode.txt")
MODE = open(_mf).read().strip() if os.path.exists(_mf) else "main"
results = []
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None, "press_until": 0.0, "inv": {"inv1": 0, "inv2": 0}, "stag_since": None, "stag_clear": None}
handle = None


def N(main, quick=3):
    return quick if MODE == "quick" else main


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


def has_tag(actor, tag):
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    try:
        return bool(actor.call_method("HasMatchingGameplayTag", args=(t,)))
    except Exception:
        return None


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def actors():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return w, pc, pawn, boss


def P():
    """Boss components by short name."""
    w, pc, pawn, boss = actors()
    return {"w": w, "pc": pc, "pawn": pawn, "boss": boss, "enc": comp(boss, "RPGBossEncounter"), "tr": comp(boss, "RPGAttackTracker"), "dbg": comp(boss, "RPGCombatDebug"), "stg": comp(boss, "RPGBossStagger"),
            "ph": comp(boss, "RPGBossPhases"), "post": comp(boss, "RPGBossPosture"), "sw": comp(boss, "RPGBossLowSweep"), "wave": comp(boss, "RPGBossShockwave"), "pu": comp(boss, "RPGBossHealPunish")}


def place(p, dist, ang_deg):
    boss, pawn = p["boss"], p["pawn"]
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw + ang_deg)
    q = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(q, bl).yaw
    pawn.set_actor_location_and_rotation(q, unreal.Rotator(0, 0, look), False, True)
    p["pc"].set_control_rotation(unreal.Rotator(0, 0, look))


def montage_name(boss):
    mc = boss.get_components_by_class(unreal.SkeletalMeshComponent)
    inst = mc[0].get_anim_instance() if mc else None
    m = inst.get_current_active_montage() if inst else None
    return m.get_name() if m else None


def javelins():
    w = world()
    return [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "RPGBossJavelin"]


def now():
    return unreal.GameplayStatics.get_time_seconds(world())


# ---- generator helpers -----------------------------------------------------------------------------------------------------------------------------------------------------
def fresh(combat=False):
    p = P()
    p["stg"].set_editor_property("stagger_seconds", 2.5)
    p["stg"].set_editor_property("cooldown_seconds", 0.0)
    p["enc"].reset_for_test()
    yield 0.8
    p = P()
    p["enc"].wake()
    p["enc"].hold_for_test(True)
    p["dbg"].debug_refill_player()
    p["tr"].enter_combat()
    if combat:
        comp(p["pawn"], "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
    yield 2.2


def until(cond, timeout, step=0.0):
    t0 = S["now"]
    while not cond():
        if S["now"] - t0 > timeout:
            return False
        yield step
    return True


def event(kind, p):
    """The interruption: a stance break asked for through the gate, or the health crossing the phase two threshold."""
    if kind == "break":
        return p["stg"].force_break_for_test()
    p["dbg"].debug_set_boss_health_fraction(0.55)
    return None


# ---- scenarios -------------------------------------------------------------------------------------------------------------------------------------------------------------
def s00_immunity():
    yield from fresh()
    p = P()
    A0 = attr(p["boss"], "Attribute.Attack")
    idle = has_tag(p["boss"], "Status.HitStunImmune")
    p["dbg"].debug_set_boss_health_fraction(0.55)
    ok = yield from until(lambda: P()["ph"].is_in_transition(), 3.0)
    yield 0.3
    roar = has_tag(P()["boss"], "Status.HitStunImmune")
    ok2 = yield from until(lambda: not P()["ph"].is_in_transition(), 4.0)
    yield 0.4
    after = has_tag(P()["boss"], "Status.HitStunImmune")
    S["A0"] = A0
    check("S00 immunity tag: idle false", idle is False, "%s" % idle)
    check("S00 immunity tag: true in the roar (the effect grants Status.HitStunImmune)", roar is True and ok, "%s" % roar)
    check("S00 immunity tag: false 0.4 s after the roar (old code kept it up to about 2.2 s)", after is False and ok2, "%s" % after)


def s01_break_in_roar():
    outcomes = []
    for i in range(N(20)):
        yield from fresh()
        p = P()
        A0 = attr(p["boss"], "Attribute.Attack")
        c0 = (p["stg"].get_stagger_count(), p["stg"].get_dropped_break_count("transition"), p["ph"].get_phase_two_count(), p["pu"].get_discarded_busy_count(), p["pu"].get_accepted_count())
        p["dbg"].debug_set_boss_health_fraction(0.55)
        yield from until(lambda: P()["ph"].is_in_transition(), 3.0)
        yield 0.3
        p = P()
        place(p, 700, 0)
        r = p["stg"].force_break_for_test()
        p["pu"].notify_heal_started_for_test()
        yield 0.05
        p = P()
        m = montage_name(p["boss"])
        mid = (r == "transition" and p["stg"].get_stagger_count() == c0[0] and not p["stg"].is_staggered() and p["stg"].get_dropped_break_count("transition") == c0[1] + 1 and p["pu"].get_accepted_count() == c0[4]
               and p["pu"].get_discarded_busy_count() == c0[3] + 1 and m is not None and "Knockdown" not in m)
        yield from until(lambda: not P()["ph"].is_in_transition(), 4.0)
        yield 0.3
        p = P()
        a = attr(p["boss"], "Attribute.Attack")
        end = p["ph"].is_phase_two() and p["ph"].get_phase_two_count() == c0[2] + 1 and abs(a - 1.25 * A0) < 0.6 and p["tr"].is_neutral()
        outcomes.append(mid and end)
        if not (mid and end):
            log("trial %d: r=%s montage=%s mid=%s end=%s attack %s -> %s" % (i, r, m, mid, end, A0, a))
    check("S01 break asked in the roar is dropped, the roar goes on, the heal punish is discarded, phase two ends normally: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def s02_posture_pinned():
    outcomes = []
    for i in range(N(3)):
        yield from fresh()
        p = P()
        p["dbg"].debug_set_boss_posture(30.0)
        yield 0.3
        s0 = P()["post"].get_suppressed_drain_count()
        P()["dbg"].debug_set_boss_health_fraction(0.55)
        yield from until(lambda: P()["ph"].is_in_transition(), 3.0)
        yield 0.25
        P()["dbg"].debug_drain_boss_posture(20.0)
        yield 0.5
        P()["dbg"].debug_drain_boss_posture(20.0)
        yield 0.4
        p = P()
        posture = attr(p["boss"], "Attribute.Poise")
        ok = abs(posture - 30.0) <= 1.0 and p["post"].get_suppressed_drain_count() >= s0 + 2 and p["post"].get_hold_name() == "Pinned" and not p["stg"].is_staggered()
        outcomes.append(ok)
        if not ok:
            log("trial %d: posture %s hold %s suppressed %d" % (i, posture, p["post"].get_hold_name(), p["post"].get_suppressed_drain_count() - s0))
        yield from until(lambda: not P()["ph"].is_in_transition(), 4.0)
    check("S02 posture is pinned at 30 during the roar, two drains ignored and counted, no break: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def s03_regen_after():
    yield from fresh()
    P()["dbg"].debug_set_boss_posture(60.0)
    yield 0.3
    P()["dbg"].debug_set_boss_health_fraction(0.55)
    yield from until(lambda: P()["ph"].is_in_transition(), 3.0)
    yield from until(lambda: not P()["ph"].is_in_transition(), 4.0)
    t_end = S["now"]
    samples = {}
    for k in (3.0, 6.5, 8.0):
        yield max(0.0, t_end + k - S["now"])
        samples[k] = attr(P()["boss"], "Attribute.Poise")
    check("S03 after the roar: posture still 60 at +3.0 s, about 66.5 at +6.5 s, about 86 at +8.0 s (regeneration starts 6 s after the end)", abs(samples[3.0] - 60) <= 0.5 and abs(samples[6.5] - 66.5) <= 3 and abs(samples[8.0] - 86) <= 3, "%s" % samples)


def queue_gap_trial(kind):
    """kind 'down' (health set during the Down window), 'getup' (during the get-up), 'riposte' (after an accepted riposte). Returns (ok, detail)."""
    yield from fresh(combat=(kind == "riposte"))
    p = P()
    p["stg"].set_editor_property("stagger_seconds", 0.6 if kind != "riposte" else 2.5)
    place(p, 110, 0)
    c0 = (p["ph"].get_phase_two_count(), p["stg"].get_stagger_count(), p["ph"].get_queued_start_count(), p["stg"].get_riposte_count())
    r = p["stg"].force_break_for_test()
    if kind == "getup":
        yield from until(lambda: P()["stg"].is_staggered() and not P()["stg"].is_critical_window_open(), 3.0)
    else:
        yield 0.3
    P()["dbg"].debug_set_boss_health_fraction(0.55)
    yield 0.2
    p = P()
    queued = p["ph"].is_transition_queued() and not p["ph"].is_in_transition() and p["ph"].get_phase_two_count() == c0[0]
    if kind == "riposte":
        S["press_until"] = S["now"] + 0.12
        yield 0.4
    both = {"bad": False}
    started = yield from until(lambda: P()["ph"].is_in_transition() or P()["ph"].get_phase_two_count() > c0[0], 8.0)
    p = P()
    gap = p["ph"].get_last_transition_start_time() - p["stg"].get_last_end_time()
    ok = r == "started" and queued and started and -0.001 <= gap <= 0.02 and p["ph"].get_queued_start_count() == c0[2] + 1 and p["stg"].get_stagger_count() == c0[1] + 1 and not p["ph"].is_transition_queued()
    if kind == "riposte":
        ok = ok and p["stg"].get_riposte_count() == c0[3] + 1
    yield from until(lambda: not P()["ph"].is_in_transition(), 4.0)
    yield 0.2
    return ok, "r=%s queued=%s gap=%.3f queued starts %d" % (r, queued, gap, p["ph"].get_queued_start_count() - c0[2])


def s04_queue_gap():
    outcomes = []
    for i in range(N(20)):
        ok, detail = yield from queue_gap_trial("down")
        outcomes.append(ok)
        if not ok:
            log("trial %d: %s" % (i, detail))
    P()["stg"].set_editor_property("stagger_seconds", 2.5)
    check("S04 a transition queued behind the break starts in the instant it ends (gap <= 0.02 s, old code up to 0.1 s): %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def s05_queue_behind_riposte():
    outcomes = []
    for i in range(N(5)):
        ok, detail = yield from queue_gap_trial("riposte")
        outcomes.append(ok)
        if not ok:
            log("trial %d: %s" % (i, detail))
    check("S05 queued behind an accepted riposte: riposte counted once, one transition after the break, gap <= 0.02 s: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def s06_queue_behind_getup():
    outcomes = []
    for i in range(N(3)):
        ok, detail = yield from queue_gap_trial("getup")
        outcomes.append(ok)
        if not ok:
            log("trial %d: %s" % (i, detail))
    P()["stg"].set_editor_property("stagger_seconds", 2.5)
    check("S06 crossing during the get-up is queued and starts at the end: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def s07_five_breaks():
    outcomes = []
    for i in range(N(20)):
        yield from fresh()
        p = P()
        p["stg"].set_editor_property("stagger_seconds", 0.6)
        c0 = (p["stg"].get_stagger_count(), p["stg"].get_dropped_break_count("staggered"), p["ph"].get_phase_two_count())
        health_first = (i % 2 == 0)
        if health_first:
            p["dbg"].debug_set_boss_health_fraction(0.55)
        res = [p["stg"].force_break_for_test() for _ in range(5)]
        if not health_first:
            p["dbg"].debug_set_boss_health_fraction(0.55)
        yield 0.25
        p = P()
        mid_ok = res[0] == "started" and res[1:] == ["staggered"] * 4 and p["stg"].get_stagger_count() == c0[0] + 1 and p["stg"].get_dropped_break_count("staggered") == c0[1] + 4 and not p["ph"].is_in_transition()
        yield 0.5
        p = P()
        waiting = p["stg"].is_staggered() and p["ph"].get_phase_two_count() == c0[2]
        started = yield from until(lambda: P()["ph"].get_phase_two_count() > c0[2], 6.0)
        p = P()
        ok = mid_ok and waiting and started and p["stg"].get_last_end_time() <= p["ph"].get_last_transition_start_time() + 0.001
        outcomes.append(ok)
        if not ok:
            log("trial %d: res=%s mid_ok=%s waiting=%s started=%s" % (i, res, mid_ok, waiting, started))
        yield from until(lambda: not P()["ph"].is_in_transition(), 4.0)
    P()["stg"].set_editor_property("stagger_seconds", 2.5)
    check("S07 five breaks in one frame make one break (started + 4 staggered), the transition waits for its end: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def s09_blade():
    for kind in ("control", "break", "transition"):
        outcomes = []
        for i in range(1 if kind == "control" else N(3)):
            yield from fresh()
            p = P()
            place(p, 250, -70)
            hp0 = attr(p["pawn"], "Attribute.Health")
            hits0 = p["sw"].get_hit_count()
            p["tr"].start_move("A4", True)
            if kind != "control":
                yield from until(lambda: P()["tr"].get_position() >= (0.62 if kind == "break" else 0.50), 3.0)
                event("break" if kind == "break" else "health", P())
                yield 0.1
                off1 = not P()["sw"].is_blade_active()
                yield 0.15
                off2 = not P()["sw"].is_blade_active()
            else:
                off1 = off2 = True
            yield 1.8
            p = P()
            lost = hp0 - attr(p["pawn"], "Attribute.Health")
            if kind == "control":
                ok = abs(lost - 20.0) < 0.01 and p["sw"].get_hit_count() == hits0 + 1
            else:
                ok = lost == 0 and off1 and off2 and p["sw"].get_hit_count() == hits0
            outcomes.append(ok)
            if not ok:
                log("S09 %s trial %d: lost %s blade off %s/%s" % (kind, i, lost, off1, off2))
            if kind == "transition":
                yield from until(lambda: not P()["ph"].is_in_transition(), 4.0)
        check("S09 A4 %s: %s %d/%d trials" % (kind, "damage 20 once" if kind == "control" else "blade off at once, no damage", sum(outcomes), len(outcomes)), all(outcomes))


def s10_pending_punish():
    for kind in ("break", "health"):
        outcomes = []
        for i in range(N(3)):
            yield from fresh()
            p = P()
            p["stg"].set_editor_property("stagger_seconds", 0.6)
            place(p, 700, 0)
            c0 = (p["pu"].get_released_count(), p["pu"].get_cancelled_count(), p["pu"].get_accepted_count())
            p["pu"].notify_heal_started_for_test()
            yield 0.2
            event(kind, P())
            yield 0.25
            p = P()
            cleared = (not p["pu"].is_pending()) and p["pu"].get_released_count() == c0[0] and p["pu"].get_cancelled_count() == c0[1] + 1 and p["pu"].get_cooldown_remaining() == 0.0
            yield from until(lambda: (not P()["stg"].is_staggered()) and (not P()["ph"].is_in_transition()), 8.0)
            yield 0.3
            P()["pu"].notify_heal_started_for_test()
            second = yield from until(lambda: P()["pu"].get_released_count() > c0[0], 1.5)
            p = P()
            ok = cleared and p["pu"].get_accepted_count() == c0[2] + 2 and second and p["pu"].get_released_count() == c0[0] + 1
            outcomes.append(ok)
            if not ok:
                log("S10 %s trial %d: cleared %s accepted %d released %d" % (kind, i, cleared, p["pu"].get_accepted_count() - c0[2], p["pu"].get_released_count() - c0[0]))
        P()["stg"].set_editor_property("stagger_seconds", 2.5)
        check("S10 pending A5 punish cleared by a %s, nothing released, cooldown untouched, the next heal is accepted: %d/%d trials" % ("stance break" if kind == "break" else "phase transition", sum(outcomes), len(outcomes)), all(outcomes))


def s11_javelin():
    for kind in ("control", "break", "health"):
        outcomes = []
        for i in range(1 if kind == "control" else N(3)):
            yield from fresh()
            p = P()
            p["stg"].set_editor_property("stagger_seconds", 0.6)
            place(p, 1000, 0)
            hp0 = attr(p["pawn"], "Attribute.Health")
            hits0 = p["pu"].get_javelin_hit_count()
            p["pu"].notify_heal_started_for_test()
            yield from until(lambda: P()["pu"].get_released_count() > 0 and len(javelins()) == 1, 3.0)
            yield 0.3
            if kind != "control":
                event(kind, P())
                yield 0.35
                gone = len(javelins()) == 0
            else:
                gone = True
            yield 2.0
            p = P()
            lost = hp0 - attr(p["pawn"], "Attribute.Health")
            if kind == "control":
                ok = p["pu"].get_javelin_hit_count() == hits0 + 1
            else:
                ok = gone and p["pu"].get_javelin_hit_count() == hits0 and lost == 0
            outcomes.append(ok)
            if not ok:
                log("S11 %s trial %d: gone %s hits %d lost %s" % (kind, i, gone, p["pu"].get_javelin_hit_count() - hits0, lost))
            yield from until(lambda: (not P()["stg"].is_staggered()) and (not P()["ph"].is_in_transition()), 8.0)
        P()["stg"].set_editor_property("stagger_seconds", 2.5)
        check("S11 javelin %s: %s %d/%d trials" % (kind, "hits once" if kind == "control" else "destroyed within 0.35 s, no hit", sum(outcomes), len(outcomes)), all(outcomes))


def s12_wave():
    for kind in ("control", "break", "health"):
        outcomes = []
        for i in range(1 if kind == "control" else N(3)):
            yield from fresh()
            p = P()
            p["stg"].set_editor_property("stagger_seconds", 0.6)
            place(p, 700, 0)
            hp0 = attr(p["pawn"], "Attribute.Health")
            hits0 = p["wave"].get_hit_count()
            p["wave"].launch_for_test()
            if kind != "control":
                yield 0.15
                event(kind, P())
                yield 0.35
                off = not P()["wave"].is_wave_active()
            else:
                off = True
            yield 1.5
            p = P()
            lost = hp0 - attr(p["pawn"], "Attribute.Health")
            ok = (p["wave"].get_hit_count() == hits0 + 1 and abs(lost - 48.0) < 0.01) if kind == "control" else (off and lost == 0 and p["wave"].get_hit_count() == hits0)
            outcomes.append(ok)
            if not ok:
                log("S12 %s trial %d: off %s lost %s" % (kind, i, off, lost))
            yield from until(lambda: (not P()["stg"].is_staggered()) and (not P()["ph"].is_in_transition()), 8.0)
        P()["stg"].set_editor_property("stagger_seconds", 2.5)
        check("S12 A6 wave %s: %s %d/%d trials" % (kind, "hits once for 48" if kind == "control" else "ends within 0.35 s, no damage", sum(outcomes), len(outcomes)), all(outcomes))


def s14_reset_in_roar():
    outcomes = []
    for i in range(N(5)):
        yield from fresh()
        p = P()
        A0 = attr(p["boss"], "Attribute.Attack")
        g0 = p["enc"].get_generation()
        p["dbg"].debug_set_boss_health_fraction(0.55)
        yield from until(lambda: P()["ph"].is_in_transition(), 3.0)
        yield 0.5
        P()["enc"].reset_for_test()
        yield 0.3
        p = P()
        a = attr(p["boss"], "Attribute.Attack")
        poise = attr(p["boss"], "Attribute.Poise")
        ok = ((not p["ph"].is_in_transition()) and (not p["ph"].is_phase_two()) and abs(a - A0) < 0.6 and has_tag(p["boss"], "Status.HitStunImmune") is False and p["post"].get_hold_name() == "None" and poise >= 99.5
              and p["enc"].get_generation() == g0 + 1 and p["enc"].is_dormant())
        c = p["ph"].get_phase_two_count()
        p["enc"].wake()
        p["enc"].hold_for_test(True)
        yield 2.5
        ok = ok and P()["ph"].get_phase_two_count() == c and not P()["ph"].is_in_transition()
        outcomes.append(ok)
        if not ok:
            log("trial %d: attack %s (A0 %s) immune %s hold %s poise %s" % (i, a, A0, has_tag(p["boss"], "Status.HitStunImmune"), p["post"].get_hold_name(), poise))
    check("S14 reset in the roar: phase one, buffs gone, immunity gone, posture free and full, one generation up, asleep, no second roar: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def s15_reset_in_break():
    outcomes = []
    for i in range(N(5)):
        yield from fresh()
        p = P()
        p["stg"].force_break_for_test()
        yield 0.3
        c = P()["ph"].get_phase_two_count()
        P()["dbg"].debug_set_boss_health_fraction(0.55)
        yield 0.7
        P()["enc"].reset_for_test()
        yield 0.3
        P()["enc"].wake()
        P()["enc"].hold_for_test(True)
        yield 4.0
        p = P()
        poise = attr(p["boss"], "Attribute.Poise")
        ok = (not p["stg"].is_staggered()) and (not p["ph"].is_transition_queued()) and p["ph"].get_phase_two_count() == c and poise >= 99.5 and p["stg"].get_cooldown_remaining() == 0.0 and p["post"].get_hold_name() == "None"
        outcomes.append(ok)
        if not ok:
            log("trial %d: staggered %s queued %s count %d poise %s hold %s" % (i, p["stg"].is_staggered(), p["ph"].is_transition_queued(), p["ph"].get_phase_two_count() - c, poise, p["post"].get_hold_name()))
    check("S15 reset during a break with a queued transition: no break, nothing queued, no transition, posture full, cooldown clear: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def s16_cooldown():
    outcomes = []
    for i in range(N(3)):
        yield from fresh()
        p = P()
        p["stg"].set_editor_property("cooldown_seconds", 5.0)
        p["stg"].set_editor_property("stagger_seconds", 0.6)
        r1 = p["stg"].try_break_for_test()
        yield from until(lambda: (not P()["stg"].is_staggered()) and P()["stg"].get_last_end_time() > 0, 6.0)
        yield 1.0
        d0 = P()["stg"].get_dropped_break_count("cooldown")
        r2 = P()["stg"].try_break_for_test()
        lines = " ".join(P()["dbg"].build_lines())
        yield 4.4
        r3 = P()["stg"].try_break_for_test()
        yield from until(lambda: not P()["stg"].is_staggered(), 6.0)
        yield 1.0
        P()["enc"].reset_for_test()
        yield 0.8
        P()["enc"].wake()
        P()["enc"].hold_for_test(True)
        yield 1.0
        p = P()
        cd = p["stg"].get_cooldown_remaining()
        r4 = p["stg"].try_break_for_test()
        ok = r1 == "started" and r2 == "cooldown" and p["stg"].get_dropped_break_count("cooldown") >= d0 + 1 and r3 == "started" and cd == 0.0 and r4 == "started" and "last: cooldown" in lines
        outcomes.append(ok)
        if not ok:
            log("trial %d: %s %s %s %s cooldown after reset %s" % (i, r1, r2, r3, r4, cd))
        yield from until(lambda: not P()["stg"].is_staggered(), 6.0)
    P()["stg"].set_editor_property("cooldown_seconds", 0.0)
    P()["stg"].set_editor_property("stagger_seconds", 2.5)
    check("S16 stance break cooldown: dropped and visible while it runs, free after it, cleared by a reset: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def s19_hold_in_break():
    outcomes = []
    for i in range(N(3)):
        yield from fresh()
        p = P()
        p["stg"].force_break_for_test()
        yield 0.2
        z0 = attr(P()["boss"], "Attribute.Poise")
        s0 = P()["post"].get_suppressed_drain_count()
        yield 0.3
        P()["dbg"].debug_drain_boss_posture(20.0)
        yield 0.2
        z1 = attr(P()["boss"], "Attribute.Poise")
        yield 0.3
        P()["dbg"].debug_drain_boss_posture(20.0)
        yield 0.2
        z2 = attr(P()["boss"], "Attribute.Poise")
        sup = P()["post"].get_suppressed_drain_count() - s0
        yield from until(lambda: not P()["stg"].is_staggered(), 8.0)
        yield 0.3
        z3 = attr(P()["boss"], "Attribute.Poise")
        ok = abs(z0) <= 0.5 and abs(z1) <= 0.5 and abs(z2) <= 0.5 and sup >= 2 and abs(z3 - 100.0) <= 0.5
        outcomes.append(ok)
        if not ok:
            log("trial %d: posture %s %s %s suppressed %d end %s" % (i, z0, z1, z2, sup, z3))
    check("S19 posture held at 0 during the break, two drains ignored and counted, refilled to 100 at the end: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def script():
    yield 9.0
    p = P()
    log("boss awake test mode %s" % MODE)
    for scenario in (s00_immunity, s01_break_in_roar, s02_posture_pinned, s03_regen_after, s04_queue_gap, s05_queue_behind_riposte, s06_queue_behind_getup, s07_five_breaks, s09_blade, s10_pending_punish, s11_javelin, s12_wave,
                     s14_reset_in_roar, s15_reset_in_break, s16_cooldown, s19_hold_in_break):
        log("== %s" % scenario.__name__)
        yield from scenario()
    check("INV1 never staggered and in transition at once (%d ticks)" % S["inv"]["inv1"], S["inv"]["inv1"] == 0)
    check("INV2 the posture hold matched the state on every tick (%d violations)" % S["inv"]["inv2"], S["inv"]["inv2"] == 0)
    p = P()
    live = yield from until(lambda: P()["tr"].is_neutral() or P()["enc"].is_dormant(), 8.0)
    check("LIVE the boss ends the run in a usable state", live and len(javelins()) == 0 and not P()["stg"].is_staggered() and not P()["ph"].is_in_transition())


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        p = P()
        p["stg"].set_editor_property("stagger_seconds", 2.5)
        p["stg"].set_editor_property("cooldown_seconds", 0.0)
    except Exception:
        pass
    log("RESULT %d/%d passed" % (sum(1 for r in results if r), len(results)))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def invariants(p):
    stg, ph, post = p["stg"], p["ph"], p["post"]
    if stg is None or ph is None or post is None:
        return
    staggered, transition = stg.is_staggered(), ph.is_in_transition()
    if staggered and transition:
        S["inv"]["inv1"] += 1
    want = "Zero" if staggered else ("Pinned" if transition else "None")
    state = (staggered, transition)
    if S.get("inv_state") != state:
        S["inv_state"] = state
        S["inv_since"] = S["now"]
    if post.get_hold_name() != want and S["now"] - S.get("inv_since", S["now"]) > 0.2:
        S["inv"]["inv2"] += 1


def _tick(dt):
    s = S
    s["t"] += dt
    s["now"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w, pc, pawn, boss = actors()
    if pawn is None or boss is None:
        return
    if s["now"] < s["press_until"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(IA_NORMAL), unreal.Vector(1, 0, 0))
    if s["gen"] is not None:
        invariants(P())
    if s["wait"] > 0:
        s["wait"] -= dt
        return
    if s["gen"] is None:
        s["gen"] = script()
    try:
        s["wait"] = float(next(s["gen"]))
    except StopIteration:
        finish()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        check("tick raised", False)
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
