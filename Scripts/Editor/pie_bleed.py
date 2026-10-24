"""
Gate 3, M12: the bleed status (URPGBossBleed): buildup per hit, a proc at the threshold (100, then +20 up to 200) that takes 3 percent of the boss's maximum health once, never during death, sleep or the phase
transition, never twice in one frame, never multiplied by the stance break's critical, cleared by the encounter reset. The boss is held awake and the player stands 110 cm in front of it; the first scenarios drive the
buildup directly (add_buildup_for_test), the last uses real light hits with the intake's bleed override (the sword's own rows have no bleed: the dex weapons come with the builds, M13). Generator style: `yield seconds` waits.
Log prefix [Bleed]; ends with RESULT n/m passed. Run pie_debug_overlay.py once after an editor start first.
"""
import math
import unreal

log = lambda m: unreal.log("[Bleed] " + m)
IA = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
BLEED_FRACTION = 0.03  # Owner decision; RPGBossBleed has no reflected fraction getter.
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


def max_attr(actor, tag):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    try:
        return c.call_method("GetMaxAttributeValue", args=(t,))
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
            "post": comp(boss, "RPGBossPosture"), "bleed": comp(boss, "RPGBossBleed"), "ph": comp(boss, "RPGBossPhases"), "intake": comp(pawn, "RPGHitIntake")}


def place(p, dist=110.0):
    boss, pawn = p["boss"], p["pawn"]
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw)
    q = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(q, bl).yaw
    pawn.set_actor_location_and_rotation(q, unreal.Rotator(0, 0, look), False, True)
    p["pc"].set_control_rotation(unreal.Rotator(0, 0, look))


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


def hit_once(action, seconds, timeout=3.5):
    """Presses the action and waits for the intake to count one more hit and for the effects that follow it. Returns True when a hit arrived."""
    p = P()
    place(p)
    p["dbg"].debug_refill_player()
    yield 0.6  # the teleport leaves the player a moment in the air
    p = P()
    n0 = p["intake"].get_boss_hit_count()
    press(action, seconds)
    ok = yield from until(lambda: P()["intake"].get_boss_hit_count() > n0, timeout)
    yield 0.3
    return ok


def health(p):
    return attr(p["boss"], "Attribute.Health")


def expected_proc_damage(p):
    maximum = max_attr(p["boss"], "Attribute.Health")
    return maximum * BLEED_FRACTION if maximum is not None else None


# ---- scenarios -------------------------------------------------------------------------------------------------------------------------------------------------------------
def a_five_hits_proc():
    yield from fresh()
    p = P()
    check("A the bleed component exists with the Freeze values", p["bleed"] is not None and p["bleed"].get_threshold() == 100.0, "threshold %s" % (p["bleed"].get_threshold() if p["bleed"] else None))
    h0 = health(p)
    results4 = [p["bleed"].add_buildup_for_test(20.0) for _ in range(4)]
    yield 0.2
    p = P()
    check("A four hits of 20 add up to 80 and do not proc", results4 == ["added"] * 4 and abs(p["bleed"].get_buildup() - 80.0) < 0.01 and p["bleed"].get_proc_count() == 0, "%s buildup %.0f" % (results4, p["bleed"].get_buildup()))
    r5 = p["bleed"].add_buildup_for_test(20.0)
    yield 0.3
    p = P()
    h1 = health(p)
    check("A the fifth hit procs once", r5 == "proc" and p["bleed"].get_proc_count() == 1, "%s procs %d" % (r5, p["bleed"].get_proc_count()))
    expected = expected_proc_damage(p)
    check("A the proc takes 3 percent of maximum health", expected is not None and abs((h0 - h1) - expected) <= 0.6 and abs(p["bleed"].get_last_proc_damage() - expected) <= 0.1, "health %s -> %s, expected %.1f, last proc damage %.1f" % (h0, h1, expected or -1.0, p["bleed"].get_last_proc_damage()))
    check("A the buildup is reset and the next threshold is 120", p["bleed"].get_buildup() == 0.0 and p["bleed"].get_threshold() == 120.0, "buildup %.0f threshold %.0f" % (p["bleed"].get_buildup(), p["bleed"].get_threshold()))


def b_same_frame():
    yield from fresh()
    b = P()["bleed"]
    procs0 = b.get_proc_count()  # the counter is kept across resets (A already procced once in this session)
    b.add_buildup_for_test(80.0)
    r1 = b.add_buildup_for_test(20.0)  # the proc
    r2 = b.add_buildup_for_test(20.0)  # the same frame: ignored
    r3 = b.add_buildup_for_test(20.0)
    yield 0.2
    p = P()
    check("B two more hits in the frame of a proc do not proc again and add nothing", r1 == "proc" and r2 == "same frame as a proc" and r3 == "same frame as a proc" and p["bleed"].get_proc_count() == procs0 + 1 and p["bleed"].get_buildup() == 0.0, "%s %s %s procs %d (before %d) buildup %.0f" % (r1, r2, r3, p["bleed"].get_proc_count(), procs0, p["bleed"].get_buildup()))
    r4 = p["bleed"].add_buildup_for_test(20.0)  # a later frame counts again
    check("B the next frame adds again", r4 == "added" and abs(p["bleed"].get_buildup() - 20.0) < 0.01, "%s buildup %.0f" % (r4, p["bleed"].get_buildup()))


def c_transition():
    yield from fresh()
    p = P()
    p["dbg"].debug_set_boss_health_fraction(0.55)
    ok = yield from until(lambda: P()["ph"].is_in_transition(), 3.0)
    yield 0.3
    p = P()
    r = p["bleed"].add_buildup_for_test(20.0)
    check("C no buildup during the phase transition", ok and r == "transition" and p["bleed"].get_buildup() == 0.0, "%s buildup %.0f" % (r, p["bleed"].get_buildup()))
    yield from until(lambda: not P()["ph"].is_in_transition(), 4.0)
    yield 0.3
    r2 = P()["bleed"].add_buildup_for_test(20.0)
    check("C buildup works again after the roar", r2 == "added", r2)


def d_dormant():
    p = P()
    p["enc"].reset_for_test()
    yield 0.8
    r = P()["bleed"].add_buildup_for_test(20.0)
    check("D a sleeping boss builds nothing", r == "dormant", r)


def g_dead():
    """Last: the pack destroys a dead boss a few seconds after its death and an encounter reset does not bring it back, so nothing may run after this."""
    yield from fresh()
    P()["dbg"].debug_kill_boss()
    yield 0.4
    r2 = P()["bleed"].add_buildup_for_test(20.0)
    check("G a dead boss builds nothing", r2 == "dead", r2)


def e_no_critical_and_no_kill():
    yield from fresh()
    p = P()
    p["stg"].set_critical_on_every_hit_for_test(True)  # the old rule multiplies EVERY health loss while the boss is down: the proc must be exempt
    broke = p["stg"].force_break_for_test()
    yield 0.6
    p = P()
    h0 = health(p)
    down = p["stg"].is_staggered()
    for _ in range(5):
        p["bleed"].add_buildup_for_test(20.0)
        yield 0.05
    yield 0.5
    p = P()
    h1 = health(p)
    expected = expected_proc_damage(p)
    check("E a proc while the boss is down (the break started: %s) takes 3 percent of maximum health, not 3 percent x 2.5" % broke, down and expected is not None and abs((h0 - h1) - expected) <= 0.6, "staggered %s, health %s -> %s, expected %.1f" % (down, h0, h1, expected or -1.0))
    p["stg"].set_critical_on_every_hit_for_test(False)
    yield from until(lambda: not P()["stg"].is_staggered(), 8.0)
    P()["bleed"].reset_bleed()  # the proc above raised the threshold to 120: five more hits of 20 would not proc
    # A proc never kills: 2 percent health left (less than the 3 percent proc), so the proc leaves 1. Below 60 percent the roar starts: wait for it to end first (buildup is ignored during it).
    p = P()
    p["dbg"].debug_set_boss_health_fraction(0.02)
    yield 0.4
    yield from until(lambda: P()["ph"].is_in_transition(), 3.0)
    yield from until(lambda: not P()["ph"].is_in_transition(), 5.0)
    yield 0.4
    p = P()
    h2 = health(p)
    for _ in range(5):
        P()["bleed"].add_buildup_for_test(20.0)
        yield 0.05
    yield 0.4
    h3 = health(P())
    check("E a proc never kills: 2 percent health left, the proc leaves 1", h2 is not None and h3 is not None and abs(h3 - 1.0) <= 0.6, "health %s -> %s" % (h2, h3))


def f_real_hits_and_reset():
    yield from fresh()
    p = P()
    p["intake"].set_bleed_override_for_test(20.0)
    procs0 = p["bleed"].get_proc_count()
    for k in range(1, 6):
        ok = yield from hit_once("IA_NormalAttack", 0.12)
        b = P()["bleed"]
        if k < 5:
            check("F real light hit %d: bleed %.0f of 100" % (k, 20.0 * k), ok and abs(b.get_buildup() - 20.0 * k) < 0.01 and b.get_proc_count() == procs0, "buildup %.0f procs %d" % (b.get_buildup(), b.get_proc_count()))
            yield 0.7
        else:
            check("F real light hit 5 procs the bleed once", ok and b.get_proc_count() == procs0 + 1 and b.get_buildup() == 0.0, "buildup %.0f procs %d" % (b.get_buildup(), b.get_proc_count()))
    P()["intake"].set_bleed_override_for_test(-1.0)
    yield from until(lambda: not P()["ph"].is_in_transition(), 4.0)  # the five hits took the boss under 60 percent: the roar starts and buildup is ignored during it
    P()["bleed"].add_buildup_for_test(40.0)  # a partial buildup on a raised threshold (120 after the proc): the reset must clear both
    yield 0.2
    b = P()["bleed"]
    before = (b.get_buildup(), b.get_threshold())
    P()["enc"].reset_for_test()
    yield 0.8
    b = P()["bleed"]
    check("F the encounter reset clears a partial buildup (40) and the raised threshold (120)", before == (40.0, 120.0) and b.get_buildup() == 0.0 and b.get_threshold() == 100.0, "before %s, after buildup %.0f threshold %.0f" % (before, b.get_buildup(), b.get_threshold()))


def script():
    yield from a_five_hits_proc()
    yield from b_same_frame()
    yield from c_transition()
    yield from d_dormant()
    yield from e_no_critical_and_no_kill()
    yield from f_real_hits_and_reset()
    yield from g_dead()


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
    if s["now"] - s.get("hb", 0.0) > 10.0:
        s["hb"] = s["now"]
        log("heartbeat: %.0f s, pawn %s, boss %s, wait %.2f, script running %s" % (s["now"], pawn.get_name() if pawn else None, boss.get_name() if boss else None, s["wait"], s["gen"] is not None))
    if boss is None:
        s["gone"] = s.get("gone", 0.0) + dt
        if s["gone"] > 15.0 and s["gen"] is not None:
            check("the boss is still in the world (the pack destroys a dead boss: a scenario must not run after a kill)", False, "gone for %.0f s" % s["gone"])
            finish()
        return
    s["gone"] = 0.0
    if pawn is None:
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
