"""
A lethal synchronized riposte (Freeze 17.4 and 18.2): the boss is set to 3 percent of its runtime maximum health, the riposte impact (100) takes it to zero and the pack's death must start: Status.Dead / the boss destroyed by the pack, one impact, no second damage.
Log prefix [RipostLethal]; ends with RESULT n/m passed. Run pie_debug_overlay.py once after an editor start first.
"""
import math
import unreal

log = lambda m: unreal.log("[RipostLethal] " + m)
IA = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
LETHAL_HEALTH_FRACTION = 0.03  # Owner's new bleed fraction; at 2000 maximum this is 60, below the fixed 100-damage riposte.
results = []
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None, "press_until": 0.0, "action": "IA_NormalAttack", "samples": None}
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
            "swing": comp(pawn, "RPGSwingTracker") if pawn else None, "intake": comp(pawn, "RPGHitIntake") if pawn else None}


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


def press(action, seconds):
    S["action"] = action
    S["press_until"] = S["now"] + seconds


def fresh():
    p = P()
    p["stg"].set_stagger_seconds_for_test(2.5)
    p["stg"].set_cooldown_for_test(0.0)
    p["stg"].set_use_riposte_clips_for_test(True)
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
    p["swing"].reset_counters()




def has_tag(actor, tag):
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    try:
        return bool(actor.call_method("HasMatchingGameplayTag", args=(t,)))
    except Exception:
        return None


def script():
    yield from fresh()
    p = P()
    p["stg"].force_break_for_test()
    yield from until(lambda: P()["stg"].get_clip_stage_name() == "down", 3.0)
    yield 0.3
    p = P()
    place(p)
    p["dbg"].debug_refill_player()
    maximum = max_attr(p["boss"], "Attribute.Health")
    if maximum is not None:
        set_attr(p["boss"], "Attribute.Health", maximum * LETHAL_HEALTH_FRACTION)
    yield 0.6
    p = P()
    impacts0 = p["stg"].get_riposte_impact_count()
    hp0 = attr(p["boss"], "Attribute.Health")
    press("IA_NormalAttack", 0.12)
    yield from until(lambda: P()["stg"].is_riposte_executing(), 1.0)
    # the impact lands 0.8 s after the start; then the pack's death runs and destroys the boss a few seconds later
    def dead_now():
        b = P()["boss"]
        if b is None:
            return True
        h = attr(b, "Attribute.Health")
        return h is not None and h <= 0.0

    died = yield from until(dead_now, 3.0)
    p = P()
    evidence = "boss gone" if p["boss"] is None else "health %s, dead tag %s, montage %s" % (attr(p["boss"], "Attribute.Health"), has_tag(p["boss"], "Status.Dead"), p["dbg"].debug_boss_montage_anim_name())
    check("L1 the riposte took the boss from %s health to zero (%s)" % (hp0, evidence), died, "")
    if p["boss"] is not None:
        yield 1.0
        p = P()
        dead_tag = has_tag(p["boss"], "Status.Dead") if p["boss"] is not None else True
        check("L1 the pack's death started: the Dead tag is on (or the boss is already destroyed): %s" % dead_tag, dead_tag is True or p["boss"] is None, "")
        check("L1 exactly one impact (%d) and the execution is over" % (p["stg"].get_riposte_impact_count() if p["boss"] is not None else -1), p["boss"] is None or (p["stg"].get_riposte_impact_count() == impacts0 + 1 and not p["stg"].is_riposte_executing()), "")
    else:
        check("L1 the boss is gone: destroyed by the pack's death flow after the lethal riposte", True, "")


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
    if s["now"] - s.get("hb", 0.0) > 15.0:
        s["hb"] = s["now"]
        log("heartbeat: %.0f s, pawn %s, boss %s, wait %.2f" % (s["now"], pawn.get_name() if pawn else None, boss.get_name() if boss else None, s["wait"]))
    if boss is None:
        s["gone"] = s.get("gone", 0.0) + dt
        if s["gone"] > 15.0 and s["gen"] is not None:
            finish()
        return
    s["gone"] = 0.0
    if pawn is None:
        return
    if s["now"] < s["press_until"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(IA + s["action"]), unreal.Vector(1, 0, 0))
    if s["samples"] is not None:
        sample()
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
