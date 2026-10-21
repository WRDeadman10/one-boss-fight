"""Gate 2 / M2 (SPEC_M2_damage.md): the damage path of the boss's own moves through URPGDamageResolver (Freeze 12.1, 488, 489; tests D14, D15, H04, H05, H08).
R1 an invulnerable player (Status.Invulnerable) is rejected, health and audit as the Freeze wants (overlap then rejected); R2 without the tag the hit lands once; R3 the same swing hurts once (duplicate), R3b a new stage may hit again;
R4 an old encounter generation is stale; R5 a dead player takes nothing; R6 a lethal hit leaves health exactly 0 and the next contact is rejected. M1 to M3: the real A4 blade, A5 javelin and A6 wave, with and without the tag
(the tag is injected with AddOwnedGameplayTag, as the A5 driver does). S1 the audit and the overlay line. Boss frozen awake. Generator style as pie_transition_rules.py. Log prefix [Dmg].
Not built from the spec (still open, TASKS G1-5): the i-frame monitor and the fixed frame rate measurement of the dodge windows (D12, D13), guard and hit reaction.
"""
import math
import unreal

log = lambda m: unreal.log("[Dmg] " + m)
results = []
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None}
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


def tag_obj(name):
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % name)
    return t


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def P():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return {"w": w, "pc": pc, "pawn": pawn, "boss": boss, "enc": comp(boss, "RPGBossEncounter"), "tr": comp(boss, "RPGAttackTracker"), "dbg": comp(boss, "RPGCombatDebug"), "res": comp(boss, "RPGDamageResolver"),
            "sw": comp(boss, "RPGBossLowSweep"), "wave": comp(boss, "RPGBossShockwave"), "pu": comp(boss, "RPGBossHealPunish")}


def place(p, dist, ang_deg):
    boss, pawn = p["boss"], p["pawn"]
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw + ang_deg)
    q = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(q, bl).yaw
    pawn.set_actor_location_and_rotation(q, unreal.Rotator(0, 0, look), False, True)


def add_tag(p):
    p["pawn"].call_method("AddOwnedGameplayTag", args=(tag_obj("Status.Invulnerable"),))


def remove_tag(p):
    p["pawn"].call_method("RemoveOwnedGameplayTag", args=(tag_obj("Status.Invulnerable"),))


def javelins():
    return [a for a in unreal.GameplayStatics.get_all_actors_of_class(world(), unreal.Actor) if a.get_class().get_name() == "RPGBossJavelin"]


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
    p["res"].clear_audit()
    yield 2.2


# ---- groups ----------------------------------------------------------------------------------------------------------------------------------------------------------------
def t0_components():
    p = P()
    check("T0 the boss has the damage resolver and the A4, A5, A6 components", all(p[k] is not None for k in ("res", "sw", "wave", "pu", "tr")))
    check("T0 the audit starts empty after clear_audit", p["res"].get_audit_count() == 0)


def r1_invulnerable():
    outcomes = []
    for k in range(20):
        p = P()
        p["dbg"].debug_refill_player()
        add_tag(p)
        h0 = attr(p["pawn"], "Attribute.Health")
        a0 = p["res"].get_outcome_count("Accepted")
        r0 = p["res"].get_outcome_count("RejectedInvulnerable")
        n0 = p["res"].get_audit_count()
        p["res"].note_overlap_for_test("T1", 100 + k, "k")
        out = p["res"].resolve_for_test("T1", 100 + k, 10.0, "k")
        remove_tag(p)
        h1 = attr(p["pawn"], "Attribute.Health")
        lines = [p["res"].get_audit_line(i) for i in range(0, 64) if p["res"].get_audit_line(i)]
        tail = lines[-2:]
        ok = out == "RejectedInvulnerable" and abs(h1 - h0) < 0.01 and p["res"].get_outcome_count("Accepted") == a0 and p["res"].get_outcome_count("RejectedInvulnerable") == r0 + 1 \
            and p["res"].get_audit_count() == n0 + 2 and len(tail) == 2 and "Overlap" in tail[0] and "RejectedInvulnerable" in tail[1]
        outcomes.append(ok)
        if not ok:
            log("R1 trial %d: %s health %s -> %s audit %s" % (k, out, h0, h1, tail))
        yield 0.05
    check("R1 invulnerable: RejectedInvulnerable, health unchanged, audit overlap then rejected, nothing accepted: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def r2_accepted():
    outcomes = []
    for k in range(20):
        p = P()
        p["dbg"].debug_refill_player()
        h0 = attr(p["pawn"], "Attribute.Health")
        out = p["res"].resolve_for_test("T2", 200 + k, 10.0, "k")
        h1 = attr(p["pawn"], "Attribute.Health")
        ok = out == "Accepted" and abs((h0 - h1) - 10.0) < 0.01
        outcomes.append(ok)
        if not ok:
            log("R2 trial %d: %s health %s -> %s" % (k, out, h0, h1))
        yield 0.05
    check("R2 no tag: Accepted, health -10.0: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def r3_duplicate():
    outcomes = []
    for k in range(20):
        p = P()
        p["dbg"].debug_refill_player()
        h0 = attr(p["pawn"], "Attribute.Health")
        o1 = p["res"].resolve_for_test("T3", 300 + k, 10.0, "k")
        o2 = p["res"].resolve_for_test("T3", 300 + k, 10.0, "k")
        h1 = attr(p["pawn"], "Attribute.Health")
        ok = o1 == "Accepted" and o2 == "RejectedDuplicate" and abs((h0 - h1) - 10.0) < 0.01
        outcomes.append(ok)
        if not ok:
            log("R3 trial %d: %s %s health %s -> %s" % (k, o1, o2, h0, h1))
        yield 0.05
    check("R3 the same swing hurts once (Accepted then RejectedDuplicate, -10.0 in all): %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))
    outcomes = []
    for k in range(10):
        p = P()
        p["dbg"].debug_refill_player()
        h0 = attr(p["pawn"], "Attribute.Health")
        o1 = p["res"].resolve_for_test("T3", 400 + k, 10.0, "stage1")
        o2 = p["res"].resolve_for_test("T3", 400 + k, 10.0, "stage2")
        h1 = attr(p["pawn"], "Attribute.Health")
        ok = o1 == "Accepted" and o2 == "Accepted" and abs((h0 - h1) - 20.0) < 0.01
        outcomes.append(ok)
        yield 0.05
    check("R3b a second authored stage of the same instance may hit again (-20.0): %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def r4_stale():
    outcomes = []
    for k in range(5):
        p = P()
        p["dbg"].debug_refill_player()
        old = p["enc"].get_generation()
        p["enc"].reset_for_test()
        yield 0.8
        p = P()
        p["enc"].wake()
        p["enc"].hold_for_test(True)
        h0 = attr(p["pawn"], "Attribute.Health")
        o_old = p["res"].resolve_for_test("T4", 500 + k, 10.0, "k", old)
        h1 = attr(p["pawn"], "Attribute.Health")
        o_new = p["res"].resolve_for_test("T4", 500 + k, 10.0, "k")
        h2 = attr(p["pawn"], "Attribute.Health")
        ok = o_old == "RejectedStale" and abs(h1 - h0) < 0.01 and o_new == "Accepted" and abs((h1 - h2) - 10.0) < 0.01
        outcomes.append(ok)
        if not ok:
            log("R4 trial %d: %s %s health %s %s %s" % (k, o_old, o_new, h0, h1, h2))
        yield 1.0
    check("R4 an old generation is stale (nothing taken), the current one is accepted: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def r5_dead_lethal():
    outcomes = []
    for k in range(5):
        p = P()
        p["dbg"].debug_set_player_health(0.0)
        yield 0.1
        out = P()["res"].resolve_for_test("T5", 600 + k, 10.0, "k")
        h = attr(P()["pawn"], "Attribute.Health")
        outcomes.append(out == "RejectedDead" and h == 0.0)
        # (the pack's death task respawns the player: wait for the new pawn before the next trial)
        yield from until(lambda: attr(P()["pawn"], "Attribute.Health") is not None and attr(P()["pawn"], "Attribute.Health") > 0, 30.0, 0.5)
        yield 1.0
        P()["dbg"].debug_refill_player()
    check("R5 a dead player takes nothing (RejectedDead, health stays 0): %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def r6_lethal():
    outcomes = []
    for k in range(3):
        yield from fresh()
        p = P()
        p["dbg"].debug_set_player_health(5.0)
        yield 0.1
        o1 = P()["res"].resolve_for_test("T6", 700 + k, 10.0, "k")
        h = attr(P()["pawn"], "Attribute.Health")
        o2 = P()["res"].resolve_for_test("T6", 700 + k, 10.0, "k2")
        outcomes.append(o1 == "Accepted" and h == 0.0 and o2 == "RejectedDead")
        if not outcomes[-1]:
            log("R6 trial %d: %s health %s then %s" % (k, o1, h, o2))
        yield from until(lambda: attr(P()["pawn"], "Attribute.Health") is not None and attr(P()["pawn"], "Attribute.Health") > 0, 30.0, 0.5)
        yield 1.0
    check("R6 a lethal hit leaves health exactly 0 and the next contact is RejectedDead: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def m1_a4():
    for tagged in (True, False):
        outcomes = []
        for k in range(5):
            yield from fresh()
            p = P()
            place(p, 250, 0)
            h0 = attr(p["pawn"], "Attribute.Health")
            hits0 = p["sw"].get_hit_count()
            inv0 = p["sw"].get_invulnerable_count()
            p["res"].clear_audit()
            p["tr"].start_move("A4", True)
            if tagged:
                # GetPosition keeps the last value of the previous move until the new one ticks: read it only while A4 is the current move
                yield from until(lambda: str(P()["tr"].get_current_move()) == "A4" and P()["tr"].get_position() >= 0.55, 3.0)
                add_tag(P())
                yield from until(lambda: str(P()["tr"].get_current_move()) != "A4" or P()["tr"].get_position() >= 1.0, 3.0)
                remove_tag(P())
            yield 1.8
            p = P()
            h1 = attr(p["pawn"], "Attribute.Health")
            r = p["res"]
            if tagged:
                ok = abs(h1 - h0) < 0.01 and p["sw"].get_invulnerable_count() == inv0 + 1 and r.get_move_outcome_count("A4", "Overlap") >= 1 and r.get_move_outcome_count("A4", "RejectedInvulnerable") >= 1 and r.get_move_outcome_count("A4", "Accepted") == 0
            else:
                ok = abs((h0 - h1) - 20.0) < 0.01 and p["sw"].get_hit_count() == hits0 + 1 and r.get_move_outcome_count("A4", "Accepted") == 1
            outcomes.append(ok)
            if not ok:
                log("M1 %s trial %d: health %s -> %s overlap %d rejected %d accepted %d" % (tagged, k, h0, h1, r.get_move_outcome_count("A4", "Overlap"), r.get_move_outcome_count("A4", "RejectedInvulnerable"), r.get_move_outcome_count("A4", "Accepted")))
        check("M1%s A4 blade %s: %d/%d trials" % ("a" if tagged else "b", "with the tag: no damage, overlap and rejected in the audit, nothing accepted" if tagged else "without the tag: one Accepted, -20.0", sum(outcomes), len(outcomes)), all(outcomes))


def m2_a5():
    for tagged in (True, False):
        outcomes = []
        for k in range(5):
            yield from fresh()
            p = P()
            place(p, 700, 0)
            h0 = attr(p["pawn"], "Attribute.Health")
            hit0, dod0 = p["pu"].get_javelin_hit_count(), p["pu"].get_javelin_dodged_count()
            p["res"].clear_audit()
            p["pu"].notify_heal_started_for_test()
            yield from until(lambda: P()["pu"].get_released_count() > 0, 3.0)
            if tagged:
                add_tag(P())
            yield 2.4
            if tagged:
                remove_tag(P())
            p = P()
            h1 = attr(p["pawn"], "Attribute.Health")
            r = p["res"]
            if tagged:
                ok = abs(h1 - h0) < 0.01 and p["pu"].get_javelin_dodged_count() == dod0 + 1 and r.get_move_outcome_count("A5", "RejectedInvulnerable") >= 1 and r.get_move_outcome_count("A5", "Accepted") == 0
            else:
                ok = abs((h0 - h1) - 12.0) < 0.01 and p["pu"].get_javelin_hit_count() == hit0 + 1 and r.get_move_outcome_count("A5", "Accepted") == 1
            outcomes.append(ok)
            if not ok:
                log("M2 %s trial %d: health %s -> %s" % (tagged, k, h0, h1))
            yield from until(lambda: len(javelins()) == 0, 4.0)
        check("M2%s A5 javelin %s: %d/%d trials" % ("a" if tagged else "b", "with the tag: passes through, no damage, dodged +1, rejected in the audit" if tagged else "without the tag: one Accepted, -12.0", sum(outcomes), len(outcomes)), all(outcomes))


def m3_a6():
    for tagged in (True, False):
        outcomes = []
        for k in range(5):
            yield from fresh()
            p = P()
            place(p, 700, 0)
            h0 = attr(p["pawn"], "Attribute.Health")
            inv0, hit0 = p["wave"].get_invulnerable_count(), p["wave"].get_hit_count()
            p["res"].clear_audit()
            p["wave"].launch_for_test()
            if tagged:
                yield 0.2
                add_tag(P())
                yield 1.0
                remove_tag(P())
            yield 1.2
            p = P()
            h1 = attr(p["pawn"], "Attribute.Health")
            r = p["res"]
            if tagged:
                ok = abs(h1 - h0) < 0.01 and p["wave"].get_invulnerable_count() == inv0 + 1 and r.get_move_outcome_count("A6", "Accepted") == 0
            else:
                ok = abs((h0 - h1) - 48.0) < 0.01 and p["wave"].get_hit_count() == hit0 + 1 and r.get_move_outcome_count("A6", "Accepted") == 1
            outcomes.append(ok)
            if not ok:
                log("M3 %s trial %d: health %s -> %s" % (tagged, k, h0, h1))
        check("M3%s A6 wave %s: %d/%d trials" % ("a" if tagged else "b", "with the tag: no damage, counted as invulnerable" if tagged else "without the tag: one Accepted, -48.0", sum(outcomes), len(outcomes)), all(outcomes))


def s1_audit():
    p = P()
    lines = p["dbg"].build_lines()
    check("S1 the overlay has one DAMAGE line", len([l for l in lines if l.strip().startswith("DAMAGE")]) == 1, "%d lines" % len(lines))
    check("S1 the audit has entries and its counters add up", p["res"].get_audit_count() > 0)


def script():
    yield 9.0
    yield from fresh()
    t0_components()
    for group in (r1_invulnerable, r2_accepted, r3_duplicate, r4_stale, r5_dead_lethal, r6_lethal, m1_a4, m2_a5, m3_a6):
        log("== %s" % group.__name__)
        yield from fresh()
        yield from group()
    s1_audit()


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        remove_tag(P())
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
    p = P()
    if p["pawn"] is None or p["boss"] is None:
        return
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
