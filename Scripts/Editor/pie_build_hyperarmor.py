"""
Gate 3, M14: the hyperarmor windows AUTHORED into the weapon attack table (DA_WeaponAttacks, Scripts/Editor/set_weapon_windows.py), with the real build and real swings against the held boss (log prefix [BuildArmor]).
pie_hyperarmor.py proves the mechanism with test windows on the sword; this driver proves the data: the Strength build (rpg.Build Strength: the claymore) carries the pack's hit stun immunity (Status.HitStunImmune and the
swing tracker's flag) inside the window of the row of its swing and nowhere else.
  Windows (seconds of the swing's montage): Strong and JumpHeavy 0.352 to 0.618 (Ability_E_Anim_Montage, one montage for both), Charged 0.423 to 1.005 (ChargedAttack_Montage).
  H1 setup: Strength equipped, the boss held awake, the rows of the swing tracker's table carry the windows (read from its last swing line).
  H2 strong, H3 jump heavy, H4 charged: one swing, the tag and the flag on for every sample inside the window (0.05 s inside each edge), off before and after it, nothing lingers after the swing; and the hit of the swing lands while the tag is on.
  H5 a hit through the damage resolver inside the window still takes its 10 health (the immunity is not invulnerability), the same hit before the window too.
  H6 negative controls: the claymore's light and jump light have no window (a swing must have happened); the Starter sword's jump heavy (rpg.Build Starter) has none either.
Needs the warm-up of RunDrivers.ps1 (no_throttle.py, legend_off.py, build_off.py, pie_debug_overlay.py). Ends with RESULT n/m passed; rpg.Build is cleared at the end.
"""
import math
import unreal

log = lambda m: unreal.log("[BuildArmor] " + m)
IA = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
JUMP_KEY = "Gamepad_FaceButton_Bottom"
results = []
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None, "press_until": 0.0, "action": "IA_StrongAttack", "samples": None, "hit_id": 9000, "nopawn": 0.0}
handle = None
STYLE = {"Starter": "SwordCombatStyle", "Strength": "ClaymoreCombatStyle"}
STRONG_WIN = (0.352, 0.618)
CHARGED_WIN = (0.423, 1.005)
EDGE = 0.05  # samples this close to an edge of the window are not judged (a frame of the montage position against the effect)


def check(name, ok, detail=""):
    results.append(bool(ok))
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    if actor is None:
        return None
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def has_tag(actor, tag):
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    try:
        return bool(actor.call_method("HasMatchingGameplayTag", args=(t,)))
    except Exception:
        return None


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


def actors():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return w, pc, pawn, boss


def P():
    w, pc, pawn, boss = actors()
    return {"w": w, "pc": pc, "pawn": pawn, "boss": boss, "enc": comp(boss, "RPGBossEncounter"), "tr": comp(boss, "RPGAttackTracker"), "dbg": comp(boss, "RPGCombatDebug"),
            "res": comp(boss, "RPGDamageResolver"), "swing": comp(pawn, "RPGSwingTracker"), "intake": comp(pawn, "RPGHitIntake"), "ld": comp(pawn, "RPGBuildLoadout")}


def console(cmd):
    try:
        w = world()
        if w is None:
            w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        unreal.SystemLibrary.execute_console_command(w, cmd)
    except Exception as e:
        log("console command '%s' failed: %s" % (cmd, e))


def place(p, dist=110.0):
    boss, pawn = p["boss"], p["pawn"]
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw)
    q = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(q, bl).yaw
    pawn.set_actor_location_and_rotation(q, unreal.Rotator(0, 0, look), False, True)
    p["pc"].set_control_rotation(unreal.Rotator(0, 0, look))
    p["dbg"].debug_set_boss_health_fraction(1.0)  # a dead boss locks the player's input (victory): every swing starts with a full boss


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


def current_montage():
    p = P()
    mesh = p["pawn"].get_components_by_class(unreal.SkeletalMeshComponent)[0]
    inst = mesh.get_anim_instance()
    m = inst.get_current_active_montage() if inst else None
    return (m.get_name(), inst.montage_get_position(m)) if m else (None, None)


def sample_tick():
    """Every frame while S['samples'] is a list: time, montage name and position, the tag, the component's flag, the number of boss hits of the intake."""
    p = P()
    name, pos = current_montage()
    S["samples"].append((S["now"], name, pos, has_tag(p["pawn"], "Status.HitStunImmune"), p["swing"].is_hyper_armor_active(), p["intake"].get_boss_hit_count()))


def to_dormant():
    P()["enc"].reset_for_test()
    yield 1.0


def equip(build, timeout=10.0):
    ld = P()["ld"]
    if ld is None:
        return "no loadout", False
    answer = ld.set_build_for_test(build)
    ok = yield from until(lambda: P()["ld"] is not None and P()["ld"].get_actual_style_name() == STYLE[build] and P()["ld"].get_state_name() == "Idle", timeout)
    yield 0.5
    return answer, ok


def fresh_fight():
    """The boss awake and held, the player in combat mode, every counter at zero."""
    p = P()
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
    p["swing"].reset_counters()
    p["swing"].clear_cost_overrides()
    p["intake"].reset_counters()


def swing_and_sample(action, seconds, jump=False, duration=2.4):
    """In front of the boss with full resources, swings (after a jump when asked) and returns (samples, attack swings started)."""
    p = P()
    place(p)
    p["dbg"].debug_refill_player()
    yield 0.7
    n0 = P()["swing"].get_attack_swing_count()
    S["samples"] = []
    if jump:
        unreal.RPGInputTestUtils.set_key_down(P()["pc"], JUMP_KEY, True)
        yield 0.12
        unreal.RPGInputTestUtils.set_key_down(P()["pc"], JUMP_KEY, False)
        yield 0.2
    press(action, seconds)
    yield duration
    samples = S["samples"]
    S["samples"] = None
    return samples, P()["swing"].get_attack_swing_count() - n0


def judge(name, samples, swings, window, max_swings=1):
    attack = [s for s in samples if s[1] and s[2] is not None]
    inside = [s for s in attack if window[0] + EDGE <= s[2] <= window[1] - EDGE]
    before = [s for s in attack if s[2] < window[0] - EDGE]
    after = [s for s in attack if s[2] > window[1] + EDGE]
    tail = [s for s in samples if s[1] is None]
    check("%s: %d swing(s), the tag and the flag are on for every sample inside %.3f to %.3f (%d samples)" % (name, swings, window[0], window[1], len(inside)), 1 <= swings <= max_swings and len(inside) >= 3 and all(s[3] is True and s[4] is True for s in inside),
          "swings %d %s" % (swings, [(round(s[2], 2), s[3], s[4]) for s in inside if not (s[3] and s[4])][:5]))
    check("%s: off before the window (%d samples) and after it (%d samples)" % (name, len(before), len(after)), len(before) >= 2 and len(after) >= 3 and all(s[3] is False for s in before + after),
          "on outside: %s" % [(round(s[2], 2)) for s in before + after if s[3]][:5])
    check("%s: nothing lingers after the swing (%d samples without a montage)" % (name, len(tail)), len(tail) >= 3 and all(s[3] is False and s[4] is False for s in tail), "")
    landed = [s for i, s in enumerate(samples) if i > 0 and s[5] > samples[i - 1][5]]
    check("%s: the hit of the swing landed (%d) while the tag was on" % (name, len(landed)), len(landed) >= 1 and all(s[3] is True for s in landed), "%s" % [(round(s[2], 2) if s[2] is not None else None, s[3]) for s in landed])


def judge_none(name, samples, swings):
    attack = [s for s in samples if s[1] and s[2] is not None]
    check("%s: a swing happened (%d swings, %d montage samples) and the tag is never on (%d samples)" % (name, swings, len(attack), len(samples)), swings == 1 and len(attack) >= 5 and all(s[3] is False and s[4] is False for s in samples),
          "%s" % [(round(s[2], 2) if s[2] is not None else None, s[3]) for s in samples if s[3]][:4])


def hit_player():
    """One hit through the damage resolver (the path of the boss's own moves): (outcome, health taken)."""
    p = P()
    S["hit_id"] += 1
    h0 = attr(p["pawn"], "Attribute.Health")
    out = p["res"].resolve_for_test("H11", S["hit_id"], 10.0, "buildarmor")
    h1 = attr(P()["pawn"], "Attribute.Health")
    return str(out), (h0 - h1) if (h0 is not None and h1 is not None) else None


def probe_at(name, action, position, expect_open):
    """Strong swing, waits until the montage is at `position`, reads the tag and sends a hit through the damage resolver: it takes its 10 health either way."""
    p = P()
    place(p)
    p["dbg"].debug_refill_player()
    yield 0.7
    press(action, 0.12)
    reached = yield from until(lambda: (current_montage()[1] or -1.0) >= position, 2.5)
    mname, pos = current_montage()
    tag = has_tag(P()["pawn"], "Status.HitStunImmune")
    out, taken = hit_player()
    check("%s: at montage position %.2f the tag is %s and a hit still takes 10 health (outcome %s, taken %s)" % (name, position, "on" if expect_open else "off", out, taken),
          reached and out == "Accepted" and taken is not None and abs(taken - 10.0) < 0.01 and tag is expect_open, "montage %s position %s tag %s" % (mname, pos, tag))
    yield 2.0


def script():
    # H1 Strength equipped, the boss held awake
    yield from to_dormant()
    answer, ok = yield from equip("Strength")
    ld = P()["ld"]
    check("H1 the Strength build is equipped (%s, style %s)" % (answer, ld.get_actual_style_name() if ld else None), ok)
    yield from fresh_fight()
    # the window of the row is what the swing tracker reads: the swing line of the first strong swing shows it
    samples, swings = yield from swing_and_sample("IA_StrongAttack", 0.12)
    line = P()["swing"].get_last_swing_text()
    check("H1 the swing tracker's row for the strong swing carries the window (%s)" % line[:160], "hyperarmor 0.35 to 0.62" in line or "hyperarmor 0.352 to 0.618" in line, "")
    judge("H2 strong", samples, swings, STRONG_WIN)
    samples, swings = yield from swing_and_sample("IA_StrongAttack", 0.12, jump=True)
    judge("H3 jump heavy", samples, swings, STRONG_WIN)
    # the pack's charged attack is counted as two swings by the tracker, 1.6 s apart, whatever the hold time (pie_builds.py B3 sees it too: the montage restarts at its charge section); both passes carry the window, so up to two swings are accepted and the sampling runs until the montage is over
    samples, swings = yield from swing_and_sample("IA_ChargedAttack", 1.0, duration=5.6)
    judge("H4 charged", samples, swings, CHARGED_WIN, max_swings=2)
    # H5 the immunity is not invulnerability: a hit inside the window and before it takes its health
    yield from probe_at("H5 strong, inside the window", "IA_StrongAttack", 0.5, True)
    yield from probe_at("H5 strong, before the window", "IA_StrongAttack", 0.2, False)
    # H6 negative controls
    samples, swings = yield from swing_and_sample("IA_NormalAttack", 0.12)
    judge_none("H6 claymore light", samples, swings)
    samples, swings = yield from swing_and_sample("IA_NormalAttack", 0.12, jump=True)
    judge_none("H6 claymore jump light", samples, swings)
    # the Starter sword: no window on its jump heavy
    yield from to_dormant()
    answer, ok = yield from equip("Starter")
    yield from fresh_fight()
    check("H6 the Starter sword is back (%s)" % P()["ld"].get_actual_style_name(), ok and P()["ld"].get_actual_style_name() == STYLE["Starter"])
    samples, swings = yield from swing_and_sample("IA_StrongAttack", 0.12, jump=True)
    judge_none("H6 starter sword jump heavy", samples, swings)
    P()["ld"].set_build_for_test("")


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        console('rpg.Build ""')
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
            console('rpg.Build ""')
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w, pc, pawn, boss = actors()
    if s["now"] - s.get("hb", 0.0) > 15.0:
        s["hb"] = s["now"]
        log("heartbeat: %.0f s, pawn %s, boss %s, wait %.2f" % (s["now"], pawn.get_name() if pawn else None, boss.get_name() if boss else None, s["wait"]))
    if pawn is None or boss is None:
        s["nopawn"] += dt
        if s["nopawn"] > 40.0 and s["gen"] is not None:
            check("the player and the boss exist (missing for 40 s)", False)
            finish()
        return
    s["nopawn"] = 0.0
    if s["now"] < s["press_until"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(IA + s["action"]), unreal.Vector(1, 0, 0))
    if s["samples"] is not None:
        sample_tick()
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
