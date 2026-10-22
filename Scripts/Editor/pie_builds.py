"""
Gate 3, M13: the builds (RPGBuildLoadout). Real presses against the held boss (the player stands 110 cm in front of it); the player never gets a weapon through a property: only the console variable rpg.Build (through the loadout's
test hook, which sets the same variable) and the pack's own equip flow that the loadout calls (KI-083: no set_editor_property on components in PIE).
  B0 start: pawn, boss, loadout, wiring report of the pack names, the boss sleeps.  B1 no build chosen: nothing is called, the sword stays, the slot is never locked, not even in a fight (the guarantee that every older driver is unchanged).
  B2 Strength while the boss sleeps: ClaymoreCombatStyle, GA_Claymore_Melee_C instead of GA_Sword_Melee_C, BP_KwangSword_C in the slot, the HUD line.  B3 Strength numbers from the table (posture, stamina, bleed, records against health drops).
  B5 Dex (in combat mode, after B3): DualSwordCombatStyle, GA_DuaSword_Melee_C, BP_DualSteelSwords_C.  B6 Dex numbers: posture 6 / 10 / 14, stamina 10, bleed 20 per record, a combo, five records proc once.
  B7 deferral and lock: a choice made while the boss is awake is deferred (no pack call), the weapon slot is locked, a real quickslot press does not leave the build, after the reset the choice applies and the slot is free.
  B8 Starter returns the sword.  B9 console selectors: rpg.Build Dex, rpg.Build Banana (ignored, counted), rpg.Build "" (clears, calls nothing).
  B10 (last: the player dies) the choice survives a respawn: the new pawn's own loadout applies it again; then back to Starter.
Not here (needs the editor or art first): B4 hyperarmor from the authored rows (the windows are not authored yet, M13_BUILDS_PLAN.md 4.3), the F6/F7/F8 keys (not built), the chain stage numbers of the dex combo (not in the swing text yet).
CAPS below says which kinds of attack each weapon has (from g3_probe_montages.py); a kind the weapon does not have is skipped with a logged line. Log prefix [Builds]; ends with RESULT n/m passed. The warm-up of RunDrivers.ps1 (no_throttle.py, legend_off.py, build_off.py, pie_debug_overlay.py) must have run: the timings assume it. Run pie_debug_overlay.py once after an editor start first.
"""
import math
import unreal

log = lambda m: unreal.log("[Builds] " + m)
IA = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
JUMP_KEY = "Gamepad_FaceButton_Bottom"
results = []
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None, "press_until": 0.0, "action": "IA_NormalAttack", "hpw": None}
handle = None

STYLE = {"Starter": "SwordCombatStyle", "Strength": "ClaymoreCombatStyle", "Dex": "DualSwordCombatStyle"}
ABILITY = {"Starter": "GA_Sword_Melee_C", "Strength": "GA_Claymore_Melee_C", "Dex": "GA_DuaSword_Melee_C"}
ACTOR = {"Starter": "BP_ToughSword_C", "Strength": "BP_KwangSword_C", "Dex": "BP_DualSteelSwords_C"}
LINE = {"Starter": "Build: Starter (Sword)", "Strength": "Build: Strength (Claymore)", "Dex": "Build: Dex (Dual Swords)"}

# The posture damage and the stamina cost per swing of each (build, kind) as the weapon attack table's Freeze values give them (RPGWeaponAttackTable::FillDefaults; the stamina of a row of -1 keeps the pack's 15).
ROWS = {
    "Strength": {"Light": (18.0, 15.0), "Strong": (30.0, 35.0), "Charged": (38.0, 35.0), "JumpLight": (18.0, 15.0), "JumpHeavy": (38.0, 35.0)},
    "Dex": {"Light": (6.0, 10.0), "Strong": (10.0, 10.0), "Charged": (14.0, 10.0), "JumpLight": (6.0, 10.0), "JumpHeavy": (14.0, 10.0)},
}
BLEED = {"Strength": 0.0, "Dex": 20.0}
# Which kinds each weapon has (g3_probe_montages.py, 2026-10-22): the claymore shares the sword's strong, charged and falling montages; the dual swords have a strong pair and a falling attack but no charged montage.
CAPS = {
    "Strength": {"Light": True, "Strong": True, "Charged": True, "JumpLight": True, "JumpHeavy": True},
    "Dex": {"Light": True, "Strong": True, "Charged": False, "JumpLight": True, "JumpHeavy": True},
}
# kind -> (input action, seconds held, jump first)
ACTIONS = {
    "Light": ("IA_NormalAttack", 0.12, False),
    "Strong": ("IA_StrongAttack", 0.12, False),
    "Charged": ("IA_ChargedAttack", 1.6, False),
    "JumpLight": ("IA_NormalAttack", 0.12, True),
    "JumpHeavy": ("IA_StrongAttack", 0.12, True),
}
OK = {"Strength": False, "Dex": False}


def check(name, ok, detail=""):
    results.append(bool(ok))
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    if actor is None:
        return None
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def attr(actor, tag):
    c = comp(actor, "BP_AttributesComponent_C")
    if c is None:
        return None
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
    return {"w": w, "pc": pc, "pawn": pawn, "boss": boss, "enc": comp(boss, "RPGBossEncounter"), "tr": comp(boss, "RPGAttackTracker"), "dbg": comp(boss, "RPGCombatDebug"), "post": comp(boss, "RPGBossPosture"),
            "bleed": comp(boss, "RPGBossBleed"), "swing": comp(pawn, "RPGSwingTracker"), "intake": comp(pawn, "RPGHitIntake"), "ld": comp(pawn, "RPGBuildLoadout")}


def console(cmd):
    """A console command in the game world, or the editor world before the PIE starts: rpg.Build is process wide."""
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
    p["dbg"].debug_set_boss_health_fraction(1.0)  # the swings hit the held boss: a dead boss locks the player's input (victory), so every swing starts with a full boss


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


def player_idle():
    pawn = P()["pawn"]
    if pawn is None:
        return True
    inst = pawn.get_components_by_class(unreal.SkeletalMeshComponent)[0].get_anim_instance()
    return inst is None or inst.get_current_active_montage() is None


def ld_detail(ld):
    """What the loadout says about itself, for the detail of a check."""
    if ld is None:
        return "no loadout"
    return "style %s, state %s, line '%s', chosen %s (choice %s), calls %d, last: %s" % (ld.get_actual_style_name(), ld.get_state_name(), ld.get_build_line(), ld.get_chosen_build_name(), ld.has_choice(), ld.get_apply_attempt_count(), ld.get_last_result()[:260])


def dump_events(title):
    ld = P()["ld"]
    if ld is None:
        return
    for ln in ld.get_event_lines():
        log("%s loadout event: %s" % (title, ln[:300]))


def equip(build, timeout=8.0):
    """Sets the choice through the hook and waits until the player holds the build's style and the loadout is idle. Returns (the hook's answer, whether it worked)."""
    ld = P()["ld"]
    if ld is None:
        return "no loadout", False
    answer = ld.set_build_for_test(build)
    want = STYLE[build]
    ok = yield from until(lambda: P()["ld"] is not None and P()["ld"].get_actual_style_name() == want and P()["ld"].get_state_name() == "Idle", timeout)
    yield 0.4
    return answer, ok


def to_dormant():
    """The encounter reset: the boss sleeps at home, the weapon slot is unlocked by the loadout."""
    P()["enc"].reset_for_test()
    yield 1.0


def fresh_fight():
    """The boss awake and held, the player in combat mode with full stamina, every counter of the fight at zero."""
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
    if p["bleed"] is not None:
        p["bleed"].reset_bleed()


def measure(action, seconds, jump=False):
    """One real swing against the held boss: in front of it with a full pool and full stamina, pressed (after a jump when asked); waits for the hit and for the swing to end. Returns the numbers of that swing."""
    p = P()
    place(p)
    p["dbg"].debug_refill_player()
    yield 0.6  # the teleport leaves the player a moment in the air: a press then would be a jump attack
    p = P()
    p["post"].set_posture_for_test(100.0)
    if p["bleed"] is not None:
        p["bleed"].reset_bleed()
    n0 = p["swing"].get_attack_swing_count()
    h0 = p["intake"].get_boss_hit_count()
    hp0 = attr(p["boss"], "Attribute.Health")
    if jump:
        unreal.RPGInputTestUtils.set_key_down(p["pc"], JUMP_KEY, True)
        yield 0.12
        unreal.RPGInputTestUtils.set_key_down(P()["pc"], JUMP_KEY, False)
        yield 0.2
    before = attr(P()["pawn"], "Attribute.Stamina")
    S["hpw"] = {"last": attr(P()["boss"], "Attribute.Health"), "events": 0}
    press(action, seconds)
    yield from until(lambda: P()["swing"].get_attack_swing_count() > n0, 2.0)
    yield 0.4  # the pack's stamina regeneration has not started yet
    p = P()
    after = attr(p["pawn"], "Attribute.Stamina")
    text = p["swing"].get_last_swing_text()
    yield from until(lambda: P()["intake"].get_boss_hit_count() > h0, 3.5)
    yield from until(player_idle, 4.0)
    yield 0.3
    p = P()
    watch, S["hpw"] = S["hpw"], None
    return {"text": text, "drop": (before - after) if (before is not None and after is not None) else None, "rec": p["intake"].get_boss_hit_count() - h0, "events": watch["events"] if watch else -1,
            "post": p["post"].get_posture(), "bleed": p["bleed"].get_buildup() if p["bleed"] is not None else -1.0, "hp_lost": (hp0 - attr(p["boss"], "Attribute.Health")) if hp0 is not None and attr(p["boss"], "Attribute.Health") is not None else None,
            "record": p["intake"].get_last_record_text()}


def kind_checks(build, kind, r):
    """Six checks of one measured swing against the table's numbers; r is None when the build's weapon is not equipped (the checks then fail, so the count of the driver stays the same)."""
    posture, stamina = ROWS[build][kind]
    tag = "%s %s" % (build, kind)
    if r is None:
        for what in ("swing text", "hit landed", "stamina", "posture", "bleed", "records against health drops"):
            check("%s: %s (skipped: the weapon is not equipped)" % (tag, what), False)
        return
    t = r["text"]
    check("%s: the swing tracker saw weapon %s, kind %s%s" % (tag, STYLE[build], kind, " (started airborne)" if kind.startswith("Jump") else ""),
          ("weapon %s," % STYLE[build]) in t and ("kind %s," % kind) in t and (kind.startswith("Jump") == ("started airborne" in t)), t[:170])
    check("%s: the hit landed (%d intake record(s))" % (tag, r["rec"]), r["rec"] >= 1, r["record"][:150])
    drop = r["drop"]
    check("%s: stamina drop %.1f (expect %.1f)" % (tag, drop if drop is not None else -1.0, stamina), drop is not None and abs(drop - stamina) <= 0.6, t[:150])
    expect_post = posture * max(r["rec"], 0)
    check("%s: posture pool 100 -> %.1f (expect -%.0f for %d record(s))" % (tag, r["post"], expect_post, r["rec"]), r["rec"] >= 1 and abs((100.0 - r["post"]) - expect_post) <= 0.8, r["record"][:150])
    expect_bleed = BLEED[build] * max(r["rec"], 0)
    check("%s: bleed buildup %.1f (expect %.1f)" % (tag, r["bleed"], expect_bleed), r["rec"] >= 1 and abs(r["bleed"] - expect_bleed) < 0.01, "")
    check("%s: records (%d) equal the boss's health drops (%d)" % (tag, r["rec"], r["events"]), r["rec"] >= 1 and r["rec"] == r["events"], "two blades in one frame would show here (risk R4)")
    if r["rec"] >= 1 and r["hp_lost"] is not None:
        log("INFO hp per hit %s %s: %.1f over %d record(s) = %.1f each" % (build, kind, r["hp_lost"], r["rec"], r["hp_lost"] / r["rec"]))


def measure_kinds(build):
    for kind in ("Light", "Strong", "Charged", "JumpLight", "JumpHeavy"):
        if not CAPS[build][kind]:
            log("SKIP %s %s: the weapon has no such montage (CAPS)" % (build, kind))
            continue
        if not OK[build]:
            kind_checks(build, kind, None)
            continue
        action, seconds, jump = ACTIONS[kind]
        r = yield from measure(action, seconds, jump)
        kind_checks(build, kind, r)
        yield 0.5


# ---- scenarios -------------------------------------------------------------------------------------------------------------------------------------------------------------
def b0_start():
    p = P()
    p["enc"].reset_for_test()
    yield 1.0
    p = P()
    ld = p["ld"]
    check("B0 the pawn, the boss, the hit intake and the loadout exist", p["pawn"] is not None and p["boss"] is not None and p["intake"] is not None and p["intake"].is_hit_intake_bound() and ld is not None, "")
    check("B0 every pack name the loadout calls was found on the live pack classes (%s)" % ld.get_wiring_report(), ld.get_wiring_report() == "ok", "")
    check("B0 the boss sleeps", p["enc"].is_dormant(), "")


def b1_no_choice():
    ld = P()["ld"]
    ld.reset_counters_for_test()
    yield 3.0
    p = P()
    ld = p["ld"]
    check("B1 no build chosen: rpg.Build is empty, no choice, state Idle (%s)" % ld.get_state_name(), (not ld.has_choice()) and ld.get_state_name() == "Idle" and ld.get_chosen_build_name() == "Starter", ld_detail(ld))
    check("B1 nothing was called in the pack (calls %d, deferred %d, locks %d)" % (ld.get_apply_attempt_count(), ld.get_deferred_count(), ld.get_lock_count()), ld.get_apply_attempt_count() == 0 and ld.get_deferred_count() == 0 and ld.get_lock_count() == 0, "")
    check("B1 the player holds the pack's sword: SwordCombatStyle, Starter, GA_Sword_Melee_C", ld.get_actual_style_name() == "SwordCombatStyle" and ld.get_build_name() == "Starter" and ld.has_weapon_ability_for_test("GA_Sword_Melee_C"), ld_detail(ld))
    check("B1 the HUD line says the sword (%s)" % ld.get_build_line(), ld.get_build_line() == LINE["Starter"], "")
    # an awake boss changes nothing without a choice: the slot is never locked and nothing is called (every older driver wakes the boss)
    p["enc"].wake()
    p["enc"].hold_for_test(True)
    yield 1.5
    ld = P()["ld"]
    check("B1 the boss is awake and still no lock, no call (locked %s, lock count %d, calls %d)" % (ld.is_weapon_slot_locked(), ld.get_lock_count(), ld.get_apply_attempt_count()), (not ld.is_weapon_slot_locked()) and ld.get_lock_count() == 0 and ld.get_apply_attempt_count() == 0, "")
    yield from to_dormant()


def b2_strength_equip():
    yield from to_dormant()
    ld = P()["ld"]
    ld.reset_counters_for_test()
    combat = ld.is_combat_enabled()
    answer, ok = yield from equip("Strength")
    p = P()
    ld = p["ld"]
    OK["Strength"] = ok and ld.get_actual_style_name() == STYLE["Strength"]
    d = ld_detail(ld)
    check("B2 Strength while the boss sleeps is Accepted (%s)" % answer, answer == "Accepted", d)
    check("B2 within 8 s the player holds ClaymoreCombatStyle and the loadout is idle (combat mode was %s; state %s)" % (combat, ld.get_state_name()), OK["Strength"], d)
    check("B2 the claymore's ability is granted and the sword's is gone", ld.has_weapon_ability_for_test(ABILITY["Strength"]) and not ld.has_weapon_ability_for_test(ABILITY["Starter"]), "")
    check("B2 the weapon actor in the slot is BP_KwangSword_C (%s)" % ld.get_equipped_actor_class_name(), ld.get_equipped_actor_class_name() == ACTOR["Strength"], "")
    check("B2 the HUD line says Strength (%s)" % ld.get_build_line(), ld.get_build_line() == LINE["Strength"] and ld.get_build_name() == "Strength", "")
    check("B2 one request, one success, no failure (calls %d, successes %d, failures %d)" % (ld.get_apply_attempt_count(), ld.get_apply_success_count(), ld.get_apply_failure_count()),
          ld.get_apply_attempt_count() >= 1 and ld.get_apply_success_count() == 1 and ld.get_apply_failure_count() == 0, d)
    check("B2 the boss sleeps, so the slot was never locked, and the hit intake is still bound", p["intake"].is_hit_intake_bound() and ld.get_lock_count() == 0 and not ld.is_weapon_slot_locked(), "")
    dump_events("B2")


def b3_strength_numbers():
    yield from fresh_fight()
    yield from measure_kinds("Strength")


def b5_dex_equip():
    yield from to_dormant()
    ld = P()["ld"]
    ld.reset_counters_for_test()
    combat = ld.is_combat_enabled()
    answer, ok = yield from equip("Dex")
    p = P()
    ld = p["ld"]
    OK["Dex"] = ok and ld.get_actual_style_name() == STYLE["Dex"]
    d = ld_detail(ld)
    check("B5 Dex while the boss sleeps is Accepted (%s)" % answer, answer == "Accepted", d)
    check("B5 within 8 s the player holds DualSwordCombatStyle and the loadout is idle (combat mode was %s; state %s)" % (combat, ld.get_state_name()), OK["Dex"], d)
    check("B5 the dual swords' ability is granted and the claymore's is gone", ld.has_weapon_ability_for_test(ABILITY["Dex"]) and not ld.has_weapon_ability_for_test(ABILITY["Strength"]), "")
    check("B5 the weapon actor in the slot is BP_DualSteelSwords_C (%s)" % ld.get_equipped_actor_class_name(), ld.get_equipped_actor_class_name() == ACTOR["Dex"], "")
    check("B5 the HUD line says Dex (%s)" % ld.get_build_line(), ld.get_build_line() == LINE["Dex"] and ld.get_build_name() == "Dex", "")
    check("B5 the intake is still bound and the swing tracker is on the pawn", p["intake"].is_hit_intake_bound() and p["swing"] is not None, "")
    dump_events("B5")


def b6_dex_numbers():
    yield from fresh_fight()
    yield from measure_kinds("Dex")
    # a combo of three taps: one swing per montage, every swing a Light swing of the dual swords
    if OK["Dex"]:
        p = P()
        place(p)
        p["dbg"].debug_refill_player()
        yield 0.6
        P()["swing"].reset_counters()
        for _ in range(3):
            press("IA_NormalAttack", 0.1)
            yield 0.5
        yield from until(player_idle, 3.5)
        sw = P()["swing"]
        lines = list(sw.get_swing_lines())
        names = [ln.split("montage ")[1].split(",")[0] if "montage " in ln else "?" for ln in lines]
        n = sw.get_attack_swing_count()
        log("INFO dex combo montages: %s" % ", ".join(names))
        check("B6 a combo of three taps: %d swings, each a Light swing of the dual swords with its own montage (%s)" % (n, ", ".join(names)), n >= 2 and len(set(names)) == n and all(("kind Light" in ln and "weapon DualSwordCombatStyle" in ln) for ln in lines), "; ".join(l[:70] for l in lines))
        check("B6 the combo paid 10 stamina per swing: extra -5 each (total %.1f for %d swings)" % (sw.get_stamina_extra_total(), n), abs(sw.get_stamina_extra_total() - (-5.0 * n)) < 0.01, "")
    else:
        check("B6 a combo of three taps (skipped: the dual swords are not equipped)", False)
        check("B6 the combo paid 10 stamina per swing (skipped: the dual swords are not equipped)", False)
    # five records proc the bleed once (threshold 100, then 120); the dual swords may record two hits per swing, so the swings are counted by records
    if OK["Dex"]:
        yield from fresh_fight()
        P()["bleed"].reset_bleed()  # the buildup of the swings above must not count (the proc counter is NOT cleared by a reset: its value now is the baseline)
        yield 0.2
        procs0 = P()["bleed"].get_proc_count()
        swings = 0
        while P()["intake"].get_boss_hit_count() < 5 and swings < 14:
            p = P()
            place(p)
            p["dbg"].debug_refill_player()
            p["post"].set_posture_for_test(100.0)
            yield 0.6
            press("IA_NormalAttack", 0.12)
            yield 0.8
            yield from until(player_idle, 4.0)
            yield 0.3
            swings += 1
        p = P()
        records = p["intake"].get_boss_hit_count()
        procs = p["bleed"].get_proc_count() - procs0
        check("B6 %d records in %d swings proc the bleed once (procs %d, buildup %.1f, threshold %.1f)" % (records, swings, procs, p["bleed"].get_buildup(), p["bleed"].get_threshold()), 5 <= records <= 10 and procs == 1, "")
        check("B6 the proc took 10.5 percent of 500 health: %.1f" % p["bleed"].get_last_proc_damage(), abs(p["bleed"].get_last_proc_damage() - 52.5) < 0.6, "")
        check("B6 the threshold rose to 120 after the proc and the buildup is below it (threshold %.1f, buildup %.1f)" % (p["bleed"].get_threshold(), p["bleed"].get_buildup()), abs(p["bleed"].get_threshold() - 120.0) < 0.01 and 0.0 <= p["bleed"].get_buildup() < 120.0, "")
    else:
        for what in ("five records proc once", "the proc took 10.5 percent", "the buildup after the proc"):
            check("B6 %s (skipped: the dual swords are not equipped)" % what, False)


def b7_defer_and_lock():
    # CONTROL first: with the boss asleep the slot is free and the same press must change the weapon, or a press that never reaches the pack would make the locked press below pass for nothing.
    yield from to_dormant()
    yield from until(lambda: not P()["ld"].is_weapon_slot_locked(), 3.0)
    style0 = P()["ld"].get_actual_style_name()
    press("IA_QuickSlotRight", 0.15)
    # the pack cycles to the staff at once; the loadout brings the build back as soon as the equip clip is over (the boss sleeps): the style is watched for 3 s, any other style counts
    control_style = style0
    for _ in range(30):
        yield 0.1
        now_style = P()["ld"].get_actual_style_name()
        if now_style != style0:
            control_style = now_style
            break
    control_changed = control_style != style0
    log("INFO B7 control: an unlocked IA_QuickSlotRight press changed the style %s -> %s" % (style0, control_style))
    if control_changed:
        yield from equip("Dex")
    # the build is Dex (B5); the boss is awake and held. The counters start before the fight so that the lock the loadout puts on when the boss wakes is counted.
    P()["ld"].reset_counters_for_test()
    yield from fresh_fight()
    locked = yield from until(lambda: P()["ld"].is_weapon_slot_locked(), 3.0)
    ld = P()["ld"]
    check("B7 the boss is awake: the pack reports the weapon slot disabled (lock count %d, breaches %d)" % (ld.get_lock_count(), ld.get_lock_breach_count()), locked and ld.get_lock_count() >= 1, ld_detail(ld))
    calls0 = ld.get_apply_attempt_count()
    answer = ld.set_build_for_test("Strength")
    yield 0.5
    ld = P()["ld"]
    check("B7 a choice made in the fight is Deferred (%s), the state is Deferred (%s), counted once (%d)" % (answer, ld.get_state_name(), ld.get_deferred_count()), answer == "Deferred" and ld.get_state_name() == "Deferred" and ld.get_deferred_count() == 1, ld_detail(ld))
    yield 4.5
    ld = P()["ld"]
    check("B7 for 4.5 s the player keeps the dual swords and nothing is called in the pack (style %s, calls %d -> %d)" % (ld.get_actual_style_name(), calls0, ld.get_apply_attempt_count()), ld.get_actual_style_name() == STYLE["Dex"] and ld.get_apply_attempt_count() == calls0, ld_detail(ld))
    check("B7 the HUD line says what is held and that the new build comes next fight (%s)" % ld.get_build_line(), ld.get_build_line() == LINE["Dex"] + " - next fight", "")
    # a real quickslot press in the fight does not leave the build
    press("IA_QuickSlotRight", 0.15)
    yield 4.0
    ld = P()["ld"]
    check("B7 a real IA_QuickSlotRight press in the fight does not change the style (%s; breaches %d); the control press with the slot free did change it (%s -> %s)" % (ld.get_actual_style_name(), ld.get_lock_breach_count(), style0, control_style),
          control_changed and ld.get_actual_style_name() == STYLE["Dex"] and ld.get_lock_breach_count() == 0, "if the control did not change the style the press never reaches the pack's cycle (or the slot holds one weapon) and this proves nothing; if this fails with a control the lock did not stop the pack's cycle: " + ld_detail(ld))
    # the fight resets: the slot is free and the deferred Strength build is applied
    unlocks0 = P()["ld"].get_unlock_count()
    P()["enc"].reset_for_test()
    freed = yield from until(lambda: not P()["ld"].is_weapon_slot_locked(), 3.0)
    ok = yield from until(lambda: P()["ld"].get_actual_style_name() == STYLE["Strength"] and P()["ld"].get_state_name() == "Idle", 10.0)
    yield 0.4
    ld = P()["ld"]
    check("B7 after the reset the slot is unlocked (unlocks %d) and the deferred Strength build is applied within 10 s (%s, %s)" % (ld.get_unlock_count(), ld.get_actual_style_name(), ld.get_state_name()), freed and ld.get_unlock_count() > unlocks0 and ok, ld_detail(ld))
    check("B7 the HUD line says Strength again and the claymore's ability is granted", ld.get_build_line() == LINE["Strength"] and ld.has_weapon_ability_for_test(ABILITY["Strength"]), "")
    dump_events("B7")


def b8_starter():
    yield from to_dormant()
    answer, ok = yield from equip("Starter")
    ld = P()["ld"]
    d = ld_detail(ld)
    check("B8 Starter is Accepted (%s) and within 8 s the player holds SwordCombatStyle, idle" % answer, answer == "Accepted" and ok and ld.get_actual_style_name() == STYLE["Starter"], d)
    check("B8 GA_Sword_Melee_C is back, the claymore's and the dual swords' abilities are gone", ld.has_weapon_ability_for_test(ABILITY["Starter"]) and not ld.has_weapon_ability_for_test(ABILITY["Strength"]) and not ld.has_weapon_ability_for_test(ABILITY["Dex"]), "")
    check("B8 the weapon actor in the slot is BP_ToughSword_C (%s)" % ld.get_equipped_actor_class_name(), ld.get_equipped_actor_class_name() == ACTOR["Starter"], "")
    check("B8 the HUD line says the starter sword (%s)" % ld.get_build_line(), ld.get_build_line() == LINE["Starter"] and ld.get_build_name() == "Starter", "")
    dump_events("B8")


def b9_selectors():
    yield from to_dormant()
    ld = P()["ld"]
    ld.reset_counters_for_test()
    console('rpg.Build "Dex"')
    chosen = yield from until(lambda: P()["ld"].has_choice() and P()["ld"].get_chosen_build_name() == "Dex", 1.5)
    check("B9 the console variable rpg.Build Dex sets the choice within 1.5 s", chosen, ld_detail(P()["ld"]))
    ok = yield from until(lambda: P()["ld"].get_actual_style_name() == STYLE["Dex"] and P()["ld"].get_state_name() == "Idle", 8.0)
    ld = P()["ld"]
    check("B9 and the dual swords are equipped (%s, %s)" % (ld.get_actual_style_name(), ld.get_state_name()), ok, ld_detail(ld))
    inv0, calls0 = ld.get_invalid_request_count(), ld.get_apply_attempt_count()
    console('rpg.Build "Banana"')
    yield 0.8
    ld = P()["ld"]
    check("B9 rpg.Build Banana is ignored and counted (invalid %d -> %d), the choice stays Dex (%s), no call (%d -> %d)" % (inv0, ld.get_invalid_request_count(), ld.get_chosen_build_name(), calls0, ld.get_apply_attempt_count()),
          ld.get_invalid_request_count() == inv0 + 1 and ld.get_chosen_build_name() == "Dex" and ld.has_choice() and ld.get_apply_attempt_count() == calls0, ld_detail(ld))
    console('rpg.Build ""')
    yield 0.8
    ld = P()["ld"]
    check("B9 rpg.Build empty clears the choice and calls nothing (choice %s, state %s, calls %d -> %d), the dual swords stay (%s)" % (ld.has_choice(), ld.get_state_name(), calls0, ld.get_apply_attempt_count(), ld.get_actual_style_name()),
          (not ld.has_choice()) and ld.get_state_name() == "Idle" and ld.get_apply_attempt_count() == calls0 and ld.get_actual_style_name() == STYLE["Dex"], ld_detail(ld))
    console('rpg.Build "Starter"')
    ok = yield from until(lambda: P()["ld"].get_actual_style_name() == STYLE["Starter"] and P()["ld"].get_state_name() == "Idle", 8.0)
    ld = P()["ld"]
    check("B9 rpg.Build Starter puts the sword back (%s, %s)" % (ld.get_actual_style_name(), ld.get_state_name()), ok and ld.has_choice(), ld_detail(ld))
    console('rpg.Build ""')
    yield 0.5


def b10_respawn():
    """The last scenario: the player dies, the pack gives the new pawn its default sword, the new pawn's loadout applies the choice again (the variable is process wide)."""
    yield from to_dormant()
    answer, ok = yield from equip("Strength")
    ld = P()["ld"]
    check("B10 Strength is equipped before the death (%s, %s)" % (ld.get_actual_style_name(), answer), ok, ld_detail(ld))
    old = P()["pawn"].get_name()
    gen0 = P()["enc"].get_generation()
    P()["dbg"].debug_set_player_health(0.0)
    respawned = yield from until(lambda: P()["pawn"] is not None and P()["pawn"].get_name() != old, 25.0)
    check("B10 the player respawns as a new pawn", respawned, "")
    yield 1.0
    p = P()
    ld = p["ld"]
    check("B10 the encounter reset (generation %d -> %d) and the new pawn has its own loadout" % (gen0, p["enc"].get_generation() if p["enc"] else -1), p["enc"] is not None and p["enc"].get_generation() > gen0 and ld is not None, "")
    if ld is None:
        for what in ("the new pawn applies Strength again", "the line says Strength", "no deferral is stuck"):
            check("B10 %s (skipped: no loadout)" % what, False)
    else:
        ok = yield from until(lambda: P()["ld"] is not None and P()["ld"].get_actual_style_name() == STYLE["Strength"] and P()["ld"].get_state_name() == "Idle", 12.0)
        ld = P()["ld"]
        check("B10 the new pawn applied the choice again within 12 s (%s, %s)" % (ld.get_actual_style_name(), ld.get_state_name()), ok, ld_detail(ld))
        check("B10 the line says Strength (%s) and the claymore's ability is granted" % ld.get_build_line(), ld.get_build_line() == LINE["Strength"] and ld.has_weapon_ability_for_test(ABILITY["Strength"]), "")
        check("B10 no deferral is stuck and nothing failed (state %s, deferred %d, failures %d)" % (ld.get_state_name(), ld.get_deferred_count(), ld.get_apply_failure_count()), ld.get_state_name() == "Idle" and ld.get_apply_failure_count() == 0, "a deferral for one tick while the encounter resets is accepted: " + ld_detail(ld))
        dump_events("B10")
    # everything back to Starter
    answer, ok = yield from equip("Starter")
    ld = P()["ld"]
    check("B10 back to Starter: the sword is held (%s, %s)" % (ld.get_actual_style_name(), answer), ok and ld.get_build_line() == LINE["Starter"], ld_detail(ld))
    ld.set_build_for_test("")
    yield 0.5


def script():
    p = P()
    if p["ld"] is None:
        check("B0 the pawn has the RPGBuildLoadout component (add the attach line of Documentation/M13_CODE_NOTES.md to RPGPlayerMovesSubsystem.cpp)", False,
              "components: %s" % [c.get_class().get_name() for c in p["pawn"].get_components_by_class(unreal.ActorComponent)] if p["pawn"] else "no pawn")
        return
    yield from b0_start()
    yield from b1_no_choice()
    yield from b2_strength_equip()
    yield from b3_strength_numbers()
    yield from b5_dex_equip()
    yield from b6_dex_numbers()
    yield from b7_defer_and_lock()
    yield from b8_starter()
    yield from b9_selectors()
    yield from b10_respawn()


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        console('rpg.Build ""')  # process wide: it must not stay set for the next driver (first, in its own try)
    except Exception:
        pass
    try:
        dump_events("end")
        P()["swing"].clear_cost_overrides()
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
            console('rpg.Build ""')  # a value left by an earlier run would be applied by the first pawn (rpg.Build is process wide)
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
        s["nopawn"] = s.get("nopawn", 0.0) + dt
        if s["nopawn"] > 40.0 and s["gen"] is not None:
            check("the player has a pawn (none for 40 s: the respawn did not come)", False)
            finish()
        return
    s["nopawn"] = 0.0
    if s["now"] < s["press_until"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(IA + s["action"]), unreal.Vector(1, 0, 0))
    if s["hpw"] is not None:
        hp = attr(boss, "Attribute.Health")  # every drop of the boss's health between two frames is one hit (or one bleed proc)
        if hp is not None:
            if s["hpw"]["last"] is not None and hp < s["hpw"]["last"] - 0.01:
                s["hpw"]["events"] += 1
            s["hpw"]["last"] = hp
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
