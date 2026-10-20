"""PIE test of the boss HUD and the victory signal (RPGBossHud): dormant -> fighting (banner, bar), phase two subtitle, stance break flash, riposte prompt, victory once, reset, second victory.
Run pie_debug_overlay.py once after an editor start first (warm-up). Log prefix [BossHud]; screenshots (with UI) go to Saved/Screenshots/WindowsEditor."""
import unreal

log = lambda m: unreal.log("[BossHud] " + m)
results = []
held = {}
state = {"phase": "start", "t": 0.0, "i": 0, "next": 0.0}
handle = None


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def ctx():
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return w, pc, pawn, boss


def place_player(pawn, pc, boss, dist, facing_boss=True):
    bl = boss.get_actor_location()
    fwd = boss.get_actor_forward_vector()
    p = unreal.Vector(bl.x + fwd.x * dist, bl.y + fwd.y * dist, bl.z + 20)
    yaw = unreal.MathLibrary.find_look_at_rotation(p, bl).yaw
    pawn.set_actor_location_and_rotation(p, unreal.Rotator(0, 0, yaw), False, True)
    pc.set_control_rotation(unreal.Rotator(roll=0, pitch=-6, yaw=yaw))


def shot(w, name):
    unreal.SystemLibrary.execute_console_command(w, "Shot ShowUI")
    log("screenshot (ShowUI) " + name)


def s_dormant(w, pc, pawn, boss):
    hud, enc, dbg = comp(boss, "RPGBossHud"), comp(boss, "RPGBossEncounter"), comp(boss, "RPGCombatDebug")
    dbg.debug_refill_player()
    check("hud component exists", hud is not None)
    check("starts dormant", hud.get_state_name() == "Dormant", hud.get_state_name())
    wd = hud.get_widget()
    check("widget created", wd is not None)
    check("bar hidden while dormant", wd is not None and not wd.is_bar_shown())
    place_player(pawn, pc, boss, 650)
    enc.wake()
    enc.hold_for_test(True)


def s_fighting(w, pc, pawn, boss):
    hud = comp(boss, "RPGBossHud")
    wd = hud.get_widget()
    check("state Fighting after wake", hud.get_state_name() == "Fighting", hud.get_state_name())
    check("bar shown", wd.is_bar_shown())
    banner = str(wd.get_banner_text())
    check("name banner shows", "EMBER WARDEN" in banner, banner)
    check("bar full", wd.get_bar_percent() > 0.95, "%.2f" % wd.get_bar_percent())
    shot(w, "fighting_banner")


def s_phase_two(w, pc, pawn, boss):
    hud, dbg = comp(boss, "RPGBossHud"), comp(boss, "RPGCombatDebug")
    dbg.debug_refill_player()
    dbg.debug_set_boss_health_fraction(0.55)


def s_phase_two_check(w, pc, pawn, boss):
    hud, dbg, ph = comp(boss, "RPGBossHud"), comp(boss, "RPGCombatDebug"), comp(boss, "RPGBossPhases")
    wd = hud.get_widget()
    dbg.debug_refill_player()
    check("phase two reached", ph.is_phase_two())
    check("bar follows health (about 0.55)", abs(wd.get_bar_percent() - 0.55) < 0.05, "%.2f" % wd.get_bar_percent())
    shot(w, "phase_two")


def s_flash(w, pc, pawn, boss):
    hud, st, enc = comp(boss, "RPGBossHud"), comp(boss, "RPGBossStagger"), comp(boss, "RPGBossEncounter")
    enc.hold_for_test(True)
    st.force_break_for_test()


def s_flash_check(w, pc, pawn, boss):
    hud = comp(boss, "RPGBossHud")
    check("posture flash on break", hud.is_posture_flashing())
    check("no prompt while the player is far", not hud.is_prompt_shown())


def s_prompt(w, pc, pawn, boss):
    place_player(pawn, pc, boss, 110)


def s_prompt_check(w, pc, pawn, boss):
    hud, st = comp(boss, "RPGBossHud"), comp(boss, "RPGBossStagger")
    check("boss is down", st.is_critical_window_open())
    check("riposte prompt shows in range", hud.is_prompt_shown(), "available=%s" % st.is_riposte_available(pawn))
    shot(w, "prompt")


def s_kill(w, pc, pawn, boss):
    comp(boss, "RPGCombatDebug").debug_kill_boss()


def s_kill_check(w, pc, pawn, boss):
    hud = comp(boss, "RPGBossHud")
    wd = hud.get_widget()
    check("state Victory", hud.get_state_name() == "Victory", hud.get_state_name())
    check("victory fired once", hud.get_victory_count() == 1, str(hud.get_victory_count()))
    banner = str(wd.get_banner_text())
    check("victory banner", "FALLS" in banner, banner)
    held["widget"] = wd
    check("bar hidden on victory", not wd.is_bar_shown())
    check("no prompt on victory", not hud.is_prompt_shown())
    shot(w, "victory")


def s_reset(w, pc, pawn, boss):
    comp(boss, "RPGBossEncounter").reset_for_test()


def s_reset_check(w, pc, pawn, boss):
    hud = comp(boss, "RPGBossHud")
    wd = hud.get_widget()
    check("dormant after reset", hud.get_state_name() == "Dormant", hud.get_state_name())
    check("bar hidden after reset", not wd.is_bar_shown())
    check("banner cleared after reset", str(wd.get_banner_text()) == "", str(wd.get_banner_text()))
    check("no victory counted by a reset", hud.get_victory_count() == 0)
    check("back to phase one", not comp(boss, "RPGBossPhases").is_phase_two())
    enc = comp(boss, "RPGBossEncounter")
    comp(boss, "RPGCombatDebug").debug_refill_player()
    enc.wake()
    enc.hold_for_test(True)


def s_second_fight_check(w, pc, pawn, boss):
    hud = comp(boss, "RPGBossHud")
    check("fighting again after a reset", hud.get_state_name() == "Fighting", hud.get_state_name())
    check("bar full again", hud.get_widget().get_bar_percent() > 0.95, "%.2f" % hud.get_widget().get_bar_percent())
    check("name banner again on the second wake", "EMBER WARDEN" in str(hud.get_widget().get_banner_text()))
    comp(boss, "RPGCombatDebug").debug_refill_player()
    comp(boss, "RPGBossEncounter").hold_for_test(True)


def s_after_destroy(w, pc, pawn, boss):
    wd = held.get("widget")
    banner = str(wd.get_banner_text()) if wd else None
    check("banner survives or boss still alive (boss=%s)" % ("alive" if boss else "destroyed"), (boss is not None) or bool(banner), repr(banner))


def s_end_state(w, pc, pawn, boss):
    wd = held.get("widget")
    check("bar and prompt hidden at the end", wd is not None and not wd.is_bar_shown() and not wd.is_prompt_shown())


STEPS = [
    (9.0, s_dormant, True), (1.6, s_fighting, True), (2.0, s_phase_two, True), (3.5, s_phase_two_check, True), (0.3, s_reset, True), (1.2, s_reset_check, True),
    (1.5, s_second_fight_check, True), (0.5, s_flash, True), (0.3, s_flash_check, True), (1.4, s_prompt, True), (0.6, s_prompt_check, True),
    (0.5, s_kill, True), (1.0, s_kill_check, True), (2.0, s_after_destroy, False), (7.0, s_end_state, False),
]


def _tick(dt):
    global handle
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0, next=STEPS[0][0])
        return
    w, pc, pawn, boss = ctx()
    if pawn is None or s["t"] < s["next"]:
        return
    if boss is None and s["i"] < len(STEPS) and STEPS[s["i"]][2]:
        return
    if s["i"] >= len(STEPS):
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("RESULT %d/%d passed" % (sum(1 for r in results if r), len(results)))
        return
    _, fn, _n = STEPS[s["i"]]
    try:
        fn(w, pc, pawn, boss)
    except Exception:
        import traceback
        check(fn.__name__ + " raised", False, traceback.format_exc())
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
