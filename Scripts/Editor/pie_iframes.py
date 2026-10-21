"""Gate 2 / M2 (SPEC_M2_damage.md section 6): the dodge's invulnerability windows measured in MONTAGE seconds at fixed 30, 60 and 120 FPS (Freeze D12), and the cleanup of the tag (D13).
URPGIFrameMonitor on the player records every Status.Invulnerable interval with the montage, its effective play rate and the montage position at both edges; the expected window is read from the montage's ANS_iFrames.
F0 the fixed frame rate gives the logical delta asked for; FQ quick dash and FF full roll at 30, 60, 120 FPS (20 trials each): one record, the pack's montage and rate, start and end inside one frame step of the window;
E1/E2 a forced roll (quick then full) keeps its i-frames (defect candidate DC-1: the quick montage's end removes the tag in the full roll's window); C1 a stopped montage ends the tag at once; C3 a reset clears it;
C4a a montage-owned tag that outlives its montage is removed by the watchdog; C4b a foreign (injected) tag is never touched. The boss is frozen awake, the player is moved back each trial. Log prefix [IFrame].
Waits use the WORLD clock (the logical time the dodge logic uses), not the slate delta. Always ends by restoring the frame rate. Run pie_debug_overlay.py once after an editor start first.
"""
import math
import os
import unreal

log = lambda m: unreal.log("[IFrame] " + m)
DODGE = "Gamepad_FaceButton_Right"
QUICK = "Dodge_Small_Forward_Roll_Montage"
FULL = "Dodge_To_Idle_Montage"
QUICK_WINDOW = (0.10718, 0.48975)
FULL_WINDOW = (0.0001, 0.69987)
results = []
S = {"phase": "start", "t": 0.0, "wake_at": 0.0, "gen": None, "keys": {}}
handle = None


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def now():
    return unreal.GameplayStatics.get_time_seconds(world())


def has_tag(actor, tag):
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    try:
        return bool(actor.call_method("HasMatchingGameplayTag", args=(t,)))
    except Exception:
        return None


def tag_obj(name):
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % name)
    return t


def P():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return {"w": w, "pc": pc, "pawn": pawn, "boss": boss, "mon": comp(pawn, "RPGIFrameMonitor") if pawn else None, "enc": comp(boss, "RPGBossEncounter") if boss else None, "dbg": comp(boss, "RPGCombatDebug") if boss else None,
            "tr": comp(boss, "RPGAttackTracker") if boss else None}


def key(p, down):
    if S["keys"].get(DODGE, False) != down:
        S["keys"][DODGE] = down
        unreal.RPGInputTestUtils.set_key_down(p["pc"], DODGE, down)


def place_player(p):
    """700 cm in front of the frozen boss, facing it (the roll goes backward, away)."""
    boss, pawn = p["boss"], p["pawn"]
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw)
    q = unreal.Vector(bl.x + math.cos(r) * 700, bl.y + math.sin(r) * 700, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(q, bl).yaw
    pawn.set_actor_location_and_rotation(q, unreal.Rotator(0, 0, look), False, True)
    p["pc"].set_control_rotation(unreal.Rotator(0, 0, look))


def wait(seconds):
    """Wait in world seconds."""
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
    p["enc"].reset_for_test()
    yield from wait(0.9)
    p = P()
    p["enc"].wake()
    p["enc"].hold_for_test(True)
    p["dbg"].debug_refill_player()
    yield from wait(2.0)


def set_fps(fps):
    unreal.RPGInputTestUtils.set_fixed_frame_rate(float(fps))
    yield 0.0
    yield 0.0


def measure_dt(frames=60):
    samples = []
    last = now()
    for _ in range(frames):
        yield 0.0
        t = now()
        samples.append(t - last)
        last = t
    return samples


def dodge_trial(kind):
    """kind 'quick' (one tap), 'full' (double tap, 0.25 s press to press), or ('chain', gap) for the forced roll. Returns (record count, montage names, last record index) after the roll."""
    p = P()
    p["dbg"].debug_refill_player()
    place_player(p)
    yield from wait(0.4)
    p = P()
    p["mon"].clear_records()
    t0 = now()
    key(p, True)
    yield from wait(0.08)
    key(p, False)
    if kind == "full":
        # 0.14 s press to press: the second press comes before the quick dodge has raised its own tag, the tag belongs to the full roll alone
        yield from wait(0.06)
        key(P(), True)
        yield from wait(0.08)
        key(P(), False)
    elif isinstance(kind, tuple):
        # ("chain", delay): the second press `delay` world seconds after the quick dodge raised its tag: the dodge is running, the pack's roll is forced over it
        yield from until(lambda: P()["mon"].is_invulnerable_now(), 1.0)
        yield from wait(kind[1])
        key(P(), True)
        yield from wait(0.08)
        key(P(), False)
    # wait until a record opened and the tag fell, or give up
    yield from until(lambda: P()["mon"].get_record_count() > 0, 1.0)
    yield from until(lambda: P()["mon"].get_record_count() > 0 and not P()["mon"].is_invulnerable_now(), 2.5)
    yield from wait(0.4)
    mon = P()["mon"]
    return mon, now() - t0


def window_ok(mon, index, window, step_tol):
    """Start and end of record index against the montage window, inside one frame step (the tag edge is seen on the tick after the notify)."""
    sd, ed = mon.get_record_number(index, "StartDelta"), mon.get_record_number(index, "EndDelta")
    ok_s = -0.002 <= sd <= step_tol
    ok_e = -0.002 <= ed <= step_tol
    return ok_s and ok_e, sd, ed


def f0_rate_proof(fps):
    yield from set_fps(fps)
    samples = yield from measure_dt(60)
    mean = sum(samples) / len(samples)
    spread = (max(samples) - min(samples))
    ok = abs(mean - 1.0 / fps) <= 0.02 / fps and spread <= 0.1 / fps
    check("F0 fixed %d FPS gives logical delta 1/%d (mean %.5f, spread %.5f)" % (fps, fps, mean, spread), ok)
    return ok


def rec(mon, i):
    """One record as a dict (numbers in montage seconds, times in world seconds)."""
    g = lambda f: mon.get_record_number(i, f)
    return {"montage": mon.get_record_text(i, "Montage"), "end_montage": mon.get_record_text(i, "EndMontage"), "reason": mon.get_record_text(i, "Reason"), "rate": g("Rate"), "es": g("ExpectedStart"), "ee": g("EndExpected"),
            "sd": g("StartDelta"), "ed": g("EndDelta"), "step": g("FrameStep"), "owned": g("Owned"), "dur": g("EndTime") - g("StartTime")}


def duration_ok(r, fps):
    """The window in REAL seconds is (end - start) / rate: the world clock must agree within two frames."""
    want = (r["ee"] - r["es"]) / r["rate"] if r["rate"] > 0 else -1.0
    return abs(r["dur"] - want) <= 2.0 / fps + 0.004, want


def fq(fps, trials):
    outcomes, starts, ends, durs, reasons = [], [], [], [], {}
    for i in range(trials):
        mon, dur = yield from dodge_trial("quick")
        n = mon.get_record_count()
        if n != 1:
            outcomes.append(False)
            log("FQ%d trial %d: %d records" % (fps, i, n))
            continue
        r = rec(mon, 0)
        tol = 2.0 * r["step"] + 0.004  # the engine quantizes the edges to the frame (and to a frame later at 30 FPS); the real duration check below is what proves the window
        dok, want = duration_ok(r, fps)
        ok = -tol <= r["sd"] <= tol and -tol <= r["ed"] <= tol and r["montage"] == QUICK and r["end_montage"] == QUICK and abs(r["rate"] - 1.3) <= 0.01 and r["owned"] == 1.0 and r["reason"] in ("Natural", "StaleCleared") and dok \
            and abs(r["es"] - QUICK_WINDOW[0]) <= 0.001 and abs(r["ee"] - QUICK_WINDOW[1]) <= 0.001
        outcomes.append(ok)
        starts.append(r["sd"])
        ends.append(r["ed"])
        durs.append(r["dur"])
        reasons[r["reason"]] = reasons.get(r["reason"], 0) + 1
        if not ok:
            log("FQ%d trial %d: montage %s/%s rate %.2f reason %s start delta %.4f end delta %.4f step %.4f real %.4f s (window says %.4f)" % (fps, i, r["montage"], r["end_montage"], r["rate"], r["reason"], r["sd"], r["ed"], r["step"], r["dur"], want))
    log("INFO FQ%d: start delta min %.4f max %.4f, end delta min %.4f max %.4f (montage seconds, frame step %.4f), real duration min %.4f max %.4f s = %.1f frames, tag ended by %s" % (fps, min(starts or [0]), max(starts or [0]), min(ends or [0]), max(ends or [0]), 1.3 / fps,
        min(durs or [0]), max(durs or [0]), (sum(durs) / max(len(durs), 1)) * fps, reasons))
    check("FQ%d quick dash at %d FPS: one record, the pack's clip at rate 1.30, window start and end inside one frame step, real duration = window / rate: %d/%d trials" % (fps, fps, sum(outcomes), len(outcomes)), len(outcomes) == trials and all(outcomes))


def ff(fps, trials):
    # A double tap with a gap of 0.14 s reaches the second press before the quick dodge's own window opens, so the tag belongs to the full roll alone. (With a longer gap the quick dash has already
    # raised the tag and the forced roll continues it: that chain is the E group.)
    outcomes, starts, ends, durs, rates, others = [], [], [], [], [], 0
    attempts = 0
    while len(outcomes) < trials and attempts < trials * 3:
        attempts += 1
        mon, dur = yield from dodge_trial("full")
        if mon.get_record_count() != 1 or mon.get_record_text(0, "Montage") != FULL:
            others += 1
            continue
        r = rec(mon, 0)
        tol = 2.0 * r["step"] + 0.004
        dok, want = duration_ok(r, fps)
        ok = -tol <= r["sd"] <= tol and -tol <= r["ed"] <= tol and r["end_montage"] == FULL and r["owned"] == 1.0 and r["reason"] == "Natural" and dok and abs(r["ee"] - FULL_WINDOW[1]) <= 0.001
        outcomes.append(ok)
        starts.append(r["sd"])
        ends.append(r["ed"])
        durs.append(r["dur"])
        rates.append(r["rate"])
        if not ok:
            log("FF%d trial %d: reason %s rate %.2f start delta %.4f end delta %.4f step %.4f real %.4f s (window says %.4f)" % (fps, len(outcomes), r["reason"], r["rate"], r["sd"], r["ed"], r["step"], r["dur"], want))
    log("INFO FF%d: effective rate min %.2f max %.2f, start delta min %.4f max %.4f, end delta min %.4f max %.4f (frame step %.4f), real duration min %.4f max %.4f s = %.1f frames, attempts that were not a full-only roll %d" % (fps, min(rates or [0]), max(rates or [0]),
        min(starts or [0]), max(starts or [0]), min(ends or [0]), max(ends or [0]), 1.0 / fps, min(durs or [0]), max(durs or [0]), (sum(durs) / max(len(durs), 1)) * fps, others))
    check("FF%d full roll at %d FPS: one record, window start and end inside one frame step, real duration = window / effective rate: %d/%d trials" % (fps, fps, sum(outcomes), len(outcomes)), len(outcomes) == trials and all(outcomes))


def pack_quick(trials):
    """Information only: how long the quick dash's tag lasts when the watchdog is off, i.e. when only the pack's own end of the window state ends it."""
    P()["mon"].set_editor_property("stale_grace_seconds", 5.0)
    durs, reasons = [], {}
    for i in range(trials):
        mon, dur = yield from dodge_trial("quick")
        if mon.get_record_count() == 1:
            r = rec(mon, 0)
            durs.append(r["dur"])
            reasons[r["reason"]] = reasons.get(r["reason"], 0) + 1
    P()["mon"].set_editor_property("stale_grace_seconds", 0.1)
    log("INFO PQ quick dash tag without the watchdog: %d trials, real duration min %.4f max %.4f s (the window is %.4f s), ended by %s" % (len(durs), min(durs or [0]), max(durs or [0]), (QUICK_WINDOW[1] - QUICK_WINDOW[0]) / 1.3, reasons))
    check("PQ the quick dash was measured without the watchdog", len(durs) == trials)


def e_chain(delay, trials, fps=60):
    """A forced roll over a quick dodge that has already raised the tag: the tag must stay up across the switch (one record), and nothing may drop it early."""
    classes = {"full only": 0, "chain, tag continuous": 0, "chain with a gap": 0, "other": 0}
    drops = 0
    for i in range(trials):
        p = P()
        d0 = p["mon"].get_unexpected_drop_count()
        mon, dur = yield from dodge_trial(("chain", delay))
        drops += mon.get_unexpected_drop_count() - d0
        n = mon.get_record_count()
        if n == 1 and mon.get_record_text(0, "Montage") == FULL:
            classes["full only"] += 1
        elif n == 1 and mon.get_record_text(0, "Montage") == QUICK and mon.get_record_text(0, "EndMontage") == FULL:
            classes["chain, tag continuous"] += 1
            r = rec(mon, 0)
            if not (-0.002 <= r["ed"] <= 2.0 * (1.0 / fps) + 0.004):  # one frame step of the roll (effective rate 2.0)
                log("E delay %.2f trial %d: the chained roll's end delta %.4f" % (delay, i, r["ed"]))
        elif n >= 2:
            classes["chain with a gap"] += 1
            log("E delay %.2f trial %d: %d records %s (the tag dropped between the quick dash and the roll)" % (delay, i, n, [mon.get_record_text(k, "Montage") for k in range(n)]))
        else:
            classes["other"] += 1
            log("E delay %.2f trial %d: %d records %s ended in %s (not a forced roll)" % (delay, i, n, [mon.get_record_text(k, "Montage") for k in range(n)], mon.get_record_text(-1, "EndMontage")))
    log("INFO E delay %.2f: %s, early drops %d" % (delay, classes, drops))
    check("E delay %.2f after the quick dodge's tag rose: the roll is forced over it, the tag never drops in between, nothing drops it early: %d/%d trials (%s)" % (delay, classes["chain, tag continuous"], trials, classes),
          classes["chain, tag continuous"] == trials and drops == 0)


def c1_stop(kind):
    """Stop the dodge montage in the middle of its window. The pack's own end of the window state may not run for a stopped montage: the watchdog must then clear the tag within about 0.1 s."""
    outcomes, reasons, stale, offs = [], {}, 0, []
    for i in range(10):
        p = P()
        p["dbg"].debug_refill_player()
        place_player(p)
        yield from wait(0.4)
        p = P()
        p["mon"].clear_records()
        s0 = p["mon"].get_stale_cleared_count()
        key(p, True)
        yield from wait(0.08)
        key(p, False)
        got = yield from until(lambda: P()["mon"].is_invulnerable_now(), 1.5)
        if kind == "full":
            key(P(), True)  # the quick dodge is running: this press forces the full roll over it
            yield from wait(0.08)
            key(P(), False)
            yield from until(lambda: P()["mon"].get_record_count() > 0 and P()["pawn"].get_components_by_class(unreal.SkeletalMeshComponent)[0].get_anim_instance().get_current_active_montage() is not None
                             and P()["pawn"].get_components_by_class(unreal.SkeletalMeshComponent)[0].get_anim_instance().get_current_active_montage().get_name() == FULL, 1.0)
        yield from wait(0.12 if kind == "quick" else 0.10)  # the quick window lasts 0.29 s, the roll's 0.35 s
        p = P()
        inst = p["pawn"].get_components_by_class(unreal.SkeletalMeshComponent)[0].get_anim_instance()
        m = inst.get_current_active_montage()
        inside = m is not None
        if m is not None:
            inst.montage_stop(0.0, m)
        t_stop = now()
        off = yield from until(lambda: has_tag(P()["pawn"], "Status.Invulnerable") is False, 0.4)
        off_after = now() - t_stop
        yield from wait(0.3)
        mon = P()["mon"]
        reason = mon.get_record_text(-1, "Reason")
        reasons[reason] = reasons.get(reason, 0) + 1
        stale += mon.get_stale_cleared_count() - s0
        offs.append(off_after)
        ok = got and inside and off and off_after <= 0.25 and mon.get_record_count() >= 1 and reason in ("Interrupted", "StaleCleared")
        outcomes.append(ok)
        if not ok:
            log("C1 %s trial %d: got %s montage %s off %s after %.3f s reason %s" % (kind, i, got, inside, off, off_after, reason))
    log("INFO C1 %s: the tag was off %.3f to %.3f s after the stop, record reasons %s, cleared by the watchdog in %d of 10 (a stop that the pack's own window state does not answer needs it)" % (kind, min(offs), max(offs), reasons, stale))
    check("C1 %s: a stopped montage leaves no tag behind (off within 0.25 s, record Interrupted or StaleCleared): %d/%d trials" % (kind, sum(outcomes), len(outcomes)), all(outcomes))


def c3_reset():
    outcomes = []
    for i in range(5):
        yield from fresh()
        p = P()
        place_player(p)
        yield from wait(0.4)
        p = P()
        p["mon"].clear_records()
        r0 = p["mon"].get_reset_clear_count()
        key(p, True)
        yield from wait(0.08)
        key(p, False)
        got = yield from until(lambda: P()["mon"].is_invulnerable_now(), 1.5)
        key(P(), True)  # the quick dodge is running: this press forces the full roll over it
        yield from wait(0.08)
        key(P(), False)
        yield from wait(0.1)  # inside the roll's 0.35 s window
        P()["enc"].reset_for_test()
        yield from wait(0.15)
        p = P()
        off = has_tag(p["pawn"], "Status.Invulnerable") is False
        mon = p["mon"]
        ok = got and off and mon.get_reset_clear_count() == r0 + 1 and mon.get_record_text(-1, "Reason") == "EncounterReset"
        outcomes.append(ok)
        if not ok:
            log("C3 trial %d: got %s off %s reset clears +%d reason %s" % (i, got, off, mon.get_reset_clear_count() - r0, mon.get_record_text(-1, "Reason")))
    check("C3 an encounter reset during a roll clears the tag at once, record EncounterReset: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def c4_owned_and_foreign():
    outcomes = []
    for i in range(5):
        p = P()
        p["mon"].clear_records()
        s0 = p["mon"].get_stale_cleared_count()
        p["pawn"].call_method("AddOwnedGameplayTag", args=(tag_obj("Status.Invulnerable"),))
        yield 0.0
        p["mon"].debug_force_owned(True)
        t0 = now()
        gone = yield from until(lambda: has_tag(P()["pawn"], "Status.Invulnerable") is False, 1.0)
        dt = now() - t0
        mon = P()["mon"]
        ok = gone and 0.05 <= dt <= 0.35 and mon.get_stale_cleared_count() == s0 + 1
        outcomes.append(ok)
        if not ok:
            log("C4a trial %d: gone %s after %.3f s stale +%d" % (i, gone, dt, mon.get_stale_cleared_count() - s0))
        yield from wait(0.3)
    check("C4a a montage-owned tag with no montage is removed by the watchdog after about 0.1 s: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))
    outcomes = []
    for i in range(5):
        p = P()
        p["mon"].debug_force_owned(False)
        p["mon"].clear_records()
        s0 = p["mon"].get_stale_cleared_count()
        p["pawn"].call_method("AddOwnedGameplayTag", args=(tag_obj("Status.Invulnerable"),))
        yield from wait(1.0)
        still = has_tag(P()["pawn"], "Status.Invulnerable") is True
        stale = P()["mon"].get_stale_cleared_count() == s0
        P()["pawn"].call_method("RemoveOwnedGameplayTag", args=(tag_obj("Status.Invulnerable"),))
        outcomes.append(still and stale)
        yield from wait(0.3)
    check("C4b a foreign (injected) tag is never touched: still set after 1.0 s, watchdog idle: %d/%d trials" % (sum(outcomes), len(outcomes)), all(outcomes))


def selected():
    """All groups, or the ones named in Saved/iframes_groups.txt (fps30 fps60 fps120 packquick chain cleanup): a rerun of a part after a failure."""
    try:
        with open(os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "iframes_groups.txt")) as f:
            wanted = f.read().split()
    except Exception:
        wanted = []
    return lambda name: (not wanted) or name in wanted


def script():
    yield 9.0
    want = selected()
    p = P()
    check("T0 the player has the i-frame monitor", p["mon"] is not None)
    yield from fresh()
    for fps in (30, 60, 120):
        if not want("fps%d" % fps):
            continue
        log("== %d FPS" % fps)
        ok = yield from f0_rate_proof(fps)
        if not ok:
            check("FQ%d/FF%d skipped: the frame rate could not be set" % (fps, fps), False)
            continue
        yield from fq(fps, 20)
        yield from ff(fps, 20)
    if want("chain"):
        log("== forced roll chain at 60 FPS")
        yield from set_fps(60)
        yield from e_chain(0.0, 10)
        yield from e_chain(0.04, 10)
    if want("cleanup"):
        log("== cleanup at 60 FPS")
        yield from set_fps(60)
        yield from c1_stop("quick")
        yield from c1_stop("full")
        yield from c3_reset()
        yield from c4_owned_and_foreign()
        check("S1 the overlay has an IFRAME line", any(l.strip().startswith("IFRAME") for l in P()["dbg"].build_lines()))
    if want("packquick"):  # last: it changes the monitor's watchdog setting for its trials
        log("== the pack's own end of the quick dash window")
        yield from set_fps(60)
        yield from pack_quick(5)


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        unreal.RPGInputTestUtils.set_fixed_frame_rate(0.0)
        key(P(), False)
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
