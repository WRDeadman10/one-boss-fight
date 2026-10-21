"""Gate 1 / M1 (SPEC_M1_trace.md): the pack's weapon trace on the boss's close attacks, measured with URPGTraceAudit (an observer) and kept in order by URPGTraceGuard (Freeze 12, 13; tests H01 to H11).
P0 the live pack names resolve. T0 windows of A1, A1b, A3a, A3b: sockets, radius, the previous positions are fresh at every open, the stored positions follow the pose (continuity). T1 step per frame against frame rate at 15, 30, 60, 120 FPS.
T2 NO TUNNEL: the sweep's reach is computed from the socket paths recorded at 120 FPS, then A1 is played at fixed 30 and 60 FPS and the pack must put the player in its hit set for every placement that is clearly inside the reach and
for none that is clearly outside (24 placements). T3 a slow strike puts the player in the hit set once (H01); T4 a clear miss does nothing (H03); T5 many overlapping samples, one insertion (H04); T6 the A2 stand-in opens two windows in one swing:
one damage event per instance (G-3). T8 the trace ends at once on a stop, a stance break, a phase transition, a reset and the boss's death (H07). T9 arena geometry blocks the pack's trace with the guard on (H11).
Uses bare montages (no attack ability: the trace runs, nothing is damaged) except T6 and T9 (the A2 ability). Boss frozen awake. Generator style, world-clock waits. Always restores the frame rate. Log prefix [Trace].
"""
import math
import os
import unreal

log = lambda m: unreal.log("[Trace] " + m)
results = []
S = {"phase": "start", "t": 0.0, "wake_at": 0.0, "gen": None}
handle = None
SOCKETS = ["BladeStart", "MiddleSocket", "BladeEnd", "Weapon Start", "Weapon End"]
R_SWEEP = 50.0
CAPSULE = 42.0
OUT_MARGIN = 70.0


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


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def now():
    return unreal.GameplayStatics.get_time_seconds(world())


def P():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return {"w": w, "pc": pc, "pawn": pawn, "boss": boss, "enc": comp(boss, "RPGBossEncounter"), "tr": comp(boss, "RPGAttackTracker"), "dbg": comp(boss, "RPGCombatDebug"), "stg": comp(boss, "RPGBossStagger"),
            "ph": comp(boss, "RPGBossPhases"), "audit": comp(boss, "RPGTraceAudit"), "guard": comp(boss, "RPGTraceGuard")}


def place(p, dist, ang_deg):
    boss, pawn = p["boss"], p["pawn"]
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw + ang_deg)
    q = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(q, bl).yaw
    pawn.set_actor_location_and_rotation(q, unreal.Rotator(0, 0, look), False, True)


def boss_mesh(p):
    return p["boss"].get_components_by_class(unreal.SkeletalMeshComponent)[0]


def weapon_mesh(p):
    return next((c for c in p["boss"].get_components_by_class(unreal.StaticMeshComponent) if "Weapon" in c.get_name()), None)


def wait(seconds):
    t_end = now() + seconds
    while now() < t_end:
        yield 0.0


def until(cond, timeout):
    t_end = now() + timeout
    while not cond():
        if now() > t_end:
            return False
        yield 0.0
    return True


def fresh():
    p = P()
    unreal.RPGInputTestUtils.set_fixed_frame_rate(0.0)
    p["enc"].reset_for_test()
    yield from wait(0.9)
    p = P()
    p["enc"].wake()
    p["enc"].hold_for_test(True)
    p["dbg"].debug_refill_player()
    p["tr"].enter_combat()
    yield from wait(2.4)
    P()["audit"].reset_counters()


def play(p, move, rate=1.0):
    ok = p["tr"].play_move_montage_for_test(move)
    if ok and rate != 1.0:
        inst = boss_mesh(p).get_anim_instance()
        inst.montage_set_play_rate(inst.get_current_active_montage(), rate)
    return ok


def montage_name(p):
    inst = boss_mesh(p).get_anim_instance()
    m = inst.get_current_active_montage() if inst else None
    return m.get_name() if m else None


def run_move(move, rate=1.0, settle=0.8):
    """Plays a bare montage and waits until the boss has no montage again (and the trace is over)."""
    p = P()
    ok = play(p, move, rate)
    yield from wait(0.15)
    yield from until(lambda: montage_name(P()) is None, 8.0)
    yield from wait(settle)
    return ok


def segment_dist(p1, p2, q1, q2):
    """Closest distance between segments p1p2 and q1q2 (3D lists)."""
    def sub(a, b): return [a[i] - b[i] for i in range(3)]
    def dot(a, b): return sum(a[i] * b[i] for i in range(3))
    d1, d2, r = sub(p2, p1), sub(q2, q1), sub(p1, q1)
    a, e, f = dot(d1, d1), dot(d2, d2), dot(d2, r)
    s = t = 0.0
    if a <= 1e-9 and e <= 1e-9:
        return math.sqrt(dot(r, r))
    if a <= 1e-9:
        t = max(0.0, min(1.0, f / e))
    else:
        c = dot(d1, r)
        if e <= 1e-9:
            s = max(0.0, min(1.0, -c / a))
        else:
            b = dot(d1, d2)
            denom = a * e - b * b
            s = max(0.0, min(1.0, (b * f - c * e) / denom)) if denom > 1e-9 else 0.0
            t = (b * s + f) / e
            if t < 0.0:
                t = 0.0
                s = max(0.0, min(1.0, -c / a))
            elif t > 1.0:
                t = 1.0
                s = max(0.0, min(1.0, (b - c) / a))
    c1 = [p1[i] + d1[i] * s for i in range(3)]
    c2 = [q1[i] + d2[i] * t for i in range(3)]
    return math.sqrt(dot(sub(c1, c2), sub(c1, c2)))


# ---- groups ----------------------------------------------------------------------------------------------------------------------------------------------------------------
def p0_preflight():
    p = P()
    missing = p["guard"].get_missing_pack_names()
    check("P0 the guard and the audit are on the boss", p["guard"] is not None and p["audit"] is not None)
    check("P0 the pack's live trace object resolves with every name the guard needs", p["guard"].is_resolved() and missing == "", "missing: %s" % missing)
    check("P0 the audit finds the pack trace", p["audit"].is_resolved())


def t0_windows():
    for move in ("A1", "A1b", "A3a", "A3b"):
        yield from fresh()
        p = P()
        place(p, 150 if move.endswith("b") else 700, 0)  # a second stage stands only inside the tracker's branch check (range 400, cone 120): it stops the montage at once otherwise
        n0 = p["audit"].get_window_count()
        played = play(p, move)
        seen = set()
        t_end = now() + 8.0
        yield 0.0
        while montage_name(P()) is not None and now() < t_end:
            seen.add(montage_name(P()))
            yield 0.0
        yield from wait(0.8)
        a = P()["audit"]
        log("INFO T0 %s: montage played %s, seen %s" % (move, played, sorted(seen)))
        n = a.get_window_count() - n0
        o = a.get_window_counter(-1, "OpenPos")
        c = a.get_window_counter(-1, "ClosePos")
        log("INFO T0 %s: windows %d open %.2f close %.2f samples %d sockets %d radius %.0f+%.0f refresh error %.2f cm continuity %.2f cm peak step %.0f cm no ability %d" % (move, n, o, c, a.get_window_counter(-1, "Samples"), a.get_counter("Sockets"),
            a.get_counter("BaseRadius"), a.get_counter("Modifier"), a.get_counter("OpenRefreshErrorCm"), a.get_counter("MaxContinuityErrorCm"), a.get_window_counter(-1, "PeakStepCm"), a.get_counter("WindowsNoAbility")))
        check("T0 %s: one trace window, sockets 5, radius 50, samples seen" % move, n == 1 and a.get_counter("Sockets") == 5 and a.get_counter("BaseRadius") == 50.0 and a.get_window_counter(-1, "Samples") >= 3)
        check("T0 %s: the previous positions are fresh at the open (error <= 1 cm) and follow the pose (continuity <= 1 cm)" % move, a.get_counter("OpenRefreshErrorCm") <= 1.0 and a.get_counter("MaxContinuityErrorCm") <= 1.0)


def t1_step_vs_fps():
    peaks = {}
    for fps in (15, 30, 60, 120):
        yield from fresh()
        p = P()
        place(p, 700, 0)
        unreal.RPGInputTestUtils.set_fixed_frame_rate(float(fps))
        yield 0.0
        yield 0.0
        P()["audit"].reset_counters()
        yield from run_move("A1")
        a = P()["audit"]
        peaks[fps] = (a.get_counter("PeakStepCm"), a.get_counter("PeakSpeedCmPerSec"), a.get_counter("MaxDt"), a.get_counter("SuspectSweeps"))
        unreal.RPGInputTestUtils.set_fixed_frame_rate(0.0)
    for fps, (step, speed, maxdt, suspect) in peaks.items():
        log("INFO T1 %d FPS: peak step %.0f cm, peak speed %.0f cm/s, max dt %.4f, suspect sweeps %d (capsule radius %.0f cm, sweep radius %.0f cm)" % (fps, step, speed, maxdt, suspect, CAPSULE, R_SWEEP))
    check("T1 the frame step shrinks with the frame rate (15 > 30 > 60 > 120 FPS) and no step is suspect (> 800 cm)", peaks[15][0] > peaks[30][0] > peaks[60][0] > peaks[120][0] and all(v[3] == 0 for v in peaks.values()))
    check("T1 the logical frame time followed the fixed rate (max dt within 15 percent)", all(abs(peaks[f][2] - 1.0 / f) <= 0.15 / f for f in peaks))


def t2_no_tunnel():
    # Ground truth: socket paths of A1 recorded at 120 FPS while the trace is open.
    yield from fresh()
    p = P()
    place(p, 700, 0)
    unreal.RPGInputTestUtils.set_fixed_frame_rate(120.0)
    yield 0.0
    yield 0.0
    p = P()
    wm = weapon_mesh(p)
    frames = []
    play(p, "A1")
    yield 0.0
    while montage_name(P()) is not None:
        pp = P()
        if pp["audit"].is_trace_active() and wm is not None:
            frames.append([[v for v in (wm.get_socket_location(s).x, wm.get_socket_location(s).y, wm.get_socket_location(s).z)] for s in SOCKETS])
        yield 0.0
    unreal.RPGInputTestUtils.set_fixed_frame_rate(0.0)
    check("T2 ground truth recorded (>= 10 frames of the open trace at 120 FPS)", len(frames) >= 10 and wm is not None, "%d frames" % len(frames))
    if len(frames) < 10:
        return
    yield from fresh()
    p = P()
    bl = p["boss"].get_actor_location()
    yaw0 = p["boss"].get_actor_rotation().yaw
    org, ext = p["pawn"].get_actor_bounds(True)
    cap = p["pawn"].get_components_by_class(unreal.CapsuleComponent)[0]
    log("INFO T2 player colliding bounds extent (%.0f, %.0f, %.0f) cm, capsule radius %.1f half height %.1f (model: radius %.0f)" % (ext.x, ext.y, ext.z, cap.get_scaled_capsule_radius(), cap.get_scaled_capsule_half_height(), CAPSULE))
    placements = [(d, a) for d in (100, 200, 300, 400, 500) for a in (-40, -15, 15, 40)]
    expected = {}
    zc = bl.z + 20
    for d, a in placements:
        r = math.radians(yaw0 + a)
        px, py = bl.x + math.cos(r) * d, bl.y + math.sin(r) * d
        axis = ([px, py, zc - 96], [px, py, zc + 96])
        dmin = 1e9
        for k in range(1, len(frames)):
            for s in range(len(SOCKETS)):
                dmin = min(dmin, segment_dist(frames[k - 1][s], frames[k][s], axis[0], axis[1]))
        expected[(d, a)] = (R_SWEEP + CAPSULE) - dmin  # margin in cm: > 0 inside the reach
    clear_in = [k for k, m in expected.items() if m >= 15.0]
    # The model knows the capsule only: whatever else of the player the pack's trace can touch (the weapon, the mesh) widens the reach, so "clearly outside" is 70 cm beyond the modelled reach.
    clear_out = [k for k, m in expected.items() if m <= -OUT_MARGIN]
    log("INFO T2 placements: %d clearly inside (>= +15 cm), %d clearly outside (<= -%.0f cm), %d between; margins %s" % (len(clear_in), len(clear_out), OUT_MARGIN, len(expected) - len(clear_in) - len(clear_out), sorted((k, round(m)) for k, m in expected.items())))
    check("T2 the scan has clear cases on both sides", len(clear_in) >= 4 and len(clear_out) >= 4, "in %d out %d" % (len(clear_in), len(clear_out)))
    for fps in (30, 60):
        misses, ghosts = [], []
        for (d, a), m in expected.items():
            if -OUT_MARGIN < m < 15.0:
                continue
            yield from fresh()
            p = P()
            unreal.RPGInputTestUtils.set_fixed_frame_rate(float(fps))
            yield 0.0
            yield 0.0
            p = P()
            place(p, d, a)
            p["audit"].reset_counters()
            yield from run_move("A1", settle=0.4)
            ins = P()["audit"].get_counter("SetInsertions")
            if m >= 15.0 and ins < 1:
                misses.append((d, a, round(m)))
            if m <= -OUT_MARGIN and ins > 0:
                ghosts.append((d, a, round(m)))
            unreal.RPGInputTestUtils.set_fixed_frame_rate(0.0)
        check("T2 %d FPS: every placement clearly inside the sweep's reach put the player in the pack's hit set (no tunnelling) - missed %s" % (fps, misses), len(misses) == 0)
        check("T2 %d FPS: no placement clearly outside the reach did (no phantom hit) - extra %s" % (fps, ghosts), len(ghosts) == 0)


def t3_to_t5():
    outcomes = []
    for dist in (70, 90):
        for i in range(10):
            yield from fresh()
            p = P()
            place(p, dist, 0)
            unreal.RPGInputTestUtils.set_fixed_frame_rate(60.0)
            yield 0.0
            p["audit"].reset_counters()
            yield from run_move("A1", rate=0.25, settle=0.4)
            a = P()["audit"]
            outcomes.append(a.get_counter("SetInsertions") == 1 and a.get_counter("OverlapSamples") >= 2)
            unreal.RPGInputTestUtils.set_fixed_frame_rate(0.0)
    check("T3 slow strike (rate 0.25) at 70 and 90 cm: the player enters the hit set exactly once, over several overlapping samples (H01): %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))
    outcomes = []
    for i in range(5):
        yield from fresh()
        p = P()
        place(p, 700, 0)
        p["audit"].reset_counters()
        yield from run_move("A1", settle=0.4)
        a = P()["audit"]
        outcomes.append(a.get_counter("SetInsertions") == 0 and a.get_counter("OverlapSamples") == 0)
    check("T4 a clear miss (player at 700 cm): no overlap, no hit set insertion (H03): %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))
    outcomes = []
    for i in range(5):
        yield from fresh()
        p = P()
        place(p, 70, 0)
        p["audit"].reset_counters()
        yield from run_move("A1", settle=0.4)
        a = P()["audit"]
        outcomes.append(a.get_counter("OverlapSamples") >= 2 and a.get_counter("SetInsertions") == 1)
        if not outcomes[-1]:
            log("T5 trial %d: overlap %s insertions %s" % (i, a.get_counter("OverlapSamples"), a.get_counter("SetInsertions")))
    check("T5 many overlapping samples, one hit set insertion (H04): %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def t6_instance():
    outcomes = []
    for dist in (60, 100, 140, 180, 220, 260):
        for i in range(5):
            yield from fresh()
            p = P()
            place(p, dist, 0)
            hp0 = attr(p["pawn"], "Attribute.Health")
            p["audit"].reset_counters()
            p["tr"].start_move("A2", True)
            yield from wait(0.3)
            yield from until(lambda: P()["tr"].get_current_move() == "None" or str(P()["tr"].get_current_move()) == "None", 6.0)
            yield from wait(0.6)
            p = P()
            a = p["audit"]
            lost = hp0 - attr(p["pawn"], "Attribute.Health")
            ok = a.get_counter("DamageAccepted") <= 1 and abs(lost - 36.0 * a.get_counter("DamageAccepted")) <= 0.6
            outcomes.append(ok)
            log("INFO T6 %d cm trial %d: windows %d insertions %d accepted %d lost %.1f" % (dist, i, a.get_counter("Windows"), a.get_counter("SetInsertions"), a.get_counter("DamageAccepted"), lost))
            if not ok:
                log("T6 FAIL detail: %s" % a.get_window_summary(-1))
    check("T6 A2 (two trace windows in one swing): at most one damage event per attack instance and health lost equals 36 per event: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def t8_interrupts():
    for kind in ("stop", "stagger", "phase", "reset", "death"):
        outcomes, afters, closes = [], [], []
        for i in range(1 if kind == "death" else 4):
            yield from fresh()
            p = P()
            place(p, 700, 0)
            p["audit"].reset_counters()
            play(p, "A1")
            yield from until(lambda: P()["audit"].is_trace_active() or montage_name(P()) is None, 2.0)
            yield from wait(0.05)  # a few samples into the window
            p = P()
            was_active = p["audit"].is_trace_active()
            if kind == "stop":
                inst = boss_mesh(p).get_anim_instance()
                inst.montage_stop(0.1, inst.get_current_active_montage())
            elif kind == "stagger":
                p["stg"].force_break_for_test()
            elif kind == "phase":
                p["dbg"].debug_set_boss_health_fraction(0.55)
            elif kind == "reset":
                p["enc"].reset_for_test()
            else:
                p["dbg"].debug_kill_boss()
            yield from wait(0.6)
            a = P()["audit"]
            after, ftc = a.get_counter("SamplesAfterInterrupt"), a.get_counter("FramesToClose")
            afters.append(after)
            closes.append(ftc)
            limit = 2 if kind == "stop" else 1
            outcomes.append(was_active and after <= limit and not a.is_trace_active())
            if not outcomes[-1]:
                log("T8 %s trial %d: was active %s after %s frames to close %s active now %s" % (kind, i, was_active, after, ftc, a.is_trace_active()))
            if kind == "phase":
                yield from until(lambda: not P()["ph"].is_in_transition(), 4.0)
        log("INFO T8 %s: samples after the interrupt max %.0f, frames to close max %.0f" % (kind, max(afters), max(closes)))
        check("T8 %s: the pack trace is open at the interrupt and ends at once (samples after it <= %d): %d/%d trials" % (kind, 2 if kind == "stop" else 1, sum(outcomes), len(outcomes)), all(outcomes))


def t9_walls():
    for guard_on in (False, True):
        outcomes = []
        for i in range(5):
            yield from fresh()
            p = P()
            p["guard"].set_editor_property("block_through_walls", guard_on)
            boss = p["boss"]
            bl = boss.get_actor_location()
            fwd = boss.get_actor_forward_vector()
            p["dbg"].debug_spawn_wall(unreal.Vector(bl.x + fwd.x * 110, bl.y + fwd.y * 110, bl.z), boss.get_actor_rotation(), unreal.Vector(0.2, 8, 6))
            place(p, 200, 0)
            hp0 = attr(p["pawn"], "Attribute.Health")
            p["audit"].reset_counters()
            p["tr"].start_move("A2", True)
            yield from wait(0.3)
            yield from until(lambda: str(P()["tr"].get_current_move()) == "None", 6.0)
            yield from wait(0.6)
            p = P()
            lost = hp0 - attr(p["pawn"], "Attribute.Health")
            hit = p["audit"].get_counter("SetInsertions") > 0
            outcomes.append(hit if not guard_on else (not hit and lost == 0))
            p["dbg"].debug_clear_walls()
            log("INFO T9 guard %s trial %d: insertions %d damage %.1f occluded samples %d" % (guard_on, i, p["audit"].get_counter("SetInsertions"), lost, p["guard"].get_occluded_sample_count()))
        if guard_on:
            check("T9 with the wall gate on: a player behind a wall (110 cm in front of the boss) is not hit by the A2 slam: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))
        else:
            log("INFO T9 baseline without the guard: the pack's own trace hit the player behind the wall in %d of %d trials (G-5 documented)" % (sum(outcomes), len(outcomes)))
    P()["guard"].set_editor_property("block_through_walls", True)


def t10_overlay():
    lines = " ".join(P()["dbg"].build_lines())
    check("T10 the overlay separates trace overlap from damage accepted", "overlap" in lines and "damage accepted" in lines and "rejected" in lines)


def selected_groups():
    """All groups, or the ones named in Saved/trace_groups.txt (a rerun of a part after a failure; the file is read once at the start)."""
    everything = (t0_windows, t1_step_vs_fps, t2_no_tunnel, t3_to_t5, t6_instance, t9_walls, t8_interrupts)
    try:
        with open(os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "trace_groups.txt")) as f:
            wanted = f.read().split()
    except Exception:
        wanted = []
    return [g for g in everything if not wanted or g.__name__ in wanted]


def script():
    yield 9.0
    yield from fresh()
    p0_preflight()
    for group in selected_groups():
        if group is t8_interrupts:
            t10_overlay()  # needs the boss: the death trial in t8 destroys it
        log("== %s" % group.__name__)
        yield from group()


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        unreal.RPGInputTestUtils.set_fixed_frame_rate(0.0)
        P()["guard"].set_editor_property("block_through_walls", True)
        P()["dbg"].debug_clear_walls()
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
    if p["pawn"] is None or p["boss"] is None:
        return
    if s["gen"] is None:
        s["gen"] = script()
        s["wake_at"] = 0.0
    if s["wake_at"] > now():
        return
    try:
        s["wake_at"] = now() + float(next(s["gen"]))
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
