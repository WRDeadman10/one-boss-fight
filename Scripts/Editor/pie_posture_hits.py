"""
Gate 3, M9: the boss's posture is a pool of its own, drained by the weapon attack table's value of every real hit; the pack's poise stays full; a pool at zero starts the stance break.
The boss is held awake (hold_for_test) and the player stands 110 cm in front of it for every press (real input: IA_NormalAttack, IA_StrongAttack, jump key). The starter sword takes the strength numbers:
light 18, strong 30, jump heavy 38. Generator style: `yield seconds` waits, `yield 0.0` polls on the next tick. Log prefix [Posture]; ends with RESULT n/m passed. Run pie_debug_overlay.py once after an editor start first.
A six lights (100 - 18 k, the sixth breaks), hits during the break are held and counted, the pool refills at the end of the get-up, the pack's poise stays at its maximum; B four strong hits (the fourth breaks);
C three jump heavies (62, 24, then the break); D regeneration after a real hit: nothing for 6 s, then 13 per second.
"""
import math
import unreal

log = lambda m: unreal.log("[Posture] " + m)
IA = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
JUMP_KEY = "Gamepad_FaceButton_Bottom"
results = []
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None, "press_until": 0.0, "action": "IA_NormalAttack"}
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
    w, pc, pawn, boss = actors()
    return {"w": w, "pc": pc, "pawn": pawn, "boss": boss, "enc": comp(boss, "RPGBossEncounter"), "tr": comp(boss, "RPGAttackTracker"), "dbg": comp(boss, "RPGCombatDebug"), "stg": comp(boss, "RPGBossStagger"),
            "post": comp(boss, "RPGBossPosture"), "intake": comp(pawn, "RPGHitIntake"), "ph": comp(boss, "RPGBossPhases")}


def place(p, dist=110.0):
    boss, pawn = p["boss"], p["pawn"]
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw)
    q = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(q, bl).yaw
    pawn.set_actor_location_and_rotation(q, unreal.Rotator(0, 0, look), False, True)
    p["pc"].set_control_rotation(unreal.Rotator(0, 0, look))


def now():
    return unreal.GameplayStatics.get_time_seconds(world())


def until(cond, timeout, step=0.0):
    t0 = S["now"]
    while not cond():
        if S["now"] - t0 > timeout:
            return False
        yield step
    return True


def fresh():
    p = P()
    p["stg"].set_stagger_seconds_for_test(2.5)  # not set_editor_property: in PIE it re-runs the boss Blueprint's construction scripts and the pack's components are rebuilt (KI-083)
    p["stg"].set_cooldown_for_test(0.0)
    p["enc"].reset_for_test()
    yield 0.8
    p = P()
    p["enc"].wake()
    p["enc"].hold_for_test(True)
    p["dbg"].debug_refill_player()
    p["tr"].enter_combat()
    comp(p["pawn"], "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
    yield 2.2
    p = P()
    p["intake"].reset_counters()


def press(action, seconds):
    S["action"] = action
    S["press_until"] = S["now"] + seconds


def hit_once(action, seconds, jump=False, timeout=3.5):
    """Presses the action (after a jump when asked) and waits for the intake to count one more hit and for the posture drain that follows it. Returns True when a hit arrived."""
    p = P()
    place(p)
    p["dbg"].debug_refill_player()  # every swing costs stamina (15 on the pack's sword): six presses would empty it
    yield 0.6  # the teleport leaves the player a moment in the air: a press then would be a jump attack
    p = P()
    n0 = p["intake"].get_boss_hit_count()
    if jump:
        unreal.RPGInputTestUtils.set_key_down(p["pc"], JUMP_KEY, True)
        yield 0.12
        unreal.RPGInputTestUtils.set_key_down(P()["pc"], JUMP_KEY, False)
        yield 0.2
    press(action, seconds)
    ok = yield from until(lambda: P()["intake"].get_boss_hit_count() > n0, timeout)
    yield 0.3
    return ok


def poise_ok():
    v = attr(P()["boss"], "Attribute.Poise")
    return v is not None and v >= 99.0, v


# ---- scenarios -------------------------------------------------------------------------------------------------------------------------------------------------------------
def a_six_lights():
    yield from fresh()
    pins = []
    for k in range(1, 7):
        ok = yield from hit_once("IA_NormalAttack", 0.12)
        p = P()
        post = p["post"].get_posture()
        pin, pv = poise_ok()
        pins.append(pin)
        if k < 6:
            check("A light %d: hit counted, posture %.0f (expect %d)" % (k, post, 100 - 18 * k), ok and abs(post - (100 - 18 * k)) <= 0.6, "last drain %s" % p["post"].get_last_drain_source())
            yield 0.7
        else:
            broke = yield from until(lambda: P()["stg"].is_staggered(), 1.5)
            p = P()
            check("A light 6 breaks the pool: posture 0, the stance break started, hold Zero", ok and broke and p["post"].get_posture() == 0.0 and p["post"].get_hold_name() == "Zero", "posture %.1f hold %s breaks asked %d result %s" % (p["post"].get_posture(), p["post"].get_hold_name(), p["post"].get_break_request_count(), p["post"].get_last_break_result()))
    check("A the pack's poise stayed full after every hit (the pack's own hit stun never started by itself)", all(pins), "%s" % pins)
    # a hit during the break is held and counted
    p = P()
    s0 = p["post"].get_suppressed_drain_count()
    d0 = p["post"].get_drain_count()
    p["stg"].set_use_riposte_clips_for_test(False)  # in front of the downed boss a press is a riposte (paired clips, the swing is cut): the stand-in lets the swing land, which is what this check needs
    yield from hit_once("IA_NormalAttack", 0.12, timeout=2.0)
    P()["stg"].set_use_riposte_clips_for_test(True)
    p = P()
    check("A a hit during the break changes nothing and is counted", p["post"].get_posture() == 0.0 and p["post"].get_suppressed_drain_count() == s0 + 1 and p["post"].get_drain_count() == d0, "suppressed %d -> %d" % (s0, p["post"].get_suppressed_drain_count()))
    ok = yield from until(lambda: not P()["stg"].is_staggered(), 8.0)
    yield 0.3
    p = P()
    check("A the pool is full again at the end of the get-up and the hold is off", ok and abs(p["post"].get_posture() - 100.0) < 0.6 and p["post"].get_hold_name() == "None", "posture %.1f hold %s" % (p["post"].get_posture(), p["post"].get_hold_name()))


def b_four_strongs():
    yield from fresh()
    for k in range(1, 5):
        ok = yield from hit_once("IA_StrongAttack", 0.12, timeout=4.0)
        p = P()
        post = p["post"].get_posture()
        if k < 4:
            check("B strong %d: posture %.0f (expect %d)" % (k, post, 100 - 30 * k), ok and abs(post - (100 - 30 * k)) <= 0.6)
            yield 1.2
        else:
            broke = yield from until(lambda: P()["stg"].is_staggered(), 1.5)
            check("B strong 4 breaks the pool (100 - 4 x 30 = -20)", ok and broke and P()["post"].get_posture() == 0.0, "posture %.1f" % P()["post"].get_posture())
    yield from until(lambda: not P()["stg"].is_staggered(), 8.0)


def c_three_jump_heavies():
    yield from fresh()
    for k in range(1, 4):
        ok = yield from hit_once("IA_StrongAttack", 0.12, jump=True, timeout=4.0)
        p = P()
        post = p["post"].get_posture()
        if k < 3:
            check("C jump heavy %d: posture %.0f (expect %d)" % (k, post, 100 - 38 * k), ok and abs(post - (100 - 38 * k)) <= 0.6, p["intake"].get_last_record_text()[:110])
            yield 1.5
        else:
            broke = yield from until(lambda: P()["stg"].is_staggered(), 1.5)
            check("C three jump heavies break the pool (114 against 100)", ok and broke and P()["post"].get_posture() == 0.0, "posture %.1f" % P()["post"].get_posture())
    yield from until(lambda: not P()["stg"].is_staggered(), 8.0)


def d_regen_after_a_hit():
    yield from fresh()
    ok = yield from hit_once("IA_NormalAttack", 0.12)
    p = P()
    t_drain = p["post"].get_last_drain_time()
    check("D one light hit: posture 82", ok and abs(p["post"].get_posture() - 82.0) <= 0.6, "%.1f" % p["post"].get_posture())
    yield max(0.0, t_drain + 5.0 - now())
    v5 = P()["post"].get_posture()
    check("D 5.0 s after the hit: no regeneration yet (82)", abs(v5 - 82.0) <= 0.6, "%.1f" % v5)
    yield max(0.0, t_drain + 7.0 - now())
    v7 = P()["post"].get_posture()
    check("D 7.0 s after the hit: regeneration has run for about 1 s (82 + 13 = 95)", 90.0 <= v7 <= 99.0, "%.1f" % v7)
    yield max(0.0, t_drain + 9.5 - now())
    v95 = P()["post"].get_posture()
    check("D 9.5 s after the hit: full (100)", abs(v95 - 100.0) <= 0.6, "%.1f" % v95)


def e_dropped_break_does_not_strand_the_pool():
    """A break request that the gate drops (a cooldown) must not leave the pool at zero for ever: nothing holds it, so it regenerates (6 s delay, 13 per second) like any other drain."""
    yield from fresh()
    P()["stg"].set_cooldown_for_test(5.0)
    P()["dbg"].debug_drain_boss_posture(100.0)
    broke = yield from until(lambda: P()["stg"].is_staggered(), 1.5)
    ended = yield from until(lambda: not P()["stg"].is_staggered(), 9.0)
    yield 0.3
    p = P()
    check("E the first break ran and ended, the pool is full again (%.1f)" % p["post"].get_posture(), broke and ended and abs(p["post"].get_posture() - 100.0) < 0.6 and p["post"].get_hold_name() == "None", "cooldown left %.1f" % p["stg"].get_cooldown_remaining())
    p["dbg"].debug_drain_boss_posture(100.0)  # inside the cooldown: the request is dropped
    yield 0.3
    p = P()
    check("E a break asked inside the cooldown is dropped (%s), the pool is 0 and nothing holds it" % p["post"].get_last_break_result(), p["post"].get_last_break_result() == "cooldown" and p["post"].get_posture() == 0.0 and p["post"].get_hold_name() == "None" and not p["stg"].is_staggered(), "posture %.1f hold %s" % (p["post"].get_posture(), p["post"].get_hold_name()))
    yield 5.5
    v55 = P()["post"].get_posture()
    check("E 5.8 s after the drain: no regeneration yet (0)", v55 < 0.6, "%.1f" % v55)
    yield 2.2
    v8 = P()["post"].get_posture()
    check("E 8 s after the drain: the pool came back from zero (about 2 s of 13 per second)", 10.0 <= v8 <= 40.0, "%.1f" % v8)
    P()["stg"].set_cooldown_for_test(0.0)


def f_break_and_threshold_in_one_hit():
    """One light hit that breaks the pool AND takes the boss under the phase two threshold (60 percent): the stance break is seen first and the roar is queued behind it (Freeze 21 and 1201), every time (the intake's record is finished one frame after the pack's event: the phase component must wait for it)."""
    outcomes = []
    for trial in range(1, 6):
        yield from fresh()
        p = P()
        p["dbg"].debug_set_boss_health_fraction(0.602)  # 301 of 500: any hit crosses 300
        p["dbg"].debug_set_boss_posture(10.0)  # one light hit (18) empties the pool
        yield 0.4
        h0 = attr(P()["boss"], "Attribute.Health")
        qs0 = P()["ph"].get_queued_start_count()
        ok = yield from hit_once("IA_NormalAttack", 0.12)
        broke = yield from until(lambda: P()["stg"].is_staggered(), 1.5)
        p = P()
        h1 = attr(p["boss"], "Attribute.Health")
        queued = p["ph"].is_transition_queued()
        in_roar = p["ph"].is_in_transition()
        started = yield from until(lambda: P()["ph"].is_in_transition(), 9.0)
        good = ok and broke and queued and not in_roar and started and P()["ph"].get_queued_start_count() == qs0 + 1
        outcomes.append(good)
        log("   trial %d: health %s -> %s, hit %s, break %s, transition queued behind it %s, roar already running %s, roar started after the break %s, queued starts %d -> %d" % (trial, h0, h1, ok, broke, queued, in_roar, started, qs0, P()["ph"].get_queued_start_count()))
        yield from until(lambda: not P()["ph"].is_in_transition(), 6.0)
    check("F a hit that breaks the pool and crosses the threshold: break first, roar queued behind it, in %d of %d trials" % (sum(outcomes), len(outcomes)), all(outcomes), "%s" % outcomes)


def script():
    yield from a_six_lights()
    yield from b_four_strongs()
    yield from c_three_jump_heavies()
    yield from d_regen_after_a_hit()
    yield from e_dropped_break_does_not_strand_the_pool()
    yield from f_break_and_threshold_in_one_hit()


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
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w, pc, pawn, boss = actors()
    if pawn is None or boss is None:
        return
    if s["now"] < s["press_until"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(IA + s["action"]), unreal.Vector(1, 0, 0))
    if s["wait"] > 0:
        s["wait"] -= dt
        return
    if s["gen"] is None:
        if s["t"] < 9.0:  # the level is waking
            return
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
