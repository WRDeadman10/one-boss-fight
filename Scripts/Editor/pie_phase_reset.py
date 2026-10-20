"""
Gate 2 checks on phase two and the reset (Freeze L01 to L04, L10, 18.1): runs on the awake, frozen boss.
 1. health 62 percent: no transition; 59 percent: one transition, buffs applied once (Attack attribute x1.25); lower health later: still one.
 2. the encounter reset twice in a row: generation +2, phase one again, Attack attribute restored, posture full, no duplicate components.
 3. phase two works again after the reset (second transition, buffs once).
 4. a stance break is running when health crosses 60 percent: no transition during the break, one transition after it ends.
Log prefix [PhaseReset]; results as PASS or FAIL lines and a summary.
"""
import unreal

log = lambda m: unreal.log("[PhaseReset] " + m)
state = {"phase": "start", "t": 0.0, "step": 0, "wait": 0.0, "res": [], "ctx": {}}
handle = None


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


def check(name, ok, detail=""):
    state["res"].append((name, ok))
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    bad = [n for n, ok in state["res"] if not ok]
    log("SUMMARY %d checks, %d failed %s" % (len(state["res"]), len(bad), bad))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wake", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is None or boss is None:
        return
    enc, ph, stg, dbg, tr, post = (comp(boss, n) for n in ("RPGBossEncounter", "RPGBossPhases", "RPGBossStagger", "RPGCombatDebug", "RPGAttackTracker", "RPGBossPosture"))
    mc = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0]
    c = s["ctx"]
    if s["phase"] == "wake":
        if s["t"] > 9.0 and "woke" not in s:
            s["woke"] = s["t"]
            pawn.set_actor_location_and_rotation(unreal.Vector(boss.get_actor_location().x + 700, boss.get_actor_location().y, boss.get_actor_location().z), unreal.Rotator(0, 180, 0), False, True)
        if "woke" in s:
            dbg.debug_refill_player()
            if (not enc.is_dormant()) and mc.get_anim_instance().get_current_active_montage() is None and s["t"] - s["woke"] > 4.0:
                enc.hold_for_test(True)
                pawn.set_actor_location_and_rotation(unreal.Vector(boss.get_actor_location().x + 2500, boss.get_actor_location().y, boss.get_actor_location().z), unreal.Rotator(0, 180, 0), False, True)
                s.update(phase="run", t=0.0, wait=1.0)
                c["attack0"] = attr(boss, "Attribute.Attack")
                c["comps0"] = sorted(x.get_class().get_name() for x in boss.get_components_by_class(unreal.ActorComponent))
                log("boss awake and held, Attack attribute %s, %d components" % (c["attack0"], len(c["comps0"])))
        return
    if s["t"] < s["wait"]:
        return
    n = s["step"]

    def nxt(wait):
        s["step"] += 1
        s["wait"] = s["t"] + wait

    A0 = c.get("attack0") or 0.0
    if n == 0:
        dbg.debug_set_boss_health_fraction(0.62)
        nxt(1.0)
    elif n == 1:
        check("L01a no transition at 62 percent", ph.get_phase_two_count() == 0 and not ph.is_phase_two())
        dbg.debug_set_boss_health_fraction(0.59)
        nxt(0.6)
    elif n == 2:
        check("L01b transition starts at 59 percent", ph.is_in_transition() and ph.get_phase_two_count() == 1, "count %d" % ph.get_phase_two_count())
        nxt(2.6)
    elif n == 3:
        a = attr(boss, "Attribute.Attack")
        check("L01c phase two after the roar", ph.is_phase_two() and not ph.is_in_transition())
        check("L04 buffs applied once (Attack x1.25)", abs(a - A0 * 1.25) < 0.6, "%s -> %s" % (A0, a))
        dbg.debug_set_boss_health_fraction(0.5)
        nxt(0.5)
    elif n == 4:
        dbg.debug_set_boss_health_fraction(0.3)
        nxt(0.5)
    elif n == 5:
        a = attr(boss, "Attribute.Attack")
        check("L02 phase two once under repeated health drops", ph.get_phase_two_count() == 1, "count %d" % ph.get_phase_two_count())
        check("L04b buffs not applied again", abs(a - A0 * 1.25) < 0.6, "%s" % a)
        c["g0"] = enc.get_generation()
        enc.reset_for_test()
        nxt(0.4)
    elif n == 6:
        enc.reset_for_test()
        nxt(1.5)
    elif n == 7:
        a = attr(boss, "Attribute.Attack")
        comps = sorted(x.get_class().get_name() for x in boss.get_components_by_class(unreal.ActorComponent))
        check("L10a generation +2 after two resets", enc.get_generation() == c["g0"] + 2, "%d -> %d" % (c["g0"], enc.get_generation()))
        check("L10b phase one again, buffs removed", (not ph.is_phase_two()) and abs(a - A0) < 0.6, "attack %s" % a)
        check("L10c posture full", post.get_posture() >= post.get_max_posture() - 0.5, "posture %.0f" % post.get_posture())
        check("L10d no duplicate components", comps == c["comps0"], "%d vs %d" % (len(comps), len(c["comps0"])))
        enc.wake()
        enc.hold_for_test(True)
        nxt(1.0)
    elif n == 8:
        dbg.debug_set_boss_health_fraction(0.58)
        nxt(0.6)
    elif n == 9:
        check("L01d second transition after the reset", ph.is_in_transition() and ph.get_phase_two_count() == 2, "count %d" % ph.get_phase_two_count())
        nxt(2.6)
    elif n == 10:
        a = attr(boss, "Attribute.Attack")
        check("L04c buffs once after the reset", ph.is_phase_two() and abs(a - A0 * 1.25) < 0.6, "attack %s" % a)
        enc.reset_for_test()
        nxt(1.0)
    elif n == 11:
        enc.wake()
        enc.hold_for_test(True)
        nxt(1.0)
    elif n == 12:
        stg.force_break_for_test()
        nxt(0.3)
    elif n == 13:
        dbg.debug_set_boss_health_fraction(0.55)
        nxt(1.2)
    elif n == 14:
        check("Queue: no transition during the stance break", stg.is_staggered() and not ph.is_in_transition() and ph.get_phase_two_count() == 2, "staggered %s count %d" % (stg.is_staggered(), ph.get_phase_two_count()))
        c["tq"] = s["t"]
        nxt(0.5)
    elif n == 15:
        if (not stg.is_staggered()) and s["t"] - c["tq"] > 0.3:
            nxt(0.8)
        elif s["t"] - c["tq"] > 14:
            check("Queue: break ended", False, "timeout")
            nxt(0.1)
        else:
            s["wait"] = s["t"] + 0.3
    elif n == 16:
        check("Queue: one transition after the break", ph.get_phase_two_count() == 3 and (ph.is_in_transition() or ph.is_phase_two()), "count %d" % ph.get_phase_two_count())
        finish()
        s["step"] = 99


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
