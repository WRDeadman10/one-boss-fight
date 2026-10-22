"""
Gate 3, M10: every swing of the player costs what the weapon attack table's row says, on top of or instead of the pack's own 15 (URPGSwingTracker). Real presses against the held boss (the player stands 110 cm in front of it):
the swing tracker finds the weapon (the starter sword), the kind from the ability's montage arrays and the stance; the stamina drop of the swing is measured 0.4 s after the press (the pack's stamina regeneration has not started).
The sword's rows leave the pack's cost (15); test overrides stand in for the strength build's 35 and the dex build's 10 (the other weapons come with the builds, M13). Log prefix [Stamina]; ends with RESULT n/m passed.
Run pie_debug_overlay.py once after an editor start first.
"""
import math
import unreal

log = lambda m: unreal.log("[Stamina] " + m)
IA = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
JUMP_KEY = "Gamepad_FaceButton_Bottom"
results = []
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None, "press_until": 0.0, "action": "IA_NormalAttack"}
handle = None
KIND = unreal.RPGAttackKind


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


def set_attr(actor, tag, value):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    c.call_method("Set Current Attribute Value", args=(t, value))


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
            "post": comp(boss, "RPGBossPosture"), "swing": comp(pawn, "RPGSwingTracker"), "intake": comp(pawn, "RPGHitIntake")}


def place(p, dist=110.0):
    boss, pawn = p["boss"], p["pawn"]
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw)
    q = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(q, bl).yaw
    pawn.set_actor_location_and_rotation(q, unreal.Rotator(0, 0, look), False, True)
    p["pc"].set_control_rotation(unreal.Rotator(0, 0, look))
    p["dbg"].debug_set_boss_health_fraction(1.0)  # the swings hit the held boss: a dead boss locks the player's input (victory), so every scenario starts with a full boss


def until(cond, timeout, step=0.0):
    t0 = S["now"]
    while not cond():
        if S["now"] - t0 > timeout:
            return False
        yield step
    return True


def fresh():
    p = P()
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
    p["swing"].reset_counters()
    p["swing"].clear_cost_overrides()


def press(action, seconds):
    S["action"] = action
    S["press_until"] = S["now"] + seconds


def swing_once(action, seconds, jump=False, stamina_start=None):
    """Teleports the player in front of the boss (a refilled stamina or the given value), lets it land, presses (after a jump when asked) and returns (stamina before, stamina 0.4 s after the swing started, the swing text)."""
    p = P()
    place(p)
    p["dbg"].debug_refill_player()
    yield 0.6
    p = P()
    if stamina_start is not None:
        set_attr(p["pawn"], "Attribute.Stamina", stamina_start)  # right before the press: the pack's stamina comes back fast
    n0 = p["swing"].get_attack_swing_count()
    before = attr(p["pawn"], "Attribute.Stamina")
    if jump:
        unreal.RPGInputTestUtils.set_key_down(p["pc"], JUMP_KEY, True)
        yield 0.12
        unreal.RPGInputTestUtils.set_key_down(P()["pc"], JUMP_KEY, False)
        yield 0.2
        before = attr(P()["pawn"], "Attribute.Stamina")
    press(action, seconds)
    yield from until(lambda: P()["swing"].get_attack_swing_count() > n0, 2.0)
    yield 0.4
    p = P()
    after = attr(p["pawn"], "Attribute.Stamina")
    text = p["swing"].get_last_swing_text()
    # let the swing finish before the next one
    yield from until(lambda: P()["pawn"].get_components_by_class(unreal.SkeletalMeshComponent)[0].get_anim_instance().get_current_active_montage() is None, 3.5)
    yield 0.3
    return before, after, text


def drop_is(name, before, after, expected, tolerance=0.6, detail=""):
    drop = (before - after) if (before is not None and after is not None) else None
    check("%s: stamina drop %.1f (expect %.1f)" % (name, drop if drop is not None else -1, expected), drop is not None and abs(drop - expected) <= tolerance, detail[:150])


def script():
    yield from fresh()
    p = P()
    log("stamina maximum %s, pack cost per swing %.0f" % (attr(p["pawn"], "Attribute.Stamina"), p["swing"].get_editor_property("pack_stamina_cost")))

    # the sword's rows leave the pack's cost
    b, a, t = yield from swing_once("IA_NormalAttack", 0.12)
    drop_is("light, no row cost", b, a, 15.0, detail=t)
    check("light: the swing tracker saw a Light swing of the sword, no extra stamina", "kind Light" in t and "weapon SwordCombatStyle" in t and "extra +0.0" in t, t[:150])
    b, a, t = yield from swing_once("IA_StrongAttack", 0.12)
    drop_is("strong, no row cost", b, a, 15.0, detail=t)
    check("strong: kind Strong", "kind Strong" in t, t[:150])
    b, a, t = yield from swing_once("IA_ChargedAttack", 1.6)
    drop_is("charged, no row cost", b, a, 15.0, detail=t)
    check("charged: kind Charged", "kind Charged" in t, t[:150])

    # overrides stand in for the strength build (35 per heavy swing) and the dex build (10 per swing)
    p = P()
    p["swing"].set_cost_override_for_test(KIND.STRONG, 35.0)
    b, a, t = yield from swing_once("IA_StrongAttack", 0.12)
    drop_is("strong with a 35 cost", b, a, 35.0, detail=t)
    check("strong with a 35 cost: the extra is 20", "extra +20.0" in t, t[:150])
    P()["swing"].set_cost_override_for_test(KIND.LIGHT, 10.0)
    b, a, t = yield from swing_once("IA_NormalAttack", 0.12)
    drop_is("light with a 10 cost (5 given back)", b, a, 10.0, detail=t)
    check("light with a 10 cost: the extra is -5", "extra -5.0" in t, t[:150])
    P()["swing"].set_cost_override_for_test(KIND.JUMP_HEAVY, 35.0)
    b, a, t = yield from swing_once("IA_StrongAttack", 0.12, jump=True)
    drop_is("jump heavy with a 35 cost", b, a, 35.0, detail=t)
    check("jump heavy: kind JumpHeavy, started airborne", "kind JumpHeavy" in t and "started airborne" in t, t[:150])

    # never below zero: 20 stamina left, a 35 swing takes it to 0
    P()["swing"].set_cost_override_for_test(KIND.STRONG, 35.0)
    b, a, t = yield from swing_once("IA_StrongAttack", 0.12, stamina_start=20.0)
    check("a 35 swing with 20 stamina left ends at 0, not below", a is not None and a >= -0.01 and a <= 0.6, "before %s after %s %s" % (b, a, t[:90]))

    # a combo: three taps in a row (the pack's input buffer chains the light montages A, B, C): every montage that starts is one swing and pays its own extra
    P()["swing"].clear_cost_overrides()
    P()["swing"].set_cost_override_for_test(KIND.LIGHT, 10.0)
    p = P()
    place(p)
    p["dbg"].debug_refill_player()
    yield 0.6
    sw = P()["swing"]
    sw.reset_counters()
    s_before = attr(P()["pawn"], "Attribute.Stamina")
    for _ in range(3):
        press("IA_NormalAttack", 0.1)
        yield 0.5
    yield from until(lambda: P()["pawn"].get_components_by_class(unreal.SkeletalMeshComponent)[0].get_anim_instance().get_current_active_montage() is None, 3.5)
    sw = P()["swing"]
    lines = list(sw.get_swing_lines())
    n = sw.get_attack_swing_count()
    names = [ln.split("montage ")[1].split(",")[0] if "montage " in ln else "?" for ln in lines]
    check("a combo of three taps: %d swings, each a Light swing of its own montage (%s)" % (n, ", ".join(names)), n >= 2 and len(set(names)) == n and all("kind Light" in ln for ln in lines), "; ".join(l[:60] for l in lines))
    check("a combo: every swing paid its own extra of -5 (total %.1f for %d swings)" % (sw.get_stamina_extra_total(), n), abs(sw.get_stamina_extra_total() - (-5.0 * n)) < 0.01 and all("extra -5.0" in ln for ln in lines), "stamina %s -> %s" % (s_before, attr(P()["pawn"], "Attribute.Stamina")))

    # a dodge out of a swing is not a swing: one attack swing, the extra of that one only
    P()["swing"].reset_counters()
    p = P()
    place(p)
    p["dbg"].debug_refill_player()
    yield 0.6
    press("IA_NormalAttack", 0.1)
    yield 0.2
    press("IA_Dodge", 0.15)
    yield 2.0
    sw = P()["swing"]
    check("a dodge out of a light swing: one attack swing (%d), the dodge's montage is counted as a montage (%d) but not as a swing, extra -5 once (%.1f)" % (sw.get_attack_swing_count(), sw.get_swing_count(), sw.get_stamina_extra_total()),
          sw.get_attack_swing_count() == 1 and sw.get_swing_count() >= 2 and abs(sw.get_stamina_extra_total() + 5.0) < 0.01, "; ".join(l[:70] for l in sw.get_swing_lines()))

    # not an attack: a jump and a dodge are not swings of the weapon
    P()["swing"].clear_cost_overrides()
    p = P()
    place(p)
    p["dbg"].debug_refill_player()
    yield 0.6
    n0 = P()["swing"].get_attack_swing_count()
    unreal.RPGInputTestUtils.set_key_down(P()["pc"], JUMP_KEY, True)
    yield 0.12
    unreal.RPGInputTestUtils.set_key_down(P()["pc"], JUMP_KEY, False)
    yield 1.5
    check("a jump is not an attack swing", P()["swing"].get_attack_swing_count() == n0, "attack swings %d -> %d" % (n0, P()["swing"].get_attack_swing_count()))


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        P()["swing"].clear_cost_overrides()
    except Exception:
        pass
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
        if s["t"] < 9.0:
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
