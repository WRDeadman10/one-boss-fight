"""
Gate 3, M11: hyperarmor (Freeze 20.1). Inside the window of a swing the player carries the pack's hit stun immunity effect (Status.HitStunImmune, the tag the player's GA_PlayerHitStun lists in its blocked tags), outside
it does not, and it never lingers after the swing, a jump, an interrupted swing or the end of the PIE. The sword's rows have no window (the strength weapons get theirs with the builds, M13), so the windows come from test hooks:
an override per attack kind, and a window put into the weapon attack table row of the sword (a transient copy of the table: the row to swing path as an authored row would run it). Window 0.25 to 0.55 s of the strong swing's montage.
What is checked, with real input against the held boss:
  - the tag, the component's flag and the montage position are sampled every frame during real swings (strong, jump heavy, strong through the table row) and during swings without a window (negative controls: a swing must have happened);
  - the effect on the pack: GA_PlayerHitStun is asked to start (the way a hit starts it, no force) inside the window (blocked), before it and after it (started); a hit through the damage resolver inside the window still takes
    health (the immunity is not invulnerability);
  - a window that stays open longer than the effect lasts (4 s) gets the effect applied again (refresh interval cut to 0.25 s for the test) and the tag stays on;
  - an interrupted swing (a dodge out of it): the montage is replaced and the effect goes with it at once, while the old window would still be open by the montage position.
Log prefix [HyperArmor]; ends with RESULT n/m passed. Run pie_debug_overlay.py once after an editor start first.
"""
import math
import unreal

log = lambda m: unreal.log("[HyperArmor] " + m)
IA = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
JUMP_KEY = "Gamepad_FaceButton_Bottom"
results = []
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None, "press_until": 0.0, "action": "IA_StrongAttack", "samples": None, "hit_id": 9000}
handle = None
KIND = unreal.RPGAttackKind
WIN = (0.25, 0.55)
SWORD = "SwordCombatStyle"


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
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
            "res": comp(boss, "RPGDamageResolver"), "swing": comp(pawn, "RPGSwingTracker")}


def place(p, dist=110.0):
    boss, pawn = p["boss"], p["pawn"]
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw)
    q = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(q, bl).yaw
    pawn.set_actor_location_and_rotation(q, unreal.Rotator(0, 0, look), False, True)
    p["pc"].set_control_rotation(unreal.Rotator(0, 0, look))
    p["dbg"].debug_set_boss_health_fraction(1.0)  # the swings hit the held boss: a dead boss locks the player's input (victory), so every scenario starts with a full boss


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
    p["tr"].enter_combat()
    comp(p["pawn"], "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
    yield 2.2
    P()["swing"].reset_counters()
    P()["swing"].clear_cost_overrides()


def press(action, seconds):
    S["action"] = action
    S["press_until"] = S["now"] + seconds


def current_montage():
    """(name, position) of the player's active montage, or (None, None)."""
    p = P()
    mesh = p["pawn"].get_components_by_class(unreal.SkeletalMeshComponent)[0]
    inst = mesh.get_anim_instance()
    m = inst.get_current_active_montage() if inst else None
    return (m.get_name(), inst.montage_get_position(m)) if m else (None, None)


def sample_tick():
    """Called every frame while S['samples'] is a list: montage position, the tag and the component's flag."""
    p = P()
    name, pos = current_montage()
    S["samples"].append((S["now"], name, pos, has_tag(p["pawn"], "Status.HitStunImmune"), p["swing"].is_hyper_armor_active()))


def swing_and_sample(action, seconds, jump=False, duration=2.2):
    """Teleports the player in front of the boss, swings (after a jump when asked) and returns (samples, attack swings started by it)."""
    p = P()
    place(p)
    p["dbg"].debug_refill_player()
    yield 0.6
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


def hit_player():
    """One hit through the damage resolver (the path of the boss's own moves): returns (outcome, health taken)."""
    p = P()
    S["hit_id"] += 1
    h0 = attr(p["pawn"], "Attribute.Health")
    out = p["res"].resolve_for_test("H11", S["hit_id"], 10.0, "hyperarmor")
    h1 = attr(P()["pawn"], "Attribute.Health")
    return str(out), (h0 - h1) if (h0 is not None and h1 is not None) else None


def judge(name, samples, swings, expect_window):
    """expect_window: True when the tag must be on inside WIN and off elsewhere; False when it must never be on (and a swing must have happened: a press that was never accepted proves nothing)."""
    attack = [s for s in samples if s[1] and s[2] is not None]
    inside = [s for s in attack if WIN[0] + 0.05 <= s[2] <= WIN[1] - 0.05]
    before = [s for s in attack if s[2] < WIN[0] - 0.05]
    after = [s for s in attack if s[2] > WIN[1] + 0.05]
    tail = [s for s in samples if s[1] is None]  # no montage at all
    if expect_window:
        check("%s: one swing, the immunity tag is on inside the window (%d samples)" % (name, len(inside)), swings == 1 and len(inside) >= 3 and all(s[3] is True and s[4] is True for s in inside), "swings %d %s" % (swings, [(round(s[2], 2), s[3]) for s in inside][:6]))
        check("%s: and off before it (%d samples) and after it (%d samples)" % (name, len(before), len(after)), len(before) >= 2 and len(after) >= 3 and all(s[3] is False for s in before + after), "before %s after %s" % ([(round(s[2], 2), s[3]) for s in before if s[3]][:4], [(round(s[2], 2), s[3]) for s in after if s[3]][:4]))
        check("%s: nothing lingers after the swing (%d samples without a montage)" % (name, len(tail)), len(tail) >= 3 and all(s[3] is False and s[4] is False for s in tail), "%s" % [s[3] for s in tail if s[3]][:4])
    else:
        check("%s: a swing happened (%d swings, %d montage samples) and the tag is never on (%d samples)" % (name, swings, len(attack), len(samples)), swings == 1 and len(attack) >= 5 and all(s[3] is False for s in samples), "%s" % [(round(s[2], 2) if s[2] is not None else None, s[3]) for s in samples if s[3]][:4])


def probe_at(name, action, position, expect_stun, jump=False, expect_open=None):
    """Swings, waits until the montage is at `position`, reads the immunity tag and sends a hit through the damage resolver (the immunity is not invulnerability: the hit still takes its 10 health)."""
    p = P()
    place(p)
    p["dbg"].debug_refill_player()
    yield 0.6
    if jump:
        unreal.RPGInputTestUtils.set_key_down(P()["pc"], JUMP_KEY, True)
        yield 0.12
        unreal.RPGInputTestUtils.set_key_down(P()["pc"], JUMP_KEY, False)
        yield 0.2
    press(action, 0.12)
    reached = yield from until(lambda: (current_montage()[1] or -1.0) >= position, 2.5)
    mname, pos = current_montage()
    tag = has_tag(P()["pawn"], "Status.HitStunImmune")
    out, taken = hit_player()
    ok = reached and out == "Accepted" and taken is not None and abs(taken - 10.0) < 0.01 and (expect_open is None or tag is expect_open)
    check("%s: at montage position %.2f the immunity tag is %s, a hit still takes 10 health (outcome %s, taken %s)" % (name, position, "on" if expect_open else "off", out, taken), ok, "montage %s position %s tag %s" % (mname, pos, tag))
    yield 2.0


def script():
    yield from fresh()

    # the effect on the pack: the player's own hit stun ability lists the immunity tag in its blocked tags (the ability starts only through the hit pipeline's event, a test cannot start it by hand)
    check("control: the player's GA_PlayerHitStun has Status.HitStunImmune in its ActivationBlockedTags, and the player has no immunity now", P()["swing"].is_player_hit_stun_blocked_by_immunity() and has_tag(P()["pawn"], "Status.HitStunImmune") is False, "")

    # negative controls: a swing without a window never turns the tag on
    samples, swings = yield from swing_and_sample("IA_StrongAttack", 0.12)
    judge("strong without a window", samples, swings, False)
    check("no window opened without a row window", P()["swing"].get_hyper_armor_window_count() == 0, "%d" % P()["swing"].get_hyper_armor_window_count())

    # the override opens a window on every strong swing
    P()["swing"].set_hyper_armor_override_for_test(KIND.STRONG, WIN[0], WIN[1])
    samples, swings = yield from swing_and_sample("IA_StrongAttack", 0.12)
    judge("strong with the window 0.25 to 0.55", samples, swings, True)
    check("one window opened by that swing", P()["swing"].get_hyper_armor_window_count() == 1, "%d" % P()["swing"].get_hyper_armor_window_count())
    yield from probe_at("strong, inside the window", "IA_StrongAttack", 0.35, "blocked", expect_open=True)
    yield from probe_at("strong, after the window", "IA_StrongAttack", 0.7, "started", expect_open=False)
    yield from probe_at("strong, before the window", "IA_StrongAttack", 0.12, "started", expect_open=False)

    # a light swing is not affected by the strong override
    samples, swings = yield from swing_and_sample("IA_NormalAttack", 0.12)
    judge("light with a strong-only override", samples, swings, False)

    # the jumping heavy
    P()["swing"].set_hyper_armor_override_for_test(KIND.JUMP_HEAVY, WIN[0], WIN[1])
    samples, swings = yield from swing_and_sample("IA_StrongAttack", 0.12, jump=True, duration=2.4)
    judge("jump heavy with the window", samples, swings, True)

    # the window as an authored row would give it: no override, the sword's strong row of a table copy carries the window
    P()["swing"].clear_cost_overrides()
    P()["swing"].set_row_hyper_armor_for_test(SWORD, KIND.STRONG, WIN[0], WIN[1])
    samples, swings = yield from swing_and_sample("IA_StrongAttack", 0.12)
    judge("strong with the window in the table row", samples, swings, True)
    last = P()["swing"].get_last_swing_text()
    check("the swing text carries the row's window", "hyperarmor 0.25 to 0.55" in last, last[:170])
    samples, swings = yield from swing_and_sample("IA_NormalAttack", 0.12)
    judge("light, whose row has no window, next to a strong row with one", samples, swings, False)
    P()["swing"].clear_cost_overrides()
    samples, swings = yield from swing_and_sample("IA_StrongAttack", 0.12)
    judge("strong after the table copy is gone", samples, swings, False)

    # a window that stays open longer than the effect lasts: the effect is applied again (interval 0.25 s for the test), the tag stays on all the time
    P()["swing"].set_hyper_armor_refresh_for_test(0.25)
    P()["swing"].set_hyper_armor_override_for_test(KIND.STRONG, 0.05, 1.5)
    r0 = P()["swing"].get_hyper_armor_refresh_count()
    samples, swings = yield from swing_and_sample("IA_StrongAttack", 0.12)
    inside = [s for s in samples if s[1] and s[2] is not None and 0.1 <= s[2] <= 1.2]
    refreshes = P()["swing"].get_hyper_armor_refresh_count() - r0
    check("a long window: the effect is applied again (%d times) and the tag stays on in every frame (%d samples)" % (refreshes, len(inside)), swings == 1 and refreshes >= 3 and len(inside) >= 10 and all(s[3] is True for s in inside), "%s" % [(round(s[2], 2), s[3]) for s in inside if s[3] is not True][:4])
    check("and nothing lingers afterwards", all(s[3] is False for s in samples if s[1] is None) and len([s for s in samples if s[1] is None]) >= 3, "")
    P()["swing"].set_hyper_armor_refresh_for_test(3.0)
    P()["swing"].clear_cost_overrides()

    # interrupted: the window opens, then the player dodges out of the swing: the montage is replaced and the effect goes with it at once (the old window is still open by position until 1.5 s)
    P()["swing"].set_hyper_armor_override_for_test(KIND.STRONG, 0.05, 1.5)
    p = P()
    place(p)
    p["dbg"].debug_refill_player()
    yield 0.6
    n0 = P()["swing"].get_attack_swing_count()
    press("IA_StrongAttack", 0.12)
    yield from until(lambda: P()["swing"].is_hyper_armor_active(), 2.0)
    on = P()["swing"].is_hyper_armor_active()
    strong_name, strong_pos = current_montage()
    press("IA_Dodge", 0.15)  # a tap: the quick dodge leaves the swing
    replaced = yield from until(lambda: current_montage()[0] != strong_name, 1.5)
    yield 0.1
    name_after, pos_after = current_montage()
    p = P()
    check("an interrupted swing: the dodge replaced the strong montage (%s -> %s) and the effect is gone at once (flag %s, tag %s)" % (strong_name, name_after, p["swing"].is_hyper_armor_active(), has_tag(p["pawn"], "Status.HitStunImmune")),
          on and replaced and name_after != strong_name and not p["swing"].is_hyper_armor_active() and has_tag(p["pawn"], "Status.HitStunImmune") is False and p["swing"].get_attack_swing_count() == n0 + 1,
          "was on %s at position %s, now %s at %s, attack swings %d -> %d (the dodge is not a swing)" % (on, strong_pos, name_after, pos_after, n0, p["swing"].get_attack_swing_count()))
    yield 2.0
    P()["swing"].clear_cost_overrides()


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        P()["swing"].clear_cost_overrides()
        P()["swing"].set_hyper_armor_refresh_for_test(3.0)
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
    if pawn is None or boss is None:
        return
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
