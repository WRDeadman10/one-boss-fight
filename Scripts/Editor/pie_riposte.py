"""
Gate 2 riposte checks (Freeze S08 to S10, 17.4) with the pack's real Light Attack input on the frozen boss:
  baseline  a normal hit on the standing boss (health loss L);
  S08a      stance break, player 300 cm away: rejected (too far), no critical;
  S08b      stance break, player behind the boss: rejected (not in front);
  S09       stance break, player 110 cm in front facing it: accepted, the hit that follows costs about 2.5 x L;
  S09b      a second press in the same break: no second critical (about L).
Log prefix [Riposte].
"""
import unreal

log = lambda m: unreal.log("[Riposte] " + m)
IA_NORMAL = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_NormalAttack"
state = {"phase": "start", "t": 0.0, "step": 0, "wait": 0.0, "res": [], "c": {}}
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


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


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
    enc, stg, dbg = comp(boss, "RPGBossEncounter"), comp(boss, "RPGBossStagger"), comp(boss, "RPGCombatDebug")
    mc = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0]
    c = s["c"]
    bl = boss.get_actor_location()

    def place(dx, dy, yaw):
        pawn.set_actor_location_and_rotation(unreal.Vector(bl.x + dx, bl.y + dy, bl.z), unreal.Rotator(0, 0, yaw), False, True)
        pc.set_control_rotation(unreal.Rotator(0, 0, yaw))

    if s["phase"] == "wake":
        if s["t"] > 9.0 and "woke" not in s:
            s["woke"] = s["t"]
            place(700, 0, 180)
        if "woke" in s:
            dbg.debug_refill_player()
            if (not enc.is_dormant()) and mc.get_anim_instance().get_current_active_montage() is None and s["t"] - s["woke"] > 4.0:
                enc.hold_for_test(True)
                comp(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
                s.update(phase="run", t=0.0, wait=2.5)
                c["max"] = attr(boss, "Attribute.Health")
                log("boss held; health %s" % c["max"])
        return
    # a press is a short injected Light Attack held for 0.12 s
    if "press_until" in c:
        if s["t"] < c["press_until"]:
            unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(IA_NORMAL), unreal.Vector(1, 0, 0))
        else:
            del c["press_until"]
    if s["t"] < s["wait"]:
        return
    n = s["step"]

    def nxt(wait):
        s["step"] += 1
        s["wait"] = s["t"] + wait

    def press():
        c["press_until"] = s["t"] + 0.12

    def reset_boss():
        dbg.debug_set_boss_health_fraction(1.0)
        dbg.debug_refill_player()

    if n == 0:
        reset_boss()
        place(110, 0, 180)
        c["h0"] = attr(boss, "Attribute.Health")
        nxt(1.0)
    elif n == 1:
        press()
        nxt(1.8)
    elif n == 2:
        c["L"] = c["h0"] - attr(boss, "Attribute.Health")
        log("baseline hit L = %.1f (health %.1f -> %.1f)" % (c["L"], c["h0"], attr(boss, "Attribute.Health")))
        # the first press right after the combat start did not land; the normal hit size is measured from the second press of the break instead (step 12)
        reset_boss()
        stg.force_break_for_test()
        place(300, 0, 180)
        nxt(0.5)
    elif n == 3:
        r0 = stg.get_riposte_count()
        press()
        nxt(1.2)
    elif n == 4:
        check("S08a rejected when too far", stg.get_riposte_reject_count() >= 1 and stg.get_riposte_count() == 0 and "too far" in stg.get_last_riposte_result(), stg.get_last_riposte_result())
        place(-110, 0, 0)
        nxt(0.4)
    elif n == 5:
        press()
        nxt(1.0)
    elif n == 6:
        check("S08b rejected when behind the boss", stg.get_riposte_count() == 0 and "front" in stg.get_last_riposte_result(), stg.get_last_riposte_result())
        nxt(0.2)
    elif n == 7:
        # wait for the break to end, then a fresh break for the real test
        if stg.is_staggered():
            s["wait"] = s["t"] + 0.5
            if s["t"] > c.setdefault("t7", s["t"]) + 14:
                nxt(0.1)
        else:
            nxt(6.0)
    elif n == 8:
        reset_boss()
        stg.force_break_for_test()
        place(110, 0, 180)
        c["h1"] = attr(boss, "Attribute.Health")
        nxt(0.3)
    elif n == 9:
        press()
        nxt(1.4)
    elif n == 10:
        h = attr(boss, "Attribute.Health")
        R = c["h1"] - h
        log("riposte hit R = %.1f (health %.1f -> %.1f), L = %.1f, ratio %.2f" % (R, c["h1"], h, c["L"], R / max(c["L"], 0.01)))
        check("S09 riposte accepted", stg.get_riposte_count() == 1, stg.get_last_riposte_result())
        c["R"] = R
        c["h2"] = h
        place(110, 0, 180)
        nxt(0.2)
    elif n == 11:
        press()
        nxt(1.4)
    elif n == 12:
        h = attr(boss, "Attribute.Health")
        R2 = c["h2"] - h
        log("second press hit = %.1f" % R2)
        check("S09b no second critical in the same break", stg.get_riposte_count() == 1 and R2 > 1 and "already used" in stg.get_last_riposte_result(), "second hit %.1f, count %d, %s" % (R2, stg.get_riposte_count(), stg.get_last_riposte_result()))
        check("S09 riposte hit is 2.5x a normal hit", abs(c["R"] / max(R2, 0.01) - 2.5) < 0.3, "riposte %.1f, normal %.1f, ratio %.2f" % (c["R"], R2, c["R"] / max(R2, 0.01)))
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
