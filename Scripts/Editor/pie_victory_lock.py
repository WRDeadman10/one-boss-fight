"""Gate 2 / L11: after the victory no combat action can run and a retry is offered. V0 control: a Light Attack press plays a player montage; V1 the boss dies, victory fires once and the player is locked;
V2 the same press now does nothing; V3 the retry line is hidden at first and shown after 3 s; V4 R reloads the level: the new boss sleeps, no victory counted, the player is free again.
Run pie_debug_overlay.py once after an editor start first. Log prefix [VictoryLock]."""
import unreal

log = lambda m: unreal.log("[VictoryLock] " + m)
IA_NORMAL = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_NormalAttack"
results = []
S = {"phase": "start", "t": 0.0, "i": 0, "next": 0.0, "mem": {}, "press_until": 0.0, "montages": [], "world": None}
handle = None


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def pawn_montage(pawn):
    mc = pawn.get_components_by_class(unreal.SkeletalMeshComponent)[0]
    inst = mc.get_anim_instance()
    m = inst.get_current_active_montage() if inst else None
    return m.get_name() if m else None


def press(seconds):
    S["press_until"] = seconds  # the step timer restarts at 0 right after the step runs
    S["montages"] = []


def s_wake(w, pc, pawn, boss):
    enc, dbg = comp(boss, "RPGBossEncounter"), comp(boss, "RPGCombatDebug")
    enc.wake()
    enc.hold_for_test(True)
    dbg.debug_refill_player()


def s_v0_press(w, pc, pawn, boss):
    press(0.2)


def s_v0_check(w, pc, pawn, boss):
    check("V0 control: a Light Attack press plays a player montage", len(S["montages"]) > 0, str(S["montages"][:3]))


def s_kill(w, pc, pawn, boss):
    S["mem"]["hp"] = None
    comp(boss, "RPGCombatDebug").debug_kill_boss()


def s_v1_check(w, pc, pawn, boss):
    hud = comp(boss, "RPGBossHud")
    check("V1 victory fired once", hud.get_victory_count() == 1, str(hud.get_victory_count()))
    check("V1 the player is locked", hud.is_player_locked())
    check("V1 the retry line is not shown yet", not hud.get_widget().is_retry_shown())
    S["mem"]["hud"] = hud
    S["mem"]["widget"] = hud.get_widget()


def s_v2_press(w, pc, pawn, boss):
    press(0.2)


def s_v2_check(w, pc, pawn, boss):
    check("V2 a Light Attack press after the victory does nothing", len(S["montages"]) == 0, str(S["montages"][:3]))


def s_v3_check(w, pc, pawn, boss):
    wd = S["mem"]["widget"]
    check("V3 the retry line is shown after the delay", wd.is_retry_shown())
    S["world"] = str(w)


def s_v4_press_r(w, pc, pawn, boss):
    unreal.RPGInputTestUtils.set_key_down(pc, "R", True)


def s_v4_release_r(w, pc, pawn, boss):
    unreal.RPGInputTestUtils.set_key_down(pc, "R", False)


def s_v4_check(w, pc, pawn, boss):
    hud = comp(boss, "RPGBossHud")
    check("V4 the level was reloaded", str(w) != S["world"], "%s -> %s" % (S["world"], w))
    check("V4 the new boss sleeps and no victory is counted", hud.get_state_name() == "Dormant" and hud.get_victory_count() == 0, "%s %d" % (hud.get_state_name(), hud.get_victory_count()))
    check("V4 the player is free again", not hud.is_player_locked())


STEPS = [
    (9.0, s_wake), (3.0, s_v0_press), (1.0, s_v0_check),
    (2.0, s_kill), (0.6, s_v1_check), (0.3, s_v2_press), (1.0, s_v2_check),
    (2.0, s_v3_check), (0.3, s_v4_press_r), (0.15, s_v4_release_r), (9.0, s_v4_check),
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
    if pawn is None:
        return
    if s["t"] < s["press_until"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(IA_NORMAL), unreal.Vector(1, 0, 0))
    m = pawn_montage(pawn)
    if m and m not in s["montages"]:
        s["montages"].append(m)
    if s["t"] < s["next"]:
        return
    if s["i"] < len(STEPS) and STEPS[s["i"]][1] in (s_v4_check,) and boss is None:
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
    s["press_until"] = max(0.0, s["press_until"])
    s["next"] = STEPS[s["i"]][0] if s["i"] < len(STEPS) else 0.5


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
