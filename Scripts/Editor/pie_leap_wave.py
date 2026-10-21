"""Gate 2 / G2-4: the A6 leap. W1 leap blocked in phase one, W2 wave hits a grounded player, W3 a jump clears it, W4 central hit priority, W5 reset mid wave stops it, W6 leap unlocked after phase two,
W7 real leap (pack ability) tracked as A6 with one wave per instance. Run pie_debug_overlay.py once after an editor start first. Log prefix [Leap]."""
import math
import unreal

log = lambda m: unreal.log("[Leap] " + m)
results = []
S = {"phase": "start", "t": 0.0, "i": 0, "next": 0.0, "mem": {}}
handle = None


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def health(actor):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="Attribute.Health")')
    try:
        return c.call_method("Get Current Attribute Value", args=(t,))
    except Exception:
        return None


def place(pawn, boss, dist, ang_deg, keep_z=False):
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw + ang_deg)
    p = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, pawn.get_actor_location().z if keep_z else bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(p, bl).yaw
    pawn.set_actor_location_and_rotation(p, unreal.Rotator(0, 0, look), False, True)


def parts(boss):
    return comp(boss, "RPGBossShockwave"), comp(boss, "RPGAttackTracker"), comp(boss, "RPGBossPhases"), comp(boss, "RPGCombatDebug"), comp(boss, "RPGBossEncounter")


def s_wake(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    enc.wake()
    enc.hold_for_test(True)
    dbg.debug_refill_player()


def s_w1(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    check("W1 leap blocked in phase one", ph.is_leap_blocked())
    tr.enter_combat()
    S["mem"] = {"inst": tr.get_attack_instance()}
    check("W1 the pack ability refuses the leap while blocked", not tr.start_move("A6", False))


def s_w2_start(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 700, 0)
    S["mem"] = {"hp": health(pawn), "n": wave.get_hit_count(), "launch": wave.get_launch_count()}
    wave.launch_for_test()


def s_w2_check(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    hp1 = health(pawn)
    check("W2 wave launched", wave.get_launch_count() == S["mem"]["launch"] + 1)
    check("W2 wave hits a grounded player", wave.get_hit_count() == S["mem"]["n"] + 1 and hp1 is not None and hp1 < S["mem"]["hp"], "health %s -> %s" % (S["mem"]["hp"], hp1))
    check("W2 one damage event", hp1 is not None and S["mem"]["hp"] - hp1 <= wave.get_editor_property("damage") + 0.01, "taken %s" % (S["mem"]["hp"] - hp1 if hp1 is not None else None))
    check("W2 wave ended at max radius", not wave.is_wave_active())


def s_w3_start(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 700, 0, keep_z=True)
    S["mem"] = {"hp": health(pawn), "j": wave.get_jumped_count(), "n": wave.get_hit_count()}
    wave.launch_for_test()


def s_w3_jump(w, pc, pawn, boss):
    unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_FaceButton_Bottom", True)
    S["mem"]["down"] = True
    S["mem"]["zs"] = []


def s_w3_release(w, pc, pawn, boss):
    unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_FaceButton_Bottom", False)
    log("jump released, player z %.0f" % pawn.get_actor_location().z)


def s_w3_check(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    log("W3 player z samples (t since last step, z): %s" % S["mem"].get("zs"))
    S["mem"]["done_zs"] = True
    hp1 = health(pawn)
    check("W3 a jump clears the wave", wave.get_jumped_count() == S["mem"]["j"] + 1 and wave.get_hit_count() == S["mem"]["n"] and hp1 == S["mem"]["hp"], "jumped %d hit %d health %s -> %s" % (wave.get_jumped_count(), wave.get_hit_count(), S["mem"]["hp"], hp1))


def s_w4_start(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 700, 0)
    S["mem"] = {"cp": wave.get_central_priority_count(), "n": wave.get_hit_count()}
    wave.launch_for_test()
    dbg.debug_set_player_health(100.0)


def s_w4_check(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    hp1 = health(pawn)
    check("W4 the wave yields to the central hit", wave.get_central_priority_count() == S["mem"]["cp"] + 1 and wave.get_hit_count() == S["mem"]["n"] and hp1 == 100.0, "health %s" % hp1)


def s_w5_start(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    place(pawn, boss, 1000, 0)
    wave.launch_for_test()


def s_w5_reset(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    check("W5 wave is running", wave.is_wave_active())
    enc.reset_for_test()


def s_w5_check(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    check("W5 a reset stops the wave", not wave.is_wave_active())
    check("W5 leap still blocked after the reset (phase one)", ph.is_leap_blocked())
    dbg.debug_refill_player()
    enc.wake()
    enc.hold_for_test(True)


def s_w6_phase(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    dbg.debug_set_boss_health_fraction(0.5)


def s_w6_check(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    check("W6 phase two reached", ph.is_phase_two() and not ph.is_in_transition())
    check("W6 leap unlocked after the transition", not ph.is_leap_blocked())
    enc.hold_for_test(True)
    tr.enter_combat()


def s_w7_start(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 600, 0)
    S["mem"] = {"inst": tr.get_attack_instance(), "commit": tr.get_commit_count(), "launch": wave.get_launch_count(), "yaw": boss.get_actor_rotation().yaw, "hp": health(pawn)}
    check("W7 leap ability starts", tr.start_move("A6"))


def s_w7_check(w, pc, pawn, boss):
    wave, tr, ph, dbg, enc = parts(boss)
    m = S["mem"]
    check("W7 tracked once as A6", tr.get_attack_instance() == m["inst"] + 1 and tr.get_commit_count() == m["commit"] + 1, "instances %d -> %d" % (m["inst"], tr.get_attack_instance()))
    check("W7 commit near 0.16 s and window near 0.75 s", 0.05 <= tr.get_last_commit_position() <= 0.4 and 0.6 <= tr.get_last_active_start_position() <= 0.95, "commit %.2f active %.2f" % (tr.get_last_commit_position(), tr.get_last_active_start_position()))
    check("W7 one wave for the leap", wave.get_launch_count() == m["launch"] + 1, "launches %d -> %d" % (m["launch"], wave.get_launch_count()))
    bl = boss.get_actor_location()
    log("INFO leap landing at %.0f, %.0f (boss yaw %.0f -> %.0f); player health %s -> %s" % (bl.x, bl.y, m["yaw"], boss.get_actor_rotation().yaw, m["hp"], health(pawn)))


STEPS = [
    (9.0, s_wake), (2.0, s_w1),
    (0.5, s_w2_start), (1.4, s_w2_check),
    (0.5, s_w3_start), (0.02, s_w3_jump), (0.1, s_w3_release), (1.2, s_w3_check),
    (0.5, s_w4_start), (1.4, s_w4_check),
    (0.5, s_w5_start), (0.3, s_w5_reset), (1.2, s_w5_check),
    (0.5, s_w6_phase), (5.0, s_w6_check),
    (1.0, s_w7_start), (3.5, s_w7_check),
]


def _tick(dt):
    global handle
    s = S
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0, next=STEPS[0][0])
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is not None and "zs" in s["mem"] and not s["mem"].get("done_zs"):
        s["mem"]["zs"].append((round(s["t"], 2), round(pawn.get_actor_location().z)))
    if pawn is None or boss is None or s["t"] < s["next"]:
        return
    if s["i"] >= len(STEPS):
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("RESULT %d/%d passed" % (sum(1 for r in results if r), len(results)))
        return
    _, fn = STEPS[s["i"]]
    try:
        fn(w, pc, pawn, boss)
    except Exception:
        import traceback
        check("step %d (%s) raised" % (s["i"], fn.__name__), False, traceback.format_exc())
    s["i"] += 1
    s["t"] = 0.0
    s["next"] = STEPS[s["i"]][0] if s["i"] < len(STEPS) else 0.5


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
