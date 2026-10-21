"""Gate 2 / M3 (SPEC_M3_legend.md section 6): the legend pass on the boss fight (log prefix [Legend]). Camera shake on the A2 and A6 slam and on the phase two roar, hit stop on the riposte hit, slow motion on the kill, and the music state machine.
L0 the gate off (rpg.Legend 0): nothing starts. L1 real A2 slam: exactly one shake per swing, distance scaling, too far, interrupted before the active window; L2 the roar once per fight; L3 A6 in phase two; L4 the riposte hit stop (and a second
press in the same break does not stop again); L5 no stacking; L6 a reset restores time; L7 the kill slow motion. M1 to M7 the music: start once, swap once at phase two, none after a reset or a kill, no double start, no swap with the gate off.
Camera: every tick the camera manager's location and rotation are sampled with a real clock; a shake is proven by the peak to peak of Z and pitch inside its window against a baseline window (the oscillator starts at a random offset, so only the peak to peak means anything).
Time: every duration is measured with the REAL clock (time.perf_counter), waits for effects are real waits (the world clock is the thing being dilated). The gate is switched on here and ALWAYS switched off again (finish and error path): rpg.Legend 0 is the state the older drivers expect.
Saved/legend_groups.txt (names separated by spaces: l0 l1 l2 l3 l4 l5 l6 m l7) selects groups for a rerun; l7 kills the boss and must be last. Run Scripts/Editor/legend_off.py and a warm-up PIE first. The editor should run with -nosound: the music tests prove the state, never audibility."""
import math
import os
import time
import unreal

log = lambda m: unreal.log("[Legend] " + m)
results = []
S = {"phase": "start", "t": 0.0, "wake_at": 0.0, "gen": None, "cam": [], "dil": [], "press_until": 0.0}
handle = None
IA_NORMAL = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_NormalAttack"


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


def console(cmd):
    unreal.SystemLibrary.execute_console_command(world(), cmd)


def P():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return {"w": w, "pc": pc, "pawn": pawn, "boss": boss, "enc": comp(boss, "RPGBossEncounter") if boss else None, "tr": comp(boss, "RPGAttackTracker") if boss else None, "dbg": comp(boss, "RPGCombatDebug") if boss else None,
            "stg": comp(boss, "RPGBossStagger") if boss else None, "ph": comp(boss, "RPGBossPhases") if boss else None, "leg": comp(boss, "RPGBossLegend") if boss else None, "mus": comp(boss, "RPGBossMusic") if boss else None,
            "hud": comp(boss, "RPGBossHud") if boss else None}


def place(p, dist, ang_deg):
    boss, pawn = p["boss"], p["pawn"]
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw + ang_deg)
    q = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(q, bl).yaw
    pawn.set_actor_location_and_rotation(q, unreal.Rotator(0, 0, look), False, True)
    p["pc"].set_control_rotation(unreal.Rotator(0, 0, look))


def gdil():
    return unreal.GameplayStatics.get_global_time_dilation(world())


def cdil(actor):
    try:
        return float(actor.get_editor_property("custom_time_dilation"))
    except Exception:
        return -1.0


def rwait(seconds):
    """Wait in REAL seconds (the world clock is what the effects dilate)."""
    t_end = time.perf_counter() + seconds
    while time.perf_counter() < t_end:
        yield 0.0


def until(cond, timeout):
    t_end = time.perf_counter() + timeout
    while not cond():
        if time.perf_counter() > t_end:
            return False
        yield 0.0
    return True


def press():
    S["press_until"] = time.perf_counter() + 0.12


def fresh():
    p = P()
    p["enc"].reset_for_test()
    yield from rwait(1.0)
    p = P()
    p["enc"].wake()
    p["enc"].hold_for_test(True)
    p["dbg"].debug_refill_player()
    yield from rwait(2.2)


def p2p(t0, t1, col):
    vals = [r[col] for r in S["cam"] if t0 <= r[0] <= t1]
    return (max(vals) - min(vals)) if len(vals) >= 3 else None


def dil_span(t0, t1, col):
    """(first time below 0.5, first time back at 0.99 or more, minimum) of one dilation column inside a real time window."""
    start = end = None
    low = 9.0
    for r in S["dil"]:
        if r[0] < t0 or r[0] > t1:
            continue
        v = r[col]
        low = min(low, v)
        if start is None and v < 0.5:
            start = r[0]
        elif start is not None and end is None and v >= 0.99:
            end = r[0]
    return start, end, low


def hf(t0, t1, col):
    """High-pass measure of the camera samples in a real time window: the largest distance of a sample from the straight line between its neighbours (time weighted). A slow drift (the camera
    settling after the player was placed, or following the boss) gives about 0; an oscillation of amplitude A gives A times a factor between about 0.9 and 2 whatever the frame rate. None without enough samples."""
    pts = [r for r in S["cam"] if t0 <= r[0] <= t1]
    if len(pts) < 5:
        return None
    best = 0.0
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        if c[0] <= a[0]:
            continue
        w = (b[0] - a[0]) / (c[0] - a[0])
        best = max(best, abs(b[col] - (a[col] + (c[col] - a[col]) * w)))
    return best


def shake_window(t_fire, seconds, amp_z, amp_pitch, scale, label, factor=0.25):
    """The pass rule: inside the shake window the high-pass measure of Z reaches a quarter of amplitude times scale and of pitch likewise (the roar's 2 cm at 24 Hz is sampled at the editor's frame rate and aliases: it asks 0.12); before the shake and after it (1.0 s after its end) the camera is quiet (high-pass Z <= 0.2 cm, pitch <= 0.05 degrees)."""
    z = hf(t_fire, t_fire + seconds, 1)
    pitch = hf(t_fire, t_fire + seconds, 2)
    base_z, base_p = hf(t_fire - 1.6, t_fire - 0.3, 1), hf(t_fire - 1.6, t_fire - 0.3, 2)
    rec_z, rec_p = hf(t_fire + seconds + 1.0, t_fire + seconds + 2.0, 1), hf(t_fire + seconds + 1.0, t_fire + seconds + 2.0, 2)
    quiet = lambda v, limit: v is None or v <= limit
    ok = z is not None and z >= amp_z * scale * factor and pitch is not None and pitch >= amp_pitch * scale * factor and quiet(base_z, 0.2) and quiet(base_p, 0.05) and quiet(rec_z, 0.2) and quiet(rec_p, 0.05)
    f = lambda v: "%.3f" % v if v is not None else None
    detail = "%s: high-pass Z %s pitch %s (needs Z >= %.2f, pitch >= %.2f), quiet before Z %s pitch %s, quiet after Z %s pitch %s" % (label, f(z), f(pitch), amp_z * scale * factor, amp_pitch * scale * factor, f(base_z), f(base_p), f(rec_z), f(rec_p))
    return ok, detail


def shake_scale(distance, inner, outer, falloff):
    if outer <= inner:
        return 1.0 if distance <= inner else 0.0
    t = max(0.0, min(1.0, (distance - inner) / (outer - inner)))
    return (1.0 - t) ** falloff


# ---- groups -----------------------------------------------------------------------------------------------------------------------------------------------------------------
def l0_gate_off():
    console("rpg.Legend 0")
    yield from fresh()
    p = P()
    leg, mus = p["leg"], p["mus"]
    check("T0 the boss has the legend and music components and the subsystem answers", leg is not None and mus is not None)
    s0 = (leg.get_slam_shake_count(), leg.get_roar_shake_count(), leg.get_hit_stop_count(), leg.get_slow_motion_count())
    sup0 = leg.get_suppressed_count()
    t0 = time.perf_counter()
    r = (leg.fire_slam_for_test("A2"), leg.fire_roar_for_test(), leg.fire_hit_stop_for_test(False), leg.fire_slow_motion_for_test())
    yield from rwait(1.0)
    p = P()
    leg = p["leg"]
    s1 = (leg.get_slam_shake_count(), leg.get_roar_shake_count(), leg.get_hit_stop_count(), leg.get_slow_motion_count())
    z = p2p(t0, t0 + 1.0, 1)
    check("L0 gate off: nothing starts (4 hooks refused, counters unchanged, suppressed +4), time and camera untouched", r == (False, False, False, False) and s1 == s0 and leg.get_suppressed_count() - sup0 >= 4
          and abs(gdil() - 1.0) < 1e-4 and abs(cdil(p["boss"]) - 1.0) < 1e-4 and abs(cdil(p["pawn"]) - 1.0) < 1e-4 and (z is None or z <= 0.2),
          "hooks %s counters %s -> %s suppressed +%d camera Z %s global %.4f" % (r, s0, s1, leg.get_suppressed_count() - sup0, "%.2f" % z if z is not None else None, gdil()))
    check("L0 gate off: the music still follows the encounter (a woken boss plays Phase 1)", p["mus"].get_active_track_name() == "Phase1", p["mus"].get_active_track_name())
    console("rpg.Legend 1")


def l1_slam():
    console("rpg.Legend 1")
    ok_all, scales, ratios = [], [], []
    shakes = {}
    for dist, label, trials in ((600, "600 cm", 5), (1500, "1500 cm", 2)):
        outcomes, zs = [], []
        for i in range(trials):
            yield from fresh()
            p = P()
            leg = p["leg"]
            place(p, dist, 0)
            yield from rwait(0.6)
            c0 = leg.get_slam_shake_count()
            p["tr"].start_move("A2", True)
            fired = yield from until(lambda: P()["leg"].get_slam_shake_count() > c0, 5.0)
            t_fire = time.perf_counter()
            yield from rwait(0.9)
            leg = P()["leg"]
            yield from until(lambda: str(P()["tr"].get_current_move()) == "None", 5.0)
            yield from rwait(0.3)
            leg = P()["leg"]
            delta = leg.get_slam_shake_count() - c0
            scale, distance = leg.get_last_shake_scale(), leg.get_last_shake_distance()
            want = shake_scale(distance, 500.0, 2500.0, 1.5)
            ok_shake, detail = shake_window(t_fire, 0.6, 5.0, 1.4, scale, "A2 at %s trial %d" % (label, i))
            z = hf(t_fire, t_fire + 0.6, 1)
            zs.append(z or 0.0)
            ok = fired and delta == 1 and abs(scale - want) <= 0.02 and ok_shake
            outcomes.append(ok)
            if not ok:
                log("L1 %s trial %d: fired %s delta %d scale %.3f (formula %.3f at %.0f cm) %s" % (label, i, fired, delta, scale, want, distance, detail))
            scales.append((label, round(scale, 3), round(distance)))
        shakes[label] = sum(zs) / max(len(zs), 1)
        check("L1 real A2 slam with the player %s away: exactly one shake per swing, scale equals the formula, the camera moves (peak to peak) and rests: %d/%d trials" % (label, sum(outcomes), len(outcomes)), all(outcomes))
    ratio = shakes["1500 cm"] / max(shakes["600 cm"], 0.001)
    check("L1d the shake at 1500 cm is weaker than at 600 cm (high-pass Z ratio 0.1 to 0.6)", 0.1 <= ratio <= 0.6, "scales %s, mean high-pass Z 600 cm %.2f 1500 cm %.2f ratio %.2f" % (scales[:1] + scales[5:6], shakes["600 cm"], shakes["1500 cm"], ratio))

    # interrupted before the active window: no shake
    outcomes = []
    for i in range(3):
        yield from fresh()
        p = P()
        place(p, 600, 0)
        yield from rwait(0.6)
        c0 = p["leg"].get_slam_shake_count()
        p["tr"].start_move("A2", True)
        yield from rwait(0.8)
        P()["stg"].force_break_for_test()
        yield from rwait(3.0)
        outcomes.append(P()["leg"].get_slam_shake_count() == c0)
    check("L1b A2 interrupted by a stance break before its active window: no shake: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))

    # too far
    outcomes = []
    for i in range(2):
        yield from fresh()
        p = P()
        place(p, 2800, 0)
        yield from rwait(0.6)
        leg = p["leg"]
        c0, far0 = leg.get_slam_shake_count(), leg.get_shake_too_far_count()
        p["tr"].start_move("A2", True)
        yield from rwait(3.2)
        leg = P()["leg"]
        outcomes.append(leg.get_slam_shake_count() == c0 and leg.get_shake_too_far_count() == far0 + 1)
    check("L1c the player 2800 cm away (beyond the outer radius): the slam is counted as too far, no shake: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def l2_roar():
    console("rpg.Legend 1")
    outcomes = []
    for fight in range(2):
        yield from fresh()
        p = P()
        place(p, 700, 0)
        yield from rwait(2.4)  # the camera needs about 2 s to settle after the player was placed: the quiet window before the roar must not contain the jump
        p = P()
        leg = p["leg"]
        r0, count0 = leg.get_roar_shake_count(), p["ph"].get_phase_two_count()
        p["dbg"].debug_set_boss_health_fraction(0.5)
        fired = yield from until(lambda: P()["leg"].get_roar_shake_count() > r0, 3.0)
        t_fire = time.perf_counter()
        yield from rwait(3.4)
        p = P()
        delta = p["leg"].get_roar_shake_count() - r0
        ok_shake, detail = shake_window(t_fire, 1.5, 2.0, 0.7, p["leg"].get_last_shake_scale(), "roar fight %d" % fight, 0.12)
        p["dbg"].debug_set_boss_health_fraction(0.4)  # the same fight: no second roar
        yield from rwait(2.5)
        p = P()
        delta2 = p["leg"].get_roar_shake_count() - r0
        ok = fired and delta == 1 and delta2 == 1 and p["ph"].get_phase_two_count() == count0 + 1 and ok_shake
        outcomes.append(ok)
        if not ok:
            log("L2 fight %d: fired %s delta %d then %d, phase two count %d (from %d) %s" % (fight, fired, delta, delta2, p["ph"].get_phase_two_count(), count0, detail))
    check("L2 the roar shakes once per fight (never twice), the camera moves and rests: %d/%d fights" % (sum(outcomes), len(outcomes)), all(outcomes))


def l3_leap():
    console("rpg.Legend 1")
    outcomes = []
    for i in range(3):
        yield from fresh()
        p = P()
        place(p, 600, 0)
        yield from rwait(0.6)
        p["dbg"].debug_set_boss_health_fraction(0.5)  # phase two: the leap is a phase two move
        yield from until(lambda: not P()["ph"].is_in_transition() and P()["ph"].is_phase_two(), 6.0)
        yield from rwait(2.5)
        p = P()
        leg = p["leg"]
        c0 = leg.get_slam_shake_count()
        p["tr"].start_move("A6", True)
        fired = yield from until(lambda: P()["leg"].get_slam_shake_count() > c0, 4.0)
        yield from until(lambda: str(P()["tr"].get_current_move()) == "None", 5.0)
        yield from rwait(0.4)
        delta = P()["leg"].get_slam_shake_count() - c0
        outcomes.append(fired and delta == 1)
        if not outcomes[-1]:
            log("L3 trial %d: fired %s delta %d" % (i, fired, delta))
    check("L3 A6 leap landing in phase two: exactly one slam shake per leap: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def hit_riposte(p):
    """Stance break, the player 110 cm in front facing the boss, one injected Light Attack press (as pie_riposte.py)."""
    p["stg"].force_break_for_test()
    place(p, 110, 0)


def l4_hit_stop():
    console("rpg.Legend 1")
    outcomes, spans = [], []
    for i in range(3):
        yield from fresh()
        p = P()
        comp(p["pawn"], "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))  # the weapon must be drawn for the press to attack
        yield from rwait(2.2)
        p = P()
        leg = p["leg"]
        h0, rip0 = leg.get_hit_stop_count(), p["stg"].get_riposte_count()
        base_boss, base_pawn = cdil(p["boss"]), cdil(p["pawn"])
        hit_riposte(p)
        yield from rwait(0.4)
        t_press = time.perf_counter()
        press()
        fired = yield from until(lambda: P()["leg"].get_hit_stop_count() > h0, 3.0)
        yield from rwait(0.9)
        p = P()
        start, end, low = dil_span(t_press, t_press + 4.0, 1)
        start_p, end_p, low_p = dil_span(t_press, t_press + 4.0, 3)
        duration = (end - start) if (start is not None and end is not None) else None
        delta = p["leg"].get_hit_stop_count() - h0
        # a second press in the same break: a normal hit, no riposte, no second hit stop
        h1 = p["leg"].get_hit_stop_count()
        press()
        yield from rwait(1.2)
        p = P()
        no_second = p["leg"].get_hit_stop_count() == h1
        ok = fired and delta == 1 and abs(low - 0.05) <= 0.01 and abs(low_p - 0.05) <= 0.01 and duration is not None and 0.04 <= duration <= 0.20 and abs(cdil(p["boss"]) - base_boss) < 1e-4 and abs(cdil(p["pawn"]) - base_pawn) < 1e-4 \
            and p["stg"].get_riposte_count() == rip0 + 1 and no_second
        outcomes.append(ok)
        spans.append(duration)
        if not ok:
            log("L4 trial %d: fired %s delta %d min dilation boss %.3f pawn %.3f duration %s now boss %.3f pawn %.3f riposte +%d second press stopped again %s" % (i, fired, delta, low, low_p, duration, cdil(p["boss"]), cdil(p["pawn"]),
                p["stg"].get_riposte_count() - rip0, not no_second))
    log("INFO L4 hit stop real durations %s s (target 0.08)" % [round(s, 3) if s else None for s in spans])
    check("L4 the riposte hit: one hit stop (boss and player at 0.05, 0.04 to 0.20 s real, restored exactly), a second press in the same break does not stop again: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def l5_no_stacking():
    console("rpg.Legend 1")
    outcomes = []
    for i in range(5):
        yield from fresh()
        p = P()
        leg = p["leg"]
        base_boss, base_pawn = cdil(p["boss"]), cdil(p["pawn"])
        t0 = time.perf_counter()
        a = leg.fire_hit_stop_for_test(False)
        yield from rwait(0.02)
        b = P()["leg"].fire_hit_stop_for_test(False)
        yield from rwait(0.6)
        p = P()
        start, end, low = dil_span(t0, t0 + 2.0, 1)
        duration = (end - start) if (start is not None and end is not None) else None
        ok = a and b and low >= 0.049 and duration is not None and abs(duration - 0.10) <= 0.06 and abs(cdil(p["boss"]) - base_boss) < 1e-4 and abs(cdil(p["pawn"]) - base_pawn) < 1e-4
        outcomes.append(ok)
        if not ok:
            log("L5 trial %d: %s %s min %.4f duration %s boss %.4f pawn %.4f" % (i, a, b, low, duration, cdil(p["boss"]), cdil(p["pawn"])))
    check("L5 two hit stops 20 ms apart never stack (minimum 0.05, about 0.10 s together, restored exactly): %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))
    outcomes = []
    for i in range(3):
        yield from fresh()
        p = P()
        base = gdil()
        t0 = time.perf_counter()
        a = p["leg"].fire_slow_motion_for_test()
        yield from rwait(0.1)
        b = P()["leg"].fire_slow_motion_for_test()
        yield from rwait(2.0)
        start, end, low = dil_span(t0, t0 + 4.0, 2)
        duration = (end - start) if (start is not None and end is not None) else None
        ok = a and b and abs(low - 0.25) <= 0.01 and duration is not None and abs(duration - 1.3) <= 0.35 and abs(gdil() - base) < 1e-4
        outcomes.append(ok)
        if not ok:
            log("L5b trial %d: %s %s min %.4f duration %s now %.4f (before %.4f)" % (i, a, b, low, duration, gdil(), base))
    check("L5b two slow motions 100 ms apart never stack (minimum 0.25, about 1.3 s together, restored exactly): %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def l6_reset():
    console("rpg.Legend 1")
    outcomes = []
    for kind, wait_s in (("hit stop", 0.03), ("slow motion", 0.4), ("slow motion", 0.4)):
        yield from fresh()
        p = P()
        leg = p["leg"]
        c0, g0 = leg.get_cancel_count(), p["enc"].get_generation()
        base = gdil()
        if kind == "hit stop":
            a = leg.fire_hit_stop_for_test(False)
        else:
            a = leg.fire_slow_motion_for_test()
        yield from rwait(wait_s)
        P()["enc"].reset_for_test()
        t_reset = time.perf_counter()
        back = yield from until(lambda: abs(gdil() - base) < 1e-4 and abs(cdil(P()["boss"]) - 1.0) < 1e-4, 1.0)
        took = time.perf_counter() - t_reset
        yield from rwait(0.3)
        p = P()
        ok = a and back and took <= 0.15 + 0.1 and p["leg"].get_cancel_count() == c0 + 1 and p["enc"].get_generation() == g0 + 1 and abs(gdil() - base) < 1e-4
        outcomes.append(ok)
        if not ok:
            log("L6 %s: started %s restored %s after %.3f s cancel +%d generation +%d global %.4f" % (kind, a, back, took, p["leg"].get_cancel_count() - c0, p["enc"].get_generation() - g0, gdil()))
    check("L6 a reset during a hit stop or a slow motion restores time within 0.25 s and counts one cancel: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def captures():
    """Four frames for a human to look at (not pass or fail): the slam shake 0.12 s after it starts, the roar shake 0.5 s into the roar, the first frame of the riposte hit stop, the kill slow motion 0.3 s after the kill.
    HighResShot 1280x720 writes into Saved/Screenshots/WindowsEditor; the log names the order the shots were requested in."""
    console("rpg.Legend 1")
    shot = lambda name: (console("HighResShot 1280x720"), log("CAPTURE requested: %s" % name))
    yield from fresh()
    p = P()
    place(p, 600, 0)
    yield from rwait(2.4)
    p = P()
    c0 = p["leg"].get_slam_shake_count()
    p["tr"].start_move("A2", True)
    yield from until(lambda: P()["leg"].get_slam_shake_count() > c0, 5.0)
    yield from rwait(0.12)
    shot("1 slam")
    yield from until(lambda: str(P()["tr"].get_current_move()) == "None", 5.0)
    yield from fresh()
    p = P()
    place(p, 700, 0)
    yield from rwait(2.4)
    p = P()
    r0 = p["leg"].get_roar_shake_count()
    p["dbg"].debug_set_boss_health_fraction(0.5)
    yield from until(lambda: P()["leg"].get_roar_shake_count() > r0, 3.0)
    yield from rwait(0.5)
    shot("2 roar")
    yield from rwait(3.0)
    yield from fresh()
    p = P()
    comp(p["pawn"], "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
    yield from rwait(2.2)
    p = P()
    h0 = p["leg"].get_hit_stop_count()
    hit_riposte(p)
    yield from rwait(0.4)
    press()
    yield from until(lambda: P()["leg"].is_hit_stop_active(), 3.0)
    shot("3 riposte hit stop")
    yield from rwait(1.5)
    yield from fresh()
    p = P()
    p["dbg"].debug_kill_boss()
    yield from until(lambda: P()["leg"].is_slow_motion_active(), 3.0)
    yield from rwait(0.3)
    shot("4 kill slow motion")
    yield from rwait(2.0)


def music_group():
    console("rpg.Legend 1")
    p = P()
    mus = p["mus"]
    has_two = mus.get_editor_property("phase_two_music") is not None
    check("M0 the Phase 2 track is imported and assigned (Scripts/Editor/import_audio.py)", has_two)
    # M1 wake: Phase 1 once per wake
    outcomes = []
    for i in range(3):
        p = P()
        p["enc"].reset_for_test()
        yield from rwait(1.0)
        p = P()
        mus = p["mus"]
        none_ok = mus.get_active_track_name() == "None"
        s1 = mus.get_start_count(1)
        p["enc"].wake()
        p["enc"].hold_for_test(True)
        yield from rwait(0.8)
        mus = P()["mus"]
        outcomes.append(none_ok and mus.get_active_track_name() == "Phase1" and mus.get_start_count(1) == s1 + 1)
        if not outcomes[-1]:
            log("M1 cycle %d: asleep state ok %s then %s, Phase 1 starts +%d" % (i, none_ok, mus.get_active_track_name(), mus.get_start_count(1) - s1))
    check("M1 reset puts the music to None, a wake starts Phase 1 exactly once: %d/%d cycles" % (sum(outcomes), len(outcomes)), all(outcomes))

    # M6 double start guard
    yield from fresh()
    p = P()
    mus = p["mus"]
    p["enc"].reset_for_test()
    yield from rwait(1.0)
    mus = P()["mus"]
    s1 = mus.get_start_count(1)
    mus.start_for_test()
    mus.start_for_test()
    check("M6 two start requests in a row start Phase 1 once", mus.get_start_count(1) == s1 + 1, "start count +%d" % (mus.get_start_count(1) - s1))

    # M2 swap at phase two, once; M4 reset during the crossfade
    outcomes = []
    for i in range(2):
        yield from fresh()
        p = P()
        mus = p["mus"]
        sw0, st2 = mus.get_swap_count(), mus.get_start_count(2)
        p["dbg"].debug_set_boss_health_fraction(0.5)
        yield from until(lambda: P()["mus"].get_active_track_name() == "Phase2", 4.0)
        yield from rwait(0.5)
        p = P()
        mus = p["mus"]
        state = mus.get_active_track_name()
        sw1, st2b = mus.get_swap_count() - sw0, mus.get_start_count(2) - st2
        p["dbg"].debug_set_boss_health_fraction(0.4)
        yield from rwait(2.0)
        mus = P()["mus"]
        again = mus.get_swap_count() - sw0
        ok = has_two and state == "Phase2" and sw1 == 1 and st2b == 1 and again == 1
        outcomes.append(ok)
        if not ok:
            log("M2 fight %d: state %s swap +%d phase 2 starts +%d, after a second drop swap +%d" % (i, state, sw1, st2b, again))
    check("M2 phase two swaps to Phase 2 exactly once per fight: %d/%d fights" % (sum(outcomes), len(outcomes)), all(outcomes))

    outcomes = []
    for i in range(2):
        yield from fresh()
        p = P()
        mus = p["mus"]
        p["dbg"].debug_set_boss_health_fraction(0.5)
        yield from until(lambda: P()["mus"].get_active_track_name() == "Phase2", 4.0)
        yield from rwait(0.5)  # inside the crossfade (2 s)
        P()["enc"].reset_for_test()
        yield from rwait(0.9)
        mus = P()["mus"]
        starts = (mus.get_start_count(1), mus.get_start_count(2))
        none_ok = mus.get_active_track_name() == "None"
        yield from rwait(1.5)
        mus = P()["mus"]
        outcomes.append(none_ok and starts == (mus.get_start_count(1), mus.get_start_count(2)) and not mus.is_any_component_playing())
        if not outcomes[-1]:
            log("M4 trial %d: state None %s, starts %s then %s, playing %s" % (i, none_ok, starts, (mus.get_start_count(1), mus.get_start_count(2)), mus.is_any_component_playing()))
    check("M3/M4 a reset during the crossfade: the music is None, nothing starts again until the boss wakes, no component plays: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))

    # M7 the gate off: no swap
    console("rpg.Legend 0")
    yield from fresh()
    p = P()
    mus = p["mus"]
    sw0 = mus.get_swap_count()
    p["dbg"].debug_set_boss_health_fraction(0.5)
    yield from rwait(3.0)
    mus = P()["mus"]
    check("M7 rpg.Legend 0: no swap, Phase 1 plays on", mus.get_swap_count() == sw0 and mus.get_active_track_name() == "Phase1", "state %s swap +%d" % (mus.get_active_track_name(), mus.get_swap_count() - sw0))
    console("rpg.Legend 1")


def l7_kill():
    console("rpg.Legend 1")
    yield from fresh()
    p = P()
    leg, hud, mus = p["leg"], p["hud"], p["mus"]
    sm0, v0, st0 = leg.get_slow_motion_count(), hud.get_victory_count(), mus.get_stop_count()
    base = gdil()
    t0 = time.perf_counter()
    p["dbg"].debug_kill_boss()
    fired = yield from until(lambda: P()["leg"].get_slow_motion_count() > sm0, 3.0)
    yield from rwait(2.2)
    p = P()
    start, end, low = dil_span(t0, t0 + 4.0, 2)
    duration = (end - start) if (start is not None and end is not None) else None
    leg, hud = p["leg"], p["hud"]
    check("L7 the kill: victory once, slow motion once (minimum 0.25, about 1.2 s real), time restored", fired and hud.get_victory_count() == v0 + 1 and leg.get_slow_motion_count() == sm0 + 1 and abs(low - 0.25) <= 0.01 and duration is not None and abs(duration - 1.2) <= 0.35
          and abs(gdil() - base) < 1e-4, "victory +%d slow motion +%d minimum %.3f duration %s global now %.4f" % (hud.get_victory_count() - v0, leg.get_slow_motion_count() - sm0, low, duration, gdil()))
    yield from until(lambda: P()["mus"] is not None and P()["mus"].get_active_track_name() == "None", 4.0)
    mus = P()["mus"]
    if mus is not None:
        check("M5 after the kill the music is None, one stop, no component plays", mus.get_active_track_name() == "None" and mus.get_stop_count() == st0 + 1 and not mus.is_any_component_playing(),
              "state %s stops +%d playing %s" % (mus.get_active_track_name(), mus.get_stop_count() - st0, mus.is_any_component_playing()))
    else:
        check("M5 the boss is gone before the music state could be read (the pack removes it a few seconds after death)", False)


def script():
    yield 9.0
    console("rpg.Legend 1")
    try:
        with open(os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "legend_groups.txt")) as f:
            wanted = f.read().split()
    except Exception:
        wanted = []
    groups = (("l0", l0_gate_off), ("l1", l1_slam), ("l2", l2_roar), ("l3", l3_leap), ("l4", l4_hit_stop), ("l5", l5_no_stacking), ("l6", l6_reset), ("m", music_group), ("l7", l7_kill), ("cap", captures))
    yield from fresh()
    for name, fn in groups:
        if (wanted and name not in wanted) or (not wanted and name == "cap"):
            continue  # cap (the four pictures) only when asked for: the kill in l7 removes the boss
        log("== %s" % name)
        yield from fn()


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        console("rpg.Legend 0")  # the state every other driver expects
    except Exception:
        pass
    log("RESULT %d/%d passed" % (sum(1 for r in results if r), len(results)))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = S
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    p = P()
    if p["pawn"] is None or p["boss"] is None and s["gen"] is None:
        return
    # samples with the real clock: the camera (shake proof) and the three dilations (time proof)
    now_real = time.perf_counter()
    if p["pc"] is not None and p["pc"].player_camera_manager is not None:
        loc = p["pc"].player_camera_manager.get_camera_location()
        rot = p["pc"].player_camera_manager.get_camera_rotation()
        s["cam"].append((now_real, loc.z, rot.pitch))
        if len(s["cam"]) > 4000:
            del s["cam"][:1000]
    s["dil"].append((now_real, cdil(p["boss"]) if p["boss"] else 1.0, gdil(), cdil(p["pawn"]) if p["pawn"] else 1.0))
    if len(s["dil"]) > 4000:
        del s["dil"][:1000]
    if now_real < s["press_until"] and p["pc"] is not None:
        unreal.RPGInputTestUtils.inject_action(p["pc"], unreal.load_asset(IA_NORMAL), unreal.Vector(1, 0, 0))
    if s["gen"] is None:
        s["gen"] = script()
        s["wake_at"] = 0.0
    if s["wake_at"] > unreal.GameplayStatics.get_time_seconds(world()):
        return
    try:
        s["wake_at"] = unreal.GameplayStatics.get_time_seconds(world()) + float(next(s["gen"]))
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
