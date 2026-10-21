"""Gate 2 / G2-11: attack priority rules (Freeze 21, B06, B10). R1 no attack during a stance break, R2 none during the phase transition, R3 none while dormant, R4 a second non-chained attack that replaces a running one is
counted as a double launch, R5 a 40 s natural fight against a player that stays close: no double launch, no vetoed start, attacks are tracked, every attack ends before the next begins.
Run pie_debug_overlay.py once after an editor start first. Log prefix [Rules]."""
import math
import unreal

log = lambda m: unreal.log("[Rules] " + m)
results = []
S = {"phase": "start", "t": 0.0, "i": 0, "next": 0.0, "mem": {}, "fight": 0.0, "seen": [], "last_move": None}
handle = None


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def place(pawn, boss, dist, ang_deg=0):
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw + ang_deg)
    p = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(p, bl).yaw
    pawn.set_actor_location_and_rotation(p, unreal.Rotator(0, 0, look), False, True)


def parts(boss):
    return comp(boss, "RPGAttackTracker"), comp(boss, "RPGBossStagger"), comp(boss, "RPGBossPhases"), comp(boss, "RPGCombatDebug"), comp(boss, "RPGBossEncounter")


def s_wake(w, pc, pawn, boss):
    tr, st, ph, dbg, enc = parts(boss)
    enc.wake()
    enc.hold_for_test(True)
    dbg.debug_refill_player()


def s_arm(w, pc, pawn, boss):
    parts(boss)[0].enter_combat()


def snap(tr):
    return {"inst": tr.get_attack_instance(), "ill": tr.get_illegal_start_count(), "dbl": tr.get_double_launch_count()}


def s_r1(w, pc, pawn, boss):
    tr, st, ph, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 200)
    S["mem"] = snap(tr)
    st.force_break_for_test()


def s_r1_play(w, pc, pawn, boss):
    tr, st, ph, dbg, enc = parts(boss)
    check("R1 the boss is staggered", st.is_staggered())
    tr.play_move_montage_for_test("A1")


def s_r1_check(w, pc, pawn, boss):
    tr, st, ph, dbg, enc = parts(boss)
    m = S["mem"]
    check("R1 an attack during the stance break is vetoed", tr.get_illegal_start_count() == m["ill"] + 1 and tr.get_attack_instance() == m["inst"], "illegal %d -> %d, instances %d -> %d" % (m["ill"], tr.get_illegal_start_count(), m["inst"], tr.get_attack_instance()))


def s_r2_start(w, pc, pawn, boss):
    tr, st, ph, dbg, enc = parts(boss)
    st.abort_stagger()
    S["mem"] = snap(tr)
    dbg.debug_set_boss_health_fraction(0.55)


def s_r2_play(w, pc, pawn, boss):
    tr, st, ph, dbg, enc = parts(boss)
    check("R2 the phase transition is running", ph.is_in_transition())
    tr.play_move_montage_for_test("A1")


def s_r2_check(w, pc, pawn, boss):
    tr, st, ph, dbg, enc = parts(boss)
    m = S["mem"]
    check("R2 an attack during the phase transition is vetoed", tr.get_illegal_start_count() == m["ill"] + 1 and tr.get_attack_instance() == m["inst"], "illegal %d -> %d" % (m["ill"], tr.get_illegal_start_count()))


def s_r3_start(w, pc, pawn, boss):
    tr, st, ph, dbg, enc = parts(boss)
    enc.reset_for_test()
    S["mem"] = snap(tr)


def s_r3_play(w, pc, pawn, boss):
    tr, st, ph, dbg, enc = parts(boss)
    check("R3 the boss sleeps after the reset", enc.is_dormant())
    tr.play_move_montage_for_test("A1")


def s_r3_check(w, pc, pawn, boss):
    tr, st, ph, dbg, enc = parts(boss)
    m = S["mem"]
    check("R3 an attack while dormant is vetoed", tr.get_illegal_start_count() == m["ill"] + 1 and tr.get_attack_instance() == m["inst"], "illegal %d -> %d" % (m["ill"], tr.get_illegal_start_count()))
    dbg.debug_refill_player()
    enc.wake()
    enc.hold_for_test(True)


def s_r4_start(w, pc, pawn, boss):
    tr, st, ph, dbg, enc = parts(boss)
    tr.enter_combat()
    place(pawn, boss, 200)
    S["mem"] = snap(tr)
    check("R4 first attack starts", tr.play_move_montage_for_test("A1"))


def s_r4_second(w, pc, pawn, boss):
    tr = parts(boss)[0]
    check("R4 second attack starts while the first is in its windup", tr.play_move_montage_for_test("A3a"))


def s_r4_check(w, pc, pawn, boss):
    tr = parts(boss)[0]
    m = S["mem"]
    check("R4 the replacement is counted as a double launch", tr.get_double_launch_count() == m["dbl"] + 1, "double launches %d -> %d" % (m["dbl"], tr.get_double_launch_count()))


def s_r5_start(w, pc, pawn, boss):
    tr, st, ph, dbg, enc = parts(boss)
    mc = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0]
    inst = mc.get_anim_instance()
    if inst.get_current_active_montage():
        inst.montage_stop(0.05)
    dbg.debug_refill_player()
    S["mem"] = snap(tr)
    S["fight"] = 0.0
    enc.hold_for_test(False)


def s_r5_tick(dt, w, pawn, boss):
    # during the fight: keep the player close and healthy, log each move once
    tr, st, ph, dbg, enc = parts(boss)
    S["fight"] += dt
    S.setdefault("put", 0.0)
    S["put"] += dt
    if S["put"] > 0.4:
        S["put"] = 0.0
        dbg.debug_refill_player()
        bl, pl = boss.get_actor_location(), pawn.get_actor_location()
        if math.hypot(pl.x - bl.x, pl.y - bl.y) > 400:
            place(pawn, boss, 200)
    mv = str(tr.get_current_move())
    if mv != "None" and mv != S["last_move"]:
        S["seen"].append(mv)
    S["last_move"] = mv if mv != "None" else None


def s_r5_check(w, pc, pawn, boss):
    tr, st, ph, dbg, enc = parts(boss)
    m = S["mem"]
    n = tr.get_attack_instance() - m["inst"]
    log("INFO moves seen in the fight: %s" % S["seen"])
    check("R5 the boss attacked in the fight (%d tracked attacks)" % n, n >= 4)
    check("R5 no double launch in the natural fight", tr.get_double_launch_count() == m["dbl"], "%d -> %d" % (m["dbl"], tr.get_double_launch_count()))
    check("R5 no vetoed start in the natural fight", tr.get_illegal_start_count() == m["ill"], "%d -> %d" % (m["ill"], tr.get_illegal_start_count()))
    check("R5 every tracked attack committed once", tr.get_commit_count() >= n)


STEPS = [
    (9.0, s_wake), (3.0, s_arm),
    (0.3, s_r1), (0.3, s_r1_play), (0.5, s_r1_check),
    (3.0, s_r2_start), (0.4, s_r2_play), (0.5, s_r2_check),
    (3.0, s_r3_start), (0.5, s_r3_play), (0.8, s_r3_check),
    (3.0, s_r4_start), (0.04, s_r4_second), (1.5, s_r4_check),
    (1.0, s_r5_start), (40.0, s_r5_check),
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
    if pawn is None or boss is None:
        return
    if s["i"] > 0 and STEPS[s["i"] - 1][1] is s_r5_start:
        s_r5_tick(dt, w, pawn, boss)
    if s["t"] < s["next"]:
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
