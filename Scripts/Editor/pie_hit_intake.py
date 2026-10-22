"""
Gate 3, M7: the hit intake (URPGHitIntake on the player) sees every hit the player lands on the boss once, with the right weapon and attack data. The boss is held awake and the player stands 110 cm in front of it;
real input presses: light attack, strong attack, charged attack, a jump attack. Per scenario: the number of intake records against the number of health drops of the boss (each hit costs health), the weapon,
the attack data and the stance of every record. Log prefix [Intake]; ends with RESULT n/m passed. Run with Scripts/run_in_editor.py after the warm-up.
"""
import unreal

log = lambda m: unreal.log("[Intake] " + m)
IA = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
JUMP_KEY = "Gamepad_FaceButton_Bottom"
# name, action, press seconds, jump first, expected attack data, expected kind, expected posture damage (the starter sword's row of the weapon attack table)
SCENARIOS = [
    ("light", "IA_NormalAttack", 0.12, False, "DefaultMeleeAttackData", "Light", 18),
    ("strong", "IA_StrongAttack", 0.12, False, "StrongMeleeAttackData", "Strong", 30),
    ("charged", "IA_ChargedAttack", 1.6, False, "ChargedMeleeAttackData", "Charged", 38),
    ("jump light", "IA_NormalAttack", 0.12, True, "DefaultMeleeAttackData", "JumpLight", 18),
    ("jump heavy", "IA_StrongAttack", 0.12, True, "StrongMeleeAttackData", "JumpHeavy", 38),
]
state = {"phase": "start", "t": 0.0, "step": 0, "wait": 0.0, "c": {}, "ok": 0, "n": 0}
handle = None


def check(name, ok, detail=""):
    state["n"] += 1
    state["ok"] += 1 if ok else 0
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


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    log("RESULT %d/%d passed" % (state["ok"], state["n"]))


def _tick(dt):
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wake", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is None or boss is None:
        return
    enc, dbg = comp(boss, "RPGBossEncounter"), comp(boss, "RPGCombatDebug")
    intake = comp(pawn, "RPGHitIntake")
    mc = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0]
    c = s["c"]
    bl = boss.get_actor_location()
    if s["phase"] == "wake":
        if s["t"] > 9.0 and "woke" not in s:
            s["woke"] = s["t"]
            pawn.set_actor_location_and_rotation(unreal.Vector(bl.x + 700, bl.y, bl.z), unreal.Rotator(0, 180, 0), False, True)
        if "woke" in s:
            dbg.debug_refill_player()
            if (not enc.is_dormant()) and mc.get_anim_instance().get_current_active_montage() is None and s["t"] - s["woke"] > 4.0:
                enc.hold_for_test(True)
                comp(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
                s.update(phase="run", t=0.0, wait=3.0)
                check("the hit intake component exists and is bound to the pack's OnHit", intake is not None and intake.is_hit_intake_bound(), "component %s" % (intake is not None))
        return
    # a press in progress: keep injecting the action every tick (the pack reads the held action)
    if "press_until" in c:
        if s["t"] < c["press_until"]:
            unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(IA + c["action"]), unreal.Vector(1, 0, 0))
        else:
            del c["press_until"]
    # count health drops of the boss, one per frame at most
    hp = attr(boss, "Attribute.Health")
    if hp is not None and "hp" in c and hp < c["hp"] - 0.01:
        c["drops"] = c.get("drops", 0) + 1
    if hp is not None:
        c["hp"] = hp
    if s["t"] < s["wait"]:
        return
    n = s["step"]
    idx = n // 4
    sub = n % 4
    if idx >= len(SCENARIOS):
        finish()
        s["step"] = 999
        return
    name, action, press, jump, expect, kind, posture = SCENARIOS[idx]
    if sub == 0:
        # reset: full boss, full posture, the player in front of it facing it
        dbg.debug_set_boss_health_fraction(1.0)
        dbg.debug_set_boss_posture(100.0)
        dbg.debug_refill_player()
        pawn.set_actor_location_and_rotation(unreal.Vector(bl.x + 110, bl.y, bl.z), unreal.Rotator(0, 180, 0), False, True)
        pc.set_control_rotation(unreal.Rotator(0, 180, 0))
        intake.reset_counters()
        c["drops"] = 0
        c["action"] = action
        s["step"] += 1
        s["wait"] = s["t"] + 1.0
    elif sub == 1:
        c["t0"] = s["t"]
        if jump:
            unreal.RPGInputTestUtils.set_key_down(pc, JUMP_KEY, True)
            c["jump_down_until"] = s["t"] + 0.12
            s["step"] += 1
            s["wait"] = s["t"] + 0.3
        else:
            c["press_until"] = s["t"] + press
            s["step"] += 1
            s["wait"] = s["t"] + press + 2.0
    elif sub == 2:
        if jump:
            unreal.RPGInputTestUtils.set_key_down(pc, JUMP_KEY, False)
            c["press_until"] = s["t"] + press
            s["step"] += 1
            s["wait"] = s["t"] + press + 2.0
        else:
            s["step"] += 1
    elif sub == 3:
        records = intake.get_boss_hit_count()
        lines = list(intake.get_record_lines())
        drops = c.get("drops", 0)
        log("%s: %d intake records, %d health drops, %d other hits" % (name, records, drops, intake.get_other_hit_count()))
        for line in lines:
            log("   " + line)
        check("%s: at least one hit reached the intake" % name, records >= 1, "%d records" % records)
        check("%s: one record per hit (records equal the boss's health drops)" % name, records == drops, "%d records, %d drops" % (records, drops))
        if lines:
            check("%s: the weapon is the sword's combat style" % name, "weapon SwordCombatStyle" in lines[0], lines[0][:120])
            check("%s: the attack data is %s" % (name, expect), all(("attack data %s" % expect) in l for l in lines), "; ".join(l.split("attack data ")[1].split(" (")[0] for l in lines if "attack data " in l))
            check("%s: the kind is %s" % (name, kind), all(("kind %s" % kind) in l for l in lines), "; ".join(l.split("kind ")[1].split(",")[0] for l in lines if "kind " in l))
            check("%s: the weapon attack table row gives posture %d" % (name, posture), all(("posture %d," % posture) in l and "no row" not in l for l in lines), "; ".join(l.split("posture ")[1].split(",")[0] for l in lines if "posture " in l))
            check("%s: the stance is %s" % (name, "airborne or started airborne" if jump else "grounded"), all((("airborne," in l or "started airborne," in l) if jump else (", grounded," in l and "started airborne" not in l)) for l in lines))
        s["step"] += 1
        s["wait"] = s["t"] + 1.0


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
