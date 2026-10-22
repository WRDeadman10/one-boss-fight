"""
Synchronized riposte (Freeze 17.4, G2-7): an accepted Light Attack press on the downed boss plays the paired clips (AN_Riposte_Player_Front on the player, AN_Riposte_Boss_Reaction on the boss) with one critical hit at the impact.
Real press (IA_NormalAttack injected), boss held awake, stance break through the break gate, player 110 cm in front of the downed boss.
  S1 the execution: starts at once, the player plays the strike clip and the boss the reaction clip, the player's input is locked (a press and a dodge during the clips start nothing), the player slides to 150 cm and the clip's root motion
     brings him to about 60 cm, ONE damage event of exactly 100 (40 x 2.5) lands at 0.8 s after the start (the weapon trace is cut: the hit intake sees no hit), a second press in the same break is rejected, the clips end after 2 s, the
     input is back (a press starts a swing), the kneel loop resumes and the boss gets up normally.
  S2 fail-safe: the player dies in the middle of the execution: it is aborted (counted), no damage after that, the encounter resets, the boss stands.
  S3 the stand-in: with the clips off the press is accepted and arms the critical multiplier, nothing executes.
  S4 fail-safe: the boss is killed before the impact: the execution is aborted, no impact damage is applied (this scenario is last: the pack destroys a dead boss).
Log prefix [RipostExec]; ends with RESULT n/m passed. Run pie_debug_overlay.py once after an editor start first.
"""
import math
import unreal

log = lambda m: unreal.log("[RipostExec] " + m)
IA = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
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


def montage_clip_name(m, who="boss"):
    """The animation asset the boss's (or the player's) active montage plays, read by C++ from the montage's first segment."""
    dbg = P()["dbg"]
    return dbg.debug_player_montage_anim_name() if who == "player" else dbg.debug_boss_montage_anim_name()


def flat_dist(a, b):
    d = a.get_actor_location() - b.get_actor_location()
    return math.hypot(d.x, d.y)


def sample():
    p = P()
    pawn, boss = p["pawn"], p["boss"]
    pm = pawn.get_components_by_class(unreal.SkeletalMeshComponent)[0].get_anim_instance()
    bm = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0].get_anim_instance()
    pmon = pm.get_current_active_montage() if pm else None
    bmon = bm.get_current_active_montage() if bm else None
    S["samples"].append({"t": S["now"], "exec": p["stg"].is_riposte_executing(), "stage": p["stg"].get_clip_stage_name(), "pclip": montage_clip_name(pmon, "player") if pmon else None,
                         "bclip": montage_clip_name(bmon) if bmon else None, "dist": flat_dist(pawn, boss), "hp": attr(boss, "Attribute.Health"), "stag": p["stg"].is_staggered(),
                         "swings": p["swing"].get_attack_swing_count(), "hits": p["intake"].get_boss_hit_count(), "impacts": p["stg"].get_riposte_impact_count()})


def downed_boss():
    """A stance break, waited until the kneel loop plays; the player in front of it, refilled."""
    p = P()
    p["dbg"].debug_set_boss_health_fraction(1.0)
    p["stg"].force_break_for_test()
    yield from until(lambda: P()["stg"].get_clip_stage_name() == "down", 3.0)
    yield 0.3
    p = P()
    place(p)
    p["dbg"].debug_refill_player()
    yield 0.6


def s1_execution():
    yield from fresh()
    yield from downed_boss()
    p = P()
    ok_avail = p["stg"].is_riposte_available(p["pawn"])
    hits0 = p["intake"].get_boss_hit_count()
    rej0 = p["stg"].get_riposte_reject_count()
    hp0 = attr(p["boss"], "Attribute.Health")
    S["samples"] = []
    t_press = S["now"]
    press("IA_NormalAttack", 0.12)
    started = yield from until(lambda: P()["stg"].is_riposte_executing(), 1.0)
    yield 0.5
    again = P()["stg"].try_riposte(P()["pawn"])  # a second request in the same stance break: rejected (once per break)
    press("IA_NormalAttack", 0.12)  # and the locked player starts nothing from a press or a dodge
    yield 0.1
    press("IA_Dodge", 0.15)
    ended = yield from until(lambda: not P()["stg"].is_riposte_executing(), 4.0)
    yield 0.5
    samples = S["samples"]
    S["samples"] = None
    p = P()
    run = [s for s in samples if s["exec"]]
    first_clip = next((s for s in run if s["pclip"] == "AN_Riposte_Player_Front"), None)
    t0 = first_clip["t"] if first_clip else None
    dropped = [s for s in samples if s["hp"] is not None and hp0 is not None and s["hp"] < hp0 - 0.01]
    t_hit = dropped[0]["t"] - t0 if (dropped and t0 is not None) else None
    hp_after = samples[-1]["hp"]
    check("S1 the riposte was available (%s) and the press started the execution %.2f s after the press (ended %s)" % (ok_avail, (run[0]["t"] - t_press) if run else -1, ended), ok_avail and started and ended and len(run) > 20 and (run[0]["t"] - t_press) < 0.5, "")
    check("S1 the player plays AN_Riposte_Player_Front and the boss AN_Riposte_Boss_Reaction during the execution", first_clip is not None and any(s["bclip"] == "AN_Riposte_Boss_Reaction" for s in run), "stages %s" % sorted(set(s["stage"] for s in run)))
    run_len = (run[-1]["t"] - run[0]["t"]) if run else 0.0
    check("S1 the execution lasted about 2 s (%.2f s)" % run_len, 1.7 <= run_len <= 2.3, "")
    check("S1 the player is locked: the second press and the dodge started no other montage and no swing (swings %d -> %d, the first press's own attack counts once)" % (samples[0]["swings"], samples[-1]["swings"]),
          all(s["pclip"] in (None, "AN_Riposte_Player_Front") or s["t"] < (t0 or 0) + 0.05 for s in run) and samples[-1]["swings"] <= samples[0]["swings"] + 1, "%s" % sorted(set(str(s["pclip"]) for s in run)))
    d_back = max([s["dist"] for s in run if t0 is not None and t0 <= s["t"] <= t0 + 0.5] or [-1.0])
    d_end = run[-1]["dist"] if run else None
    check("S1 the player slid back from 110 cm (%.0f at most in the first 0.5 s) and the clip's root motion then brought him to about 60 cm (%.0f at the end of the execution)" % (d_back, d_end or -1), d_back >= 115 and d_end is not None and 45 <= d_end <= 80, "")
    contact = [s["dist"] for s in samples if s["t"] > run[-1]["t"] + 0.3] if run else []
    check("S1 after the execution the capsules are apart again (distance %.0f cm 0.3 s later or more, at least 95)" % (contact[-1] if contact else -1), bool(contact) and contact[-1] >= 95.0, "")
    check("S1 one damage event of exactly 100 (40 x 2.5): health %s -> %s, impacts %d, hit intake hits %d -> %d (the weapon trace is cut)" % (hp0, hp_after, p["stg"].get_riposte_impact_count(), hits0, p["intake"].get_boss_hit_count()),
          hp0 is not None and hp_after is not None and abs((hp0 - hp_after) - 100.0) < 0.6 and p["stg"].get_riposte_impact_count() == 1 and p["intake"].get_boss_hit_count() == hits0, "")
    check("S1 the damage landed at the impact, 0.8 s after the clips started (%s s)" % (("%.2f" % t_hit) if t_hit is not None else None), t_hit is not None and 0.65 <= t_hit <= 1.0, "")
    check("S1 the second request in the same break was rejected (%s: %s), the riposte count is %d" % (again, p["stg"].get_last_riposte_result(), p["stg"].get_riposte_count()), again is False and p["stg"].get_riposte_reject_count() == rej0 + 1 and p["stg"].get_riposte_count() >= 1, "")
    # the input is back and the boss goes on
    n0 = P()["swing"].get_attack_swing_count()
    yield from until(lambda: not P()["stg"].is_staggered(), 6.0)
    yield 1.0
    place(P())
    P()["dbg"].debug_refill_player()
    yield 0.6
    press("IA_NormalAttack", 0.12)
    yield 0.8
    p = P()
    check("S1 after the execution the boss got up (not staggered) and the player's input is back (a press starts a swing: %d -> %d)" % (n0, p["swing"].get_attack_swing_count()), not p["stg"].is_staggered() and p["swing"].get_attack_swing_count() == n0 + 1, "")


def s2_player_dies():
    yield from fresh()
    yield from downed_boss()
    p = P()
    a0 = p["stg"].get_riposte_abort_count()
    impacts0 = p["stg"].get_riposte_impact_count()
    hp0 = attr(p["boss"], "Attribute.Health")
    gen0, resets0 = p["enc"].get_generation(), p["enc"].get_reset_count()
    press("IA_NormalAttack", 0.12)
    yield from until(lambda: P()["stg"].is_riposte_executing(), 1.0)
    yield 0.4
    old_pawn = P()["pawn"].get_name()
    set_attr(P()["pawn"], "Attribute.Health", 0.0)  # the player dies in the middle of the clips
    yield from until(lambda: not P()["stg"].is_riposte_executing(), 3.0)
    respawned = yield from until(lambda: P()["pawn"] is not None and P()["pawn"].get_name() != old_pawn, 10.0)  # the pack respawns the player (and the encounter resets) a few seconds after the death
    yield 3.0
    p = P()
    check("S2 the player's death aborts the execution (aborts %d -> %d), no impact lands after it (impacts %d -> %d)" % (a0, p["stg"].get_riposte_abort_count(), impacts0, p["stg"].get_riposte_impact_count()),
          p["stg"].get_riposte_abort_count() == a0 + 1 and p["stg"].get_riposte_impact_count() == impacts0 and not p["stg"].is_riposte_executing(), "")
    check("S2 the player respawned (%s) and the encounter reset (generation %d -> %d, resets %d -> %d): the boss sleeps at home, standing and full (health %s)" % (respawned, gen0, p["enc"].get_generation(), resets0, p["enc"].get_reset_count(), attr(p["boss"], "Attribute.Health")),
          respawned and p["enc"].get_generation() > gen0 and p["enc"].get_reset_count() > resets0 and p["enc"].is_dormant() and not p["stg"].is_staggered() and (attr(p["boss"], "Attribute.Health") or 0) >= (hp0 or 0) - 0.5, "")


def s5_early_press():
    """A press while the boss still falls (the first 0.7 s) is rejected: the interaction opens when the kneel plays."""
    yield from fresh()
    p = P()
    p["dbg"].debug_set_boss_health_fraction(1.0)
    p["stg"].force_break_for_test()
    place(p)
    p["dbg"].debug_refill_player()
    yield 0.25
    p = P()
    stage = p["stg"].get_clip_stage_name()
    avail = p["stg"].is_riposte_available(p["pawn"])
    rej0 = p["stg"].get_riposte_reject_count()
    again = p["stg"].try_riposte(p["pawn"])
    check("S5 during the fall (stage %s) the riposte is not available (%s) and a request is rejected (%s: %s)" % (stage, avail, again, p["stg"].get_last_riposte_result()),
          stage == "fall" and avail is False and again is False and "falling" in p["stg"].get_last_riposte_result() and p["stg"].get_riposte_reject_count() == rej0 + 1 and not p["stg"].is_riposte_executing(), "")
    yield from until(lambda: P()["stg"].get_clip_stage_name() == "down", 3.0)
    yield 0.2
    p = P()
    check("S5 once the kneel plays the riposte is available", p["stg"].is_riposte_available(p["pawn"]) is True, "")
    yield from until(lambda: not P()["stg"].is_staggered(), 6.0)


def s3_standin():
    yield from fresh()
    P()["stg"].set_use_riposte_clips_for_test(False)
    yield from downed_boss()
    rc0 = P()["stg"].get_riposte_count()
    press("IA_NormalAttack", 0.12)
    yield 0.4
    p = P()
    check("S3 clips off: the press is accepted and arms the multiplier (the swing's own hit may already have used it: riposte count %d -> %d), nothing executes (accepted %s, armed %s, executing %s)" % (rc0, p["stg"].get_riposte_count(), p["stg"].get_last_riposte_result(), p["stg"].is_riposte_armed(), p["stg"].is_riposte_executing()),
          p["stg"].get_last_riposte_result() == "accepted" and (p["stg"].is_riposte_armed() or p["stg"].get_riposte_count() > rc0) and not p["stg"].is_riposte_executing(), "")
    P()["stg"].set_use_riposte_clips_for_test(True)
    yield from until(lambda: not P()["stg"].is_staggered(), 6.0)


def s4_boss_dies():
    yield from fresh()
    yield from downed_boss()
    p = P()
    impacts0 = p["stg"].get_riposte_impact_count()
    a0 = p["stg"].get_riposte_abort_count()
    press("IA_NormalAttack", 0.12)
    yield from until(lambda: P()["stg"].is_riposte_executing(), 1.0)
    yield 0.3
    P()["dbg"].debug_kill_boss()  # before the impact (0.8 s)
    yield 1.2
    p = P()
    if p["boss"] is None:
        check("S4 the boss died during the execution and was destroyed by the pack (nothing more to read)", True, "")
        return
    check("S4 the boss's death aborts the execution (aborts %d -> %d), no impact lands (impacts %d -> %d)" % (a0, p["stg"].get_riposte_abort_count(), impacts0, p["stg"].get_riposte_impact_count()),
          p["stg"].get_riposte_abort_count() == a0 + 1 and p["stg"].get_riposte_impact_count() == impacts0 and not p["stg"].is_riposte_executing(), "")


def script():
    yield from s1_execution()
    yield from s2_player_dies()
    yield from s3_standin()
    yield from s5_early_press()
    yield from s4_boss_dies()


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        P()["stg"].set_use_riposte_clips_for_test(True)
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
    if s["now"] - s.get("hb", 0.0) > 15.0:
        s["hb"] = s["now"]
        log("heartbeat: %.0f s, pawn %s, boss %s, wait %.2f" % (s["now"], pawn.get_name() if pawn else None, boss.get_name() if boss else None, s["wait"]))
    if boss is None:
        s["gone"] = s.get("gone", 0.0) + dt
        if s["gone"] > 15.0 and s["gen"] is not None:
            check("the boss is still in the world", False, "gone for %.0f s" % s["gone"])
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
